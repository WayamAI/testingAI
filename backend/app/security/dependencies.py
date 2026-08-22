from fastapi import Depends, HTTPException, Header
from app.core.security import decode_access_token
from app.database.mongo import get_database
from app.models.user import User


async def get_current_user(authorization: str | None = Header(default=None)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.removeprefix("Bearer ")
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    db = get_database()
    doc = await db.users.find_one({"_id": payload["sub"]})
    if not doc:
        raise HTTPException(status_code=401, detail="User not found")
    return User.model_validate(doc)


async def get_current_org_scope(user: User = Depends(get_current_user)) -> str:
    """Every org-scoped route depends on this to get the caller's
    organization_id — never trust a client-supplied org id."""
    return user.organization_id
