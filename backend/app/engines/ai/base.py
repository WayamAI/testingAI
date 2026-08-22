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


# --- Sub-project 3: AI Test Intelligence additions ---------------------

class BaselineTestGenInput(BaseModel):
    repo_summary: str
    categories: list[str]


class GeneratedPlaywrightTest(BaseModel):
    title: str
    category: str
    code: str
    confidence: float


class DocScenarioInput(BaseModel):
    document_text: str


class ExtractedScenario(BaseModel):
    title: str
    description: str
    category: str
    confidence: float


class RiskFileSummary(BaseModel):
    path: str
    risk_score: float
    risk_label: str
    change_frequency: int
    bug_fix_ratio: float
    churn: int
    author_count: int


class RiskNarrativeInput(BaseModel):
    top_files: list[RiskFileSummary]


class RiskNarrative(BaseModel):
    narrative: str
    confidence: float


class CommitSummary(BaseModel):
    sha: str
    author: str
    message: str


class GitCorrelationContext(BaseModel):
    candidate_commits: list[CommitSummary]
    top_candidate_sha: str | None = None
    top_candidate_diff: str = ""


class FailureAnalysisWithCommit(BaseModel):
    root_cause: str
    confidence: float
    recommendation: str
    affected_component: str
    likely_commit_sha: str | None = None
    likely_commit_message: str | None = None


class DomCandidate(BaseModel):
    index: int
    tag: str
    text: str
    selector_hint: str


class SelfHealInput(BaseModel):
    original_selector: str
    failure_context: str
    candidates: list[DomCandidate]


class SelfHealPick(BaseModel):
    candidate_index: int
    confidence: float
    reasoning: str


class AIProvider(ABC):
    @abstractmethod
    async def generate_test_cases(self, input: TestGenInput) -> list[GeneratedTestCase]: ...

    @abstractmethod
    async def analyze_failure(self, context: FailureContext) -> FailureAnalysis: ...

    # Concrete with a NotImplementedError default (not abstract) so stub
    # providers (OpenAIProvider etc.) remain instantiable without having
    # to individually override every sub-project 3 method — the same
    # pattern app/engines/ai/stub_providers.py already uses.
    async def generate_baseline_tests(self, input: BaselineTestGenInput) -> list[GeneratedPlaywrightTest]:
        raise NotImplementedError

    async def extract_scenarios(self, input: DocScenarioInput) -> list[ExtractedScenario]:
        raise NotImplementedError

    async def generate_tests_from_scenarios(self, scenarios: list[ExtractedScenario]) -> list[GeneratedPlaywrightTest]:
        raise NotImplementedError

    async def generate_risk_narrative(self, input: RiskNarrativeInput) -> RiskNarrative:
        raise NotImplementedError

    async def analyze_failure_with_git(self, context: FailureContext, git: GitCorrelationContext) -> FailureAnalysisWithCommit:
        raise NotImplementedError

    async def pick_self_heal_candidate(self, input: SelfHealInput) -> SelfHealPick:
        raise NotImplementedError
