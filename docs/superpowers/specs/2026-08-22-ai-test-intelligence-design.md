# WayamAI Testing Cloud — Sub-project 3: AI Test Intelligence

Date: 2026-08-22
Status: Approved for implementation

## Context

Ported from a sibling Wayam product's ("AIDLC") Testing & Quality module,
adapted to this codebase's stack (Motor/MongoDB, the existing `AIProvider`
abstraction with Ollama→demo fallback — not OpenAI) and its existing
git-clone/ZIP intake (`app/intake/`, `app/detection/`). User confirmed:
build all 7 capabilities in one pass, sequenced by dependency (baseline
generation and defect prediction first, since selection/root-cause/
self-healing all consume their output).

## Goals — 7 capabilities

1. **Repo Test Baseline** — clone a repo (reuses `app/intake/git_clone.py`),
   AI-generates categorized Playwright tests (auth/api/crud/ui_form/
   ui_navigation/ui_component/integration/edge_case/performance/
   accessibility) from a repo-structure summary, stores them as real
   `.spec.ts` files in the workspace + `TestCase` docs. Incremental
   re-scan: track `last_scanned_commit`, diff against it on re-scan,
   generate tests only for categories touched by changed files, append —
   never regenerate/duplicate existing baseline tests.
2. **Doc-Driven Tests** — upload PDF/DOCX/TXT/MD (PRD/spec/API-def), parse
   real text (`pypdf`, `python-docx`), AI extracts test scenarios from the
   extracted text, generates Playwright tests from them. Fills the
   previously-flagged document-upload gap.
3. **Live Test Runner** — given a connected project + a running app URL,
   analyzes the URL's live HTML + detected stack, AI-generates Playwright
   tests, executes them for real via the frontend's already-installed
   `@playwright/test` + Chromium (reused, not reinstalled), captures a
   screenshot per test (Playwright's `screenshot: 'on'` reporter setting —
   honestly labeled as per-test, not per-step, in this first cut), full
   run history persisted.
4. **Defect Prediction** — mines real `git log --numstat` history per file:
   `risk = 0.30×change_frequency + 0.35×bug_fix_ratio + 0.20×churn +
   0.15×author_count` (each min-max normalized across the repo's files).
   AI narrative on the top-N riskiest files; deterministic fallback
   narrative (template, not LLM) when AI is unavailable.
5. **AI Root Cause Analysis** — extends the existing `analyze_failure_with_fallback`
   with real git correlation: pulls recent commits in the workspace,
   ranks candidates by file-path overlap with the failure's stack trace,
   gets the real diff (`git show`) of the top candidate, feeds
   error+diff+commit list to the AI for root cause / confidence /
   likely-commit / remediation / re-run action.
6. **Intelligent Test Selection & Optimization** — maps changed files
   (`git diff` since a base commit) to baseline tests via direct file
   match + directory-proximity match, weighted by capability 4's risk
   score; explainable per-test score breakdown; executes only the
   selected subset. Duplicate-test and coverage-gap detection are
   computed for real (title/step similarity, category coverage vs.
   detected routes). Flaky/long-running detection is computed for real
   **only** when a test has ≥3 historical `TestResult`s — otherwise
   explicitly reported "not available: insufficient run history", never
   fabricated.
7. **Self-Healing Tests** — scoped strictly to selector-not-found
   failures (all other failure types explicitly out of scope, reported
   as such). Live-scans the real DOM via Playwright for candidate
   elements, gives the AI a **numbered list of real selectors** and lets
   it pick only an index (structurally cannot invent a selector),
   validates the candidate against the live page, and requires explicit
   human approval in the UI before any write-back to the test file.

## Non-goals

- Not porting AIDLC's OpenAI-based `ai_service.py` pattern — reusing this
  codebase's `AIProvider`/`OllamaProvider`/`DemoAIProvider` abstraction and
  extending it with new methods, so demo-fallback and `source` tagging stay
  consistent everywhere.
- Not adding real DOM sandboxing beyond Playwright's own browser process
  isolation; not adding CI integration for these flows this round.
- Self-healing write-back is manual-approval only — no auto-apply.

## Architecture (per-feature, repeated pattern)

```
backend/app/models/<feature>.py         Pydantic: entity + *Out schemas + label enum
backend/app/services/<feature>_service.py   core logic (generation/scoring/collection)
backend/app/engines/ai/base.py          [MODIFY] new input/output dataclasses per feature
backend/app/engines/ai/demo_provider.py [MODIFY] deterministic fallback per new method
backend/app/engines/ai/ollama_provider.py [MODIFY] real-provider prompt per new method
backend/app/engines/ai/factory.py       [MODIFY] *_with_fallback() wrapper per new method
backend/app/routes/<feature>.py         REST endpoints under /api/testing/<feature>,
                                         org-scoped via existing get_current_user /
                                         get_current_org_scope
backend/app/main.py                     [MODIFY] register router
backend/tests/test_<feature>_*.py       real end-to-end tests — real app_client/db
                                         fixtures + real JWT session, never mocked auth
frontend/src/services/api/<feature>.ts  TS interfaces + api methods (this repo's existing
                                         per-feature-file convention, not one lib/api.ts)
frontend/src/pages/...                  UI surfaced under the existing Connect Project
                                         page / Test Suites / Quality pages — no new
                                         top-level sidebar sections (still Testing+Quality
                                         only per sub-project 2's scope)
```

## Data model additions

`baseline_scans`, `generated_tests` (with `category`, `source_commit`),
`doc_uploads`, `extracted_scenarios`, `live_runs` (+ screenshot artifact
paths), `file_risk_scores`, `root_cause_analyses` (extends existing
`ai_requests`), `test_selection_runs`, `self_heal_attempts` (status:
`proposed|approved|rejected`).

## Safety

- AI-generated Playwright test code is written to disk but never executed
  without going through the same subprocess-timeout execution path as
  sub-project 2's `SubprocessExecutionProvider` — no blind eval.
- Self-healing AI output is constrained to an index into a real candidate
  list — cannot inject arbitrary selector strings.
- Every AI-derived claim (root cause, risk narrative, doc-extracted
  scenario) carries `source: "ai" | "demo_fallback"` and, where
  applicable, a numeric confidence — never presented as certain.

## Testing

Real end-to-end per feature, using the same fixture-repo pattern as
sub-project 2 (`backend/tests/fixtures/`) — real git repos with real
commit history for defect prediction / root cause / test selection; a
real tiny web page for live-runner / self-healing DOM tests.

## Definition of done

- [ ] All 7 capabilities have real backend logic (no fabricated
      results) and pass real end-to-end tests.
- [ ] Repo Test Baseline and Doc-Driven Tests both produce real,
      syntactically-valid Playwright test files.
- [ ] Defect Prediction scores come from real `git log` mining on a real
      fixture repo with crafted commit history.
- [ ] Root Cause Analysis correlates against a real commit in a real
      fixture repo.
- [ ] Test Selection's flaky-detection honestly reports "not available"
      below the history threshold, and real above it.
- [ ] Self-Healing only activates on selector-not-found failures, never
      writes back without an explicit approval action.
- [ ] Existing sub-project 1 & 2 demo journeys still pass unchanged.
