from datetime import datetime, timezone
from app.models.organization import Organization
from app.models.user import User
from app.models.project import Project
from app.models.requirement import Requirement
from app.models.test_suite import TestSuite
from app.models.test_case import TestCase
from app.models.test_run import TestRun
from app.models.test_result import TestResult
from app.models.defect import Defect
from app.models.quality_score import QualityScore
from app.models.ai_request import AIRequest


def test_organization_model_defaults():
    org = Organization(name="Wayam Demo Organization")
    assert org.id is not None
    assert org.name == "Wayam Demo Organization"
    assert isinstance(org.created_at, datetime)


def test_test_case_model_required_fields():
    case = TestCase(
        organization_id="org1",
        project_id="proj1",
        title="Password reset happy path",
        type="functional",
        priority="high",
        status="draft",
        steps=["Navigate to reset page", "Submit valid email"],
        expected_result="Reset email is sent",
        created_by="user1",
    )
    assert case.priority == "high"
    assert case.automation_status == "manual"


def test_quality_score_breakdown():
    qs = QualityScore(
        organization_id="org1",
        project_id="proj1",
        overall=86,
        functional=91,
        reliability=85,
        security=92,
        performance=83,
        accessibility=79,
        coverage=94,
    )
    assert qs.overall == 86
