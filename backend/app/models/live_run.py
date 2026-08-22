from app.models.base import MongoDocument


class LiveRun(MongoDocument):
    organization_id: str
    project_id: str
    url: str
    categories: list[str]
    source: str  # ai|demo_fallback
    total: int
    passed: int
    failed: int
    rejected_invalid_syntax: int = 0


class LiveRunResult(MongoDocument):
    organization_id: str
    project_id: str
    run_id: str
    title: str
    category: str
    status: str  # passed|failed|timedOut|interrupted
    duration_ms: int
    screenshot_path: str | None = None
