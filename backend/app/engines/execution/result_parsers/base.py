from dataclasses import dataclass


@dataclass
class DiscoveredTestResult:
    name: str
    status: str  # passed|failed|skipped
    duration_ms: int
    error_message: str | None = None
    stack_trace: str | None = None
