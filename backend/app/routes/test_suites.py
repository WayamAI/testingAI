from fastapi import APIRouter, Depends, HTTPException
from app.schemas.testing import TestSuiteCreate, TestSuiteOut, AddCasesRequest
from app.security.dependencies import get_current_user, get_current_org_scope
from app.models.user import User
from app.services import testing_service

router = APIRouter(prefix="/api/test-suites", tags=["test-suites"])


@router.post("", response_model=TestSuiteOut, status_code=201)
async def create_test_suite(payload: TestSuiteCreate, user: User = Depends(get_current_user)):
    suite = await testing_service.create_test_suite(user.organization_id, user.id, payload.project_id, payload.name, payload.description)
    return TestSuiteOut(**suite.model_dump())


@router.get("", response_model=list[TestSuiteOut])
async def list_test_suites(project_id: str | None = None, org_id: str = Depends(get_current_org_scope)):
    suites = await testing_service.list_test_suites(org_id, project_id)
    return [TestSuiteOut(**s.model_dump()) for s in suites]


@router.post("/{suite_id}/add-cases", response_model=TestSuiteOut)
async def add_cases(suite_id: str, payload: AddCasesRequest, org_id: str = Depends(get_current_org_scope)):
    suite = await testing_service.add_cases_to_suite(org_id, suite_id, payload.case_ids)
    if not suite:
        raise HTTPException(status_code=404, detail="Test suite not found")
    return TestSuiteOut(**suite.model_dump())
