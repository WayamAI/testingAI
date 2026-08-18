from app.database.mongo import get_database
from app.models.requirement import Requirement
from app.models.test_case import TestCase
from app.models.test_suite import TestSuite


async def create_requirement(org_id: str, user_id: str, project_id: str, title: str, description: str) -> Requirement:
    db = get_database()
    req = Requirement(organization_id=org_id, project_id=project_id, title=title, description=description, created_by=user_id)
    await db.requirements.insert_one(req.model_dump(by_alias=True))
    return req


async def list_requirements(org_id: str, project_id: str | None) -> list[Requirement]:
    db = get_database()
    query = {"organization_id": org_id}
    if project_id:
        query["project_id"] = project_id
    return [Requirement.model_validate(d) async for d in db.requirements.find(query)]


async def create_test_case(org_id: str, user_id: str, payload) -> TestCase:
    db = get_database()
    case = TestCase(
        organization_id=org_id,
        project_id=payload.project_id,
        requirement_id=payload.requirement_id,
        title=payload.title,
        description=payload.description,
        type=payload.type,
        priority=payload.priority,
        steps=payload.steps,
        expected_result=payload.expected_result,
        source=payload.source,
        ai_confidence=payload.ai_confidence,
        created_by=user_id,
    )
    await db.test_cases.insert_one(case.model_dump(by_alias=True))
    return case


async def list_test_cases(org_id: str, project_id: str | None) -> list[TestCase]:
    db = get_database()
    query = {"organization_id": org_id}
    if project_id:
        query["project_id"] = project_id
    return [TestCase.model_validate(d) async for d in db.test_cases.find(query)]


async def create_test_suite(org_id: str, user_id: str, project_id: str, name: str, description: str) -> TestSuite:
    db = get_database()
    suite = TestSuite(organization_id=org_id, project_id=project_id, name=name, description=description, created_by=user_id)
    await db.test_suites.insert_one(suite.model_dump(by_alias=True))
    return suite


async def add_cases_to_suite(org_id: str, suite_id: str, case_ids: list[str]) -> TestSuite | None:
    db = get_database()
    await db.test_suites.update_one(
        {"_id": suite_id, "organization_id": org_id},
        {"$addToSet": {"test_case_ids": {"$each": case_ids}}},
    )
    doc = await db.test_suites.find_one({"_id": suite_id, "organization_id": org_id})
    return TestSuite.model_validate(doc) if doc else None


async def get_test_suite(org_id: str, suite_id: str) -> TestSuite | None:
    db = get_database()
    doc = await db.test_suites.find_one({"_id": suite_id, "organization_id": org_id})
    return TestSuite.model_validate(doc) if doc else None


async def list_test_suites(org_id: str, project_id: str | None) -> list[TestSuite]:
    db = get_database()
    query = {"organization_id": org_id}
    if project_id:
        query["project_id"] = project_id
    return [TestSuite.model_validate(d) async for d in db.test_suites.find(query)]
