# Progress Tracker

> This is the canonical high-level project progress file. Update it
> after every meaningful implementation milestone.

## Project

**Autonomous Dev Team**

## Current Stage

**Stage:** Phase 2 / GitHub App integration\
**Overall status:** Phases 0 and 1 complete; Phase 2 is beginning.

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
  0       Architecture & repository foundation   COMPLETE
  1       Platform skeleton                      COMPLETE
  2       GitHub App integration                 IN PROGRESS
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
-   [x] Run the workflow successfully on hosted GitHub Actions.

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

None. Multi-agent orchestration remains prohibited until the
single-agent PR loop is proven.

## Milestone History

### 2026-08-24 — Phase 0 local foundation

Status:
COMPLETED

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
- hosted CI run `32725249850`: all 10 matrix jobs passed, including
  JavaScript/Python checks, dependency audits, migration rollback/upgrade,
  three container builds, and secret scanning.

Decisions:
- upgraded FastAPI to 0.141.1 and pinned patched Starlette 1.3.1 after the
  dependency audit detected advisories in Starlette 0.47.3;
- pinned PostCSS 8.5.23 after the JavaScript audit identified
  GHSA-fxqj-rqcc-2cmp in the previous transitive version;
- upgraded GitHub Actions to supported Node 24-era majors after the first
  hosted run exposed the retired Gitleaks v2 runtime;
- kept the sandbox manager intentionally deferred until Phase 4;
- kept human merge as the default and did not introduce multi-agent behavior.

Known issues:
- no unresolved Phase 0 findings are known at this milestone.

Next:
- implement the Phase 1 persisted project/task vertical slice.

### 2026-08-24 — Phase 1 persisted platform slice

Status:
COMPLETED

Implemented:
- tenant-scoped User, Organization, Membership, Project, Repository,
  ProjectRule, Task, and AuditEvent persistence models;
- reversible platform-skeleton migration with tenant-safe composite foreign
  keys, uniqueness constraints, indexes, and optimistic project versions;
- development-only bootstrap authentication that fails closed in production;
- versioned project, task, cancellation, pagination, and activity APIs with
  consistent error envelopes, correlation IDs, idempotency, and audit events;
- a responsive application shell, dashboard, projects, project detail, task
  creation, task detail, cancellation control, and settings placeholder;
- shared runtime-validated TypeScript contracts and real PostgreSQL API
  integration coverage in CI.

Validated:
- Python Ruff and strict MyPy checks passed;
- Python unit suite passed with the PostgreSQL integration test skipped unless
  explicitly enabled;
- live container-backed API flow passed: project create/idempotent retry, task
  create, task cancel, and activity retrieval;
- migration `0002_platform_skeleton` downgraded to `0001_foundation` and upgraded
  again successfully on live PostgreSQL;
- production Next.js build passed;
- browser smoke flow passed from empty state through project creation, task
  creation, cancellation, audit visibility, and mobile overflow validation.
- hosted CI run `32729601466`: all 11 jobs passed, including the real
  PostgreSQL tenant-isolation API integration job, migration rollback/upgrade,
  three container builds, dependency audits, and secret scanning.

Decisions:
- bootstrap bearer authentication is strictly local/development-only; selecting
  the production identity provider remains an explicit product decision;
- task execution remains disabled, preserving the documented dependency on the
  later repository-intelligence and sandbox phases;
- client request IDs are stable across form submissions so create operations
  retain idempotency under retries.

Known issues:
- the dashboard readiness request occasionally exceeded the original 2.5-second
  client timeout, which was raised to 5 seconds while preserving a bounded wait.

Next:
- begin Phase 2 GitHub App integration without starting repository code
  execution or multi-agent behavior.

### 2026-08-24 — Phase 2 webhook trust boundary

Status:
PARTIAL

Implemented:
- disabled-by-default GitHub webhook configuration with validated secret and
  bounded payload size;
- raw-body HMAC-SHA256 signature verification before JSON parsing;
- supported-event allowlist including installation, repository, issue, pull
  request, check, workflow, push, and setup ping events;
- durable webhook delivery records with payload digests, installation and
  repository identifiers, processing status, and database-unique delivery IDs;
- replay-safe duplicate handling and a reversible webhook-ingress migration.

Validated:
- unit coverage for raw-body signature integrity and invalid signatures;
- integration coverage prepared for accepted, duplicate, and invalid signed
  deliveries against PostgreSQL;
- Ruff, strict MyPy, and the local non-integration Python suite pass.
- migration `0003_github_webhook_ingress` upgraded, downgraded, and upgraded
  successfully on live PostgreSQL;
- a locally signed `issues` delivery returned `accepted`, and an exact replay
  returned `duplicate`; integration was then restored to disabled-by-default.

Decisions:
- installation setup callbacks will not trust `installation_id` alone; tenant
  claiming must combine one-time state with verified GitHub identity or signed
  installation state;
- delivery ingestion persists `pending` work quickly; durable workflow dispatch
  and normalization are the next slice rather than request-thread work;
- GitHub integration remains disabled until a unique webhook secret and real
  GitHub App are configured.

Known issues:
- the PostgreSQL webhook integration test still requires hosted validation;
- no GitHub App installation, repository synchronization, token service, or
  remote write action exists yet.

Next:
- validate migration rollback/upgrade and signed delivery integration in CI;
- implement installation identity, repository synchronization, and the
  short-lived token provider boundary before any branch or pull-request action.

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
