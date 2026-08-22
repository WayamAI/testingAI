from abc import ABC, abstractmethod
from typing import AsyncIterator
from pydantic import BaseModel


class ExecutionEvent(BaseModel):
    type: str  # "status" | "result"
    test_case_id: str | None = None
    status: str | None = None  # queued|preparing|running|passed|failed|skipped|flaky
    duration_ms: int = 0
    error_message: str | None = None
    stack_trace: str | None = None


class ExecutionProvider(ABC):
    @abstractmethod
    def run_suite(self, run_id: str, case_ids: list[str]) -> AsyncIterator[ExecutionEvent]: ...
