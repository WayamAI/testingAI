import logging
from app.engines.ai.base import (
    AIProviderError, TestGenInput, FailureContext, GeneratedTestCase, FailureAnalysis,
    BaselineTestGenInput, GeneratedPlaywrightTest, DocScenarioInput, ExtractedScenario,
    RiskNarrativeInput, RiskNarrative, GitCorrelationContext, FailureAnalysisWithCommit,
    SelfHealInput, SelfHealPick,
)
from app.engines.ai.ollama_provider import OllamaProvider
from app.engines.ai.demo_provider import DemoAIProvider

logger = logging.getLogger(__name__)


async def generate_test_cases_with_fallback(input: TestGenInput) -> tuple[list[GeneratedTestCase], str]:
    try:
        cases = await OllamaProvider().generate_test_cases(input)
        return cases, "ai"
    except AIProviderError as exc:
        logger.warning("Ollama generate_test_cases failed, falling back to demo: %s", exc)
        cases = await DemoAIProvider().generate_test_cases(input)
        return cases, "demo_fallback"


async def analyze_failure_with_fallback(context: FailureContext) -> tuple[FailureAnalysis, str]:
    try:
        analysis = await OllamaProvider().analyze_failure(context)
        return analysis, "ai"
    except AIProviderError as exc:
        logger.warning("Ollama analyze_failure failed, falling back to demo: %s", exc)
        analysis = await DemoAIProvider().analyze_failure(context)
        return analysis, "demo_fallback"


async def generate_baseline_tests_with_fallback(input: BaselineTestGenInput) -> tuple[list[GeneratedPlaywrightTest], str]:
    try:
        tests = await OllamaProvider().generate_baseline_tests(input)
        return tests, "ai"
    except AIProviderError as exc:
        logger.warning("Ollama generate_baseline_tests failed, falling back to demo: %s", exc)
        tests = await DemoAIProvider().generate_baseline_tests(input)
        return tests, "demo_fallback"


async def extract_scenarios_with_fallback(input: DocScenarioInput) -> tuple[list[ExtractedScenario], str]:
    try:
        scenarios = await OllamaProvider().extract_scenarios(input)
        return scenarios, "ai"
    except AIProviderError as exc:
        logger.warning("Ollama extract_scenarios failed, falling back to demo: %s", exc)
        scenarios = await DemoAIProvider().extract_scenarios(input)
        return scenarios, "demo_fallback"


async def generate_tests_from_scenarios_with_fallback(scenarios: list[ExtractedScenario]) -> tuple[list[GeneratedPlaywrightTest], str]:
    try:
        tests = await OllamaProvider().generate_tests_from_scenarios(scenarios)
        return tests, "ai"
    except AIProviderError as exc:
        logger.warning("Ollama generate_tests_from_scenarios failed, falling back to demo: %s", exc)
        tests = await DemoAIProvider().generate_tests_from_scenarios(scenarios)
        return tests, "demo_fallback"


async def generate_risk_narrative_with_fallback(input: RiskNarrativeInput) -> tuple[RiskNarrative, str]:
    try:
        narrative = await OllamaProvider().generate_risk_narrative(input)
        return narrative, "ai"
    except AIProviderError as exc:
        logger.warning("Ollama generate_risk_narrative failed, falling back to demo: %s", exc)
        narrative = await DemoAIProvider().generate_risk_narrative(input)
        return narrative, "demo_fallback"


async def analyze_failure_with_git_fallback(context: FailureContext, git: GitCorrelationContext) -> tuple[FailureAnalysisWithCommit, str]:
    try:
        analysis = await OllamaProvider().analyze_failure_with_git(context, git)
        return analysis, "ai"
    except AIProviderError as exc:
        logger.warning("Ollama analyze_failure_with_git failed, falling back to demo: %s", exc)
        analysis = await DemoAIProvider().analyze_failure_with_git(context, git)
        return analysis, "demo_fallback"


async def pick_self_heal_candidate_with_fallback(input: SelfHealInput) -> tuple[SelfHealPick, str]:
    try:
        pick = await OllamaProvider().pick_self_heal_candidate(input)
        return pick, "ai"
    except AIProviderError as exc:
        logger.warning("Ollama pick_self_heal_candidate failed, falling back to demo: %s", exc)
        pick = await DemoAIProvider().pick_self_heal_candidate(input)
        return pick, "demo_fallback"
