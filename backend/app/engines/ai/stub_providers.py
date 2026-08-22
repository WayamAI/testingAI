from app.engines.ai.base import AIProvider, TestGenInput, GeneratedTestCase, FailureContext, FailureAnalysis


class _NotImplementedProvider(AIProvider):
    async def generate_test_cases(self, input: TestGenInput) -> list[GeneratedTestCase]:
        raise NotImplementedError("Provider not yet implemented")

    async def analyze_failure(self, context: FailureContext) -> FailureAnalysis:
        raise NotImplementedError("Provider not yet implemented")


class OpenAIProvider(_NotImplementedProvider):
    pass


class AnthropicProvider(_NotImplementedProvider):
    pass


class GeminiProvider(_NotImplementedProvider):
    pass
