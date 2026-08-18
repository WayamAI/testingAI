from fastapi import APIRouter, Depends, HTTPException
from app.schemas.project import ProjectCreate, ProjectOut
from app.security.dependencies import get_current_user, get_current_org_scope
from app.models.user import User
from app.services import project_service

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("", response_model=ProjectOut, status_code=201)
async def create_project(payload: ProjectCreate, user: User = Depends(get_current_user)):
    project = await project_service.create_project(
        user.organization_id, user.id, payload.name, payload.project_type
    )
    return ProjectOut(**project.model_dump())


@router.get("", response_model=list[ProjectOut])
async def list_projects(org_id: str = Depends(get_current_org_scope)):
    projects = await project_service.list_projects(org_id)
    return [ProjectOut(**p.model_dump()) for p in projects]


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(project_id: str, org_id: str = Depends(get_current_org_scope)):
    project = await project_service.get_project(org_id, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectOut(**project.model_dump())
