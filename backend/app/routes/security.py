from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.models.user import User
from app.security.dependencies import get_current_user
from app.services import security_service

router = APIRouter(prefix="/api/projects", tags=["security"])


class SecurityFindingOut(BaseModel):
    id: str
    tool: str
    severity: str
    file: str | None
    line: int | None
    issue: str
    evidence: str | None
    recommendation: str | None


class ScanSummaryOut(BaseModel):
    scan_id: str
    provider_status: dict[str, str]
    total_findings: int


@router.post("/{project_id}/security-scans", response_model=ScanSummaryOut)
async def run_scan(project_id: str, user: User = Depends(get_current_user)):
    try:
        summary = await security_service.run_security_scan(user.organization_id, project_id)
    except security_service.ProjectNotConnected as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return ScanSummaryOut(**summary)


@router.get("/{project_id}/security-findings", response_model=list[SecurityFindingOut])
async def list_findings(project_id: str, user: User = Depends(get_current_user)):
    findings = await security_service.list_findings(user.organization_id, project_id)
    return [SecurityFindingOut(**f.model_dump()) for f in findings]
