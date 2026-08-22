from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.models.user import User
from app.security.dependencies import get_current_user
from app.services import baseline_service

router = APIRouter(prefix="/api/testing/baseline", tags=["baseline"])


class GeneratedTestOut(BaseModel):
    id: str
    category: str
    title: str
    code: str
    confidence: float
    source: str
    commit_sha: str | None
    file_path: str


class BaselineScanOut(BaseModel):
    scan_id: str | None
    generated: int
    rejected_invalid_syntax: int = 0
    source: str
    categories_scanned: list[str]
    message: str | None = None
    tests: list[dict] = []


@router.post("/{project_id}/scan", response_model=BaselineScanOut)
async def run_scan(project_id: str, user: User = Depends(get_current_user)):
    try:
        result = await baseline_service.run_baseline_scan(user.organization_id, user.id, project_id)
    except baseline_service.ProjectNotConnected as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return BaselineScanOut(**result)


@router.get("/{project_id}/tests", response_model=list[GeneratedTestOut])
async def list_tests(project_id: str, user: User = Depends(get_current_user)):
    tests = await baseline_service.list_generated_tests(user.organization_id, project_id)
    return [GeneratedTestOut(**t.model_dump()) for t in tests]
