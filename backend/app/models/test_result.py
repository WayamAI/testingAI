from app.models.base import MongoDocument


class TestResult(MongoDocument):
    organization_id: str
    project_id: str
    run_id: str
    test_case_id: str
    status: str  # passed|failed|skipped|blocked|flaky
    duration_ms: int = 0
    error_message: str | None = None
    stack_trace: str | None = None
