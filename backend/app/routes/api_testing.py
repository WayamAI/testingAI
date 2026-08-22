from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.engines.api_testing.base import ApiTestingUnavailable
from app.models.user import User
from app.security.dependencies import get_current_user
from app.services import api_testing_service

router = APIRouter(prefix="/api/projects", tags=["api-testing"])


class RunApiTestsRequest(BaseModel):
    base_url: str


class ApiTestResultOut(BaseModel):
    name: str
    status: str
    status_code: int | None
    duration_ms: int


class ApiTestRunOut(BaseModel):
    run_id: str
    endpoints_tested: int
    results: list[ApiTestResultOut]


@router.post("/{project_id}/api-tests", response_model=ApiTestRunOut)
async def run_api_tests(project_id: str, payload: RunApiTestsRequest, user: User = Depends(get_current_user)):
    try:
        summary = await api_testing_service.run_api_tests(user.organization_id, user.id, project_id, payload.base_url)
    except (api_testing_service.ProjectNotConnected, ApiTestingUnavailable) as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return ApiTestRunOut(**summary)
