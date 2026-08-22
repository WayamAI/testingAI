from app.models.base import MongoDocument


class AIRequest(MongoDocument):
    organization_id: str
    project_id: str | None = None
    kind: str  # test_generation|failure_analysis
    input_summary: str
    source: str  # ai|demo_fallback
    output_summary: str
    created_by: str
