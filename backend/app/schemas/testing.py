from pydantic import BaseModel


class RequirementCreate(BaseModel):
    project_id: str
    title: str
    description: str


class RequirementOut(BaseModel):
    id: str
    project_id: str
    title: str
    description: str


class TestCaseCreate(BaseModel):
    project_id: str
    requirement_id: str | None = None
    title: str
    description: str = ""
    type: str
    priority: str
    steps: list[str]
    expected_result: str
    source: str = "manual"
    ai_confidence: float | None = None


class TestCaseOut(BaseModel):
    id: str
    project_id: str
    title: str
    type: str
    priority: str
    status: str
    steps: list[str]
    expected_result: str
    automation_status: str
    source: str


class TestSuiteCreate(BaseModel):
    project_id: str
    name: str
    description: str = ""


class TestSuiteOut(BaseModel):
    id: str
    project_id: str
    name: str
    description: str
    test_case_ids: list[str]


class AddCasesRequest(BaseModel):
    case_ids: list[str]
