from app.engines.ai.base import (
    AIProvider, TestGenInput, GeneratedTestCase, FailureContext, FailureAnalysis,
)

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
