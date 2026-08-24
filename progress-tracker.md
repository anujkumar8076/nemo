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
- hosted CI run `32730726057`: all 11 jobs passed, including signed-delivery
  PostgreSQL integration, migration rollback/upgrade, security scans, and all
  production container builds.

Decisions:
- installation setup callbacks will not trust `installation_id` alone; tenant
  claiming must combine one-time state with verified GitHub identity or signed
  installation state;
- delivery ingestion persists `pending` work quickly; durable workflow dispatch
  and normalization are the next slice rather than request-thread work;
- GitHub integration remains disabled until a unique webhook secret and real
  GitHub App are configured.

Known issues:
- no GitHub App installation, repository synchronization, token service, or
  remote write action exists yet.

Next:
- validate migration rollback/upgrade and signed delivery integration in CI;
- implement installation identity, repository synchronization, and the
  short-lived token provider boundary before any branch or pull-request action.

### 2026-08-24 — Phase 2 GitHub App credential boundary

Status:
PARTIAL

Implemented:
- server-only RSA GitHub App JWT generation with bounded ten-minute claims;
- opaque, expiring installation-token responses without fixed-length token
  assumptions or persistent token storage;
- repository-scoped permission support for future write operations;
- paginated installation repository discovery using one ephemeral token;
- typed, sanitized GitHub provider and rate-limit failures with retry times;
- an independent remote-action feature gate requiring App ID and private key.

Validated:
- generated App JWT signature, issuer, and lifetime verified with an ephemeral
  RSA public key;
- installation-token request headers, API version, repository scoping, and
  secret-safe representation tested through a fake GitHub transport;
- multi-page repository discovery proves a single installation token is used;
- rate-limit tests prove retry metadata is retained while provider bodies are
  not exposed;
- local suite currently passes 12 non-integration tests with two PostgreSQL
  tests gated for CI.
- full monorepo lint, strict type checks, tests, Python compilation, and
  production Next.js build passed;
- Python dependency audit found no known vulnerabilities;
- production non-root API image built successfully with the pinned RSA
  cryptography stack.
- hosted CI run `32732316776`: all 11 jobs passed, including PostgreSQL
  integration, migration rollback/upgrade, dependency audits, secret scanning,
  and all production container builds.

Decisions:
- installation tokens remain in process memory only and are never database
  records, browser values, or agent inputs;
- remote repository mutations remain disabled until installation ownership and
  repository inventory are persisted and verified.

Known issues:
- a real GitHub App identity and public HTTPS webhook endpoint are still needed
  for contract testing against GitHub.

Next:
- add tenant-owned installation and repository inventory persistence and sync;
- validate installation and repository synchronization against PostgreSQL.

### 2026-08-24 — Phase 2 tenant-owned repository inventory

Status:
PARTIAL

Implemented:
- tenant-owned GitHub installation records with provider identity, permissions,
  repository selection, lifecycle status, and synchronization timestamps;
- a separate installation repository inventory with composite tenant foreign
  keys, provider metadata, availability, and removal history;
- atomic, row-locked repository reconciliation with idempotent upserts,
  removal marking, metadata refresh, and duplicate-input rejection;
- an isolated loopback-only ephemeral PostgreSQL Compose stack for repeatable
  local integration validation.

Validated:
- Ruff formatting/lint and strict mypy checks passed for source, migrations,
  and tests;
- migration `0004_github_install_inventory` upgraded from base, downgraded to
  base, and upgraded again against PostgreSQL 17.6;
- all three real PostgreSQL integration tests passed, including repository
  addition, metadata update, removal, cross-tenant installation denial, and
  refusal to synchronize a revoked installation;
- the local unit suite passes with database tests gated when PostgreSQL is not
  explicitly enabled.
- hosted CI run `32733678309`: all 11 jobs passed, including inventory
  integration, full migration rollback/upgrade, dependency audits, secret
  scanning, and all production container builds.

Decisions:
- installation inventory is not a project assignment; repositories can be
  visible to the App before a human connects one to a project;
- synchronization requires an already active, tenant-owned installation and
  cannot claim an installation from an untrusted callback or webhook payload;
- removed repositories retain non-secret metadata and removal time for audit
  continuity while becoming unavailable for future work.

Known issues:
- no authenticated installation-claim state flow exists yet;
- real GitHub contract validation still needs a GitHub App and public HTTPS
  callback/webhook endpoint.

Next:
- implement a signed, one-time installation state flow bound to the initiating
  tenant/user before any installation can be claimed;
- connect a selected repository to a project only after verified installation
  ownership exists;
- validate removal and revoked-installation behavior with real GitHub fixtures.

### 2026-08-24 — Phase 2 tenant inventory API and settings UI

Status:
PARTIAL

Implemented:
- authenticated, keyset-paginated read APIs for GitHub installations and
  repository inventory, with organization filtering on every query;
- removed repositories hidden by default with an explicit audit-oriented
  include flag, while cross-tenant installation filters return no records;
- runtime-validated TypeScript contracts for installation and repository page
  responses before provider data reaches UI components;
- a request-time-rendered settings integration view with live disconnected,
  available, partial-error, empty, suspended, revoked, and pagination states;
- API version `0.5.0` for the new read surface.

Validated:
- full monorepo formatting, lint, strict type checks, unit tests, Python
  compilation, and production Next.js build passed;
- API unit suite: 12 passed with four PostgreSQL tests explicitly gated;
- all four PostgreSQL integration tests passed, covering keyset pagination,
  removed-record defaults, invalid cursors, and cross-tenant filtering;
- contract suite: four passed; web component suite: four passed;
- high-severity JavaScript dependency audit found no known vulnerabilities;
- production non-root API and web images built successfully;
- browser validation at desktop and 390px mobile widths showed no console
  errors or page overflow and confirmed no unsafe installation action appears;
- runtime validation caught and fixed a build-time static-rendering defect; the
  production build now identifies `/settings` as dynamic server rendering.
- hosted CI run `32735932472`: all 11 jobs passed, including tenant inventory
  API integration, JavaScript contracts/UI, dependency and secret scans,
  migration validation, and all production container builds.

Decisions:
- inventory reads are available before installation claiming because they do
  not create ownership, mutate GitHub, or expose credentials;
- the UI does not render repository URLs as links until provider URL trust and
  navigation policy are explicitly enforced;
- installation and repository fetches fail independently so the page can show
  partial verified state without presenting false success.

Known issues:
- no safe installation claim can be exposed until GitHub user identity is
  verified in addition to one-time tenant state;
- a real GitHub App and public HTTPS callback/webhook endpoint are still needed
  for provider contract validation.

Next:
- implement the GitHub user-identity verification boundary and one-time claim
  state without persisting provider access tokens;
- connect a human-selected available repository to a project before enabling
  any branch or pull-request write.

### 2026-08-24 — Phase 2 one-time installation claim state

Status:
PARTIAL

Implemented:
- durable claim sessions bound to the initiating organization and user;
- 256-bit random state represented as a masked secret with only a SHA-256
  digest persisted;
- ten-minute default expiry with a hard thirty-minute lifetime ceiling;
- database-constrained stages for awaiting setup, awaiting GitHub user
  authorization, and completed identity proof;
- immutable setup installation identifiers, row-locked transitions,
  idempotent same-ID callbacks, replay rejection, and sanitized conflict
  handling;
- verified non-secret GitHub user identity evidence retained with the consumed
  claim while provider access tokens remain absent from storage.

Validated:
- Ruff formatting/lint and strict mypy checks passed;
- unit suite passes with integration tests gated when PostgreSQL is absent;
- migration `0005_github_install_claims` upgraded from base, downgraded to
  base, and upgraded again against PostgreSQL 17.6;
- all six PostgreSQL integration tests passed, including masked/digested state,
  tenant/user binding, immutable setup ID, expiry, successful verified claim,
  and replay rejection.
- hosted CI run `32737175683`: all 11 jobs passed, including migration
  validation, PostgreSQL integration, dependency and secret scans, and all
  production container builds.

Decisions:
- setup callbacks may record a candidate installation but can never create
  tenant ownership;
- only the future GitHub user authorization adapter may construct verified
  installation evidence consumed by the claim completion service;
- state remains a short-lived bearer secret, so callback failures use generic
  errors that do not reveal whether a digest exists.

Known issues:
- no configuration, OAuth code exchange, user-installation verification, or
  public setup/callback endpoint exists yet;
- a real GitHub App and public HTTPS callback are still required for provider
  contract validation.

Next:
- implement a server-only GitHub user authorization adapter that exchanges a
  one-time code, lists installations accessible to that user, produces typed
  proof, and discards the token;
- expose the install/setup/callback flow only after the adapter and redirect
  allowlist are fully tested;
- synchronize inventory immediately after a verified claim.

### 2026-08-24 — Phase 2 GitHub user authorization adapter

Status:
PARTIAL

Implemented:
- a disabled-by-default, server-only OAuth configuration boundary requiring
  GitHub App credentials, OAuth credentials, and credential-free HTTPS
  provider, callback, and installation URLs;
- one-time OAuth code exchange with secret-wrapped user tokens;
- authenticated GitHub user lookup and complete paginated enumeration of that
  user's accessible App installations;
- exact installation-ID verification that emits only typed, non-secret claim
  evidence and never returns or persists the user access token;
- sanitized provider and malformed-response errors that exclude OAuth payloads
  and credentials.

Validated:
- full monorepo lint, formatting, strict type checks, unit tests, compilation,
  and production Next.js build passed;
- API suite: 19 passed with six PostgreSQL tests explicitly gated;
- adapter tests cover form exchange, secret use, authenticated user identity,
  multi-page exact matching, inaccessible installation rejection, and OAuth
  error sanitization;
- high-severity JavaScript dependency audit found no known vulnerabilities;
- the production non-root API image built successfully and the Compose model
  validated with user authorization disabled by default.

Decisions:
- user access tokens exist only inside the adapter call and are represented as
  masked secrets; the claim service receives no credential;
- provider responses are parsed into strict minimum contracts while unknown
  fields are ignored for forward compatibility;
- public installation and callback routes remain unavailable in this slice, so
  unverified setup identifiers still cannot create tenant ownership.

Known issues:
- hosted CI has not yet validated the authorization adapter;
- no public begin/setup/OAuth callback flow or redirect allowlist is exposed;
- a real GitHub App and public HTTPS callback are required for end-to-end
  provider contract validation.

Next:
- implement and test the disabled-by-default begin/setup/OAuth callback flow
  with fixed trusted redirects and generic failure responses;
- complete the one-time claim only after adapter proof, then synchronize the
  installation inventory with an ephemeral App installation token;
- connect a human-selected available repository to a project before enabling
  branch or pull-request writes.

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
