from fastapi import APIRouter, Depends
from app.security.dependencies import get_current_org_scope
from app.database.mongo import get_database
from app.services import quality_service, defect_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("")
async def dashboard(project_id: str, org_id: str = Depends(get_current_org_scope)):
    db = get_database()
    query = {"organization_id": org_id, "project_id": project_id}

    total_tests = await db.test_cases.count_documents(query)
    executed = await db.test_results.count_documents(query)
    passed = await db.test_results.count_documents({**query, "status": "passed"})
    failed = await db.test_results.count_documents({**query, "status": "failed"})
    skipped = await db.test_results.count_documents({**query, "status": "skipped"})
    flaky = await db.test_results.count_documents({**query, "status": "flaky"})
    critical_defects = await defect_service.count_open_critical(org_id, project_id)
    score = await quality_service.compute_quality_score(org_id, project_id)

    recent_runs_cursor = db.test_runs.find(query).sort("created_at", -1).limit(5)
    recent_runs = [
        {
            "id": r["_id"],
            "status": r["status"],
            "passed": r.get("passed", 0),
            "failed": r.get("failed", 0),
            "total": r.get("total", 0),
            "created_at": str(r.get("created_at")),
        }
        async for r in recent_runs_cursor
    ]

    pass_rate = round(passed / executed, 4) if executed else 0.0

    return {
        "total_tests": total_tests,
        "executed": executed,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "flaky_tests": flaky,
        "pass_rate": pass_rate,
        "critical_defects": critical_defects,
        "quality_score": score["overall"],
        "recent_runs": recent_runs,
    }
