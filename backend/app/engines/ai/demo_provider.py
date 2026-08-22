import difflib

from app.engines.ai.base import (
    AIProvider, TestGenInput, GeneratedTestCase, FailureContext, FailureAnalysis,
    BaselineTestGenInput, GeneratedPlaywrightTest, DocScenarioInput, ExtractedScenario,
    RiskNarrativeInput, RiskNarrative, GitCorrelationContext, FailureAnalysisWithCommit,
    SelfHealInput, SelfHealPick,
)
from app.services.playwright_codegen import render_test

_SCENARIO_KEYWORDS = ["should", "must", "shall", "can", "will", "needs to", "is able to"]
_CATEGORY_KEYWORDS = {
    "auth": ["login", "log in", "sign in", "authenticate", "password", "session"],
    "api": ["api", "endpoint", "request", "response", "webhook"],
    "crud": ["create", "update", "delete", "edit", "remove"],
    "ui_form": ["form", "field", "input", "submit"],
    "ui_navigation": ["navigate", "menu", "link", "page", "route"],
    "accessibility": ["accessible", "accessibility", "screen reader", "aria", "wcag"],
    "performance": ["fast", "performance", "load time", "latency", "response time"],
}


def _infer_category(text: str) -> str:
    lowered = text.lower()
    for category, keywords in _CATEGORY_KEYWORDS.items():
        if any(kw in lowered for kw in keywords):
            return category
    return "integration"

_NEGATIVE_SUFFIXES = [
    ("Invalid input", "negative", "medium", 0.9),
    ("Unregistered/unknown record", "negative", "medium", 0.85),
    ("Expired token or session", "negative", "high", 0.88),
    ("Repeated/duplicate submission", "boundary", "medium", 0.8),
    ("Rate limiting enforced", "security", "high", 0.82),
    ("Concurrent requests", "boundary", "medium", 0.75),
]


class DemoAIProvider(AIProvider):
    async def generate_test_cases(self, input: TestGenInput) -> list[GeneratedTestCase]:
        subject = input.requirement_text.strip().rstrip(".")
        cases = [
            GeneratedTestCase(
                title=f"{subject} — happy path",
                type="functional",
                priority="high",
                steps=[f"Perform the primary action described: {subject}", "Verify the expected outcome"],
                expected_result="The action completes successfully as specified",
                ai_confidence=0.95,
            )
        ]
        for label, type_, priority, confidence in _NEGATIVE_SUFFIXES:
            cases.append(
                GeneratedTestCase(
                    title=f"{subject} — {label}",
                    type=type_,
                    priority=priority,
                    steps=[f"Attempt: {subject}", f"Trigger condition: {label}"],
                    expected_result="System handles the condition gracefully without data corruption",
                    ai_confidence=confidence,
                )
            )
        return cases

    async def analyze_failure(self, context: FailureContext) -> FailureAnalysis:
        msg = context.error_message.lower()
        if "timeout" in msg:
            root_cause = "The operation exceeded its expected time budget, likely due to a slow downstream dependency or an unmet wait condition."
            component = "Execution environment / network layer"
        elif "assert" in msg or "expected" in msg:
            root_cause = "The observed output diverged from the expected value, suggesting a recent behavioral change or data mismatch."
            component = "Application logic under test"
        else:
            root_cause = "An unhandled error interrupted the test before it could reach its assertions."
            component = "Test target"
        return FailureAnalysis(
            root_cause=root_cause,
            confidence=0.72,
            recommendation="Re-run in isolation to rule out flakiness, then inspect recent changes to the affected component.",
            affected_component=component,
        )

    # --- Sub-project 3 additions -----------------------------------

    async def generate_baseline_tests(self, input: BaselineTestGenInput) -> list[GeneratedPlaywrightTest]:
        tests = []
        for category in input.categories:
            title = f"{category.replace('_', ' ').title()} baseline check"
            tests.append(GeneratedPlaywrightTest(
                title=title,
                category=category,
                code=render_test(category, title),
                confidence=0.65,  # template-based, not code-aware — honestly modest
            ))
        return tests

    async def extract_scenarios(self, input: DocScenarioInput) -> list[ExtractedScenario]:
        scenarios: list[ExtractedScenario] = []
        for line in input.document_text.splitlines():
            stripped = line.strip(" -*\t")
            if len(stripped) < 15:
                continue
            lowered = stripped.lower()
            if not any(kw in lowered for kw in _SCENARIO_KEYWORDS):
                continue
            scenarios.append(ExtractedScenario(
                title=stripped[:120],
                description=stripped,
                category=_infer_category(stripped),
                confidence=0.6,
            ))
            if len(scenarios) >= 20:
                break
        return scenarios

    async def generate_tests_from_scenarios(self, scenarios: list[ExtractedScenario]) -> list[GeneratedPlaywrightTest]:
        return [
            GeneratedPlaywrightTest(
                title=s.title,
                category=s.category,
                code=render_test(s.category, s.title),
                confidence=min(s.confidence, 0.65),
            )
            for s in scenarios
        ]

    async def generate_risk_narrative(self, input: RiskNarrativeInput) -> RiskNarrative:
        if not input.top_files:
            return RiskNarrative(narrative="No files with real commit history were found to assess.", confidence=1.0)
        lines = []
        for f in input.top_files[:5]:
            lines.append(
                f"`{f.path}` scores {f.risk_score:.2f} ({f.risk_label}): changed {f.change_frequency} time(s), "
                f"{f.bug_fix_ratio * 100:.0f}% of those were bug fixes, {f.churn} lines churned across "
                f"{f.author_count} author(s)."
            )
        narrative = (
            "Based on real commit history, the highest-risk files are:\n" + "\n".join(lines) +
            "\nFiles with a high bug-fix ratio and multiple authors are statistically more likely to "
            "regress — prioritize review and test coverage there before release."
        )
        return RiskNarrative(narrative=narrative, confidence=0.7)

    async def analyze_failure_with_git(self, context: FailureContext, git: GitCorrelationContext) -> FailureAnalysisWithCommit:
        base = await self.analyze_failure(context)
        if git.top_candidate_sha and git.candidate_commits:
            top = next((c for c in git.candidate_commits if c.sha == git.top_candidate_sha), git.candidate_commits[0])
            recommendation = (
                f"{base.recommendation} The most likely commit is {top.sha[:8]} by {top.author} "
                f"(\"{top.message}\") — review its diff for the affected component."
            )
            return FailureAnalysisWithCommit(
                root_cause=base.root_cause,
                confidence=base.confidence,
                recommendation=recommendation,
                affected_component=base.affected_component,
                likely_commit_sha=top.sha,
                likely_commit_message=top.message,
            )
        return FailureAnalysisWithCommit(
            root_cause=base.root_cause,
            confidence=base.confidence * 0.8,  # lower confidence: no git correlation available
            recommendation=base.recommendation + " No recent commit could be correlated with this failure.",
            affected_component=base.affected_component,
        )

    async def pick_self_heal_candidate(self, input: SelfHealInput) -> SelfHealPick:
        target = f"{input.original_selector} {input.failure_context}".lower()
        best_index = 0
        best_score = -1.0
        for candidate in input.candidates:
            probe = f"{candidate.tag} {candidate.text} {candidate.selector_hint}".lower()
            score = difflib.SequenceMatcher(None, target, probe).ratio()
            if score > best_score:
                best_score = score
                best_index = candidate.index
        return SelfHealPick(
            candidate_index=best_index,
            confidence=round(best_score, 2),
            reasoning=f"Selected by text/attribute similarity to the original selector and failure context ({best_score:.2f} match).",
        )
