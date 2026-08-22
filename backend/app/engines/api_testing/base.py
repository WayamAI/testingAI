from dataclasses import dataclass


@dataclass
class ApiTestResult:
    name: str  # e.g. "GET /users/{id}"
    status: str  # passed|failed
    status_code: int | None
    duration_ms: int
    error_message: str | None = None


class ApiTestingUnavailable(Exception):
    """Raised with a specific reason — no spec found, no base URL, etc."""
