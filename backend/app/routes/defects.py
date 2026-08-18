from fastapi import APIRouter, Depends
from app.schemas.quality import DefectCreate, DefectOut
from app.security.dependencies import get_current_user, get_current_org_scope
from app.models.user import User
from app.services import defect_service

router = APIRouter(prefix="/api/defects", tags=["defects"])


@router.post("", response_model=DefectOut, status_code=201)
async def create_defect(payload: DefectCreate, user: User = Depends(get_current_user)):
    defect = await defect_service.create_defect(user.organization_id, user.id, payload)
    return DefectOut(**defect.model_dump())


@router.get("", response_model=list[DefectOut])
async def list_defects(project_id: str | None = None, org_id: str = Depends(get_current_org_scope)):
    defects = await defect_service.list_defects(org_id, project_id)
    return [DefectOut(**d.model_dump()) for d in defects]
