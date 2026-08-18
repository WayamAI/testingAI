from pydantic import BaseModel
from app.engines.ai.base import GeneratedTestCase, FailureAnalysis


class GenerateTestsRequest(BaseModel):
    requirement_text: str


class GenerateTestsResponse(BaseModel):
    cases: list[GeneratedTestCase]
    source: str


class AnalyzeFailureRequest(BaseModel):
    error_message: str
    stack_trace: str = ""
    test_case_title: str = ""


class AnalyzeFailureResponse(BaseModel):
    analysis: FailureAnalysis
    source: str
