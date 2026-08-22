"""DetectionEngine — inspects a workspace and produces a real
ApplicationProfile, or a clear reason why none could be produced.
Never guesses beyond what a manifest file actually supports.
"""
from pathlib import Path

from app.detection.rules import DETECTION_RULES, ApplicationProfile


class DetectionEngine:
    def detect(self, workspace_path: Path) -> ApplicationProfile | None:
        for rule in DETECTION_RULES:
            if rule.matcher(workspace_path):
                return rule.build(workspace_path)
        return None

    def not_available_reason(self, workspace_path: Path) -> str:
        manifests_checked = ", ".join(r.manifest_file for r in DETECTION_RULES)
        return (
            "No recognized test manifest found "
            f"(checked for: {manifests_checked})."
        )
