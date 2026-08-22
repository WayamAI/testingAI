# WayamAI Testing Cloud — Sub-project 2: Real Testing & Quality Execution (first cut)

Date: 2026-08-22
Status: Approved for implementation

## Context

Sub-project 1 (merged to `main`) built the architectural skeleton: auth,
org/project multi-tenancy, provider abstractions, and the primary demo
journey working end-to-end against seeded MongoDB data via a
`DemoExecutionProvider` and `DemoAIProvider`. Every result a user sees today
is either seeded or simulated — nothing runs against a real project yet.

This sub-project's explicit brief: reduce product surface to **only Testing
and Quality** (drop every other sidebar section), and make test execution
**real** for a first cut — a user can point the platform at an actual
project and get genuine pass/fail/security/API results, not simulated ones.
Keep it basic and workable; deeper coverage (performance, accessibility,
visual, mobile, real Docker sandboxing) is explicitly deferred.

## Goals

1. Prune the sidebar to two groups only: **Overview** (Dashboard) and
   **Test Management** + **Quality** — remove AI Testing, Web Testing, API
   Testing, Mobile Testing, Performance, Security, Data, Automation,
   Integrations, and Administration as standalone nav sections and their
   stub pages/routes entirely.
2. A user can connect a real project two ways: paste a public git URL, or
   upload a ZIP. The platform clones/extracts it into an isolated
   per-project workspace — never executes it in place, never on the host
   filesystem outside that workspace.
3. `DetectionEngine` inspects the workspace and produces a real
   `ApplicationProfile` (language, framework, test framework, package
   manager) from manifest files — no guessing beyond what the manifest
   supports.
4. `SubprocessExecutionProvider` (a second `ExecutionProvider`
   implementation alongside the existing Demo one) actually runs the
   detected project's real test command, captures real stdout/stderr,
   parses framework-native JSON/JUnit output into genuine `TestResult`
   documents, and streams progress over the existing WebSocket channel
   unchanged.
5. `SecurityScanProvider` runs Semgrep (auto ruleset) for SAST and
   `pip-audit`/`npm audit` for dependency vulnerabilities when the
   relevant manifest exists, producing real `SecurityFinding` documents.
6. `APITestProvider` discovers an OpenAPI/Swagger file in the connected
   repo (or accepts one pasted/uploaded), generates real HTTP requests
   against a user-supplied base URL, and records real status
   codes/latency/schema-conformance as `TestResult`s of type `api`.
7. Every capability not covered this round (performance, accessibility,
   visual regression, mobile, chaos, contract testing beyond basic schema
   checks) is declared but shows `NOT AVAILABLE` / `REQUIRES
   CONFIGURATION` with the specific reason — never fabricated.
8. Demo mode/data from sub-project 1 keeps working unchanged and stays
   clearly labeled — real projects and demo data never mix.

## Non-goals (explicitly deferred)

- Docker/container sandboxing (isolation stays: per-project workspace dir +
  subprocess timeout, documented as a known limitation).
- Performance, accessibility, visual regression, mobile, chaos testing.
- Self-healing, intelligent test selection, flaky-test statistical
  detection, AI root-cause analysis beyond what sub-project 1 already has.
- CI/CD, Slack/Teams/Jira/GitHub-app integrations, RBAC beyond the
  existing org-scoping, billing.
- Private repo credentials (public git URLs and ZIP upload only).

## Architecture

```
backend/app/
  intake/
    workspace.py       per-project isolated dir under backend/workspaces/{project_id}/
    git_clone.py        git clone --depth 1 into workspace, timeout + error handling
    zip_extract.py       safe zip extraction (path-traversal guarded, size-limited)
  detection/
    engine.py            DetectionEngine.detect(workspace_path) -> ApplicationProfile
    rules.py              manifest -> language/framework/test-framework mapping table
  engines/execution/
    subprocess_provider.py   SubprocessExecutionProvider(ExecutionProvider)
    result_parsers/          per-framework JSON/JUnit output -> TestResult[]
  engines/security/
    base.py                SecurityScanProvider ABC
    semgrep_provider.py      real Semgrep subprocess -> SecurityFinding[]
    dependency_provider.py   pip-audit / npm audit subprocess -> SecurityFinding[]
  engines/api_testing/
    base.py                 APITestProvider ABC
    openapi_provider.py      discovers/parses OpenAPI spec, executes real requests
  models/
    security_finding.py     new MongoDocument
  routes/
    intake.py               POST /api/projects/{id}/connect-repo, /connect-zip
    security.py              GET/POST /api/projects/{id}/security-scans
    api_testing.py            GET/POST /api/projects/{id}/api-tests
```

`SubprocessExecutionProvider` implements the exact same `ExecutionProvider`
interface as `DemoExecutionProvider` from sub-project 1 — the WebSocket
live-execution frontend view is unchanged; only the provider selected by
`get_execution_provider(project)` differs based on `project.source`.

`Project` model gains `source: "demo" | "connected"` and, when connected,
`application_profile: ApplicationProfile | None`.

## Frontend changes

- `Sidebar.tsx`: `SIDEBAR_GROUPS` reduced to `Overview` and `Test
  Management` + `Quality` only; all removed groups' page/route files
  deleted along with their router entries. `Overview` keeps only
  `Dashboard` (drop `Quality Intelligence`/`Activity` stub pages — they
  belong to a removed concept, not Testing/Quality).
- `Test Management` gains a **Connect Project** action (git URL or ZIP
  upload) that calls the new intake routes and shows real-time detection
  progress; the existing per-suite "Run" flow works unchanged for
  connected projects, now backed by `SubprocessExecutionProvider`.
- New minimal **Security Findings** view and **API Tests** view live under
  `Test Management` (not as separate top-level sections) showing the new
  real data.
- A **capability badge** component shows `AVAILABLE` / `REQUIRES
  CONFIGURATION` / `NOT AVAILABLE` per testing type on the project page,
  driven by the `ApplicationProfile` (e.g., no `requirements.txt`/
  `package.json` test script found → unit testing `NOT AVAILABLE` with
  reason shown).

## Detection rules (first cut)

| Manifest | Language | Test framework | Run command |
|---|---|---|---|
| `package.json` with `"test"` script | JS/TS | Jest/Vitest (whichever devDependency present) | `npm test -- --json` (or vitest equivalent) |
| `requirements.txt` or `pyproject.toml` | Python | PyTest | `pytest --json-report --json-report-file=report.json` |
| none of the above | — | — | unit/integration testing `NOT AVAILABLE`: "No recognized test manifest found" |

This table is intentionally small for the first cut — `rules.py` is
structured as an ordered list of `(matcher, profile_factory)` so later
sub-projects add JUnit/Go-test/etc. without touching calling code.

## Error handling

- Invalid git URL / clone timeout / unreachable host → stored
  `AnalysisError` with cause + remediation, project stays in `error` intake
  state, never crashes the request.
- Malformed/oversized ZIP, zip-slip attempts → rejected before extraction
  with a specific reason.
- No test command detected → capability badge `NOT AVAILABLE`, not an
  error.
- Test command present but install/run fails → captured as a real failed
  `TestRun` with the actual stderr surfaced, not a silent skip.
- Semgrep/pip-audit/npm-audit not installed on the host → capability badge
  `REQUIRES CONFIGURATION` with the exact missing binary named.

## Testing

- Backend pytest: `DetectionEngine` against small fixture repos (checked
  into `backend/tests/fixtures/` — one tiny real Jest project, one tiny
  real PyTest project, one with no test manifest); `SubprocessExecutionProvider`
  against those same fixtures asserting real pass/fail counts;
  `SecurityScanProvider` against a fixture with one intentionally
  vulnerable dependency; zip-extract path-traversal rejection test;
  git-clone timeout/invalid-URL test.
- Frontend: sidebar renders only the two retained groups + Overview;
  removed routes 404 or redirect cleanly (no dead nav entries pointing at
  deleted pages).
- One Playwright E2E: connect the fixture ZIP project → see real detected
  profile → run → see real pass/fail results from the actual subprocess.

## Definition of done for this sub-project

- [ ] Sidebar shows only Overview, Test Management, Quality — all other
      groups and their page/route files removed.
- [ ] `POST /api/projects/{id}/connect-repo` and `/connect-zip` work,
      produce a real `ApplicationProfile`, and handle bad input without
      crashing.
- [ ] `SubprocessExecutionProvider` runs a real fixture project's test
      suite and produces genuine `TestResult`s streamed over the existing
      WebSocket channel.
- [ ] Security scan and API test routes return real findings/results on
      fixture projects, and a correct "not available"/"requires
      configuration" state when tools/specs are absent.
- [ ] Capability badges never claim a testing type is available when it
      isn't.
- [ ] Demo mode/journey from sub-project 1 still passes unchanged.
- [ ] Backend pytest, frontend typecheck/build, and the new Playwright E2E
      all pass.
