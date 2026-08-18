import pytest
from app.engines.ai.demo_provider import DemoAIProvider
from app.engines.ai.base import AIProviderError, TestGenInput, FailureContext
from app.engines.ai.factory import generate_test_cases_with_fallback
from app.engines.ai.ollama_provider import OllamaProvider


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
        # OllamaProvider's own methods only ever raise AIProviderError (all
        # transport/decode/validation failures are normalized to it inside
        # the provider) — the factory's fallback contract is scoped to that
        # exception type, so the simulated failure here matches that contract.
        raise AIProviderError("simulated outage")

    monkeypatch.setattr(ollama_provider.OllamaProvider, "generate_test_cases", broken_generate)

    cases, source = await generate_test_cases_with_fallback(
        TestGenInput(requirement_text="Users can add items to their cart.")
    )
    assert source == "demo_fallback"
    assert len(cases) >= 1


@pytest.mark.asyncio
async def test_ollama_chat_wraps_malformed_response_shape_as_provider_error(monkeypatch):
    """A 200 response with syntactically valid JSON but an unexpected shape
    (e.g. "message" is null instead of an object) must not leak a bare
    TypeError out of _chat — it must surface as AIProviderError, since the
    factory's fallback narrowing depends on OllamaProvider only ever raising
    AIProviderError.
    """
    import httpx as httpx_module
    from app.engines.ai import ollama_provider as ollama_module

    class _FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"message": None}  # indexing ["content"] on None -> TypeError

    class _FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def post(self, *args, **kwargs):
            return _FakeResponse()

    monkeypatch.setattr(httpx_module, "AsyncClient", _FakeAsyncClient)

    provider = OllamaProvider()
    with pytest.raises(AIProviderError):
        await provider.generate_test_cases(TestGenInput(requirement_text="Anything."))
