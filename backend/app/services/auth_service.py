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
    """Resolve the canonical demo user seeded onto "Wayam Demo Organization".

    `email` has no uniqueness constraint, so a stray demo@wayam.ai user from
    an unrelated org (e.g. left over from local dev poking at the DB) could
    otherwise be matched non-deterministically by a bare find_one. Prefer the
    user attached to the seeded demo org; fall back to any demo@wayam.ai user
    if the seed hasn't run yet, then to provisioning a fresh one.
    """
    db = get_database()
    seed_org = await db.organizations.find_one({"name": "Wayam Demo Organization"})
    if seed_org:
        seeded_user = await db.users.find_one({"organization_id": seed_org["_id"], "email": "demo@wayam.ai"})
        if seeded_user:
            user = User.model_validate(seeded_user)
            return create_access_token(user.id, user.organization_id), user

    existing = await db.users.find_one({"email": "demo@wayam.ai"})
    if existing:
        user = User.model_validate(existing)
        return create_access_token(user.id, user.organization_id), user
    return await login_or_provision("demo@wayam.ai", "demo")
