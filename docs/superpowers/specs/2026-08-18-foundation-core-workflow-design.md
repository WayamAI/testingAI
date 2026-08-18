# WayamAI Testing Cloud — Sub-project 1: Foundation + Core Workflow Skeleton

Date: 2026-08-18
Status: Approved for implementation

## Context

WayamAI Testing Cloud is a brand-new, standalone enterprise SaaS platform for
AI-powered software testing (full product vision: see the master prompt
supplied at project kickoff — 160 sections covering test management, AI
generation, execution, web/API/mobile/performance/security testing, quality
scoring, release readiness, integrations, RBAC, billing, etc.). Building the
whole thing in one pass is not viable; this spec covers only the first
sub-project, which establishes the architectural skeleton and makes the
platform's primary demo journey (spec §93) work end-to-end with real,
persisted data — not a static prototype.

Everything not explicitly listed under "In scope" below is deferred to a
later sub-project and must not silently be built now.

## Goals

1. A completely independent repo, database, and auth — no dependency on any
   other Wayam product (AIDLC or otherwise).
2. Every item in the full sidebar (spec §20) renders a real page — populated
   from seeded demo data where the feature is in scope this round, or a
   clearly labeled "not yet available in this phase" state otherwise. Never
   a dead link, blank page, or fake button (§134).
3. The primary demo journey (§93) works fully, backed by real API calls and
   real MongoDB persistence: Login → Dashboard → Project → Requirement → AI
   Test Generation → Test Suite → Run → Live Execution → Failure → AI
   Failure Analysis → Defect → Quality Score → Release Readiness → Quality
   Gate.
4. AI and execution are built behind provider abstractions so later
   sub-projects can add real providers without touching calling code.
5. Demo mode is real: seeded "Wayam Demo Organization" / "Acme Commerce"
   project with a realistic mix of passing, failing, flaky, and skipped
   tests, and genuine defects — not an all-green showcase (§92, §138-139).

## Non-goals (explicitly deferred)

- Real browser/mobile/performance/security execution engines (only the
  Demo provider ships this round; interfaces are defined for the rest).
- OAuth/SSO/SAML/MFA (interface acknowledged in schema, not implemented).
- Billing, GitHub/Jira/Slack live integrations, self-hosted runner.
- Any P1/P2 feature from the master spec's priority list (§133) beyond what
  is needed to make the sidebar non-dead and the primary journey work.

## Architecture

```
testingAI/
  frontend/    React 18 + TS + Vite + Tailwind + shadcn/ui   (dev :5173)
  backend/     FastAPI + Pydantic v2 + Motor/MongoDB         (dev :8000)
  worker/      ARQ worker process, Redis-backed queue
  docs/
  scripts/     dev.sh — starts all three, checks Mongo/Redis reachability
  .env.example
  README.md
```

No Docker Compose in this sub-project — local processes only, per explicit
decision. MongoDB is reachable locally on `mongodb://localhost:27017`
(confirmed running via an existing Docker container on this machine).
Redis is confirmed running natively on the default port for the worker
queue.

### Backend layout (per master spec §12)

```
backend/app/
  core/            settings, security (JWT), demo-mode gate
  database/        Motor client, index setup
  models/          Pydantic Mongo document models
  schemas/         request/response Pydantic schemas
  routes/          auth, organizations, projects, requirements,
                    test-suites, test-cases, test-runs, executions,
                    defects, quality, releases, ai, dashboard
  services/        business logic per domain
  engines/
    ai/            AIProvider, OllamaProvider, DemoAIProvider,
                    stub OpenAI/Anthropic/Gemini providers
    execution/     ExecutionProvider, DemoExecutionProvider,
                    stub Playwright/API/Mobile/Performance providers
  workers/         ARQ task definitions (shared with worker/ process)
  security/        JWT dependency, org-scoping dependency, RBAC checks
  analytics/       quality score + risk score calculators
  utils/, middleware/
```

### Frontend layout (per master spec §11)

Standard structure from the master spec (components/{ui,layout,dashboard,
testing,ai,execution,analytics,quality}, pages/, hooks/, contexts/,
services/api/, types/, lib/, config/). Sidebar renders all §20 groups;
routes not yet backed by real data show a consistent "phase 2" empty state
component rather than being omitted.

## Data model (collections in scope)

`organizations, users, projects, environments, requirements, test_suites,
test_cases, test_runs, test_results, defects, quality_scores, ai_requests,
audit_logs`

Each document carries `organization_id`, `created_by`, `created_at`,
`updated_at` per §147. Org isolation is enforced by a single FastAPI
dependency (`get_current_org_scope`) injected into every route — not
reimplemented per-endpoint.

## Auth & multi-tenancy

- JWT access tokens (password hashing via passlib/bcrypt).
- `DEMO_MODE=true` (default in `.env.example`) allows a one-click "Demo
  Login" button and accepts any email/password pair, auto-provisioning a
  personal org on first login. This behavior is isolated behind a single
  `if settings.DEMO_MODE` branch in the auth service, clearly commented.
- Hierarchy enforced: Organization → Project → (Environment) → Tests,
  matching §14.

## AI provider abstraction

```python
class AIProvider(ABC):
    async def generate_test_cases(self, input: TestGenInput) -> list[GeneratedTestCase]: ...
    async def analyze_failure(self, context: FailureContext) -> FailureAnalysis: ...

class OllamaProvider(AIProvider):
    # base_url=https://ollama.com, model=gpt-oss:120b-cloud, api key from env
    # calls wrapped with timeout + try/except -> raises AIProviderError

class DemoAIProvider(AIProvider):
    # deterministic, realistic canned generation using input text keywords
    # always succeeds — this is the guaranteed fallback
```

A thin `get_ai_provider()` factory tries `OllamaProvider` first; on any
failure (timeout, auth, network) it logs and falls back to
`DemoAIProvider` for that request, and the API response includes a
`source: "ai" | "demo_fallback"` field so the UI can show a subtle badge
(§113-114) — never silently pretends a fallback answer came from the live
model. `OpenAIProvider`, `AnthropicProvider`, `GeminiProvider` classes
exist with method signatures only, raising `NotImplementedError` — future
sub-project fills them in.

## Execution provider abstraction

```python
class ExecutionProvider(ABC):
    async def run_suite(self, run: TestRun) -> AsyncIterator[ExecutionEvent]: ...

class DemoExecutionProvider(ExecutionProvider):
    # simulates queued -> preparing -> running -> per-test pass/fail/flaky
    # with randomized-but-seeded realistic timing, streamed over WebSocket
```

`PlaywrightExecutionProvider`, `APIExecutionProvider`,
`MobileExecutionProvider`, `PerformanceExecutionProvider` are declared as
stubs implementing the same interface, not implemented. WebSocket channel:
`/ws/executions/{run_id}` streams `ExecutionEvent`s to the frontend's live
execution view.

## Demo data seed

A `scripts/seed_demo.py` (or FastAPI startup seed in `DEMO_MODE`) creates:
- Org: "Wayam Demo Organization"
- Project: "Acme Commerce" (auth, catalog, cart, checkout, payments, orders,
  profile, admin, API, database areas per §136)
- Suites: Authentication, Checkout, Payment, Order, API, Regression, Smoke,
  Security, Accessibility, Performance (§137) — populated with realistic
  test case counts, not just names
- At least one recent test run per suite with a realistic mix of
  passed/failed/skipped/flaky results (§138)
- At least one critical defect linked to a failed test (§138)
- A computed quality score in the "requires review" range (§139: score
  ~86, pass rate ~93%, 1 critical defect, 7 flaky tests, 84% coverage)

## Primary journey — acceptance criteria

The following must work via real UI actions hitting real backend endpoints
with real persistence (no client-side mocking):

1. Login (demo login button, or any email/password in demo mode)
2. Dashboard shows real aggregated metrics computed from seeded data
3. Open Acme Commerce → open a requirement
4. AI Test Generator: submit requirement text → backend calls
   `get_ai_provider()` → returns generated test cases with type/priority/
   confidence → user can Accept/Edit/Reject
5. Accepted cases saved into a new Test Suite
6. Run the suite → WebSocket live execution view shows progressive
   status per test
7. At least one result fails → "Analyze with AI" triggers
   `analyze_failure` → shows root cause/confidence/recommendation
8. "Create Defect" from the failure pre-fills fields from the failure
   context and persists a defect document
9. Quality Score recalculates and is visibly explainable (sub-scores)
10. Release Readiness page shows computed status (READY / READY WITH RISK
    / REQUIRES REVIEW / BLOCKED) and a Quality Gate evaluation against a
    default policy (pass rate ≥ 95%, no open critical defects, etc.)

## Error handling & demo fallback

- Global FastAPI exception handler returns consistent `{error: {code,
  message}}` shape; internal exceptions never leaked to the client (§87).
- Every AI call: Ollama → on failure, Demo fallback, response tagged.
- Every execution: Demo provider only this round, so no fallback needed,
  but errors during simulated execution still surface as a failed test
  result, not a crashed run.

## Testing

- Backend: pytest — auth (incl. demo mode), org isolation (cross-org
  access denied), AI provider fallback behavior, the core workflow routes.
- Frontend: `tsc --noEmit`, eslint clean, `vite build` succeeds.
- One Playwright E2E exercising the acceptance-criteria journey above
  end-to-end against the running dev stack.

## Definition of done for this sub-project

- [ ] `scripts/dev.sh` starts backend, frontend, worker; checks Mongo/Redis
- [ ] Backend boots, connects to MongoDB, `/api/health` reports all subsystems
- [ ] Demo login works; org/project created and isolated
- [ ] All §20 sidebar items route to a real page (seeded data or labeled stub)
- [ ] Primary journey acceptance criteria above all pass manually and via
      the Playwright E2E
- [ ] AI fallback verified by forcing an Ollama failure
- [ ] `.env.example` present with no real secrets; Ollama key only in local
      untracked `.env`
- [ ] Repo pushed to `github.com/WayamAI/testingAI` on `main`
