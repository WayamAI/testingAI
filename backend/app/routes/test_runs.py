from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.security.dependencies import get_current_user
from app.models.user import User
from app.services import execution_service, testing_service

router = APIRouter(prefix="/api/test-runs", tags=["test-runs"])


class CreateRunRequest(BaseModel):
    suite_id: str


class RunOut(BaseModel):
    id: str
    suite_id: str
    status: str


@router.post("", response_model=RunOut, status_code=201)
async def create_run(payload: CreateRunRequest, user: User = Depends(get_current_user)):
    suite = await testing_service.get_test_suite(user.organization_id, payload.suite_id)
    if not suite:
        raise HTTPException(status_code=404, detail="Test suite not found")
    run = await execution_service.create_run(user.organization_id, user.id, suite.project_id, suite.id)
    return RunOut(id=run.id, suite_id=run.suite_id, status=run.status)


@router.get("/{run_id}", response_model=RunOut)
async def get_run(run_id: str, user: User = Depends(get_current_user)):
    run = await execution_service.get_run(user.organization_id, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Test run not found")
    return RunOut(id=run.id, suite_id=run.suite_id, status=run.status)
