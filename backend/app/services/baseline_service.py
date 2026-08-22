"""Feature 1: Repo Test Baseline — AI-generates categorized Playwright
tests for a connected repo, incrementally re-scanning only what changed.
"""
from app.database.mongo import get_database
from app.engines.ai.base import BaselineTestGenInput
from app.engines.ai.factory import generate_baseline_tests_with_fallback
from app.intake.workspace import workspace_path
from app.models.base import new_id
from app.models.generated_test import GeneratedTest
from app.services import git_mining, repo_summary
from app.services.playwright_codegen import CATEGORIES, validate_js_syntax

BASELINE_DIR_NAME = "wayam_baseline_tests"
_CATEGORY_PATH_HINTS = {
    "auth": ["auth", "login", "session", "password"],
    "api": ["api", "route", "endpoint", "controller"],
    "crud": ["model", "crud", "repository", "service"],
    "ui_form": ["form"],
    "ui_navigation": ["nav", "router", "page"],
    "ui_component": ["component"],
    "performance": ["perf"],
    "accessibility": ["a11y", "accessib"],
}


class ProjectNotConnected(Exception):
    pass


def _infer_categories_from_changed_files(changed_files: list[str]) -> list[str]:
    matched: list[str] = []
    for path in changed_files:
        lowered = path.lower()
        for category, hints in _CATEGORY_PATH_HINTS.items():
            if any(hint in lowered for hint in hints) and category not in matched:
                matched.append(category)
    return matched or ["integration"]  # a real change with no keyword match still deserves a baseline check


async def run_baseline_scan(org_id: str, user_id: str, project_id: str) -> dict:
    workspace = workspace_path(project_id)
    if not workspace.exists():
        raise ProjectNotConnected("This project has no connected workspace to scan.")

    db = get_database()
    project_doc = await db.projects.find_one({"_id": project_id, "organization_id": org_id})
    last_scanned = project_doc.get("baseline_last_scanned_commit") if project_doc else None

    is_git = await git_mining.is_git_repo(workspace)
    head_sha = await git_mining.get_head_sha(workspace) if is_git else None

    if is_git and last_scanned and head_sha == last_scanned:
        return {"scan_id": None, "generated": 0, "source": "none", "categories_scanned": [], "message": "No new commits since the last baseline scan."}

    if is_git and last_scanned and head_sha:
        changed = await git_mining.get_changed_files(workspace, last_scanned)
        categories = _infer_categories_from_changed_files(changed) if changed else []
        if not categories:
            return {"scan_id": None, "generated": 0, "source": "none", "categories_scanned": [], "message": "No file changes detected since the last baseline scan."}
    else:
        categories = list(CATEGORIES)  # first scan: full baseline across every category

    summary = repo_summary.build_summary(workspace)
    generated, source = await generate_baseline_tests_with_fallback(
        BaselineTestGenInput(repo_summary=summary, categories=categories)
    )

    baseline_dir = workspace / BASELINE_DIR_NAME
    baseline_dir.mkdir(exist_ok=True)

    scan_id = new_id()
    persisted: list[GeneratedTest] = []
    rejected = 0

    for item in generated:
        if not await validate_js_syntax(item.code):
            rejected += 1
            continue  # never persist AI output that isn't real, runnable code

        filename = f"{item.category}_{new_id()[:8]}.spec.js"
        file_path = baseline_dir / filename
        file_path.write_text(item.code)

        record = GeneratedTest(
            organization_id=org_id,
            project_id=project_id,
            scan_id=scan_id,
            category=item.category,
            title=item.title,
            code=item.code,
            confidence=item.confidence,
            source=source,
            commit_sha=head_sha,
            file_path=str(file_path.relative_to(workspace)),
            origin="baseline",
        )
        await db.generated_tests.insert_one(record.model_dump(by_alias=True))
        persisted.append(record)

    if head_sha:
        await db.projects.update_one(
            {"_id": project_id, "organization_id": org_id},
            {"$set": {"baseline_last_scanned_commit": head_sha}},
        )

    return {
        "scan_id": scan_id,
        "generated": len(persisted),
        "rejected_invalid_syntax": rejected,
        "source": source,
        "categories_scanned": categories,
        "tests": [t.model_dump() for t in persisted],
    }


async def list_generated_tests(org_id: str, project_id: str) -> list[GeneratedTest]:
    db = get_database()
    cursor = db.generated_tests.find({"organization_id": org_id, "project_id": project_id}).sort("created_at", -1)
    return [GeneratedTest.model_validate(d) async for d in cursor]
