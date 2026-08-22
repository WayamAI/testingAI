from app.models.base import MongoDocument


class DocUpload(MongoDocument):
    organization_id: str
    project_id: str
    filename: str
    extracted_char_count: int
    scenarios_extracted: int
    tests_generated: int
    source: str  # ai|demo_fallback
