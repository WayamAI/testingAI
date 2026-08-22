"""Selects the ExecutionProvider for a project: real SubprocessExecutionProvider
for connected projects with a detected test command, DemoExecutionProvider
for demo projects. Never silently substitutes one for the other."""
from app.detection.engine import DetectionEngine
from app.engines.execution.base import ExecutionProvider
from app.engines.execution.demo_provider import DemoExecutionProvider
from app.engines.execution.subprocess_provider import SubprocessExecutionProvider
from app.intake.workspace import workspace_path
from app.models.project import Project

_detection_engine = DetectionEngine()


class NoExecutableTestsError(Exception):
    """Raised with a specific, user-facing reason — never fabricate a run."""


def get_execution_provider(project: Project) -> ExecutionProvider:
    if project.source != "connected":
        return DemoExecutionProvider()

    workspace = workspace_path(project.id)
    if not workspace.exists():
        raise NoExecutableTestsError(
            "This project's workspace is missing — reconnect the repository or ZIP."
        )

    profile = _detection_engine.detect(workspace)
    if profile is None:
        raise NoExecutableTestsError(_detection_engine.not_available_reason(workspace))

    return SubprocessExecutionProvider(workspace, profile)
