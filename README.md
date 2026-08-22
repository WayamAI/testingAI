# WayamAI Testing Cloud

WayamAI gives engineering teams a single AI-powered platform to plan,
generate, execute, and analyze software tests end to end — replacing a
patchwork of test case spreadsheets, manual execution logs, and disconnected
defect trackers with one system that understands requirements, writes tests,
runs them, and explains what broke.

This repository is **Sub-project 1: Foundation + Core Workflow Skeleton** of
a much larger platform. It establishes the architectural skeleton (auth,
multi-tenancy, provider abstractions, data model) and makes the platform's
primary demo journey work end-to-end against real, persisted data — not a
static prototype. See `docs/superpowers/specs/2026-08-18-foundation-core-workflow-design.md`
for the full design spec this build follows.

## Architecture

```
testingAI/
  frontend/               React 18 + TS + Vite + Tailwind + shadcn/ui  (dev :5173)
    src/
      components/          ai/, common/, dashboard/, execution/, layout/, quality/
      config/               env.ts — reads VITE_* at build/run time
      contexts/             AuthContext
      hooks/                useExecutionSocket, useDefaultProjectId
      pages/                ~90 route pages (real pages + EmptyState placeholders)
      services/api/         auth, dashboard, ai, testing, execution, quality
    e2e/                    Playwright spec — primary demo journey
  backend/                 FastAPI + Pydantic v2 + Motor/MongoDB          (dev :8000)
    app/
      core/                 settings (Settings/get_settings), security (JWT)
      database/              Motor client, connection handling
      models/                Pydantic Mongo document models
      schemas/               request/response Pydantic schemas
      routes/                auth, projects, requirements, test_suites,
                              test_cases, test_runs, websocket_execution,
                              defects, quality, ai, dashboard
      services/              business logic per domain
      engines/
        ai/                  AIProvider, OllamaProvider, DemoAIProvider,
                              stub OpenAI/Anthropic/Gemini providers
        execution/            ExecutionProvider, DemoExecutionProvider,
                              stub Playwright/API/Mobile/Performance providers
      security/               JWT dependency, org-scoping dependency
      seed/                   seed_demo.py — demo org/project/data
      middleware/             global error handler
    tests/                   pytest — auth, org isolation, AI fallback, core routes
  worker/                  ARQ worker process, Redis-backed queue           (scaffold)
    worker.py                WorkerSettings — placeholder task; this phase's
                              execution runs synchronously in the backend's
                              WebSocket handler, not through this queue
  docs/
    superpowers/plans/, specs/   planning and design docs for this build
  scripts/
    dev.sh                  starts backend, worker, frontend; checks Mongo/Redis
  .env.example               shared template (Mongo/Redis/JWT/Ollama/VITE_* keys)
  backend/.env.example       backend + worker subset of the above
  frontend/.env.example      VITE_* subset of the above
```

No Docker Compose in this sub-project — local processes only, per explicit
decision. MongoDB is expected locally on `mongodb://localhost:27017`, Redis
on `redis://localhost:6379`.

## Local setup

1. Make sure MongoDB is reachable at `mongodb://localhost:27017` and Redis at
   `redis://localhost:6379` (e.g. via Docker containers or local installs).
2. Copy the root template into each service, filling in a real
   `OLLAMA_API_KEY` (an Ollama Cloud key — see https://ollama.com):
   ```bash
   cp .env.example backend/.env
   cp .env.example worker/.env
   cp .env.example frontend/.env   # only the VITE_* keys are read here
   ```
   Trimmed, service-specific starting points are also provided —
   `backend/.env.example` and `frontend/.env.example` — if you'd rather copy
   only the keys each service actually reads (see the settings reference
   below).
3. Create Python virtualenvs and install dependencies:
   ```bash
   cd backend && python3 -m venv .venv && source .venv/bin/activate \
     && pip install -r requirements.txt && deactivate && cd ..
   cd worker && python3 -m venv .venv && source .venv/bin/activate \
     && pip install -r requirements.txt && deactivate && cd ..
   ```
4. Install frontend dependencies:
   ```bash
   cd frontend && npm install && cd ..
   ```
5. Run everything:
   ```bash
   ./scripts/dev.sh
   ```
   This starts the backend (`:8000`, auto-reload), the ARQ worker, and the
   frontend (`:5173`), warning (not blocking) if Mongo/Redis aren't
   reachable yet. `Ctrl-C` stops all three.
6. Open http://localhost:5173/login and click **Demo Login**.

### Settings reference

The backend (`backend/app/core/config.py`) reads exactly these keys from
`.env` (via `pydantic-settings`), all with sane local defaults:

| Key | Default | Used by |
|---|---|---|
| `MONGODB_URI` | `mongodb://localhost:27017` | backend, worker |
| `DATABASE_NAME` | `wayam_testing_cloud` | backend |
| `JWT_SECRET` | `change-me-in-local-env` | backend (auth) |
| `JWT_EXPIRE_MINUTES` | `1440` | backend (auth) |
| `DEMO_MODE` | `true` | backend (auth, demo login gate) |
| `REDIS_URL` | `redis://localhost:6379` | worker |
| `OLLAMA_BASE_URL` | `https://ollama.com` | backend (AI provider) |
| `OLLAMA_API_KEY` | *(empty)* | backend (AI provider) |
| `OLLAMA_MODEL` | `gpt-oss:120b-cloud` | backend (AI provider) |

The frontend (`frontend/src/config/env.ts`) reads only:

| Key | Default | Used by |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000` | API base URL |
| `VITE_DEMO_MODE` | — | shows/hides the Demo Login affordance |

## Demo mode

`DEMO_MODE=true` (the default) enables a one-click **Demo Login** button on
the login page and accepts any email/password pair, auto-provisioning a
personal org on first login. This is isolated behind a single
`if settings.demo_mode` branch in `backend/app/services/auth_service.py`.

The Demo Login button always resolves to `demo@wayam.ai`, which is seeded
once (idempotently, on backend startup) onto a fixed **"Wayam Demo
Organization"** / **"Acme Commerce"** project by
`backend/app/seed/seed_demo.py`. The seed creates ten realistic test suites
(Authentication, Checkout, Payment, Order, API, Regression, Smoke, Security,
Accessibility, Performance) with populated test cases, at least one recent
run per suite with a genuine mix of passed/failed/skipped/flaky results, and
at least one open critical defect — deliberately **not** an all-green
showcase, so the Dashboard, Quality Score, and Release Readiness pages have
real signal to show from the first login.

AI calls (test generation, failure analysis) try the real `OllamaProvider`
first; on any failure (timeout, auth, malformed response) they fall back to
a deterministic `DemoAIProvider` for that single request, and the API
response carries a `source: "ai" | "demo_fallback"` field so the UI can
render a small, honest badge — a fallback answer is never presented as if
it came from the live model.

## Running tests

```bash
# Backend
cd backend && source .venv/bin/activate && pytest

# Frontend unit/component tests
cd frontend && npx vitest run

# Frontend type-check + lint + build
cd frontend && npx tsc -b && npx oxlint && npx vite build

# End-to-end (primary demo journey), against a running dev stack
cd frontend && npx playwright test
```

## Sub-project 2: real testing & quality execution

Sub-project 2 (spec: `docs/superpowers/specs/2026-08-22-real-testing-execution-design.md`)
narrowed the product surface to **Testing and Quality only** — every other
sidebar section (AI Testing, Web/API/Mobile Testing, Performance, Security,
Data, Automation, Integrations, Administration) was removed along with its
stub pages, and real execution capability was added:

- **Connect Project** (`/connect-project`): paste a public git URL or
  upload a ZIP. The platform clones/extracts it into an isolated
  `backend/workspaces/{project_id}/` directory, detects its real stack
  (currently: Node/Jest/Vitest via `package.json`, Python/PyTest via
  `requirements.txt`/`pyproject.toml`), and shows the genuine result — or a
  specific "no recognized test manifest" reason, never a guess.
- **Run Tests** executes the connected project's own real test command as
  a supervised subprocess (`SubprocessExecutionProvider`), parses its
  native JSON/JUnit-XML report, and streams genuine pass/fail results over
  the same WebSocket live-execution view sub-project 1 built — demo and
  connected projects share the UI, never the data.
- **Run Security Scan** runs real Semgrep (SAST) and pip-audit/npm audit
  (dependency vulnerabilities) against the workspace, persists actual
  findings, and folds them into the Quality Score's security sub-score
  once a scan has run (previously a fixed placeholder).
- **Run API Tests** discovers a real OpenAPI/Swagger spec in the connected
  repo and executes real HTTP GET requests against a supplied base URL for
  every parameter-free endpoint (parameterized endpoints are explicitly
  skipped with a reason in this first cut, not faked).

Deferred from this round: private repos, non-GET API testing, JUnit/Go-test
etc. detection rules, and container/VM sandboxing (isolation is a per-project
workspace directory plus a subprocess timeout, not a container boundary).

## What's implemented in this phase vs. deferred

This build makes the primary demo journey real and persisted: **Login →
Dashboard → Project → Requirement → AI Test Generation → Test Suite → Run →
Live Execution → Failure → AI Failure Analysis → Defect → Quality Score →
Release Readiness → Quality Gate.** Every item in the full sidebar renders a
real page backed by seeded data, or a clearly labeled "not yet available in
this phase" empty state — never a dead link or blank page.

Deferred to a later sub-project (mirroring the spec's Non-goals):

- **Real browser/mobile/performance/security execution engines.** Only the
  `DemoExecutionProvider` ships this round; `PlaywrightExecutionProvider`,
  `APIExecutionProvider`, `MobileExecutionProvider`, and
  `PerformanceExecutionProvider` exist as interface-only stubs.
- **OAuth/SSO/SAML/MFA.** Acknowledged in the schema, not implemented —
  auth is JWT + demo mode only.
- **Billing, and live GitHub/Jira/Slack integrations**, plus a
  self-hosted runner.
- **Any P1/P2 feature** from the master spec's priority list beyond what's
  needed to make the sidebar non-dead and the primary journey work.
- **Background task processing.** The ARQ `worker/` process boots and is
  wired to Redis, but this phase's execution runs synchronously inside the
  backend's WebSocket handler (`backend/app/routes/websocket_execution.py`)
  rather than through enqueued jobs; the worker currently carries only a
  placeholder task as scaffolding for later async work (report generation,
  scheduled runs, etc.).
