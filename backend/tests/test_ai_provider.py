import pytest
from app.engines.ai.demo_provider import DemoAIProvider
from app.engines.ai.base import TestGenInput, FailureContext
from app.engines.ai.factory import generate_test_cases_with_fallback


@pytest.mark.asyncio
async def test_demo_provider_generates_cases_from_requirement():
    provider = DemoAIProvider()
    result = await provider.generate_test_cases(
        TestGenInput(requirement_text="Users can reset their password using their registered email.")
    )
    assert len(result) >= 5
    titles = [c.title for c in result]
    assert any("invalid" in t.lower() or "expired" in t.lower() for t in titles)
    assert all(0 <= c.ai_confidence <= 1 for c in result)


@pytest.mark.asyncio
async def test_demo_provider_analyzes_failure():
    provider = DemoAIProvider()
    analysis = await provider.analyze_failure(
        FailureContext(
            error_message="Timeout waiting for element #submit-payment",
            stack_trace="TimeoutError at checkout.spec.ts:42",
            test_case_title="Checkout: submit payment",
        )
    )
    assert analysis.root_cause
    assert 0 <= analysis.confidence <= 1


@pytest.mark.asyncio
async def test_factory_falls_back_to_demo_when_ollama_unreachable(monkeypatch):
    from app.engines.ai import ollama_provider

    async def broken_generate(self, input):
        raise ConnectionError("simulated outage")

    monkeypatch.setattr(ollama_provider.OllamaProvider, "generate_test_cases", broken_generate)

    cases, source = await generate_test_cases_with_fallback(
        TestGenInput(requirement_text="Users can add items to their cart.")
    )
    assert source == "demo_fallback"
    assert len(cases) >= 1
