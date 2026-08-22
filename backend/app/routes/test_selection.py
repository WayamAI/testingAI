from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.models.user import User
from app.security.dependencies import get_current_user
from app.services import test_selection_service

router = APIRouter(prefix="/api/testing/selection", tags=["test-selection"])


class SelectionOut(BaseModel):
    since_commit: str
    changed_files: list[str]
    relevant_categories: list[str]
    selected: list[dict]
    skipped: list[dict]
    estimated_tests_skipped: int


class DuplicateOut(BaseModel):
    test_a_id: str
    test_a_title: str
    test_b_id: str
    test_b_title: str
    similarity: float


class FlakyReportOut(BaseModel):
    test_case_id: str
    title: str
    flaky_score: float | None
    run_count: int
    status: str


@router.get("/{project_id}/select", response_model=SelectionOut)
async def select(project_id: str, since_commit: str | None = None, user: User = Depends(get_current_user)):
    try:
        result = await test_selection_service.select_tests(user.organization_id, project_id, since_commit)
    except (test_selection_service.ProjectNotConnected, test_selection_service.NoBaselineReference) as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return SelectionOut(**result)


@router.get("/{project_id}/duplicates", response_model=list[DuplicateOut])
async def duplicates(project_id: str, user: User = Depends(get_current_user)):
    return await test_selection_service.find_duplicates(user.organization_id, project_id)


@router.get("/{project_id}/coverage-gaps", response_model=list[str])
async def coverage_gaps(project_id: str, user: User = Depends(get_current_user)):
    return await test_selection_service.find_coverage_gaps(user.organization_id, project_id)


@router.get("/{project_id}/flaky-report", response_model=list[FlakyReportOut])
async def flaky_report(project_id: str, user: User = Depends(get_current_user)):
    return await test_selection_service.flaky_report(user.organization_id, project_id)
