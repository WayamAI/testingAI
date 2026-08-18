import asyncio
import random
from app.database.mongo import get_database
from app.core.security import hash_password
from app.models.organization import Organization
from app.models.user import User
from app.models.project import Project
from app.models.test_suite import TestSuite
from app.models.test_case import TestCase
from app.models.test_run import TestRun
from app.models.test_result import TestResult
from app.models.defect import Defect

_SUITES = [
    ("Authentication Suite", ["Login", "Logout", "Password reset", "Session expiry", "MFA challenge", "Account lockout", "OAuth login", "Token refresh", "Concurrent sessions", "Remember me"]),
    ("Checkout Suite", ["Add to cart", "Update quantity", "Remove item", "Apply coupon", "Guest checkout", "Shipping selection", "Address validation", "Order summary", "Cart persistence", "Empty cart handling", "Multi-currency"]),
    ("Payment Suite", ["Card payment success", "Card declined", "Payment timeout", "Refund flow", "Partial refund", "Payment retry", "Wallet payment", "Currency conversion", "Fraud check", "Saved card reuse"]),
    ("Order Suite", ["Order creation", "Order cancellation", "Order status update", "Order history", "Invoice generation", "Order tracking", "Return request", "Reorder", "Bulk order", "Order notification email"]),
    ("API Suite", ["GET /products", "POST /orders", "PUT /cart", "DELETE /cart/item", "Auth token validation", "Rate limit enforcement", "Pagination", "Error response schema", "Webhook delivery", "API versioning"]),
    ("Regression Suite", ["Full checkout regression", "Login regression", "Search regression", "Cart regression", "Profile update regression", "Admin dashboard regression", "Notification regression", "Search filters regression"]),
    ("Smoke Suite", ["App loads", "Login smoke", "Checkout smoke", "Search smoke", "Admin loads"]),
    ("Security Suite", ["SQL injection attempt", "XSS attempt", "CSRF token validation", "Broken access control check", "Sensitive data exposure check", "Rate limiting on login", "Security headers present"]),
    ("Accessibility Suite", ["Keyboard navigation", "Screen reader labels", "Color contrast", "Form label association", "Focus order", "Alt text on images", "ARIA landmarks"]),
    ("Performance Suite", ["Homepage load time", "Checkout API latency", "Search response time", "Cart update latency", "Product page load", "Concurrent user load"]),
]

_TYPE_BY_SUITE_PREFIX = {
    "Authentication": "functional", "Checkout": "functional", "Payment": "functional",
    "Order": "functional", "API": "api", "Regression": "regression", "Smoke": "smoke",
    "Security": "security", "Accessibility": "accessibility", "Performance": "performance",
}


async def seed_demo_data() -> None:
    db = get_database()
    rng = random.Random("wayam-demo-seed")

    existing_org = await db.organizations.find_one({"name": "Wayam Demo Organization"})
    if existing_org:
        return

    org = Organization(name="Wayam Demo Organization")
    await db.organizations.insert_one(org.model_dump(by_alias=True))

    demo_user = User(
        email="demo@wayam.ai",
        hashed_password=hash_password("demo"),
        name="Demo User",
        organization_id=org.id,
        role="owner",
    )
    await db.users.insert_one(demo_user.model_dump(by_alias=True))

    project = Project(organization_id=org.id, name="Acme Commerce", project_type="e_commerce", created_by=demo_user.id)
    await db.projects.insert_one(project.model_dump(by_alias=True))

    failed_result_for_defect = None

    for suite_name, case_titles in _SUITES:
        suite_type = _TYPE_BY_SUITE_PREFIX[suite_name.split(" ")[0]]
        suite = TestSuite(organization_id=org.id, project_id=project.id, name=suite_name, created_by=demo_user.id)

        case_ids = []
        for title in case_titles:
            case = TestCase(
                organization_id=org.id, project_id=project.id,
                title=title, type=suite_type,
                priority=rng.choice(["low", "medium", "high", "critical"]),
                steps=[f"Set up preconditions for {title}", f"Execute: {title}", "Verify expected outcome"],
                expected_result=f"{title} behaves as specified",
                status="active", automation_status=rng.choice(["manual", "automated"]),
                created_by=demo_user.id,
            )
            await db.test_cases.insert_one(case.model_dump(by_alias=True))
            case_ids.append(case.id)

        suite.test_case_ids = case_ids
        await db.test_suites.insert_one(suite.model_dump(by_alias=True))

        run = TestRun(
            organization_id=org.id, project_id=project.id, suite_id=suite.id,
            status="completed", total=len(case_ids), created_by=demo_user.id,
        )
        counts = {"passed": 0, "failed": 0, "skipped": 0, "blocked": 0}
        for case_id in case_ids:
            roll = rng.random()
            status = "passed" if roll > 0.22 else ("failed" if roll > 0.08 else ("flaky" if roll > 0.04 else "skipped"))
            bucket = "passed" if status == "passed" else ("failed" if status in ("failed", "flaky") else "skipped")
            counts[bucket] = counts.get(bucket, 0) + 1

            error_message = None
            stack_trace = None
            if status in ("failed", "flaky"):
                error_message = rng.choice([
                    "Timeout waiting for element #submit-payment",
                    "Expected status 200 but received 500",
                    "AssertionError: expected 'Order Confirmed' but got 'Order Pending'",
                ])
                stack_trace = f"at {suite_name.replace(' ', '_')}.spec.ts:{rng.randint(10, 120)}"

            result = TestResult(
                organization_id=org.id, project_id=project.id, run_id=run.id,
                test_case_id=case_id, status=status, duration_ms=rng.randint(80, 2200),
                error_message=error_message, stack_trace=stack_trace,
            )
            await db.test_results.insert_one(result.model_dump(by_alias=True))

            if suite_name == "Payment Suite" and status == "failed" and failed_result_for_defect is None:
                failed_result_for_defect = result

        run.passed = counts.get("passed", 0)
        run.failed = counts.get("failed", 0)
        run.skipped = counts.get("skipped", 0)
        await db.test_runs.insert_one(run.model_dump(by_alias=True))

    if failed_result_for_defect:
        defect = Defect(
            organization_id=org.id, project_id=project.id,
            title="Payment times out under checkout load",
            description="Checkout payment submission intermittently times out, leaving orders in a pending state.",
            severity="critical", priority="high", status="open",
            related_test_result_id=failed_result_for_defect.id,
            related_test_case_id=failed_result_for_defect.test_case_id,
            created_by=demo_user.id,
        )
        await db.defects.insert_one(defect.model_dump(by_alias=True))


if __name__ == "__main__":
    asyncio.run(seed_demo_data())
