import pytest
from app.database.mongo import get_database
from app.seed.seed_demo import seed_demo_data


@pytest.mark.asyncio
async def test_seed_creates_acme_commerce_with_realistic_mix():
    await seed_demo_data()
    db = get_database()

    org = await db.organizations.find_one({"name": "Wayam Demo Organization"})
    assert org is not None

    project = await db.projects.find_one({"organization_id": org["_id"], "name": "Acme Commerce"})
    assert project is not None

    suite_count = await db.test_suites.count_documents({"project_id": project["_id"]})
    assert suite_count >= 10

    case_count = await db.test_cases.count_documents({"project_id": project["_id"]})
    assert case_count >= 80

    statuses = set()
    async for r in db.test_results.find({"project_id": project["_id"]}):
        statuses.add(r["status"])
    assert {"passed", "failed"}.issubset(statuses), "seed must include both passing and failing results, not all-green"

    critical_defects = await db.defects.count_documents({"project_id": project["_id"], "severity": "critical"})
    assert critical_defects >= 1


@pytest.mark.asyncio
async def test_seed_is_idempotent():
    await seed_demo_data()
    db = get_database()
    org_count = await db.organizations.count_documents({"name": "Wayam Demo Organization"})
    assert org_count == 1
