"""Real DOM candidate discovery and live selector validation for
self-healing — shells out to a real headless Chromium via the frontend's
already-installed @playwright/test, never fabricates a candidate list or
a validation result.
"""
import asyncio
import json
from pathlib import Path

from app.engines.ai.base import DomCandidate

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
SCAN_SCRIPT = SCRIPTS_DIR / "dom_scan.js"
VALIDATE_SCRIPT = SCRIPTS_DIR / "validate_selector.js"
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent.parent / "frontend"
SCAN_TIMEOUT_SECONDS = 30


class DomScanError(Exception):
    pass


def _node_modules() -> Path:
    node_modules = FRONTEND_DIR / "node_modules"
    if not node_modules.exists():
        raise DomScanError(
            f"Playwright is not installed at {node_modules} — run `npm install` in frontend/ first."
        )
    return node_modules


async def _run_node_script(script: Path, args: list[str]) -> str:
    node_modules = _node_modules()
    proc = await asyncio.create_subprocess_exec(
        "node", str(script), *args,
        env={"NODE_PATH": str(node_modules), "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"},
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=SCAN_TIMEOUT_SECONDS)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        raise DomScanError(f"{script.name} timed out after {SCAN_TIMEOUT_SECONDS}s.")

    if proc.returncode != 0:
        raise DomScanError(f"{script.name} failed: {stderr.decode(errors='replace')[-500:]}")
    return stdout.decode()


async def scan_live_dom(url: str) -> list[DomCandidate]:
    stdout = await _run_node_script(SCAN_SCRIPT, [url])
    try:
        raw = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise DomScanError(f"DOM scan produced no parseable output: {exc}")
    return [DomCandidate(**item) for item in raw]


async def validate_selector_live(url: str, selector: str) -> int:
    """Returns the real number of elements the selector resolves to on the
    live page right now — the caller decides what count is acceptable."""
    stdout = await _run_node_script(VALIDATE_SCRIPT, [url, selector])
    try:
        return json.loads(stdout)["count"]
    except (json.JSONDecodeError, KeyError) as exc:
        raise DomScanError(f"Selector validation produced no parseable output: {exc}")
