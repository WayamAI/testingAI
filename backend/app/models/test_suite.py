from app.models.base import MongoDocument


class TestSuite(MongoDocument):
    organization_id: str
    project_id: str
    name: str
    description: str = ""
    test_case_ids: list[str] = []
    created_by: str
