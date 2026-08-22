from abc import ABC, abstractmethod
from pydantic import BaseModel


class TestGenInput(BaseModel):
    requirement_text: str


class GeneratedTestCase(BaseModel):
    title: str
    type: str
    priority: str
    steps: list[str]
    expected_result: str
    ai_confidence: float


class FailureContext(BaseModel):
    error_message: str
    stack_trace: str = ""
    test_case_title: str = ""


class FailureAnalysis(BaseModel):
    root_cause: str
    confidence: float
    recommendation: str
    affected_component: str


class AIProviderError(Exception):
    pass


class AIProvider(ABC):
    @abstractmethod
    async def generate_test_cases(self, input: TestGenInput) -> list[GeneratedTestCase]: ...

    @abstractmethod
    async def analyze_failure(self, context: FailureContext) -> FailureAnalysis: ...
