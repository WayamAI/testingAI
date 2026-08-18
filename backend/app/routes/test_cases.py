from fastapi import APIRouter, Depends
from app.schemas.testing import TestCaseCreate, TestCaseOut
from app.security.dependencies import get_current_user, get_current_org_scope
from app.models.user import User
from app.services import testing_service

router = APIRouter(prefix="/api/test-cases", tags=["test-cases"])


@router.post("", response_model=TestCaseOut, status_code=201)
async def create_test_case(payload: TestCaseCreate, user: User = Depends(get_current_user)):
    case = await testing_service.create_test_case(user.organization_id, user.id, payload)
    return TestCaseOut(**case.model_dump())


@router.get("", response_model=list[TestCaseOut])
async def list_test_cases(project_id: str | None = None, org_id: str = Depends(get_current_org_scope)):
    cases = await testing_service.list_test_cases(org_id, project_id)
    return [TestCaseOut(**c.model_dump()) for c in cases]
