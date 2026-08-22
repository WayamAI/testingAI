import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.models.user import User
from app.security.dependencies import get_current_user
from app.services import doc_driven_service
from app.services.document_parsing import DocumentParseError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/testing/doc-driven", tags=["doc-driven"])


class DocDrivenResultOut(BaseModel):
    scenarios_extracted: int
    tests_generated: int
    rejected_invalid_syntax: int = 0
    source: str = "none"
    scenario_source: str = "none"
    message: str | None = None
    tests: list[dict] = []


class DocUploadOut(BaseModel):
    id: str
    filename: str
    extracted_char_count: int
    scenarios_extracted: int
    tests_generated: int
    source: str


@router.post("/{project_id}/upload", response_model=DocDrivenResultOut)
async def upload_document(project_id: str, file: UploadFile = File(...), user: User = Depends(get_current_user)):
    content = await file.read()
    try:
        result = await doc_driven_service.process_document(
            user.organization_id, user.id, project_id, file.filename or "upload", content
        )
    except DocumentParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return DocDrivenResultOut(**result)


@router.get("/{project_id}/uploads", response_model=list[DocUploadOut])
async def list_uploads(project_id: str, user: User = Depends(get_current_user)):
    uploads = await doc_driven_service.list_doc_uploads(user.organization_id, project_id)
    return [DocUploadOut(**u.model_dump()) for u in uploads]
