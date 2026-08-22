import json
import httpx
from pydantic import ValidationError
from app.core.config import get_settings
from app.engines.ai.base import (
    AIProvider, AIProviderError, TestGenInput, GeneratedTestCase, FailureContext, FailureAnalysis,
    BaselineTestGenInput, GeneratedPlaywrightTest, DocScenarioInput, ExtractedScenario,
    RiskNarrativeInput, RiskNarrative, GitCorrelationContext, FailureAnalysisWithCommit,
    SelfHealInput, SelfHealPick,
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

_BASELINE_SYSTEM_PROMPT = (
    "You are a QA automation expert generating Playwright test skeletons "
    "(CommonJS JS, using `const { test, expect } = require('@playwright/test');`). "
    "Given a repository summary and a list of test categories, produce one "
    "test per category. Respond ONLY with a JSON array of objects with keys: "
    "title, category, code (a complete, syntactically valid Playwright test "
    "file body as a single string), confidence (0-1)."
)

_SCENARIO_SYSTEM_PROMPT = (
    "You are a QA analyst extracting testable scenarios from a requirements "
    "document. Respond ONLY with a JSON array of objects with keys: title, "
    "description, category (one of auth, api, crud, ui_form, ui_navigation, "
    "ui_component, integration, edge_case, performance, accessibility), "
    "confidence (0-1). Extract only scenarios genuinely supported by the text."
)

_RISK_NARRATIVE_SYSTEM_PROMPT = (
    "You are a software quality analyst. Given real per-file risk metrics "
    "mined from git history, write a short, honest narrative (2-4 sentences) "
    "explaining which files are riskiest and why. Respond ONLY with a JSON "
    "object with keys: narrative, confidence (0-1)."
)

_ROOT_CAUSE_GIT_SYSTEM_PROMPT = (
    "You are a debugging expert. Given a test failure and real candidate "
    "commits (with one likely-offending commit's diff), identify the root "
    "cause. Respond ONLY with a JSON object with keys: root_cause, "
    "confidence (0-1), recommendation, affected_component, "
    "likely_commit_sha, likely_commit_message. If no commit correlates, set "
    "likely_commit_sha and likely_commit_message to null."
)

_SELF_HEAL_SYSTEM_PROMPT = (
    "You are repairing a broken Playwright selector. You are given the "
    "original selector, the failure context, and a NUMBERED list of real "
    "candidate DOM elements. You MUST pick exactly one candidate by its "
    "index — you cannot invent a new selector. Respond ONLY with a JSON "
    "object with keys: candidate_index (integer, must be one of the given "
    "indices), confidence (0-1), reasoning."
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
        except (httpx.HTTPError, KeyError, ConnectionError, json.JSONDecodeError, TypeError) as exc:
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

    # --- Sub-project 3 additions -----------------------------------

    async def generate_baseline_tests(self, input: BaselineTestGenInput) -> list[GeneratedPlaywrightTest]:
        user = f"Repository summary:\n{input.repo_summary}\n\nCategories: {', '.join(input.categories)}"
        content = await self._chat(_BASELINE_SYSTEM_PROMPT, user)
        try:
            raw = json.loads(content)
            return [GeneratedPlaywrightTest(**item) for item in raw]
        except (json.JSONDecodeError, ValidationError, TypeError, KeyError) as exc:
            raise AIProviderError(f"malformed response: {exc}") from exc

    async def extract_scenarios(self, input: DocScenarioInput) -> list[ExtractedScenario]:
        content = await self._chat(_SCENARIO_SYSTEM_PROMPT, input.document_text[:12000])
        try:
            raw = json.loads(content)
            return [ExtractedScenario(**item) for item in raw]
        except (json.JSONDecodeError, ValidationError, TypeError, KeyError) as exc:
            raise AIProviderError(f"malformed response: {exc}") from exc

    async def generate_tests_from_scenarios(self, scenarios: list[ExtractedScenario]) -> list[GeneratedPlaywrightTest]:
        summary = "\n".join(f"- [{s.category}] {s.title}: {s.description}" for s in scenarios)
        user = f"Scenarios:\n{summary}"
        content = await self._chat(_BASELINE_SYSTEM_PROMPT, user)
        try:
            raw = json.loads(content)
            return [GeneratedPlaywrightTest(**item) for item in raw]
        except (json.JSONDecodeError, ValidationError, TypeError, KeyError) as exc:
            raise AIProviderError(f"malformed response: {exc}") from exc

    async def generate_risk_narrative(self, input: RiskNarrativeInput) -> RiskNarrative:
        summary = "\n".join(
            f"- {f.path}: risk={f.risk_score:.2f} ({f.risk_label}), changed {f.change_frequency}x, "
            f"bug_fix_ratio={f.bug_fix_ratio:.2f}, churn={f.churn}, authors={f.author_count}"
            for f in input.top_files
        )
        content = await self._chat(_RISK_NARRATIVE_SYSTEM_PROMPT, summary)
        try:
            raw = json.loads(content)
            return RiskNarrative(**raw)
        except (json.JSONDecodeError, ValidationError, TypeError, KeyError) as exc:
            raise AIProviderError(f"malformed response: {exc}") from exc

    async def analyze_failure_with_git(self, context: FailureContext, git: GitCorrelationContext) -> FailureAnalysisWithCommit:
        commits_summary = "\n".join(f"- {c.sha[:8]} by {c.author}: {c.message}" for c in git.candidate_commits)
        user = (
            f"Test: {context.test_case_title}\nError: {context.error_message}\n"
            f"Stack: {context.stack_trace}\n\nCandidate recent commits:\n{commits_summary}\n\n"
            f"Diff of most likely commit ({git.top_candidate_sha}):\n{git.top_candidate_diff}"
        )
        content = await self._chat(_ROOT_CAUSE_GIT_SYSTEM_PROMPT, user)
        try:
            raw = json.loads(content)
            return FailureAnalysisWithCommit(**raw)
        except (json.JSONDecodeError, ValidationError, TypeError, KeyError) as exc:
            raise AIProviderError(f"malformed response: {exc}") from exc

    async def pick_self_heal_candidate(self, input: SelfHealInput) -> SelfHealPick:
        candidates_summary = "\n".join(
            f"{c.index}: <{c.tag}> text=\"{c.text}\" selector_hint=\"{c.selector_hint}\""
            for c in input.candidates
        )
        user = (
            f"Original selector: {input.original_selector}\n"
            f"Failure context: {input.failure_context}\n\nCandidates:\n{candidates_summary}"
        )
        content = await self._chat(_SELF_HEAL_SYSTEM_PROMPT, user)
        try:
            raw = json.loads(content)
            pick = SelfHealPick(**raw)
        except (json.JSONDecodeError, ValidationError, TypeError, KeyError) as exc:
            raise AIProviderError(f"malformed response: {exc}") from exc

        valid_indices = {c.index for c in input.candidates}
        if pick.candidate_index not in valid_indices:
            # The AI must pick a real candidate — never trust an out-of-range
            # index. Treat this as a provider failure so the caller falls
            # back to the deterministic demo picker instead of writing back
            # a fabricated selector.
            raise AIProviderError(f"candidate_index {pick.candidate_index} not among real candidates {sorted(valid_indices)}")
        return pick
