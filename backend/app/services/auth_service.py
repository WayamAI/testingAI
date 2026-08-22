from pymongo.errors import DuplicateKeyError

from app.core.config import get_settings
from app.core.security import hash_password, verify_password, create_access_token
from app.database.mongo import get_database
from app.models.organization import Organization
from app.models.user import User


async def login_or_provision(email: str, password: str) -> tuple[str, User]:
    """In demo mode: find-or-create the user, accepting any password.
    Outside demo mode: require an exact match, raise ValueError otherwise.

    Provisioning is race-safe: the unique index on users.email (see
    app.database.mongo.ensure_indexes) means two near-simultaneous
    first-logins for the same email can no longer both succeed at
    insert_one — the loser catches DuplicateKeyError and re-fetches the
    winner's real record instead of creating a second user/org pair."""
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
    new_user = User(
        email=email,
        hashed_password=hash_password(password),
        name=email.split("@")[0].title(),
        organization_id=org.id,
        role="owner",
    )

    try:
        await db.organizations.insert_one(org.model_dump(by_alias=True))
        await db.users.insert_one(new_user.model_dump(by_alias=True))
        user = new_user
    except DuplicateKeyError:
        # Another concurrent request won the race. Clean up the org this
        # attempt created (it has no user attached) and use the winner's.
        await db.organizations.delete_one({"_id": org.id})
        winner = await db.users.find_one({"email": email})
        user = User.model_validate(winner)

    token = create_access_token(user.id, user.organization_id)
    return token, user


async def demo_login() -> tuple[str, User]:
    """The "Demo Login" button — same provisioning as any other email,
    just with a fixed identity. Race-safety comes from login_or_provision
    itself now, not from special-casing here."""
    return await login_or_provision("demo@wayam.ai", "demo")
