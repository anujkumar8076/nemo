# Autonomous Dev Team — Project Overview & Product Specification

**Working title:** Autonomous Dev Team
**Category:** Autonomous Software Engineering / AI DevOps / Self-Healing Development Platform
**Status:** Product Definition v1

---

## 1. Project in One Sentence

Autonomous Dev Team is a platform that can **build, maintain, monitor, diagnose, repair, test, review, and prepare code changes as GitHub pull requests** using autonomous AI engineering agents while keeping humans in control of production merges.

---

## 2. Product Vision

Modern coding agents are good at responding to prompts, but software engineering does not stop after code is written.

Real software must be:

- maintained;
- monitored;
- debugged;
- tested;
- reviewed;
- secured;
- deployed;
- verified in production.

The product should behave less like an autocomplete assistant and more like an **always-available engineering team**.

The desired user experience is:

```text
"Build this"
    ↓
System understands the repo
    ↓
Plans
    ↓
Builds
    ↓
Tests
    ↓
Reviews
    ↓
Creates PR
```

and, after deployment:

```text
Production breaks
    ↓
System notices
    ↓
Investigates
    ↓
Fixes
    ↓
Tests
    ↓
Creates PR
    ↓
Human merges
    ↓
System confirms recovery
```

---

## 3. Core Problem

Developers lose time on:

- repetitive bug fixing;
- broken deployments;
- dependency issues;
- test failures;
- regressions;
- production incidents;
- routine maintenance;
- code review;
- monitoring multiple projects;
- translating issue descriptions into implementation plans.

Existing AI coding tools often require the user to continuously initiate and supervise each step.

This project closes the loop between:

```text
Request → Code → Test → PR → Deploy → Monitor → Incident → Repair
```

---

## 4. Target Users

### Primary

- solo developers;
- indie hackers;
- startup engineering teams;
- small SaaS teams;
- developers managing several repositories;
- teams already using GitHub and cloud deployment platforms.

### Secondary

- agencies;
- open-source maintainers;
- platform teams;
- internal developer productivity teams.

---

## 5. User Promise

The user should be able to say:

> “This repository is mine. These are the rules. Build features I request, watch the application after deployment, and when something breaks, investigate it and prepare a safe fix for me.”

The user should **not** need to manually choose the frontend agent, backend agent, database agent, or reviewer.

The platform routes work automatically.

---

## 6. Main Product Modes

# Build Mode

Used for planned engineering work.

Examples:

- “Add Google OAuth.”
- “Fix issue #82.”
- “Upgrade this app to the new SDK.”
- “Create a responsive dashboard.”
- “Add tests to the payments service.”
- “Refactor the notification module.”

Flow:

```text
Task
 ↓
Repo analysis
 ↓
Risk classification
 ↓
Plan
 ↓
Human plan approval when required
 ↓
Implementation
 ↓
Tests
 ↓
Security/review
 ↓
Pull Request
```

---

# Guardian Mode

Used for continuous application maintenance.

Signals can include:

- failed health checks;
- failed GitHub Actions;
- failed deployments;
- runtime 5xx spikes;
- exceptions;
- latency anomalies;
- monitoring alerts.

Flow:

```text
Production signal
 ↓
Incident correlation
 ↓
Triage
 ↓
Evidence collection
 ↓
Reproduction
 ↓
Repair
 ↓
Tests
 ↓
Review
 ↓
Pull Request
 ↓
Human merge
 ↓
Deployment verification
```

Guardian Mode is the product's key differentiator from a normal coding agent.

---

## 7. User Journey

### 7.1 Onboarding

```text
Sign up
   ↓
Install GitHub App
   ↓
Choose repositories
   ↓
Create project
   ↓
System scans repository
   ↓
Confirm detected stack
   ↓
Define project rules
   ↓
Optional: connect deployment/monitoring
```

Detected project metadata might show:

```text
Framework: Next.js
Language: TypeScript
Package manager: pnpm
Database: PostgreSQL
Tests: Vitest + Playwright
CI: GitHub Actions
Deployment: Vercel
```

---

### 7.2 Project Setup

A project contains:

- repository;
- default branch;
- deployment environments;
- build commands;
- test commands;
- lint commands;
- project rules;
- AI/model policy;
- cost budget;
- Guardian Mode policy;
- notification settings.

Example rules:

```text
- Reuse existing UI components.
- Never introduce `any`.
- Do not modify database migrations without approval.
- Run pnpm lint before opening a PR.
- Run Playwright for authentication changes.
- Do not change public API contracts without approval.
```

---

### 7.3 Creating a Task

User enters:

```text
Add Google OAuth login.
Use the existing users table.
Keep email/password login working.
Add tests.
```

The system returns:

```text
Risk: HIGH

Affected:
- authentication
- backend
- database
- frontend

Plan:
1. Inspect current auth flow.
2. Define provider identity mapping.
3. Implement OAuth callback.
4. Add login UI.
5. Add regression tests.
6. Run security review.
7. Run full CI.

[Approve] [Edit]
```

---

### 7.4 Execution View

The normal user sees a clean timeline:

```text
✓ Repository analyzed
✓ Plan approved
✓ Backend change complete
● Frontend implementation
○ Tests
○ Security
○ Review
○ Pull request
```

Advanced users may inspect:

- agent transcript;
- shell commands;
- files changed;
- test logs;
- token usage;
- cost;
- sandbox state.

---

### 7.5 Completion

```text
Task complete

PR #142 — Add Google OAuth

11 files changed
34/34 tests passed
Build passed
Security review passed
Code review passed

Risk: High
Human review required

[Open Pull Request]
```

---

## 8. GitHub-Native Workflow

Users should not be forced to use the dashboard.

A GitHub issue can trigger work:

```text
Issue #128
"Fix checkout validation"

label: ai-dev
        ↓
Platform starts
        ↓
Comments plan/progress
        ↓
Creates PR
        ↓
Links PR back to issue
```

Future command examples:

```text
@devteam plan this
@devteam fix this
@devteam retry
@devteam explain failure
```

---

## 9. Guardian Mode User Experience

A production incident might appear as:

```text
INC-1024
Production API Failure

Status: Repairing
Severity: High

Detected: 02:37
Service: api
Route: POST /api/auth/login
Error rate: 41%
Deployment: dpl_...
Commit: 41fac8a

Root cause confidence: 91%
```

Timeline:

```text
02:37 Incident detected
02:38 Matching errors correlated
02:38 Recent deployment identified
02:40 Failure reproduced
02:42 Root cause identified
02:47 Repair implemented
02:50 Regression tests passed
02:53 Security review passed
02:55 PR #219 created
```

User receives:

> “A production authentication regression was detected. A verified repair is ready in PR #219.”

---

## 10. Major Features

### Project Management

- organizations/workspaces;
- projects;
- repository connection;
- project rules;
- repository indexing;
- architecture profile;
- environments.

### Task Management

- manual task creation;
- task from GitHub issue;
- task history;
- status timeline;
- cancellation;
- retry;
- priority;
- budget;
- risk classification.

### Autonomous Engineering

- repository analysis;
- architecture planning;
- task decomposition;
- code modification;
- shell/tool execution;
- testing;
- debugging;
- iterative repair;
- code review;
- security review;
- PR generation.

### Multi-Agent Routing

- triage agent;
- project manager;
- architect;
- planner;
- developer;
- frontend;
- backend;
- database;
- tester;
- security;
- reviewer.

The system does not always invoke every agent.

### Guardian Mode

- health monitoring;
- CI failure detection;
- deployment failure detection;
- runtime incident intake;
- incident correlation;
- evidence collection;
- automated diagnosis;
- automated repair;
- PR generation;
- post-deploy verification.

### GitHub Integration

- GitHub App;
- issue triggers;
- PR creation;
- comments;
- checks;
- commit status;
- CI feedback;
- review feedback;
- branch management.

### Deployment Integrations

Initial:
- Vercel.

Provider contract enables:
- Render;
- Fly.io;
- Railway;
- AWS;
- others.

### Monitoring Integrations

Initial:
- built-in HTTP health checks;
- generic webhook.

Then:
- Vercel signals/log forwarding;
- Sentry;
- Datadog;
- OpenTelemetry;
- Grafana Alertmanager;
- CloudWatch.

### AI / Model Management

- multiple providers;
- per-project model policy;
- automatic model routing;
- local model support;
- cost limits;
- token accounting;
- fallback models.

### Auditability

- complete run history;
- every code change attributable to task/agent;
- tool-call timeline;
- review findings;
- cost records;
- approval records.

---

## 11. Functional Requirements

### FR-001 Authentication

Users can authenticate securely and manage sessions.

### FR-002 GitHub Installation

Users can install the GitHub App and grant access to selected repositories.

### FR-003 Repository Analysis

System identifies:

- stack;
- package manager;
- build command;
- test commands;
- linting;
- CI;
- source structure;
- deployment config.

### FR-004 Project Rules

Users can define persistent instructions and protected areas.

### FR-005 Task Creation

Tasks can originate from:

- dashboard;
- GitHub issue;
- API;
- monitoring incident;
- schedule.

### FR-006 Planning

System generates a structured plan before medium/high-risk implementation.

### FR-007 Approval

System supports waiting for human approval without losing workflow state.

### FR-008 Sandboxed Execution

Code execution occurs in isolated environments.

### FR-009 Iterative Repair

Failed validation is routed back to a repair step.

### FR-010 Pull Requests

Successful changes are committed to a branch and exposed through a PR.

### FR-011 Incident Creation

Production signals can create correlated incidents.

### FR-012 Automatic Diagnosis

Incident workflows collect sufficient evidence and attempt reproduction.

### FR-013 Deployment Verification

Merged repairs are verified after deployment.

### FR-014 Cost Controls

Users can configure budgets and maximum attempts.

### FR-015 Cancellation

Users can cancel an active run and terminate its sandbox.

---

## 12. Non-Functional Requirements

### Security

- zero cross-tenant data leakage;
- isolated code execution;
- least-privilege GitHub permissions;
- encrypted secrets;
- signed webhook validation;
- full audit log.

### Reliability

- workflow state survives process restart;
- webhook processing is idempotent;
- agent crashes do not corrupt task state;
- sandboxes are disposable.

### Scalability

Initial:
- dozens of concurrent task runs.

Architecture target:
- horizontally scalable workers and isolated sandboxes.

### Performance

Targets for MVP:

- webhook acknowledgement < 2 seconds;
- task creation < 1 second excluding model processing;
- sandbox startup target < 30 seconds;
- live UI updates within several seconds.

### Observability

Every workflow and agent run must be traceable.

---

## 13. Safety Model

The platform has permission tiers.

### Level 0 — Read Only

- inspect repo;
- plan;
- explain.

### Level 1 — Workspace Write

- modify sandbox;
- run commands;
- no remote push.

### Level 2 — GitHub Write

- create branch;
- commit;
- push;
- create PR.

### Level 3 — Restricted Operations

- migrations;
- infrastructure;
- protected configuration;
- secrets.

Require explicit policy/approval.

### Level 4 — Production Mutation

Examples:
- auto-merge;
- rollback;
- production config changes.

Disabled by default.

---

## 14. Risk-Based Workflow

Do not spend ten agent calls on a typo.

### Low Risk

Examples:

- README;
- copy;
- small styling;
- isolated tests.

Flow:

```text
Developer → Test → Review → PR
```

### Medium Risk

Examples:

- standard API;
- normal feature;
- dashboard page.

Flow:

```text
Planner → Developer/Specialists → Test → Review → PR
```

### High Risk

Examples:

- auth;
- payments;
- migrations;
- infra;
- permissions.

Flow:

```text
Architect → Planner → Specialists → Test → Security → Review → PR
```

### Critical

System may default to diagnosis-only until human approval.

---

## 15. Core Data Concepts

### Project

A logical application connected to one or more repositories/environments.

### Task

Requested engineering outcome.

### Plan

Structured implementation strategy.

### Task Node

An executable unit in the dependency graph.

### Agent Run

One agent execution.

### Sandbox

Isolated execution environment.

### Incident

Correlated production problem.

### Evidence

Logs, traces, failing checks, stack traces, metrics, deployment info.

### Finding

A test/security/review issue.

### Verification

Evidence that a deployed repair restored health.

---

## 16. Recommended Tech Stack

### Frontend

```text
Next.js
React
TypeScript
Tailwind CSS
shadcn/ui
```

### Backend

```text
Python
FastAPI
Pydantic
SQLAlchemy
Alembic
```

### Workflow

```text
Temporal
```

### Database

```text
PostgreSQL
```

### Cache / operational state

```text
Redis
```

### AI Agent Runtime

```text
OpenHands SDK
OpenHands Agent Server
```

### Execution Isolation

```text
Docker → Kubernetes later
```

### Git

```text
Git
GitHub App
GitHub REST/GraphQL APIs
GitHub Webhooks
GitHub Checks
```

### Storage

```text
Cloudflare R2 / S3
MinIO for local self-hosted development
```

### Monitoring

```text
OpenTelemetry
Prometheus
Grafana
Loki
Tempo
```

### Models

Provider abstraction supporting:

```text
OpenAI
Anthropic
Gemini
OpenRouter
Ollama / local models
```

---

## 17. Suggested Monorepo

```text
autonomous-dev-team/
│
├── apps/
│   ├── web/                 # Next.js
│   ├── api/                 # FastAPI
│   └── worker/              # Temporal workers
│
├── packages/
│   ├── contracts/           # shared API/event schemas
│   ├── github/              # GitHub integration
│   ├── agent-core/          # agent interfaces/prompts/tools
│   ├── integrations/        # monitoring/deployment adapters
│   └── ui/                  # shared frontend UI
│
├── services/
│   └── sandbox-manager/
│
├── infra/
│   ├── docker/
│   ├── kubernetes/
│   └── terraform/
│
├── docs/
│   ├── PROJECT_OVERVIEW.md
│   ├── ARCHITECTURE.md
│   └── IMPLEMENTATION_PLAN.md
│
├── .github/
│   └── workflows/
│
├── AGENTS.md
└── README.md
```

A Python/TypeScript monorepo may use separate package tooling rather than forcing one package manager across both ecosystems.

---

## 18. Project Configuration File

Consider supporting:

```yaml
# .autodev/project.yml

version: 1

project:
  name: my-saas

commands:
  install: pnpm install --frozen-lockfile
  lint: pnpm lint
  test: pnpm test
  build: pnpm build

policies:
  require_plan_for:
    - database
    - auth
    - infrastructure

  protected_paths:
    - .github/workflows/**
    - migrations/**

guardian:
  enabled: true

  health_checks:
    - name: web
      url: https://example.com/api/health
      interval_seconds: 60
      failure_threshold: 3

pull_requests:
  auto_create: true
  auto_merge: false
```

Repository-side configuration keeps behavior version-controlled.

---

## 19. MVP Scope

### Include

- authentication;
- GitHub App;
- one repository per project initially;
- repo scan;
- project rules;
- manual task;
- planning;
- one primary coding agent;
- sandbox;
- test/build execution;
- review agent;
- branch/commit/PR;
- activity UI;
- cost/token tracking;
- cancellation;
- audit log.

### Guardian MVP

- HTTP health checks;
- GitHub check/Actions failures;
- Vercel deployment event adapter;
- generic incident webhook;
- incident timeline;
- repair → PR;
- deployment verification.

### Defer

- full enterprise RBAC;
- arbitrary cloud production modification;
- automatic merge;
- dozens of specialist agents;
- fully autonomous DB migration;
- multi-cloud deployment actions;
- self-hosted model marketplace;
- mobile app.

---

## 20. Version Roadmap

### V0 — Technical Prototype

Goal:

```text
Repository + prompt → sandbox → code → tests → patch
```

### V1 — Developer MVP

Goal:

```text
GitHub repo + task → plan → verified PR
```

### V1.5 — Guardian MVP

Goal:

```text
CI/deployment/health failure → incident → repair PR
```

### V2 — Multi-Agent Team

Goal:

```text
risk-based architect/planner/specialists/review/security
```

### V3 — Autonomous Maintenance Platform

Goal:

- broader monitoring integrations;
- scheduled maintenance;
- dependency repairs;
- performance investigations;
- controlled low-risk auto-merge;
- post-deployment closed loop.

---

## 21. What Makes the Product Different

A normal coding assistant:

```text
User → prompt → code suggestion
```

A cloud coding agent:

```text
User → task → autonomous code change → PR
```

This project:

```text
User / Production
       ↓
Build OR Incident
       ↓
Autonomous engineering
       ↓
Verification
       ↓
PR
       ↓
Deployment observation
       ↓
Continuous maintenance
```

The core differentiator is the closed lifecycle:

> **Build → Verify → Deploy → Observe → Repair**

---

## 22. Product Metrics

Track:

- successful tasks / attempted tasks;
- PR acceptance rate;
- percentage of PRs merged without manual code changes;
- test pass rate;
- incident detection precision;
- false incident rate;
- mean time to detection;
- mean time from incident to repair PR;
- post-merge repair success rate;
- cost per successful task;
- average agent retries;
- percentage requiring human rescue.

The most important metric is not “lines of AI-generated code.”

It is:

> **Verified engineering outcomes successfully accepted by users.**

---

## 23. Initial Business / Packaging Concept

Potential tiers later:

### Local / Open Source

- local execution;
- own model keys;
- local Docker;
- GitHub integration;
- limited Guardian setup.

### Cloud

- managed sandboxes;
- hosted workers;
- managed integrations;
- collaboration;
- usage analytics.

### Team / Enterprise

- RBAC;
- SSO;
- audit retention;
- private networking;
- policy controls;
- self-hosting;
- enterprise model endpoints.

Do not optimize monetization before execution reliability is proven.

---

## 24. Key Risks

### AI reliability

Mitigation:
- structured plans;
- tests;
- bounded repair loops;
- independent review;
- human merge.

### Arbitrary code execution

Mitigation:
- isolation;
- no host mounts;
- resource limits;
- egress controls;
- short-lived credentials.

### Prompt injection

Mitigation:
- trust hierarchy;
- policy engine;
- repository content treated as data;
- sensitive tools permissioned separately.

### Cost runaway

Mitigation:
- per-task budget;
- per-project monthly budget;
- token/cost telemetry;
- bounded retries;
- model routing.

### False production incidents

Mitigation:
- correlation;
- thresholds;
- repeated health checks;
- confidence;
- suppression windows.

### Dangerous automatic repairs

Mitigation:
- risk classification;
- protected paths;
- required human approval;
- no default auto-merge.

---

## 25. Definition of Done for the Product

A first production-worthy version is successful when a developer can:

1. sign in;
2. install the GitHub App;
3. connect a repository;
4. configure project rules;
5. submit an engineering task;
6. receive and approve a plan;
7. watch an isolated agent execute it;
8. receive a passing tested/reviewed PR;
9. enable Guardian Mode;
10. have a real CI/deployment/health incident automatically produce a diagnostic or repair PR;
11. merge the PR manually;
12. have the system verify the new production deployment.

---

## 26. Product North Star

The north-star experience is:

```text
Developer wakes up.

Notification:

"Your production API began failing at 02:37.
The issue was traced to a breaking SDK response introduced
in yesterday's deployment.

A regression test and repair are ready in PR #219.

Tests: passed
Security: passed
Build: passed
Production impact: authentication endpoint

Review PR"
```

That is the product.

---

**End of Project Overview**
