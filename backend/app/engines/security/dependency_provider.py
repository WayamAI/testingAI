"""Real dependency vulnerability scanning: pip-audit for Python
(requirements.txt), npm audit for Node (package.json / package-lock.json).
"""
import asyncio
import json
import shutil
from pathlib import Path

from app.engines.security.base import RawFinding, SecurityScanProvider, SecurityScanUnavailable

TOOLS_VENV = Path(__file__).resolve().parent.parent.parent.parent / ".tools-venv"
PIP_AUDIT_BIN = TOOLS_VENV / "bin" / "pip-audit"
SCAN_TIMEOUT_SECONDS = 90

_PIP_AUDIT_SEVERITY_DEFAULT = "medium"  # pip-audit doesn't always report severity; be conservative


class PipAuditProvider(SecurityScanProvider):
    name = "pip-audit"

    def applies_to(self, workspace_path: Path) -> bool:
        return (workspace_path / "requirements.txt").exists()

    async def scan(self, workspace_path: Path) -> list[RawFinding]:
        pip_audit = str(PIP_AUDIT_BIN) if PIP_AUDIT_BIN.exists() else shutil.which("pip-audit")
        if not pip_audit:
            raise SecurityScanUnavailable(
                f"pip-audit is not installed on this server (expected at {PIP_AUDIT_BIN} or on PATH)."
            )

        reqs = workspace_path / "requirements.txt"
        proc = await asyncio.create_subprocess_exec(
            pip_audit, "-r", str(reqs), "--format", "json",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=SCAN_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            raise SecurityScanUnavailable(f"pip-audit timed out after {SCAN_TIMEOUT_SECONDS}s.")

        try:
            data = json.loads(stdout)
        except json.JSONDecodeError:
            raise SecurityScanUnavailable(
                f"pip-audit produced no parseable output: {stderr.decode(errors='replace')[-500:]}"
            )

        findings: list[RawFinding] = []
        for dep in data.get("dependencies", []):
            for vuln in dep.get("vulns", []):
                findings.append(RawFinding(
                    tool="pip-audit",
                    severity=_PIP_AUDIT_SEVERITY_DEFAULT,
                    file="requirements.txt",
                    line=None,
                    issue=f"{dep.get('name')} {dep.get('version')}: {vuln.get('id')}",
                    evidence=", ".join(vuln.get("aliases", [])) or vuln.get("id", ""),
                    recommendation=(
                        f"Upgrade to a fixed version: {', '.join(vuln.get('fix_versions', []) or ['see advisory'])}"
                    ),
                ))
        return findings


class NpmAuditProvider(SecurityScanProvider):
    name = "npm-audit"

    def applies_to(self, workspace_path: Path) -> bool:
        return (workspace_path / "package.json").exists()

    async def scan(self, workspace_path: Path) -> list[RawFinding]:
        npm = shutil.which("npm")
        if not npm:
            raise SecurityScanUnavailable("npm is not installed on this server.")

        proc = await asyncio.create_subprocess_exec(
            npm, "audit", "--json",
            cwd=str(workspace_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=SCAN_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            raise SecurityScanUnavailable(f"npm audit timed out after {SCAN_TIMEOUT_SECONDS}s.")

        try:
            data = json.loads(stdout)
        except json.JSONDecodeError:
            # npm audit exits non-zero with vulnerabilities present but
            # still emits JSON on stdout in that case; only truly empty
            # output is unparseable.
            raise SecurityScanUnavailable("npm audit produced no parseable output (dependencies may not be installed yet).")

        findings: list[RawFinding] = []
        for name, vuln in data.get("vulnerabilities", {}).items():
            findings.append(RawFinding(
                tool="npm-audit",
                severity=vuln.get("severity", "medium"),
                file="package.json",
                line=None,
                issue=f"{name}: {vuln.get('severity', 'unknown')} severity vulnerability",
                evidence=vuln.get("range", ""),
                recommendation="Run `npm audit fix` or upgrade the affected package directly.",
            ))
        return findings
