"""Real SAST scanning via Semgrep's auto ruleset, invoked from an isolated
tools venv (backend/.tools-venv) so its dependency pins never collide with
the FastAPI app's own dependency tree."""
import asyncio
import json
import shutil
from pathlib import Path

from app.engines.security.base import RawFinding, SecurityScanProvider, SecurityScanUnavailable

TOOLS_VENV = Path(__file__).resolve().parent.parent.parent.parent / ".tools-venv"
SEMGREP_BIN = TOOLS_VENV / "bin" / "semgrep"
SCAN_TIMEOUT_SECONDS = 120

_SEVERITY_MAP = {"ERROR": "high", "WARNING": "medium", "INFO": "low"}


class SemgrepProvider(SecurityScanProvider):
    name = "semgrep"

    def applies_to(self, workspace_path: Path) -> bool:
        # Semgrep's auto ruleset works across languages; only gate on the
        # binary actually being installed — not on any specific manifest.
        return True

    async def scan(self, workspace_path: Path) -> list[RawFinding]:
        semgrep = str(SEMGREP_BIN) if SEMGREP_BIN.exists() else shutil.which("semgrep")
        if not semgrep:
            raise SecurityScanUnavailable(
                "Semgrep is not installed on this server (expected at "
                f"{SEMGREP_BIN} or on PATH)."
            )

        proc = await asyncio.create_subprocess_exec(
            semgrep, "--config=auto", "--json", "--quiet", "--timeout", "60", str(workspace_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=SCAN_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            raise SecurityScanUnavailable(f"Semgrep scan timed out after {SCAN_TIMEOUT_SECONDS}s.")

        try:
            data = json.loads(stdout)
        except json.JSONDecodeError:
            raise SecurityScanUnavailable(
                f"Semgrep produced no parseable output: {stderr.decode(errors='replace')[-500:]}"
            )

        findings: list[RawFinding] = []
        for result in data.get("results", []):
            severity = _SEVERITY_MAP.get(result.get("extra", {}).get("severity", "INFO"), "low")
            findings.append(RawFinding(
                tool="semgrep",
                severity=severity,
                file=result.get("path"),
                line=result.get("start", {}).get("line"),
                issue=result.get("check_id", "unknown-rule"),
                evidence=(result.get("extra", {}).get("lines") or "")[:500],
                recommendation=result.get("extra", {}).get("message", "Review the flagged code for the referenced rule."),
            ))
        return findings
