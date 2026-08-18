import logging
from app.engines.ai.base import AIProviderError, TestGenInput, FailureContext, GeneratedTestCase, FailureAnalysis
from app.engines.ai.ollama_provider import OllamaProvider
from app.engines.ai.demo_provider import DemoAIProvider

logger = logging.getLogger(__name__)


async def generate_test_cases_with_fallback(input: TestGenInput) -> tuple[list[GeneratedTestCase], str]:
    try:
        cases = await OllamaProvider().generate_test_cases(input)
        return cases, "ai"
    except (AIProviderError, Exception) as exc:
        logger.warning("Ollama generate_test_cases failed, falling back to demo: %s", exc)
        cases = await DemoAIProvider().generate_test_cases(input)
        return cases, "demo_fallback"


async def analyze_failure_with_fallback(context: FailureContext) -> tuple[FailureAnalysis, str]:
    try:
        analysis = await OllamaProvider().analyze_failure(context)
        return analysis, "ai"
    except (AIProviderError, Exception) as exc:
        logger.warning("Ollama analyze_failure failed, falling back to demo: %s", exc)
        analysis = await DemoAIProvider().analyze_failure(context)
        return analysis, "demo_fallback"
