from pathlib import Path

import pytest

from app.engines.security.dependency_provider import PipAuditProvider
from app.engines.security.semgrep_provider import SemgrepProvider

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.asyncio
async def test_pip_audit_flags_known_vulnerable_dependency():
    provider = PipAuditProvider()
    workspace = FIXTURES / "vulnerable_python_project"
    assert provider.applies_to(workspace)
    findings = await provider.scan(workspace)
    assert len(findings) > 0
    assert any("urllib3" in f.issue for f in findings)


def test_pip_audit_does_not_apply_without_requirements_txt():
    provider = PipAuditProvider()
    assert provider.applies_to(FIXTURES / "vulnerable_python_project") is True
    assert provider.applies_to(FIXTURES / "no_manifest_project") is False


@pytest.mark.asyncio
async def test_semgrep_runs_and_returns_parseable_findings_list():
    provider = SemgrepProvider()
    findings = await provider.scan(FIXTURES / "jest_project")
    # The fixture is intentionally simple/clean — asserting the call
    # succeeds and returns a list is the real assertion here; a specific
    # finding count would be brittle against ruleset updates.
    assert isinstance(findings, list)
