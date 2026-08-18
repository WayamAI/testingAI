import json
import httpx
from pydantic import ValidationError
from app.core.config import get_settings
from app.engines.ai.base import (
    AIProvider, AIProviderError, TestGenInput, GeneratedTestCase, FailureContext, FailureAnalysis,
)

_GENERATE_SYSTEM_PROMPT = (
    "You are a QA test design expert. Given a requirement, produce 5-8 test "
    "cases covering happy path, negative, boundary, and security scenarios. "
    "Respond ONLY with a JSON array of objects with keys: title, type, "
    "priority, steps (array of strings), expected_result, ai_confidence (0-1)."
)

_ANALYZE_SYSTEM_PROMPT = (
    "You are a test failure analysis expert. Given an error message, stack "
    "trace, and test name, respond ONLY with a JSON object with keys: "
    "root_cause, confidence (0-1), recommendation, affected_component."
)


class OllamaProvider(AIProvider):
    def __init__(self):
        settings = get_settings()
        self.base_url = settings.ollama_base_url
        self.api_key = settings.ollama_api_key
        self.model = settings.ollama_model

    async def _chat(self, system: str, user: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{self.base_url}/api/chat",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": user},
                        ],
                        "stream": False,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                return data["message"]["content"]
        except (httpx.HTTPError, KeyError, ConnectionError, json.JSONDecodeError) as exc:
            raise AIProviderError(str(exc)) from exc

    async def generate_test_cases(self, input: TestGenInput) -> list[GeneratedTestCase]:
        content = await self._chat(_GENERATE_SYSTEM_PROMPT, input.requirement_text)
        try:
            raw = json.loads(content)
            return [GeneratedTestCase(**item) for item in raw]
        except (json.JSONDecodeError, ValidationError, TypeError, KeyError) as exc:
            raise AIProviderError(f"malformed response: {exc}") from exc

    async def analyze_failure(self, context: FailureContext) -> FailureAnalysis:
        user = (
            f"Test: {context.test_case_title}\nError: {context.error_message}\n"
            f"Stack: {context.stack_trace}"
        )
        content = await self._chat(_ANALYZE_SYSTEM_PROMPT, user)
        try:
            raw = json.loads(content)
            return FailureAnalysis(**raw)
        except (json.JSONDecodeError, ValidationError, TypeError, KeyError) as exc:
            raise AIProviderError(f"malformed response: {exc}") from exc
