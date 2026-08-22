from app.models.base import MongoDocument


class Project(MongoDocument):
    organization_id: str
    name: str
    project_type: str  # web_application|api|mobile_application|...
    created_by: str
    source: str = "demo"  # demo|connected
    intake_status: str = "none"  # none|cloning|extracting|detecting|ready|error
    intake_error: str | None = None
    repo_url: str | None = None
    # Flattened ApplicationProfile fields, populated once detection succeeds
    detected_language: str | None = None
    detected_test_framework: str | None = None
