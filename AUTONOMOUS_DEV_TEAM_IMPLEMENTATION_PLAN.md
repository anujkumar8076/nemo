# Autonomous Dev Team — Senior Engineering Implementation Plan

**Document type:** Delivery / Engineering Plan
**Approach:** Incremental, production-oriented, testable at every phase
**Rule:** Do not build the full multi-agent system until the single-agent execution loop is reliable.

---

## 1. Delivery Strategy

Build the platform in vertical slices.

Bad approach:

```text
Build 12 agents
Build dashboard
Build monitoring
Build deployment integrations
Then try to connect everything
```

Preferred approach:

```text
Repository
   ↓
Task
   ↓
Sandbox
   ↓
Agent
   ↓
Tests
   ↓
PR
```

Make that reliable first.

Then:

```text
Production signal
   ↓
Incident
   ↓
Same repair engine
   ↓
PR
```

Then introduce specialist agents and advanced automation.

---

## 2. Engineering Phases

```text
Phase 0   Foundation / ADRs
Phase 1   Platform Skeleton
Phase 2   GitHub Integration
Phase 3   Repository Intelligence
Phase 4   Sandbox Runtime
Phase 5   Single-Agent Build Loop
Phase 6   Validation + PR Pipeline
Phase 7   Dashboard / Human Control
Phase 8   Guardian Mode
Phase 9   Automated Incident Repair
Phase 10  Multi-Agent Routing
Phase 11  Security Hardening
Phase 12  Observability / Cost / Reliability
Phase 13  Production Scale
```

Each phase has a hard exit criterion.

---

# PHASE 0 — Architecture & Repository Foundation

## Goal

Create the engineering baseline before application features.

## Tasks

- create monorepo;
- define coding standards;
- define branch strategy;
- add AGENTS.md;
- create ADR directory;
- define API/event versioning;
- establish formatting/linting;
- configure pre-commit hooks;
- configure CI;
- add secret scanning;
- create local Docker Compose.

## Suggested layout

```text
apps/
  web/
  api/
  worker/

packages/
  contracts/
  github/
  agent-core/
  integrations/
  ui/

services/
  sandbox-manager/

infra/
  docker/
  kubernetes/
  terraform/

docs/
```

## ADRs to write

```text
ADR-001 FastAPI control plane
ADR-002 Temporal workflows
ADR-003 PostgreSQL source of truth
ADR-004 GitHub App authentication
ADR-005 OpenHands execution foundation
ADR-006 sandbox isolation model
ADR-007 human merge by default
ADR-008 provider adapter interfaces
```

## CI baseline

For every PR:

- frontend lint;
- frontend typecheck;
- frontend tests;
- backend lint;
- backend typecheck;
- backend tests;
- migration validation;
- secret scan;
- dependency scan;
- container build.

## Exit criteria

```text
✓ repo boots locally with one command
✓ CI is green
✓ database migrations work
✓ web/API/worker can communicate
✓ environment schema documented
```

---

# PHASE 1 — Platform Skeleton

## Goal

Create the core product entities and API.

## Backend

Implement:

```text
User
Organization
Membership
Project
Repository
ProjectRule
Task
AuditEvent
```

Endpoints:

```text
GET    /health
POST   /projects
GET    /projects/{id}
PATCH  /projects/{id}

POST   /projects/{id}/tasks
GET    /tasks/{id}
POST   /tasks/{id}/cancel

GET    /projects/{id}/activity
```

## Frontend

Build:

- sign-in shell;
- dashboard;
- projects;
- project detail;
- create task;
- task detail;
- settings placeholder.

## Infrastructure

- Postgres;
- Redis;
- Temporal;
- API;
- worker;
- web.

## Testing

- API integration test against real Postgres;
- frontend component tests;
- e2e smoke test.

## Exit criteria

User can create a project and a task and see persisted state.

---

# PHASE 2 — GitHub App Integration

## Goal

Securely connect repositories and react to GitHub events.

## Tasks

### GitHub App

Create app with minimal permissions.

Implement:

- installation callback;
- installation storage;
- installation repository sync;
- short-lived installation token service;
- repo list;
- repo metadata.

### Webhook receiver

Endpoint:

```text
POST /webhooks/github
```

Must:

1. verify signature;
2. record delivery ID;
3. reject duplicates;
4. normalize event;
5. persist;
6. start workflow;
7. return quickly.

### Supported initial events

```text
installation
installation_repositories
issues
issue_comment
pull_request
check_run
check_suite
workflow_run
push
```

### Repository actions

Create services for:

```text
clone_repository()
create_branch()
commit_changes()
push_branch()
create_pull_request()
comment_on_issue()
create_check_run()
update_check_run()
```

Do not let agents directly hold GitHub App private keys.

## Tests

- signed webhook fixtures;
- invalid signature;
- replayed delivery;
- removed repository;
- revoked installation;
- rate-limit handling.

## Exit criteria

```text
✓ user installs GitHub App
✓ repo appears in dashboard
✓ issue event appears in activity
✓ backend can create a test branch/PR in sandbox test repo
```

---

# PHASE 3 — Repository Intelligence

## Goal

Build a deterministic understanding of a repository before adding autonomous code changes.

## Implement Repository Scanner

Detect:

- language;
- framework;
- package manager;
- monorepo;
- source directories;
- package manifests;
- tests;
- build command;
- lint command;
- CI workflows;
- Dockerfiles;
- deployment config;
- DB/ORM;
- AGENTS.md;
- README architecture hints.

Store a `RepositorySnapshot`.

## Repository Map

Produce:

```json
{
  "languages": ["typescript"],
  "frameworks": ["nextjs"],
  "package_manager": "pnpm",
  "commands": {
    "install": "pnpm install --frozen-lockfile",
    "test": "pnpm test",
    "lint": "pnpm lint",
    "build": "pnpm build"
  }
}
```

## Add project-rule import

Read:

```text
AGENTS.md
.autodev/project.yml
```

Project configuration must never override platform security policy.

## Optional semantic index

Add only after deterministic scanning works.

Potential stack:

- tree-sitter;
- ripgrep;
- embeddings;
- pgvector.

## Exit criteria

Given an unknown repo, the platform produces a reliable executable project profile.

---

# PHASE 4 — Sandbox Runtime

## Goal

Execute arbitrary repository code without exposing the host/control plane.

## Build Sandbox Manager

Interface:

```python
create_sandbox(task_id, repo, commit)
exec(sandbox_id, command)
read_file(sandbox_id, path)
write_file(sandbox_id, path, content)
get_diff(sandbox_id)
destroy_sandbox(sandbox_id)
```

## MVP runtime

Docker.

Mandatory controls:

- non-root;
- CPU limit;
- memory limit;
- pids limit;
- timeout;
- disk quota where possible;
- isolated filesystem;
- no Docker socket;
- no host home;
- ephemeral workspace;
- network disabled by default or tightly controlled.

## Agent server

Integrate OpenHands Agent Server/SDK inside or against the sandbox.

Pin known-compatible versions.

## Lifecycle

```text
REQUESTED
 ↓
PROVISIONING
 ↓
READY
 ↓
RUNNING
 ↓
STOPPING
 ↓
DESTROYED
```

Other terminal states:

```text
FAILED
TIMED_OUT
CANCELLED
```

## Cleanup worker

Destroy orphaned sandboxes.

## Tests

Adversarial:

- attempt `/etc` modifications;
- attempt host filesystem access;
- fork bomb;
- memory exhaustion;
- endless process;
- outbound network attempt;
- secret environment enumeration.

## Exit criteria

Repository commands can run in a disposable environment and cannot directly access host secrets/files.

---

# PHASE 5 — Single-Agent Build Loop

## Goal

Achieve the first real autonomous engineering workflow.

Do **not** add specialist agents yet.

## Workflow

```text
Task
 ↓
Repository snapshot
 ↓
Generate plan
 ↓
Approval if required
 ↓
Sandbox
 ↓
Coding Agent
 ↓
Diff
 ↓
Validation
```

## Agent tools

Provide:

- file read/write;
- shell;
- repository search;
- Git diff;
- test execution;
- browser only when required.

## System policies

Agent cannot:

- push to GitHub directly;
- merge;
- obtain control-plane secrets;
- disable platform validation;
- edit protected paths without policy authorization.

## Agent result contract

```json
{
  "status": "completed",
  "summary": "...",
  "files_changed": [],
  "commands_run": [],
  "tests": [],
  "known_risks": [],
  "needs_human": false
}
```

## Bounded execution

Limits:

- wall clock;
- token cost;
- tool steps;
- repair iterations.

## Exit criteria

On a benchmark set of small real repositories:

```text
task → code → passing expected tests
```

works reliably enough to continue.

---

# PHASE 6 — Validation & Pull Request Pipeline

## Goal

Turn successful sandbox changes into trusted PRs.

## Validation Pipeline

```text
Diff
 ↓
format
 ↓
lint
 ↓
typecheck
 ↓
targeted tests
 ↓
full required tests
 ↓
build
 ↓
review
 ↓
policy checks
```

## Review Agent

Independent prompt/context from coder.

Outputs findings:

```json
{
  "decision": "APPROVED",
  "findings": [],
  "require_changes": false
}
```

## Repair loop

```text
Review/Test failure
      ↓
Coder receives structured finding
      ↓
attempt repair
      ↓
validation again
```

Set maximum retry count.

## PR creation

Control plane:

1. receives final diff;
2. creates branch;
3. commits;
4. pushes;
5. creates PR;
6. posts validation check.

Suggested branch:

```text
autodev/task-<id>-<slug>
```

## PR body

Include:

- task;
- plan;
- implementation summary;
- risk;
- test evidence;
- review result;
- files changed;
- limitations;
- rollback notes.

## Exit criteria

A dashboard-created task can end as a high-quality GitHub PR with no manual Git commands.

---

# PHASE 7 — Dashboard & Human Control

## Goal

Make autonomous execution understandable and controllable.

## Pages

```text
/dashboard

/projects
/projects/:id
/projects/:id/tasks
/projects/:id/incidents
/projects/:id/settings

/tasks/:id
/incidents/:id
/integrations
/usage
/audit
```

## Task detail

Display:

- status;
- plan;
- agent step;
- changed files;
- command timeline;
- tests;
- findings;
- cost;
- PR.

## Controls

- approve plan;
- reject plan;
- edit instructions;
- cancel;
- retry;
- stop sandbox;
- open PR.

## Live updates

Use:

- SSE initially, or
- WebSocket if bidirectional live interaction becomes necessary.

## Exit criteria

A non-expert user can understand what the system is doing without reading raw agent transcripts.

---

# PHASE 8 — Guardian Mode Foundations

## Goal

Detect real operational failures.

## Incident model

Implement:

```text
Incident
IncidentEvent
IncidentEvidence
IncidentFingerprint
```

## Generic incident webhook

```text
POST /webhooks/incidents/{integration_id}
```

Supports external systems immediately.

## Built-in health checker

Config:

```yaml
url: https://app.example.com/api/health
interval: 60
timeout: 10
failure_threshold: 3
recovery_threshold: 2
```

Checks:

- HTTP status;
- latency;
- optional body assertion.

Avoid one-failure incidents.

## GitHub CI signals

Consume:

- check failures;
- workflow failures.

Link:

```text
check → commit SHA → repository → project
```

## Vercel adapter

Initial capabilities:

- deployment state event;
- deployment metadata;
- map deployment to Git commit;
- collect references to available logs/evidence.

Where runtime log forwarding is available, normalize it through the provider adapter.

## Incident correlation

Fingerprint using:

```text
project
environment
error type
stack frame
route
deployment
commit
```

## Exit criteria

The platform can create one meaningful incident from repeated/related production signals without flooding the user.

---

# PHASE 9 — Automatic Incident Repair

## Goal

Turn an incident into an autonomous repair PR.

## Workflow

```text
Incident
 ↓
Evidence Collector
 ↓
Triage
 ↓
Create sandbox at failing SHA
 ↓
Reproduce
 ↓
Root cause
 ↓
Repair plan
 ↓
Implementation
 ↓
Regression test
 ↓
Validation
 ↓
PR
```

## Evidence collector

Collect:

- deployment;
- commit SHA;
- recent commits;
- stack trace;
- endpoint;
- logs;
- CI results;
- health results;
- timestamps.

## Reproduction requirement

The preferred repair has:

```text
failing reproduction before fix
+
passing reproduction after fix
```

If reproduction is impossible, lower confidence and strengthen human review requirements.

## Incident PR

PR links back to incident.

## Exit criteria

Controlled fault injection in a test deployment automatically yields a relevant repair PR.

---

# PHASE 10 — Deployment Verification

## Goal

Close the production feedback loop.

## After merge

Watch:

```text
PR merged
 ↓
new deployment
 ↓
deployment ready
 ↓
run verification
```

## Verification

- health endpoint;
- critical synthetic flow;
- original incident fingerprint absent;
- error rate below threshold;
- observation window.

## Result

```text
HEALTHY
 → close incident

FAILED
 → reopen incident
 → capture new evidence
 → no blind infinite repair loop
```

## Exit criteria

A merged test incident repair automatically transitions to RESOLVED only after production verification succeeds.

---

# PHASE 11 — Risk Engine & Multi-Agent Routing

## Goal

Add specialization only where it improves outcomes.

## Build deterministic risk rules first

Signals:

- path changed;
- task language;
- repository technology;
- auth;
- payment;
- DB;
- infra;
- secrets;
- migration;
- dependency major version;
- blast radius.

LLM classification augments rules; it does not replace hard policy.

## Agent workflows

### Low

```text
Developer
 ↓
Test
 ↓
Review
```

### Medium

```text
Planner
 ↓
Developer / Specialist
 ↓
Test
 ↓
Review
```

### High

```text
Architect
 ↓
Planner
 ↓
Specialist Agents
 ↓
Test
 ↓
Security
 ↓
Review
```

## Parallel tasks

Only run tasks concurrently when their dependency graph permits it.

Use independent worktrees/sandboxes.

## Integration step

Before final validation:

- merge specialist changes;
- resolve conflicts;
- run combined test suite.

## Exit criteria

Multi-agent mode measurably improves complex-task success without unacceptable cost inflation.

---

# PHASE 12 — Security Agent & Policy Engine

## Goal

Make high-risk changes defensible.

## Policy layer

Implement platform policy separately from LLMs.

Possible policy examples:

```text
DENY agents from modifying .github/workflows without approval
DENY production secret access
REQUIRE security review for auth/*
REQUIRE plan approval for migrations/*
REQUIRE human merge for risk >= HIGH
```

Evaluate before tool execution when possible.

## Security checks

Integrate deterministic scanners:

- Semgrep;
- Trivy;
- dependency audit commands;
- secret scanning.

AI Security Agent interprets and contextualizes findings.

Do not rely only on an LLM for vulnerability detection.

## Exit criteria

High-risk test cases are blocked or escalated according to policy.

---

# PHASE 13 — Model Router & Cost Control

## Goal

Avoid hard dependency on one LLM and prevent runaway spend.

## Provider interface

```python
class ModelProvider:
    async def generate(...)
    async def tool_call(...)
    async def health(...)
```

## Router

Inputs:

- risk;
- task type;
- context requirement;
- cost budget;
- provider availability.

## Budgets

Support:

```text
task max cost
daily project budget
monthly organization budget
max repair attempts
max tokens
```

## Usage ledger

Store:

```text
provider
model
input_tokens
output_tokens
cached_tokens
estimated_cost
agent
task
timestamp
```

## Exit criteria

A provider outage can fail over without losing the task workflow, and a task cannot exceed configured spend.

---

# PHASE 14 — Observability & Operations

## Goal

Operate the product itself reliably.

## OpenTelemetry

Instrument:

- API;
- webhook processing;
- workflows;
- activities;
- sandbox lifecycle;
- LLM calls;
- GitHub API;
- deployment adapters.

## Metrics

```text
tasks_started_total
tasks_completed_total
tasks_failed_total
agent_attempts_total
sandbox_start_seconds
incident_detect_seconds
incident_to_pr_seconds
pr_accepted_total
repair_verified_total
llm_cost_total
```

## Dashboards

- platform health;
- agent reliability;
- sandbox health;
- integration failures;
- task conversion funnel;
- Guardian performance;
- cost.

## Alerts

- workflow backlog;
- sandbox provisioning failure;
- webhook error rate;
- GitHub token failures;
- DB saturation;
- budget anomalies.

## Exit criteria

Operators can identify why a task failed without SSHing into random containers.

---

# PHASE 15 — Production Hardening

## Goal

Move from useful MVP to trustworthy service.

## Sandbox

Move execution workers to:

- Kubernetes;
- pod quotas;
- network policies;
- stronger runtime isolation if required.

## Security

- KMS/Vault;
- key rotation;
- RBAC;
- tenant isolation tests;
- penetration testing;
- dependency/SBOM;
- image signing.

## Reliability

- Postgres HA/backups;
- Temporal production topology;
- object-store lifecycle;
- dead-letter/replay tools;
- disaster recovery runbook.

## Deployment

- staged rollout;
- feature flags;
- canary workers;
- backward-compatible event schemas.

## Exit criteria

Production readiness review passes.

---

# 3. Recommended First 6 Engineering Milestones

To avoid an overlong build before seeing value, treat these as the first concrete milestones.

## M1 — Repo Analyzer

Input:

```text
GitHub repo
```

Output:

```text
stack + commands + project map
```

## M2 — Secure Sandbox

Input:

```text
repo + commit
```

Output:

```text
isolated runnable workspace
```

## M3 — Agent Patch

Input:

```text
repo + task
```

Output:

```text
working git diff
```

## M4 — Verified Patch

Input:

```text
diff
```

Output:

```text
lint/test/build/review result
```

## M5 — Automatic PR

Input:

```text
verified diff
```

Output:

```text
GitHub pull request
```

## M6 — Guardian Repair

Input:

```text
production/CI incident
```

Output:

```text
verified repair PR
```

If M1–M5 are unreliable, do not expand to the full agent team.

---

# 4. API Contracts — Initial Set

Suggested external API:

```text
POST /v1/projects
GET  /v1/projects/{project_id}

POST /v1/projects/{project_id}/tasks
GET  /v1/tasks/{task_id}
POST /v1/tasks/{task_id}/approve
POST /v1/tasks/{task_id}/cancel
POST /v1/tasks/{task_id}/retry

GET  /v1/projects/{project_id}/incidents
GET  /v1/incidents/{incident_id}

POST /v1/integrations
GET  /v1/integrations

POST /webhooks/github
POST /webhooks/vercel
POST /webhooks/incidents/{integration_id}
```

Avoid exposing internal agent APIs to browsers.

---

# 5. Workflow State Machines

## Task

```text
CREATED
 ↓
ANALYZING
 ↓
PLANNING
 ↓
WAITING_APPROVAL
 ↓
EXECUTING
 ↓
VALIDATING
 ↓
REVIEWING
 ↓
CREATING_PR
 ↓
COMPLETED
```

Terminal alternatives:

```text
FAILED
CANCELLED
BLOCKED
BUDGET_EXCEEDED
```

## Incident

```text
OPEN
 ↓
TRIAGED
 ↓
INVESTIGATING
 ↓
REPAIRING
 ↓
PR_READY
 ↓
WAITING_MERGE
 ↓
VERIFYING
 ↓
RESOLVED
```

Alternative:

```text
SUPPRESSED
NEEDS_HUMAN
REOPENED
```

---

# 6. Testing Strategy

## Unit

Test:

- parsers;
- risk rules;
- adapters;
- event normalization;
- policy;
- cost calculations.

## Integration

Real ephemeral:

- Postgres;
- Temporal;
- Redis;
- sandbox manager.

## GitHub contract tests

Use a dedicated test repository/GitHub App installation.

## Agent evaluation suite

Create fixture repositories containing known bugs:

```text
fixture-nextjs-auth
fixture-fastapi-api
fixture-react-ui
fixture-node-runtime
fixture-db-migration
```

Measure:

- solved;
- failed;
- unsafe;
- unnecessary changes;
- cost;
- attempts.

## Guardian chaos suite

Inject:

- broken env assumption;
- dependency mismatch;
- API 500;
- build failure;
- failed health endpoint;
- syntax regression;
- DB connection failure.

Confirm correct detection and behavior.

---

# 7. Security Test Plan

Before production:

- webhook forgery;
- webhook replay;
- GitHub token theft scenario;
- malicious repository;
- prompt injection in README;
- prompt injection in issue;
- symlink attacks;
- path traversal;
- sandbox escape attempts;
- network exfiltration;
- secrets in logs;
- fork bomb;
- resource exhaustion;
- cross-tenant IDOR;
- SSRF through agent tool;
- package install script abuse.

---

# 8. Developer Experience

## Local startup

Target:

```bash
make dev
```

or equivalent.

Starts:

- web;
- API;
- Temporal;
- Postgres;
- Redis;
- worker.

Sandbox integration may require a separate runtime service.

## Seed command

Provide:

```text
make seed
```

with:

- dev user;
- project;
- sample task;
- fake incident.

## Test commands

Provide stable root commands:

```text
make lint
make test
make test-integration
make e2e
make security
```

---

# 9. Configuration / Environment Design

Use typed environment validation.

Categories:

```text
DATABASE_*
TEMPORAL_*
REDIS_*
GITHUB_APP_*
ENCRYPTION_*
OBJECT_STORAGE_*
MODEL_PROVIDER_*
OTEL_*
```

Never expose server secrets through `NEXT_PUBLIC_*`.

Keep local `.env.example` values fake.

---

# 10. Backlog Prioritization

Use:

### P0

Blocks safe execution:

- auth;
- tenant isolation;
- GitHub signature validation;
- sandbox isolation;
- cancellation;
- durable workflow;
- PR correctness.

### P1

Core product:

- repo scan;
- task plan;
- agent run;
- validation;
- activity UI;
- Guardian incidents.

### P2

Scale/quality:

- multi-agent;
- extra integrations;
- model routing;
- advanced analytics.

### P3

Polish:

- customization;
- marketplace;
- advanced team features.

---

# 11. What Not to Build First

Do not begin with:

- ten different agent personas;
- Kubernetes before Docker prototype;
- vector database before repo scanning works;
- complicated billing;
- mobile app;
- auto-merge;
- direct autonomous production modifications;
- custom LLM training;
- custom workflow engine;
- custom container runtime;
- full IDE.

These create complexity without proving the core loop.

---

# 12. First Production Demo

The first convincing demo should be deliberately end-to-end.

## Demo A — Build Mode

1. Connect a small GitHub application.
2. Submit: “Add rate limiting to this API.”
3. System analyzes repository.
4. System creates plan.
5. User approves.
6. Sandbox implements.
7. Tests are added.
8. Review passes.
9. PR appears automatically.

## Demo B — Guardian Mode

1. Deploy a known-good test app.
2. Push an intentionally faulty commit.
3. Deployment becomes unhealthy or emits a controlled incident.
4. Guardian detects it.
5. Incident appears.
6. Agent reproduces the bug.
7. Agent fixes it.
8. Regression test passes.
9. PR appears.
10. Human merges.
11. New deployment goes live.
12. Guardian verifies recovery and closes incident.

If these two demos work reliably, the core product thesis is proven.

---

# 13. Engineering Quality Gates Before Beta

Required:

```text
✓ no sandbox has host Docker socket
✓ webhook signatures verified
✓ GitHub credentials short-lived
✓ encryption at rest for stored secrets
✓ task cancellation works
✓ orphan cleanup works
✓ workflow restart/resume tested
✓ tenant isolation tested
✓ budgets enforced
✓ logs redact credentials
✓ test fixture success rate measured
✓ Guardian deduplication tested
✓ agent cannot auto-merge by default
✓ audit events persisted
✓ incident repair PR includes evidence
```

---

# 14. Suggested Team Ownership

If multiple engineers work on the project:

### Platform Engineer

- Temporal;
- database;
- events;
- GitHub App;
- integrations.

### Agent Engineer

- OpenHands integration;
- prompts;
- tools;
- routing;
- evaluations.

### Runtime/Security Engineer

- sandbox;
- isolation;
- resource policy;
- secrets;
- Kubernetes.

### Frontend/Product Engineer

- dashboard;
- task UX;
- incident UX;
- project settings.

One developer can initially cover all roles, but ownership boundaries should still exist in the codebase.

---

# 15. Implementation Order Summary

Build exactly in this order:

```text
1. Repo + CI foundation
2. Web/API/DB skeleton
3. GitHub App
4. Repository scanner
5. Sandbox manager
6. Single coding agent
7. Test/build validation
8. Review loop
9. Automatic PR
10. Dashboard polish
11. Incident model
12. Health/CI/Vercel signals
13. Incident repair workflow
14. Post-deploy verification
15. Risk engine
16. Architect/planner/specialists
17. Security agent + deterministic scanners
18. Model router + budgets
19. Hardening / Kubernetes
20. Beta
```

This sequence minimizes rework because every later feature builds on the same execution engine.

---

# 16. Final Engineering Principle

The platform must optimize for:

> **verified autonomous outcomes, not autonomous activity.**

An agent producing a lot of code is not success.

Success is:

```text
correct scope
+ minimal safe change
+ reproducible evidence
+ passing tests
+ independent review
+ auditable PR
+ healthy production after deployment
```

That principle should guide every implementation decision.

---

**End of Implementation Plan**
