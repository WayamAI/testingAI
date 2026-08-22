from app.models.base import MongoDocument


class TestRun(MongoDocument):
    organization_id: str
    project_id: str
    suite_id: str
    environment: str = "demo"
    status: str = "queued"  # queued|running|completed|cancelled
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    blocked: int = 0
    started_at: str | None = None
    completed_at: str | None = None
    created_by: str
