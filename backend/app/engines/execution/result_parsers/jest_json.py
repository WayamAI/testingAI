"""Parses real `jest --json` / `vitest run --reporter=json` output."""
import json
from pathlib import Path

from app.engines.execution.result_parsers.base import DiscoveredTestResult

_STATUS_MAP = {"passed": "passed", "failed": "failed", "pending": "skipped", "skipped": "skipped", "todo": "skipped"}


def parse(report_path: Path) -> list[DiscoveredTestResult]:
    if not report_path.exists():
        return []
    data = json.loads(report_path.read_text())
    results: list[DiscoveredTestResult] = []
    for file_result in data.get("testResults", []):
        for assertion in file_result.get("assertionResults", []):
            title = assertion.get("fullName") or assertion.get("title", "unnamed test")
            status = _STATUS_MAP.get(assertion.get("status", "failed"), "failed")
            duration = int(assertion.get("duration") or 0)
            error_message = None
            stack_trace = None
            failure_messages = assertion.get("failureMessages") or []
            if failure_messages:
                error_message = failure_messages[0].splitlines()[0][:500]
                stack_trace = "\n".join(failure_messages)[:4000]
            results.append(DiscoveredTestResult(title, status, duration, error_message, stack_trace))
    return results
