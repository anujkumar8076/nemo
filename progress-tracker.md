# Progress Tracker

> This is the canonical high-level project progress file. Update it
> after every meaningful implementation milestone.

## Project

**Autonomous Dev Team**

## Current Stage

**Stage:** Phase 0 / Hosted CI verification\
**Overall status:** Foundation implemented and locally verified; the hosted CI exit gate awaits a GitHub remote and first push.

## Product Goal

Build an autonomous software engineering platform with:

``` text
Build Mode:
Task → Plan → Code → Test → Review → PR

Guardian Mode:
Production Failure → Detect → Diagnose → Repair → Test → PR → Verify
```

## Phase Status

  Phase   Scope                                  Status
  ------- -------------------------------------- -------------
  0       Architecture & repository foundation   IN PROGRESS
  1       Platform skeleton                      NOT STARTED
  2       GitHub App integration                 NOT STARTED
  3       Repository intelligence                NOT STARTED
  4       Sandbox runtime                        NOT STARTED
  5       Single-agent build loop                NOT STARTED
  6       Validation + PR pipeline               NOT STARTED
  7       Dashboard + human control              NOT STARTED
  8       Guardian Mode foundations              NOT STARTED
  9       Automatic incident repair              NOT STARTED
  10      Deployment verification                NOT STARTED
  11      Risk engine + multi-agent routing      NOT STARTED
  12      Security/policy hardening              NOT STARTED
  13      Model router + budgets                 NOT STARTED
  14      Observability + operations             NOT STARTED
  15      Production hardening                   NOT STARTED

## Completed Design Work

-   [x] Product concept defined.
-   [x] Build Mode defined.
-   [x] Guardian Mode defined.
-   [x] Human-approval boundary defined.
-   [x] Risk-based multi-agent model defined.
-   [x] GitHub App direction selected.
-   [x] FastAPI control-plane direction selected.
-   [x] Next.js frontend direction selected.
-   [x] PostgreSQL authoritative-state direction selected.
-   [x] Temporal durable-workflow direction selected.
-   [x] OpenHands-based agent runtime direction selected.
-   [x] Docker-first sandbox direction selected.
-   [x] Provider-neutral integration strategy defined.
-   [x] Production incident repair loop defined.
-   [x] Initial implementation sequence defined.

## Next Milestone --- Phase 0

-   [x] Initialize monorepo.
-   [x] Create `apps/web`.
-   [x] Create `apps/api`.
-   [x] Create `apps/worker`.
-   [x] Create shared package structure.
-   [x] Add local Docker Compose.
-   [x] Add PostgreSQL.
-   [x] Add Redis.
-   [x] Add Temporal.
-   [x] Establish CI.
-   [x] Establish lint/type/test commands.
-   [x] Add secret scanning.
-   [x] Add dependency scanning for JavaScript and Python.
-   [x] Add ADR directory.
-   [x] Add root `AGENTS.md`.
-   [x] Add these project context files to repository.
-   [x] Verify one-command local startup.
-   [ ] Run the workflow successfully on hosted GitHub Actions.

## First Six Product Milestones

### M1 --- Repository Analyzer

**Status:** NOT STARTED

Success: `GitHub repo → stack + commands + repository map`

### M2 --- Secure Sandbox

**Status:** NOT STARTED

Success: `repo + commit → isolated runnable workspace`

### M3 --- Agent Patch

**Status:** NOT STARTED

Success: `repo + task → focused git diff`

### M4 --- Verified Patch

**Status:** NOT STARTED

Success: `diff → lint/test/build/review evidence`

### M5 --- Automatic Pull Request

**Status:** NOT STARTED

Success: `verified diff → GitHub PR`

### M6 --- Guardian Repair

**Status:** NOT STARTED

Success: `CI/deployment/runtime incident → verified repair PR`

## Current Architecture Decisions

  Decision                 Choice
  ------------------------ ---------------------------------------
  Frontend                 Next.js + TypeScript
  API                      FastAPI + Python
  Database                 PostgreSQL
  Workflow                 Temporal
  Agent foundation         OpenHands SDK / Agent Server
  Sandbox                  Docker initially
  Production sandbox       Kubernetes / stronger isolation later
  Source control           GitHub App
  Cache                    Redis
  Object storage           S3-compatible
  Observability            OpenTelemetry
  Merge policy             Human approval by default
  Deployment integration   Vercel first, provider-neutral core

## Open Decisions

-   [ ] Authentication provider for product users.
-   [ ] Exact deployment target for control plane.
-   [ ] Exact object-storage provider.
-   [ ] Initial LLM provider/model set.
-   [ ] Billing implementation/timing.
-   [ ] Kubernetes provider for production.
-   [ ] Stronger sandbox runtime requirement for beta.
-   [ ] Initial notification channel.
-   [ ] Open-source licensing strategy for this project.

## Known Risks

-   arbitrary repository code execution;
-   prompt injection from repository/issues/logs;
-   model cost runaway;
-   agent loops;
-   false-positive incidents;
-   cross-tenant leakage;
-   GitHub permission overreach;
-   unsafe automatic repair;
-   dependency/license drift in reused agent components.

## Blockers

Phase 0 cannot satisfy its hosted-CI exit criterion until this local
repository has a GitHub destination and the workflow runs there. This
does not affect local verification. Multi-agent orchestration remains
prohibited until the single-agent PR loop is proven.

## Milestone History

### 2026-08-24 — Phase 0 local foundation

Status:
PARTIAL — all local exit evidence is green; hosted GitHub Actions has
not run because no remote is configured.

Implemented:
- monorepo foundation with Next.js web, FastAPI API, and Temporal worker;
- PostgreSQL, Redis, Temporal, Temporal UI, API, worker, and web Compose stack;
- versioned health contracts and dependency-aware readiness checks;
- baseline Alembic migration and rollback path;
- CI jobs for JavaScript/Python quality gates, migrations, dependency and
  secret scanning, and container builds;
- eight architecture decision records, environment schema, pre-commit hooks,
  and repository AI workflow instructions;
- non-root application containers with no host Docker socket exposure.

Validated:
- `pnpm check`: lint, formatting, strict typing, 8 tests, compile, and
  production web build passed;
- `pnpm security`: no known JavaScript vulnerabilities;
- `pip-audit apps/api` and `pip-audit apps/worker`: no known vulnerabilities;
- `alembic downgrade base` then `alembic upgrade head`: passed on live PostgreSQL;
- live readiness: PostgreSQL, Redis, and Temporal all reported available;
- live Temporal workflow: worker executed `ConnectivityWorkflow` successfully;
- container builds: API, worker, and web passed; the rebuilt API remained healthy;
- web smoke check: HTTP 200 and expected application content.

Decisions:
- upgraded FastAPI to 0.141.1 and pinned patched Starlette 1.3.1 after the
  dependency audit detected advisories in Starlette 0.47.3;
- pinned PostCSS 8.5.23 after the JavaScript audit identified
  GHSA-fxqj-rqcc-2cmp in the previous transitive version;
- kept the sandbox manager intentionally deferred until Phase 4;
- kept human merge as the default and did not introduce multi-agent behavior.

Known issues:
- hosted CI has not run because the repository has no GitHub remote;
- no unresolved local security findings are known at this milestone.

Next:
- create or select the GitHub repository, push the foundation, and require a
  green hosted CI run before marking Phase 0 complete;
- then implement the Phase 1 persisted project/task vertical slice.

## Update Template

Copy this section when recording a milestone:

``` text
### YYYY-MM-DD — <Milestone>

Status:
COMPLETED / PARTIAL / BLOCKED

Implemented:
- ...

Validated:
- command:
- result:

Decisions:
- ...

Known issues:
- ...

Next:
- ...
```

## Completion Rule

Never mark a phase `DONE` solely because code exists. It must satisfy
the phase exit criteria and have validation evidence.
