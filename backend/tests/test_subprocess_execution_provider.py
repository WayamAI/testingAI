import shutil
from pathlib import Path

import pytest

from app.detection.engine import DetectionEngine
from app.engines.execution.subprocess_provider import SubprocessExecutionProvider

FIXTURES = Path(__file__).parent / "fixtures"


async def _collect_results(provider):
    events = []
    async for event in provider.run_suite(run_id="test-run", case_ids=[]):
        events.append(event)
    return events


@pytest.mark.asyncio
async def test_real_jest_fixture_produces_genuine_pass_and_fail(tmp_path):
    workspace = tmp_path / "jest_project"
    shutil.copytree(FIXTURES / "jest_project", workspace)

    profile = DetectionEngine().detect(workspace)
    assert profile is not None

    provider = SubprocessExecutionProvider(workspace, profile)
    events = await _collect_results(provider)

    results = [e for e in events if e.type == "result"]
    assert len(results) == 3
    statuses = {e.status for e in results}
    assert "passed" in statuses
    assert "failed" in statuses
    failed = next(e for e in results if e.status == "failed")
    assert "asserted wrong" in failed.discovered_test_name


@pytest.mark.asyncio
async def test_real_pytest_fixture_produces_genuine_pass_and_fail(tmp_path):
    workspace = tmp_path / "pytest_project"
    shutil.copytree(FIXTURES / "pytest_project", workspace)

    profile = DetectionEngine().detect(workspace)
    assert profile is not None

    provider = SubprocessExecutionProvider(workspace, profile)
    events = await _collect_results(provider)

    results = [e for e in events if e.type == "result"]
    assert len(results) == 3
    statuses = {e.status for e in results}
    assert "passed" in statuses
    assert "failed" in statuses
