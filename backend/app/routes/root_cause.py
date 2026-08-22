from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.models.user import User
from app.security.dependencies import get_current_user
from app.services import root_cause_service

router = APIRouter(prefix="/api/testing/root-cause", tags=["root-cause"])


class AnalyzeRequest(BaseModel):
    error_message: str
    stack_trace: str = ""
    test_case_title: str = ""


class AnalyzeResultOut(BaseModel):
    id: str
    root_cause: str
    confidence: float
    recommendation: str
    affected_component: str
    likely_commit_sha: str | None
    likely_commit_message: str | None
    source: str
    git_correlation_available: bool


class HistoryEntryOut(BaseModel):
    id: str
    test_case_title: str
    root_cause: str
    confidence: float
    likely_commit_sha: str | None
    source: str


@router.post("/{project_id}/analyze", response_model=AnalyzeResultOut)
async def analyze(project_id: str, payload: AnalyzeRequest, user: User = Depends(get_current_user)):
    result = await root_cause_service.analyze_with_correlation(
        user.organization_id, project_id, payload.error_message, payload.stack_trace, payload.test_case_title
    )
    return AnalyzeResultOut(**result)


@router.get("/{project_id}/history", response_model=list[HistoryEntryOut])
async def history(project_id: str, user: User = Depends(get_current_user)):
    entries = await root_cause_service.list_history(user.organization_id, project_id)
    return [HistoryEntryOut(**e.model_dump()) for e in entries]
