from pathlib import Path

from app.detection.engine import DetectionEngine

FIXTURES = Path(__file__).parent / "fixtures"


def test_detects_node_jest_project():
    engine = DetectionEngine()
    profile = engine.detect(FIXTURES / "jest_project")
    assert profile is not None
    assert profile.language == "javascript/typescript"
    assert profile.test_framework == "jest"
    assert profile.result_format == "jest-json"


def test_detects_python_pytest_project():
    engine = DetectionEngine()
    profile = engine.detect(FIXTURES / "pytest_project")
    assert profile is not None
    assert profile.language == "python"
    assert profile.test_framework == "pytest"
    assert profile.result_format == "pytest-junitxml"


def test_reports_reason_when_no_manifest_found():
    engine = DetectionEngine()
    profile = engine.detect(FIXTURES / "no_manifest_project")
    assert profile is None
    reason = engine.not_available_reason(FIXTURES / "no_manifest_project")
    assert "No recognized test manifest" in reason
