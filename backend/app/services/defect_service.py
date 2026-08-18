from app.database.mongo import get_database
from app.models.defect import Defect


async def create_defect(org_id: str, user_id: str, payload) -> Defect:
    db = get_database()
    defect = Defect(
        organization_id=org_id,
        project_id=payload.project_id,
        title=payload.title,
        description=payload.description,
        severity=payload.severity,
        priority=payload.priority,
        related_test_result_id=payload.related_test_result_id,
        related_test_case_id=payload.related_test_case_id,
        created_by=user_id,
    )
    await db.defects.insert_one(defect.model_dump(by_alias=True))
    return defect


async def list_defects(org_id: str, project_id: str | None) -> list[Defect]:
    db = get_database()
    query = {"organization_id": org_id}
    if project_id:
        query["project_id"] = project_id
    return [Defect.model_validate(d) async for d in db.defects.find(query)]


async def count_open_critical(org_id: str, project_id: str) -> int:
    db = get_database()
    return await db.defects.count_documents({
        "organization_id": org_id, "project_id": project_id,
        "severity": "critical", "status": {"$ne": "closed"},
    })
