from app.core.config import get_settings
from app.core.security import hash_password, verify_password, create_access_token
from app.database.mongo import get_database
from app.models.organization import Organization
from app.models.user import User


async def login_or_provision(email: str, password: str) -> tuple[str, User]:
    """In demo mode: find-or-create the user, accepting any password.
    Outside demo mode: require an exact match, raise ValueError otherwise."""
    db = get_database()
    settings = get_settings()
    existing = await db.users.find_one({"email": email})

    if existing:
        user = User.model_validate(existing)
        if settings.demo_mode:
            token = create_access_token(user.id, user.organization_id)
            return token, user
        if not verify_password(password, user.hashed_password):
            raise ValueError("invalid credentials")
        token = create_access_token(user.id, user.organization_id)
        return token, user

    if not settings.demo_mode:
        raise ValueError("invalid credentials")

    org = Organization(name=f"{email.split('@')[0].title()}'s Organization")
    await db.organizations.insert_one(org.model_dump(by_alias=True))

    user = User(
        email=email,
        hashed_password=hash_password(password),
        name=email.split("@")[0].title(),
        organization_id=org.id,
        role="owner",
    )
    await db.users.insert_one(user.model_dump(by_alias=True))
    token = create_access_token(user.id, user.organization_id)
    return token, user


async def demo_login() -> tuple[str, User]:
    db = get_database()
    existing = await db.users.find_one({"email": "demo@wayam.ai"})
    if existing:
        user = User.model_validate(existing)
        return create_access_token(user.id, user.organization_id), user
    return await login_or_provision("demo@wayam.ai", "demo")
