from app.models.base import MongoDocument


class Defect(MongoDocument):
    organization_id: str
    project_id: str
    title: str
    description: str
    severity: str  # low|medium|high|critical
    priority: str
    status: str = "open"  # open|in_progress|resolved|closed
    related_test_result_id: str | None = None
    related_test_case_id: str | None = None
    ai_root_cause: str | None = None
    ai_recommendation: str | None = None
    created_by: str
