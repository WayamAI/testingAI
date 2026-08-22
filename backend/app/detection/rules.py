"""Manifest -> language/framework/test-command mapping table.

An ordered list so later sub-projects append rules (JUnit, Go test, etc.)
without touching `engine.py` or callers. First matching rule wins.
"""
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


@dataclass
class ApplicationProfile:
    language: str
    package_manager: str
    test_framework: str
    test_command: list[str]
    result_format: str  # "jest-json" | "pytest-json" | "none"


@dataclass
class DetectionRule:
    name: str
    manifest_file: str
    matcher: Callable[[Path], bool]
    build: Callable[[Path], ApplicationProfile]


def _package_json_has_test_script(workspace: Path) -> bool:
    manifest = workspace / "package.json"
    if not manifest.exists():
        return False
    try:
        data = json.loads(manifest.read_text())
    except (json.JSONDecodeError, OSError):
        return False
    return bool(data.get("scripts", {}).get("test"))


def _build_node_profile(workspace: Path) -> ApplicationProfile:
    manifest = json.loads((workspace / "package.json").read_text())
    deps = {**manifest.get("dependencies", {}), **manifest.get("devDependencies", {})}
    if "vitest" in deps:
        framework = "vitest"
        command = ["npx", "vitest", "run", "--reporter=json", "--outputFile=wayam-test-report.json"]
    else:
        framework = "jest"
        command = ["npx", "jest", "--json", "--outputFile=wayam-test-report.json"]
    return ApplicationProfile(
        language="javascript/typescript",
        package_manager="npm",
        test_framework=framework,
        test_command=command,
        result_format="jest-json",
    )


def _has_python_manifest(workspace: Path) -> bool:
    return (workspace / "requirements.txt").exists() or (workspace / "pyproject.toml").exists()


def _has_pytest_test_files(workspace: Path) -> bool:
    return any(workspace.rglob("test_*.py")) or any(workspace.rglob("*_test.py"))


def _build_python_profile(workspace: Path) -> ApplicationProfile:
    return ApplicationProfile(
        language="python",
        package_manager="pip",
        test_framework="pytest",
        # JUnit XML is built into pytest core — no extra plugin required in
        # the target project, unlike the pytest-json-report plugin.
        test_command=["python", "-m", "pytest", "--junitxml=wayam-test-report.xml"],
        result_format="pytest-junitxml",
    )


DETECTION_RULES: list[DetectionRule] = [
    DetectionRule(
        name="node-jest-vitest",
        manifest_file="package.json",
        matcher=_package_json_has_test_script,
        build=_build_node_profile,
    ),
    DetectionRule(
        name="python-pytest",
        manifest_file="requirements.txt / pyproject.toml",
        matcher=lambda w: _has_python_manifest(w) and _has_pytest_test_files(w),
        build=_build_python_profile,
    ),
]
