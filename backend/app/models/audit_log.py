from app.models.base import MongoDocument


class AuditLog(MongoDocument):
    organization_id: str
    user_id: str
    action: str
    resource_type: str
    resource_id: str | None = None
    details: dict = {}
