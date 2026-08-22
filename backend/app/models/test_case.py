from app.models.base import MongoDocument


class TestCase(MongoDocument):
    organization_id: str
    project_id: str
    requirement_id: str | None = None
    title: str
    description: str = ""
    type: str  # functional|regression|smoke|security|accessibility|performance|api|...
    priority: str  # low|medium|high|critical
    status: str = "draft"  # draft|active|deprecated
    preconditions: str = ""
    steps: list[str] = []
    expected_result: str
    tags: list[str] = []
    automation_status: str = "manual"  # manual|automated
    source: str = "manual"  # manual|ai_generated|imported
    ai_confidence: float | None = None
    created_by: str
