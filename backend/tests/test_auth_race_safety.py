import asyncio

import pytest
from httpx import ASGITransport, AsyncClient

from app.database.mongo import get_database
from app.main import app
from app.services.auth_service import login_or_provision


@pytest.mark.asyncio
async def test_concurrent_first_logins_for_same_email_create_only_one_user():
    """Real bug this test reproduces: a bare find-then-insert in
    login_or_provision let two concurrent first-logins for the same new
    email each pass the find_one check and insert a separate user/org —
    which is exactly how two demo@wayam.ai accounts ended up in different
    orgs in production use. The unique index + DuplicateKeyError retry in
    auth_service.login_or_provision must make this race-safe."""
    email = "racecondition@example.com"
    db = get_database()
    await db.users.delete_many({"email": email})

    results = await asyncio.gather(*[login_or_provision(email, "x") for _ in range(10)])

    user_ids = {user.id for _, user in results}
    org_ids = {user.organization_id for _, user in results}
    assert len(user_ids) == 1, f"expected exactly one user, got {len(user_ids)}: {user_ids}"
    assert len(org_ids) == 1, f"expected exactly one org, got {len(org_ids)}: {org_ids}"

    real_count = await db.users.count_documents({"email": email})
    assert real_count == 1

    await db.users.delete_many({"email": email})
    for org_id in org_ids:
        await db.organizations.delete_one({"_id": org_id})


@pytest.mark.asyncio
async def test_demo_login_is_stable_across_repeated_calls():
    """Every call to /api/auth/demo-login must resolve to the same real
    user — the original bug meant this was not guaranteed."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        responses = await asyncio.gather(*[client.post("/api/auth/demo-login") for _ in range(5)])

    user_ids = {r.json()["user"]["id"] for r in responses}
    assert len(user_ids) == 1
