"""Discovers an OpenAPI/Swagger spec in a connected project's workspace
and executes real HTTP GET requests against a user-supplied base URL,
recording genuine status codes and latency. First cut deliberately limits
itself to safe, non-mutating GET requests without required path/query
parameters — anything else is skipped with a reason, never faked.
"""
import re
import time
from pathlib import Path

import httpx
import yaml

from app.engines.api_testing.base import ApiTestingUnavailable, ApiTestResult

_SPEC_FILENAMES = ["openapi.json", "openapi.yaml", "openapi.yml", "swagger.json", "swagger.yaml", "swagger.yml"]
REQUEST_TIMEOUT_SECONDS = 10


def discover_spec(workspace_path: Path) -> dict | None:
    for name in _SPEC_FILENAMES:
        for candidate in workspace_path.rglob(name):
            try:
                text = candidate.read_text()
                if candidate.suffix == ".json":
                    import json
                    return json.loads(text)
                return yaml.safe_load(text)
            except Exception:
                continue
    return None


def _has_required_params(operation: dict) -> bool:
    for param in operation.get("parameters", []):
        if param.get("required") and param.get("in") in ("path", "query"):
            return True
    return False


async def run_get_endpoints(spec: dict, base_url: str) -> list[ApiTestResult]:
    paths = spec.get("paths", {})
    if not paths:
        raise ApiTestingUnavailable("OpenAPI spec has no paths defined.")

    results: list[ApiTestResult] = []
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        for path, operations in paths.items():
            get_op = operations.get("get")
            if get_op is None:
                continue
            name = f"GET {path}"
            if _has_required_params(get_op) or re.search(r"\{[^}]+\}", path):
                results.append(ApiTestResult(
                    name=name, status="failed", status_code=None, duration_ms=0,
                    error_message="Skipped: endpoint requires path/query parameters not supported in this first cut.",
                ))
                continue

            url = base_url.rstrip("/") + path
            started = time.monotonic()
            try:
                resp = await client.get(url)
                duration_ms = int((time.monotonic() - started) * 1000)
                status = "passed" if resp.status_code < 500 else "failed"
                error_message = None if status == "passed" else f"Server error: HTTP {resp.status_code}"
                results.append(ApiTestResult(name, status, resp.status_code, duration_ms, error_message))
            except httpx.RequestError as exc:
                duration_ms = int((time.monotonic() - started) * 1000)
                results.append(ApiTestResult(name, "failed", None, duration_ms, f"Request failed: {exc}"))

    return results
