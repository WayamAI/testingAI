from app.database.mongo import get_database
from app.models.audit_log import AuditLog


async def log_audit_event(org_id: str, user_id: str, action: str, resource_type: str, resource_id: str | None = None, details: dict | None = None) -> None:
    db = get_database()
    entry = AuditLog(
        organization_id=org_id,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {},
    )
    await db.audit_logs.insert_one(entry.model_dump(by_alias=True))
