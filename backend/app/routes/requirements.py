from fastapi import APIRouter, Depends
from app.schemas.testing import RequirementCreate, RequirementOut
from app.security.dependencies import get_current_user, get_current_org_scope
from app.models.user import User
from app.services import testing_service

router = APIRouter(prefix="/api/requirements", tags=["requirements"])


@router.post("", response_model=RequirementOut, status_code=201)
async def create_requirement(payload: RequirementCreate, user: User = Depends(get_current_user)):
    req = await testing_service.create_requirement(user.organization_id, user.id, payload.project_id, payload.title, payload.description)
    return RequirementOut(**req.model_dump())


@router.get("", response_model=list[RequirementOut])
async def list_requirements(project_id: str | None = None, org_id: str = Depends(get_current_org_scope)):
    reqs = await testing_service.list_requirements(org_id, project_id)
    return [RequirementOut(**r.model_dump()) for r in reqs]
