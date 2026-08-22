"""Feature 3: Live Test Runner — given a real running app URL, scans its
real DOM to inform AI-generated Playwright tests, then actually executes
them for real in headless Chromium (reusing the frontend's already-
installed @playwright/test), capturing a real screenshot per test and
persisting full run history. Per-test (not per-step) screenshots in this
first cut — stated honestly, not oversold.
"""
import asyncio
import json
from pathlib import Path

from app.database.mongo import get_database
from app.engines.ai.base import BaselineTestGenInput, DomCandidate
from app.engines.ai.factory import generate_baseline_tests_with_fallback
from app.intake.workspace import workspace_path
from app.models.base import new_id
from app.models.live_run import LiveRun, LiveRunResult
from app.services.dom_scan_service import DomScanError, FRONTEND_DIR, scan_live_dom
from app.services.playwright_codegen import validate_js_syntax

LIVE_RUNS_DIR_NAME = "wayam_live_runs"
RUN_TIMEOUT_SECONDS = 60
PLAYWRIGHT_BIN = FRONTEND_DIR / "node_modules" / ".bin" / "playwright"


class LiveRunnerError(Exception):
    pass


def _infer_live_categories(candidates: list[DomCandidate]) -> list[str]:
    categories = ["ui_component"]  # always a real baseline check
    haystack = " ".join(f"{c.tag} {c.text} {c.selector_hint}".lower() for c in candidates)
    if "password" in haystack or "log in" in haystack or "sign in" in haystack:
        categories.append("auth")
    if any(c.tag in ("input", "textarea", "select") for c in candidates):
        categories.append("ui_form")
    if any(c.tag == "a" for c in candidates):
        categories.append("ui_navigation")
    return categories[:4]  # keep real-browser runtime bounded


def _build_page_summary(url: str, candidates: list[DomCandidate]) -> str:
    lines = [f"Live page at {url} — {len(candidates)} interactive element(s) found:"]
    for c in candidates[:30]:
        lines.append(f"  <{c.tag}> \"{c.text}\" -> {c.selector_hint}")
    return "\n".join(lines)


async def run_live_tests(org_id: str, project_id: str, url: str) -> dict:
    if not PLAYWRIGHT_BIN.exists():
        raise LiveRunnerError(f"Playwright is not installed at {PLAYWRIGHT_BIN} — run `npm install` in frontend/ first.")

    try:
        candidates = await scan_live_dom(url)
    except DomScanError as exc:
        raise LiveRunnerError(str(exc))

    categories = _infer_live_categories(candidates)
    summary = _build_page_summary(url, candidates)
    generated, source = await generate_baseline_tests_with_fallback(
        BaselineTestGenInput(repo_summary=summary, categories=categories)
    )

    scan_id = new_id()
    run_dir = workspace_path(project_id) / LIVE_RUNS_DIR_NAME / scan_id
    run_dir.mkdir(parents=True, exist_ok=True)

    config_path = run_dir / "playwright.config.js"
    config_path.write_text(
        "module.exports = { use: { baseURL: " + json.dumps(url) + ", screenshot: 'on' }, timeout: 15000 };\n"
    )

    category_by_file: dict[str, str] = {}
    rejected = 0
    for item in generated:
        if not await validate_js_syntax(item.code):
            rejected += 1
            continue
        filename = f"{item.category}_{new_id()[:8]}.spec.js"
        (run_dir / filename).write_text(item.code)
        category_by_file[filename] = item.category

    if not category_by_file:
        raise LiveRunnerError("No syntactically valid tests could be generated for this page.")

    results_dir = run_dir / "test-results"
    report_path = run_dir / "report.json"
    proc = await asyncio.create_subprocess_exec(
        str(PLAYWRIGHT_BIN), "test", str(run_dir),
        f"--config={config_path}", "--reporter=json", f"--output={results_dir}",
        cwd=str(FRONTEND_DIR),
        env={"NODE_PATH": str(FRONTEND_DIR / "node_modules"), "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"},
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=RUN_TIMEOUT_SECONDS)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        raise LiveRunnerError(f"Live test run timed out after {RUN_TIMEOUT_SECONDS}s.")

    try:
        report = json.loads(stdout)
    except json.JSONDecodeError:
        raise LiveRunnerError(f"Playwright produced no parseable report: {stderr.decode(errors='replace')[-500:]}")

    db = get_database()
    run_id = new_id()
    persisted: list[LiveRunResult] = []
    passed = failed = 0

    for suite in report.get("suites", []):
        for spec in suite.get("specs", []):
            file_name = Path(spec.get("file", "")).name
            category = category_by_file.get(file_name, "unknown")
            for test in spec.get("tests", []):
                for result in test.get("results", []):
                    status = result.get("status", "unknown")
                    screenshot = next(
                        (a["path"] for a in result.get("attachments", []) if a.get("name") == "screenshot"), None
                    )
                    record = LiveRunResult(
                        organization_id=org_id, project_id=project_id, run_id=run_id,
                        title=spec.get("title", "unnamed"), category=category, status=status,
                        duration_ms=int(result.get("duration", 0)), screenshot_path=screenshot,
                    )
                    await db.live_run_results.insert_one(record.model_dump(by_alias=True))
                    persisted.append(record)
                    if status == "passed":
                        passed += 1
                    elif status in ("failed", "timedOut", "interrupted"):
                        failed += 1

    run_record = LiveRun(
        id=run_id, organization_id=org_id, project_id=project_id, url=url, categories=categories,
        source=source, total=len(persisted), passed=passed, failed=failed, rejected_invalid_syntax=rejected,
    )
    await db.live_runs.insert_one(run_record.model_dump(by_alias=True))

    return {
        "run_id": run_id, "url": url, "categories": categories, "source": source,
        "total": len(persisted), "passed": passed, "failed": failed, "rejected_invalid_syntax": rejected,
        "results": [r.model_dump() for r in persisted],
    }


async def list_runs(org_id: str, project_id: str) -> list[LiveRun]:
    db = get_database()
    cursor = db.live_runs.find({"organization_id": org_id, "project_id": project_id}).sort("created_at", -1)
    return [LiveRun.model_validate(d) async for d in cursor]


async def get_run_results(org_id: str, run_id: str) -> list[LiveRunResult]:
    db = get_database()
    cursor = db.live_run_results.find({"organization_id": org_id, "run_id": run_id})
    return [LiveRunResult.model_validate(d) async for d in cursor]
