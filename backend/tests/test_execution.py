import pytest
from app.engines.execution.demo_provider import DemoExecutionProvider
from app.engines.execution.base import ExecutionEvent


@pytest.mark.asyncio
async def test_demo_provider_streams_events_for_each_case():
    provider = DemoExecutionProvider()
    case_ids = ["case-1", "case-2", "case-3"]
    events = []
    async for event in provider.run_suite(run_id="run-1", case_ids=case_ids):
        assert isinstance(event, ExecutionEvent)
        events.append(event)

    final_statuses = {e.test_case_id: e.status for e in events if e.type == "result"}
    assert set(final_statuses.keys()) == set(case_ids)
    assert all(s in ("passed", "failed", "skipped", "flaky") for s in final_statuses.values())
    assert any(s == "failed" for s in final_statuses.values()), "demo run should include at least one failure for realism"
