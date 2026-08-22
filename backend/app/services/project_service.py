from app.database.mongo import get_database
from app.models.project import Project


async def create_project(org_id: str, user_id: str, name: str, project_type: str) -> Project:
    db = get_database()
    project = Project(
        organization_id=org_id,
        name=name,
        project_type=project_type,
        created_by=user_id,
    )
    await db.projects.insert_one(project.model_dump(by_alias=True))
    return project


async def list_projects(org_id: str) -> list[Project]:
    db = get_database()
    cursor = db.projects.find({"organization_id": org_id})
    return [Project.model_validate(doc) async for doc in cursor]


async def get_project(org_id: str, project_id: str) -> Project | None:
    db = get_database()
    doc = await db.projects.find_one({"_id": project_id, "organization_id": org_id})
    return Project.model_validate(doc) if doc else None
