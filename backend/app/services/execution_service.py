from app.database.mongo import get_database
from app.models.test_run import TestRun
from app.models.test_result import TestResult
from app.models.project import Project
from app.engines.execution.base import ExecutionEvent
from app.engines.execution.factory import get_execution_provider, NoExecutableTestsError
from app.services import testing_service


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
    """Selects the real or demo execution provider for the project, persists
    each TestResult, updates the run aggregate, and calls on_event(event)
    for every event so the caller (WebSocket route) can forward it live."""
    db = get_database()
    counts = {"passed": 0, "failed": 0, "skipped": 0, "flaky": 0}

    project_doc = await db.projects.find_one({"_id": project_id, "organization_id": org_id})
    project = Project.model_validate(project_doc) if project_doc else None

    try:
        provider = get_execution_provider(project) if project else None
    except NoExecutableTestsError as exc:
        await db.test_runs.update_one({"_id": run.id}, {"$set": {"status": "blocked"}})
        await on_event(ExecutionEvent(type="status", status="blocked", error_message=str(exc)))
        return

    if provider is None:
        await db.test_runs.update_one({"_id": run.id}, {"$set": {"status": "blocked"}})
        await on_event(ExecutionEvent(type="status", status="blocked", error_message="Project not found"))
        return

    await db.test_runs.update_one({"_id": run.id}, {"$set": {"status": "running", "total": len(case_ids)}})

    async for event in provider.run_suite(run_id=run.id, case_ids=case_ids):
        if event.type == "result":
            test_case_id = event.test_case_id
            if test_case_id is None and event.discovered_test_name:
                case = await testing_service.get_or_create_test_case_by_name(
                    org_id, project_id, run.created_by, event.discovered_test_name
                )
                test_case_id = case.id

            if test_case_id is not None:
                # Resolve the id onto the outgoing event too, so the
                # WebSocket forwards a fully-resolved result — the frontend
                # timeline keys/displays off test_case_id and has no other
                # way to learn the id for a newly-discovered test.
                event.test_case_id = test_case_id
                result = TestResult(
                    organization_id=org_id,
                    project_id=project_id,
                    run_id=run.id,
                    test_case_id=test_case_id,
                    status=event.status,
                    duration_ms=event.duration_ms,
                    error_message=event.error_message,
                    stack_trace=event.stack_trace,
                )
                await db.test_results.insert_one(result.model_dump(by_alias=True))
                bucket = "passed" if event.status == "passed" else event.status
                if bucket in counts:
                    counts[bucket] += 1
        elif event.type == "status" and event.status == "failed":
            await db.test_runs.update_one({"_id": run.id}, {"$set": {"status": "failed"}})
            await on_event(event)
            return
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
