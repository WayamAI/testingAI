from app.models.base import MongoDocument


class Requirement(MongoDocument):
    organization_id: str
    project_id: str
    title: str
    description: str
    created_by: str
