"""Parses real `pytest --junitxml=...` output (stdlib-only, no test-side
plugin required)."""
import xml.etree.ElementTree as ET
from pathlib import Path

from app.engines.execution.result_parsers.base import DiscoveredTestResult


def parse(report_path: Path) -> list[DiscoveredTestResult]:
    if not report_path.exists():
        return []
    tree = ET.parse(report_path)
    root = tree.getroot()
    testcases = root.iter("testcase")

    results: list[DiscoveredTestResult] = []
    for case in testcases:
        classname = case.get("classname", "")
        name = case.get("name", "unnamed test")
        full_name = f"{classname}::{name}" if classname else name
        duration_ms = int(float(case.get("time", "0")) * 1000)

        failure = case.find("failure")
        error = case.find("error")
        skipped = case.find("skipped")

        if failure is not None:
            status = "failed"
            error_message = (failure.get("message") or "")[:500]
            stack_trace = (failure.text or "")[:4000]
        elif error is not None:
            status = "failed"
            error_message = (error.get("message") or "")[:500]
            stack_trace = (error.text or "")[:4000]
        elif skipped is not None:
            status = "skipped"
            error_message = None
            stack_trace = None
        else:
            status = "passed"
            error_message = None
            stack_trace = None

        results.append(DiscoveredTestResult(full_name, status, duration_ms, error_message, stack_trace))
    return results
