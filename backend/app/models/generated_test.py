from app.models.base import MongoDocument


class GeneratedTest(MongoDocument):
    organization_id: str
    project_id: str
    scan_id: str
    category: str
    title: str
    code: str
    confidence: float
    source: str  # ai|demo_fallback
    commit_sha: str | None = None
    file_path: str | None = None  # where the .spec.js was written, if a workspace exists
    origin: str = "baseline"  # baseline|doc_driven
