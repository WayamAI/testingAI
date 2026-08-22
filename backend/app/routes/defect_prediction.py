from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.models.user import User
from app.security.dependencies import get_current_user
from app.services import defect_prediction_service

router = APIRouter(prefix="/api/testing/defect-prediction", tags=["defect-prediction"])


class FileRiskScoreOut(BaseModel):
    file_path: str
    change_frequency: int
    bug_fix_ratio: float
    churn: int
    author_count: int
    risk_score: float
    risk_label: str


class DefectPredictionScanOut(BaseModel):
    scan_id: str
    files_analyzed: int
    top_files: list[dict]
    narrative: str
    source: str


@router.post("/{project_id}/scan", response_model=DefectPredictionScanOut)
async def run_scan(project_id: str, user: User = Depends(get_current_user)):
    try:
        result = await defect_prediction_service.run_defect_prediction(user.organization_id, project_id)
    except (defect_prediction_service.ProjectNotConnected, defect_prediction_service.NotAGitRepo) as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return DefectPredictionScanOut(**result)


@router.get("/{project_id}/scores", response_model=list[FileRiskScoreOut])
async def list_scores(project_id: str, user: User = Depends(get_current_user)):
    scores = await defect_prediction_service.list_risk_scores(user.organization_id, project_id)
    return [FileRiskScoreOut(**s.model_dump()) for s in scores]
