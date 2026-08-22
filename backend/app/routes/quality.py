from fastapi import APIRouter, Depends
from app.schemas.quality import QualityScoreOut, ReleaseReadinessOut
from app.security.dependencies import get_current_org_scope
from app.services import quality_service

router = APIRouter(prefix="/api/quality", tags=["quality"])


@router.get("/score", response_model=QualityScoreOut)
async def get_quality_score(project_id: str, org_id: str = Depends(get_current_org_scope)):
    score = await quality_service.compute_quality_score(org_id, project_id)
    return QualityScoreOut(**score)


@router.get("/release-readiness", response_model=ReleaseReadinessOut)
async def get_release_readiness(project_id: str, org_id: str = Depends(get_current_org_scope)):
    readiness = await quality_service.compute_release_readiness(org_id, project_id)
    return ReleaseReadinessOut(**readiness)
