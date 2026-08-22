from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.models.user import User
from app.security.dependencies import get_current_user
from app.services import self_heal_service
from app.services.dom_scan_service import DomScanError

router = APIRouter(prefix="/api/testing/self-heal", tags=["self-heal"])


class ProposeRequest(BaseModel):
    url: str
    original_selector: str
    failure_context: str = ""


class ApproveRequest(BaseModel):
    target_file: str | None = None
    target_line: int | None = None


class AttemptOut(BaseModel):
    id: str
    url: str
    original_selector: str
    proposed_selector: str
    ai_confidence: float
    ai_reasoning: str
    source: str
    live_validation_count: int
    status: str
    target_file: str | None
    target_line: int | None
    applied: bool


@router.post("/{project_id}/propose", response_model=AttemptOut)
async def propose(project_id: str, payload: ProposeRequest, user: User = Depends(get_current_user)):
    try:
        attempt = await self_heal_service.propose_heal(
            user.organization_id, project_id, payload.url, payload.original_selector, payload.failure_context
        )
    except (DomScanError, self_heal_service.NoCandidatesFound) as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return AttemptOut(**attempt.model_dump())


@router.post("/{project_id}/attempts/{attempt_id}/approve", response_model=AttemptOut)
async def approve(project_id: str, attempt_id: str, payload: ApproveRequest, user: User = Depends(get_current_user)):
    try:
        attempt = await self_heal_service.approve_heal(
            user.organization_id, attempt_id, payload.target_file, payload.target_line
        )
    except self_heal_service.AttemptNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except self_heal_service.InvalidApproval as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return AttemptOut(**attempt.model_dump())


@router.post("/{project_id}/attempts/{attempt_id}/reject", response_model=AttemptOut)
async def reject(project_id: str, attempt_id: str, user: User = Depends(get_current_user)):
    try:
        attempt = await self_heal_service.reject_heal(user.organization_id, attempt_id)
    except self_heal_service.AttemptNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return AttemptOut(**attempt.model_dump())


@router.get("/{project_id}/attempts", response_model=list[AttemptOut])
async def list_attempts(project_id: str, user: User = Depends(get_current_user)):
    attempts = await self_heal_service.list_attempts(user.organization_id, project_id)
    return [AttemptOut(**a.model_dump()) for a in attempts]
