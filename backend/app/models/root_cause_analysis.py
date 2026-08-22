from app.models.base import MongoDocument


class RootCauseAnalysis(MongoDocument):
    organization_id: str
    project_id: str
    error_message: str
    stack_trace: str
    test_case_title: str
    root_cause: str
    confidence: float
    recommendation: str
    affected_component: str
    likely_commit_sha: str | None = None
    likely_commit_message: str | None = None
    source: str  # ai|demo_fallback
