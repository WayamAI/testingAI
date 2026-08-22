from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.models.user import User
from app.security.dependencies import get_current_user
from app.services import live_runner_service

router = APIRouter(prefix="/api/testing/live-runner", tags=["live-runner"])


class RunLiveRequest(BaseModel):
    url: str


class LiveRunOut(BaseModel):
    run_id: str
    url: str
    categories: list[str]
    source: str
    total: int
    passed: int
    failed: int
    rejected_invalid_syntax: int = 0
    results: list[dict] = []


class LiveRunSummaryOut(BaseModel):
    id: str
    url: str
    categories: list[str]
    source: str
    total: int
    passed: int
    failed: int


@router.post("/{project_id}/run", response_model=LiveRunOut)
async def run(project_id: str, payload: RunLiveRequest, user: User = Depends(get_current_user)):
    try:
        result = await live_runner_service.run_live_tests(user.organization_id, project_id, payload.url)
    except live_runner_service.LiveRunnerError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return LiveRunOut(**result)


@router.get("/{project_id}/runs", response_model=list[LiveRunSummaryOut])
async def list_runs(project_id: str, user: User = Depends(get_current_user)):
    runs = await live_runner_service.list_runs(user.organization_id, project_id)
    return [LiveRunSummaryOut(**r.model_dump()) for r in runs]
