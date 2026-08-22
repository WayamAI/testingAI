from app.database.mongo import get_database
from app.models.test_run import TestRun
from app.models.test_result import TestResult
from app.engines.execution.demo_provider import DemoExecutionProvider


async def create_run(org_id: str, user_id: str, project_id: str, suite_id: str) -> TestRun:
    db = get_database()
    run = TestRun(organization_id=org_id, project_id=project_id, suite_id=suite_id, created_by=user_id)
    await db.test_runs.insert_one(run.model_dump(by_alias=True))
    return run


async def get_run(org_id: str, run_id: str) -> TestRun | None:
    db = get_database()
    doc = await db.test_runs.find_one({"_id": run_id, "organization_id": org_id})
    return TestRun.model_validate(doc) if doc else None


async def execute_and_persist(org_id: str, project_id: str, run: TestRun, case_ids: list[str], on_event):
    """Runs the demo provider, persists each TestResult, updates the run
    aggregate, and calls on_event(event) for every event so the caller
    (WebSocket route) can forward it live."""
    db = get_database()
    provider = DemoExecutionProvider()
    counts = {"passed": 0, "failed": 0, "skipped": 0, "flaky": 0}

    await db.test_runs.update_one({"_id": run.id}, {"$set": {"status": "running", "total": len(case_ids)}})

    async for event in provider.run_suite(run_id=run.id, case_ids=case_ids):
        if event.type == "result":
            result = TestResult(
                organization_id=org_id,
                project_id=project_id,
                run_id=run.id,
                test_case_id=event.test_case_id,
                status=event.status,
                duration_ms=event.duration_ms,
                error_message=event.error_message,
                stack_trace=event.stack_trace,
            )
            await db.test_results.insert_one(result.model_dump(by_alias=True))
            bucket = "passed" if event.status == "passed" else event.status
            if bucket in counts:
                counts[bucket] += 1
        await on_event(event)

    await db.test_runs.update_one(
        {"_id": run.id},
        {"$set": {
            "status": "completed",
            "passed": counts["passed"],
            "failed": counts["failed"],
            "skipped": counts["skipped"],
            "blocked": 0,
        }},
    )
