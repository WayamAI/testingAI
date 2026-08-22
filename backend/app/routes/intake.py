import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.detection.engine import DetectionEngine
from app.intake.git_clone import GitCloneError, clone_repository
from app.intake.zip_extract import ZipExtractError, extract_zip
from app.models.user import User
from app.schemas.project import ProjectOut
from app.security.dependencies import get_current_user
from app.services import audit_service, project_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/projects", tags=["intake"])

_detection_engine = DetectionEngine()


class ConnectRepoRequest(BaseModel):
    repo_url: str


async def _detect_and_mark(org_id: str, project_id: str, repo_url: str | None, workspace):
    profile = _detection_engine.detect(workspace)
    if profile is None:
        reason = _detection_engine.not_available_reason(workspace)
        await project_service.set_intake_status(org_id, project_id, "ready", None)
        await project_service.mark_connected(org_id, project_id, repo_url, None, None)
        return reason
    await project_service.mark_connected(org_id, project_id, repo_url, profile.language, profile.test_framework)
    return None


@router.post("/{project_id}/connect-repo", response_model=ProjectOut)
async def connect_repo(project_id: str, payload: ConnectRepoRequest, user: User = Depends(get_current_user)):
    project = await project_service.get_project(user.organization_id, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    await project_service.set_intake_status(user.organization_id, project_id, "cloning")
    try:
        workspace = await clone_repository(project_id, payload.repo_url)
    except GitCloneError as exc:
        await project_service.set_intake_status(user.organization_id, project_id, "error", str(exc))
        raise HTTPException(status_code=422, detail=str(exc))

    await project_service.set_intake_status(user.organization_id, project_id, "detecting")
    undetected_reason = await _detect_and_mark(user.organization_id, project_id, payload.repo_url, workspace)

    try:
        await audit_service.log_audit_event(user.organization_id, user.id, "project.connect_repo", "project", project_id)
    except Exception as e:
        logger.error("Failed to log audit event for repo connect: %s", e)

    updated = await project_service.get_project(user.organization_id, project_id)
    out = ProjectOut(**updated.model_dump())
    if undetected_reason:
        out.intake_error = undetected_reason
    return out


@router.post("/{project_id}/connect-zip", response_model=ProjectOut)
async def connect_zip(project_id: str, file: UploadFile = File(...), user: User = Depends(get_current_user)):
    project = await project_service.get_project(user.organization_id, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    await project_service.set_intake_status(user.organization_id, project_id, "extracting")
    content = await file.read()
    try:
        workspace = extract_zip(project_id, content)
    except ZipExtractError as exc:
        await project_service.set_intake_status(user.organization_id, project_id, "error", str(exc))
        raise HTTPException(status_code=422, detail=str(exc))

    await project_service.set_intake_status(user.organization_id, project_id, "detecting")
    undetected_reason = await _detect_and_mark(user.organization_id, project_id, None, workspace)

    try:
        await audit_service.log_audit_event(user.organization_id, user.id, "project.connect_zip", "project", project_id)
    except Exception as e:
        logger.error("Failed to log audit event for zip connect: %s", e)

    updated = await project_service.get_project(user.organization_id, project_id)
    out = ProjectOut(**updated.model_dump())
    if undetected_reason:
        out.intake_error = undetected_reason
    return out
