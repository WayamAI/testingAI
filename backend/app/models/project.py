from app.models.base import MongoDocument


class Project(MongoDocument):
    organization_id: str
    name: str
    project_type: str  # web_application|api|mobile_application|...
    created_by: str
