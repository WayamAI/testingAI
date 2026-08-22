from app.database.mongo import get_database
from app.engines.api_testing.base import ApiTestingUnavailable
from app.engines.api_testing.openapi_provider import discover_spec, run_get_endpoints
from app.intake.workspace import workspace_path
from app.models.base import new_id
from app.models.test_result import TestResult


class ProjectNotConnected(Exception):
    pass


async def run_api_tests(org_id: str, user_id: str, project_id: str, base_url: str) -> dict:
    workspace = workspace_path(project_id)
    if not workspace.exists():
        raise ProjectNotConnected("This project has no connected workspace to discover an API spec from.")

    spec = discover_spec(workspace)
    if spec is None:
        raise ApiTestingUnavailable(
            "No OpenAPI/Swagger spec found in the connected repository "
            "(looked for openapi.json/yaml, swagger.json/yaml)."
        )

    from app.services import testing_service

    results = await run_get_endpoints(spec, base_url)

    db = get_database()
    run_id = new_id()
    persisted = []
    for item in results:
        case = await testing_service.get_or_create_test_case_by_name(org_id, project_id, user_id, item.name)
        result = TestResult(
            organization_id=org_id,
            project_id=project_id,
            run_id=run_id,
            test_case_id=case.id,
            status=item.status,
            duration_ms=item.duration_ms,
            error_message=item.error_message,
            stack_trace=None,
        )
        await db.test_results.insert_one(result.model_dump(by_alias=True))
        persisted.append({"name": item.name, "status": item.status, "status_code": item.status_code, "duration_ms": item.duration_ms})

    return {"run_id": run_id, "endpoints_tested": len(persisted), "results": persisted}
