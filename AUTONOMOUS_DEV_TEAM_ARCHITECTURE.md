# Autonomous Dev Team — System Architecture

**Document type:** Production Architecture Specification
**Status:** Proposed v1 Architecture
**Primary goal:** Build an autonomous software-engineering and maintenance platform that can implement requested changes, detect production failures, diagnose root causes, create verified fixes, and open GitHub pull requests for human approval.

---

## 1. Executive Architecture Summary

The platform has two primary operating modes:

1. **Build Mode** — a user submits a feature, bug, refactor, or engineering task. The system analyzes the repository, plans the work, executes it in isolated sandboxes, tests/reviews it, and creates a pull request.
2. **Guardian Mode** — the system continuously receives production/deployment/CI/monitoring signals. When a verified incident occurs, it automatically triages the incident, reproduces it, routes it to the correct agent(s), validates a repair, and creates a pull request.

The system is intentionally designed as an **orchestration platform**, not a single autonomous LLM.

```text
                         USER / EXTERNAL EVENTS
                                  │
              ┌───────────────────┼────────────────────┐
              │                   │                    │
              ▼                   ▼                    ▼
        Web Dashboard       GitHub Events       Monitoring Events
              │                   │                    │
              └───────────────────┼────────────────────┘
                                  ▼
                           EVENT INGESTION
                                  │
                                  ▼
                         DURABLE ORCHESTRATOR
                                  │
                                  ▼
                            TRIAGE / ROUTER
                                  │
             ┌────────────────────┼─────────────────────┐
             ▼                    ▼                     ▼
          LOW RISK            MEDIUM RISK            HIGH RISK
             │                    │                     │
             │                 Planner              Architect
             │                    │                     │
             └────────────────────┼─────────────────────┘
                                  ▼
                         TASK DEPENDENCY GRAPH
                                  │
                 ┌────────────────┼────────────────┐
                 ▼                ▼                ▼
           Frontend Agent    Backend Agent     Database Agent
                 │                │                │
                 └────────────────┼────────────────┘
                                  ▼
                             Test Agent
                                  │
                           ┌──────┴──────┐
                           │ failed?     │
                           ▼             ▼
                       Fix Router      Security
                           ▲             │
                           │             ▼
                           └──────── Review Agent
                                         │
                                  ┌──────┴──────┐
                                  │ rejected?   │
                                  ▼             ▼
                              Fix Router        CI
                                                │
                                                ▼
                                           Pull Request
                                                │
                                                ▼
                                         Human Approval
                                                │
                                                ▼
                                              Merge
                                                │
                                                ▼
                                            Deployment
                                                │
                                                ▼
                                      Production Verification
                                       ┌────────┴────────┐
                                       ▼                 ▼
                                    FAILED             HEALTHY
                                       │                 │
                                       ▼                 ▼
                                Reopen Incident     Close Incident
```

---

## 2. Architectural Principles

### 2.1 Human control at the production boundary

The default policy is:

- agents may inspect repositories;
- agents may create branches;
- agents may modify code;
- agents may execute tests/builds;
- agents may create pull requests;
- agents may comment on issues and PRs;
- agents **must not merge production changes by default**.

Auto-merge is an optional later capability restricted by explicit policy.

### 2.2 Event-driven first

The platform should react to real events rather than relying primarily on polling.

Typical events:

- GitHub issue created/labeled;
- pull request updated;
- GitHub check failed;
- deployment failed;
- runtime error threshold exceeded;
- uptime check failed;
- security alert generated;
- user-created task;
- scheduled maintenance task.

### 2.3 Durable workflows

An engineering repair may last minutes or hours and may contain retries, approvals, waiting periods, crashes, or worker restarts.

Therefore execution state must not live only in process memory.

Use a durable workflow engine for:

- retries;
- timeouts;
- state transitions;
- approval waits;
- resumability;
- compensation/cleanup;
- concurrency control;
- scheduled jobs.

### 2.4 Isolation by default

Every coding task executes inside an isolated environment.

MVP:
- Docker container per task/agent workspace.
- Git worktree or isolated clone.
- CPU, memory, runtime, disk, and network limits.

Production hardening:
- Kubernetes Jobs/Pods;
- gVisor, Kata Containers, or Firecracker-class isolation when needed;
- per-task service identity;
- outbound network allowlists;
- ephemeral secrets.

### 2.5 Provider-neutral integrations

Vercel is a first-class integration, not a hard dependency.

Define adapters for:

```text
DeploymentProvider
MonitoringProvider
SourceControlProvider
LLMProvider
SandboxProvider
NotificationProvider
```

Possible integrations:

- GitHub;
- Vercel;
- Render;
- Fly.io;
- AWS;
- Sentry;
- Datadog;
- Grafana;
- generic webhook;
- OpenTelemetry;
- Slack/email later.

---

## 3. Core System Components

### 3.1 Web Application

Responsibilities:

- authentication;
- onboarding;
- GitHub repository connection;
- project setup;
- project rules;
- task creation;
- plan approval;
- live agent activity;
- incident timeline;
- PR status;
- Guardian Mode configuration;
- model/budget settings;
- security policies;
- audit logs.

Recommended stack:

- Next.js + TypeScript;
- React;
- Tailwind CSS;
- shadcn/ui;
- TanStack Query where useful;
- server-sent events or WebSockets for live task updates.

The frontend does not directly execute agents.

---

### 3.2 Control Plane API

Recommended:

- Python;
- FastAPI;
- Pydantic;
- SQLAlchemy;
- Alembic.

Responsibilities:

- user/project APIs;
- GitHub installation management;
- task creation;
- incident creation;
- integration management;
- workflow start/cancel/retry;
- policy evaluation;
- API authentication;
- webhook validation;
- usage and cost accounting.

Why Python:

- strong AI/agent ecosystem;
- straightforward OpenHands integration;
- mature async ecosystem;
- excellent typed validation with Pydantic.

---

### 3.3 GitHub App

Use a GitHub App instead of storing user PATs.

Permissions should follow least privilege.

Likely capabilities:

- read repository metadata;
- read/write contents only where required;
- read/write issues;
- read/write pull requests;
- read/write checks;
- read actions/check results;
- receive webhooks.

Primary events:

```text
issues
issue_comment
pull_request
pull_request_review
push
check_run
check_suite
workflow_run
installation
installation_repositories
```

Security requirements:

- verify webhook signatures;
- deduplicate deliveries;
- store delivery ID;
- reject replayed/expired events;
- encrypt installation credentials/tokens at rest;
- request only required permissions.

---

## 4. Event Ingestion Layer

All inbound events are normalized into an internal event format.

Example:

```json
{
  "event_id": "evt_01...",
  "source": "vercel",
  "type": "deployment.failed",
  "project_id": "proj_123",
  "environment": "production",
  "severity_hint": "high",
  "occurred_at": "2026-08-23T12:00:00Z",
  "correlation": {
    "deployment_id": "dpl_...",
    "commit_sha": "abc123"
  },
  "payload_ref": "blob://..."
}
```

Requirements:

- idempotency;
- signature verification;
- schema versioning;
- rate limiting;
- payload size limits;
- event persistence;
- dead-letter handling;
- replay support.

Recommended implementation:

- API webhook receiver;
- persist event immediately;
- acknowledge quickly;
- start durable workflow asynchronously.

Do not perform long AI work inside the webhook request.

---

## 5. Workflow Orchestrator

### Recommended: Temporal

Temporal is the preferred production orchestration layer.

Use it for workflows such as:

```text
BuildTaskWorkflow
IncidentRepairWorkflow
PRValidationWorkflow
DeploymentVerificationWorkflow
ScheduledMaintenanceWorkflow
RepositoryIndexWorkflow
```

Example incident workflow:

```text
Receive Incident
    ↓
Correlate / Deduplicate
    ↓
Collect Evidence
    ↓
Triage
    ↓
Risk Classification
    ↓
Create Sandbox
    ↓
Reproduce
    ↓
Plan Repair
    ↓
Implement
    ↓
Run Tests
    ↓
Security Review
    ↓
Code Review
    ↓
Run CI
    ↓
Create PR
    ↓
Wait for Human
    ↓
Observe Deployment
    ↓
Verify Production
    ↓
Close/Reopen Incident
```

Alternative for an early prototype:
- a Postgres-backed state machine.

Do not build the production version around transient Redis jobs alone.

---

## 6. Agent Orchestration Layer

The orchestration layer decides **which agents are necessary**.

Agents should be tools in a workflow, not independent uncontrolled processes.

### 6.1 Triage Agent

Inputs:

- issue/task text;
- repository map;
- production logs;
- failing checks;
- recent commits;
- deployment metadata;
- known project rules.

Outputs structured JSON:

```json
{
  "category": "backend_runtime_failure",
  "risk": "high",
  "confidence": 0.92,
  "affected_domains": ["backend", "database"],
  "requires_architect": true,
  "requires_security": true,
  "recommended_workflow": "high_risk_repair"
}
```

No source changes allowed.

---

### 6.2 Project Manager Agent

Responsibilities:

- clarify target outcome from available context;
- track task state;
- enforce scope;
- coordinate dependencies;
- determine whether the requested outcome is complete.

No direct code edits by default.

---

### 6.3 Architect Agent

Used for high-risk/complex tasks.

Responsibilities:

- repository architecture analysis;
- affected-system identification;
- interface design;
- data-flow decisions;
- migration impact;
- compatibility risks;
- rollout/rollback strategy;
- technical plan.

Produces an Architecture Decision / implementation brief.

---

### 6.4 Planner Agent

Converts architecture/task into a dependency graph.

Example:

```json
{
  "tasks": [
    {
      "id": "T1",
      "role": "database",
      "description": "Add provider identity fields",
      "depends_on": []
    },
    {
      "id": "T2",
      "role": "backend",
      "description": "Implement OAuth callback",
      "depends_on": ["T1"]
    },
    {
      "id": "T3",
      "role": "frontend",
      "description": "Add Google sign-in UI",
      "depends_on": ["T2"]
    }
  ]
}
```

---

### 6.5 Specialist Agents

Initial specialist roles:

- General Developer Agent;
- Frontend Agent;
- Backend Agent;
- Database Agent.

Future roles:

- Infrastructure Agent;
- Mobile Agent;
- Data/ML Agent;
- Documentation Agent;
- Performance Agent.

The orchestrator chooses specialists based on repository technology and task scope.

---

### 6.6 Test Agent

Responsibilities:

- identify existing test commands;
- run unit/integration/e2e tests;
- add tests for the change;
- reproduce reported failure;
- verify regression;
- return structured failures.

The test agent does not silently weaken tests to make them pass.

---

### 6.7 Security Agent

Triggered for:

- authentication;
- authorization;
- secrets;
- payment logic;
- user-data handling;
- database migrations;
- dependencies;
- infrastructure;
- user-supplied execution;
- explicitly high-risk changes.

Checks:

- injection;
- XSS;
- CSRF;
- SSRF;
- auth bypass;
- insecure direct object references;
- secret leakage;
- vulnerable dependencies;
- dangerous permissions;
- insecure deserialization;
- network exposure.

---

### 6.8 Review Agent

Independent from implementation agents.

Checks:

- task requirements;
- correctness;
- code quality;
- unnecessary changes;
- architectural consistency;
- regression risk;
- tests;
- project rules;
- maintainability.

Returns:

```text
APPROVED
CHANGES_REQUESTED
BLOCKED
```

with machine-readable findings.

---

### 6.9 Fix Router

Failures must return to the responsible agent.

Example:

```text
Backend test failure
      ↓
Fix Router
      ↓
Backend Agent
      ↓
Test Agent
```

Do not restart the full workflow for every failure.

Retry policy:

- max repair loops per stage;
- escalating model capability;
- stop on repeated identical failure;
- human escalation after budget/attempt threshold.

---

## 7. Agent Runtime

### Recommended base: OpenHands SDK / Agent Server

Use OpenHands as an execution/agent foundation rather than rebuilding terminal/file/browser tooling from scratch.

OpenHands currently exposes:

- Software Agent SDK;
- Agent Server;
- Automation components;
- Sandbox Server;
- Docker/Kubernetes-capable execution patterns.

Important: pin versions and review the license of every OpenHands repository/component separately.

### Agent Tool Set

Agents may receive scoped access to:

- filesystem;
- shell;
- Git;
- test runners;
- package managers;
- browser;
- local application ports;
- approved internet destinations;
- repository search;
- static analysis;
- GitHub APIs through the control plane.

Agents should **not** receive unrestricted production credentials.

---

## 8. Sandbox Architecture

### MVP

```text
Worker
  │
  └── Docker Sandbox
        ├── ephemeral filesystem
        ├── git clone/worktree
        ├── repository dependencies
        ├── agent server
        ├── test tools
        └── scoped environment variables
```

### Sandbox controls

- non-root user;
- no Docker socket mount;
- read-only base image;
- writable workspace only;
- memory limit;
- CPU limit;
- process limit;
- disk quota;
- execution timeout;
- no host filesystem;
- sanitized environment;
- egress filtering;
- secret redaction.

### Production

```text
Kubernetes
   ↓
Task Pod
   ↓
Sandbox
   ↓
Agent Server
   ↓
Ephemeral Workspace
```

Potential stronger isolation later:

- gVisor;
- Kata;
- Firecracker microVMs.

---

## 9. Repository Understanding Layer

Do not repeatedly send the entire repository to the model.

Build a repository intelligence service.

Stored information:

- languages/frameworks;
- directory tree;
- package manifests;
- build commands;
- test commands;
- lint commands;
- service map;
- APIs;
- database models;
- dependency graph;
- CODEOWNERS;
- AGENTS.md/project instructions;
- CI workflows;
- deployment files;
- recent relevant commits.

### Index strategy

1. deterministic parsing first;
2. semantic retrieval second;
3. fresh local code search during execution.

Use tree-sitter/LSP/AST tooling where practical.

Vector search is supplemental—not the source of truth.

---

## 10. Shared Project State

Agents need a durable common state.

Core records:

```text
Project
Repository
RepositorySnapshot
Task
TaskPlan
TaskNode
AgentRun
Sandbox
Incident
IncidentEvidence
Finding
Review
PullRequest
Deployment
Verification
Integration
ProjectRule
SecretReference
UsageRecord
AuditEvent
```

PostgreSQL is the source of truth.

Redis may be used for:

- cache;
- short-lived locks;
- rate limits;
- live presence;
- transient fan-out.

Do not use Redis as the authoritative workflow database.

---

## 11. Guardian Mode Architecture

Guardian Mode monitors deployed software and initiates repair workflows.

```text
              Production Application
                       │
       ┌───────────────┼─────────────────┐
       ▼               ▼                 ▼
   Uptime Check     Runtime Logs      Deploy/CI Events
       │               │                 │
       └───────────────┼─────────────────┘
                       ▼
                Signal Normalizer
                       │
                       ▼
               Incident Correlator
                       │
                 Real incident?
                 ┌─────┴─────┐
                 ▼           ▼
                NO          YES
                 │           │
              suppress       ▼
                         Triage Agent
                              │
                              ▼
                        Repair Workflow
```

### Signal sources

MVP:

- generic HTTP health checks;
- GitHub Actions/check failures;
- Vercel deployment events;
- manually forwarded runtime errors;
- generic webhook.

Next:

- Vercel log drains;
- Sentry;
- Datadog;
- OpenTelemetry;
- Grafana Alertmanager;
- AWS CloudWatch;
- Render;
- Fly.io.

### Incident correlation

Avoid creating a repair task for every 500 error.

Group by:

- project;
- environment;
- error fingerprint;
- stack trace;
- endpoint;
- deployment;
- commit SHA;
- time window.

Apply thresholds:

```text
1 isolated 500                    → record only
10 matching errors / 5 minutes   → warning
error-rate threshold exceeded    → incident
health check fails N times       → incident
deployment failed                → incident
CI required check failed         → workflow-specific event
```

---

## 12. Automatic Repair Flow

```text
Incident
   ↓
Collect evidence
   ├── logs
   ├── stack trace
   ├── recent commits
   ├── deployment SHA
   ├── health-check result
   └── relevant files
   ↓
Create sandbox from failing commit
   ↓
Attempt reproduction
   ↓
Root-cause analysis
   ↓
Risk classification
   ↓
Repair plan
   ↓
Implementation
   ↓
Regression test
   ↓
Full required checks
   ↓
Security/review gates
   ↓
Branch + PR
```

The PR should contain:

- incident reference;
- root cause;
- reproduction;
- fix summary;
- files changed;
- tests executed;
- security findings;
- risk;
- rollback instructions;
- evidence of successful verification.

---

## 13. Deployment Verification

After human merge:

```text
GitHub Merge
    ↓
Deployment Provider
    ↓
deployment.completed
    ↓
Verification Workflow
    ↓
Health checks
    ↓
Synthetic critical path
    ↓
Error-rate observation window
    ↓
Healthy?
 ┌──┴──┐
 NO   YES
 │     │
 ▼     ▼
Reopen Close
```

For failed verification:

- reopen incident;
- capture new evidence;
- optionally create rollback recommendation;
- do not endlessly patch production.

---

## 14. Risk Engine

Every task gets:

```text
risk_score = impact × uncertainty × privilege × blast_radius
```

Factors include:

- auth changes;
- payment changes;
- migrations;
- infrastructure;
- secrets;
- production config;
- deletion;
- dependency major updates;
- amount of changed code;
- test coverage;
- agent confidence;
- number of services affected.

### Example policy

| Risk | Workflow | Human Plan Approval | Security Agent | Auto PR | Auto Merge |
|---|---|---:|---:|---:|---:|
| Low | Developer → Test → Review | Optional | Optional | Yes | Future opt-in |
| Medium | Planner → Specialists → Test → Review | Yes | Conditional | Yes | No |
| High | Architect → Planner → Specialists → Test → Security → Review | Yes | Required | Yes | No |
| Critical | Diagnose only / constrained repair | Required | Required | Conditional | Never |

---

## 15. Model Routing

Create an internal provider abstraction.

```text
ModelRouter.generate()
ModelRouter.tool_agent()
ModelRouter.embed()
```

Providers can include:

- OpenAI;
- Anthropic;
- Gemini;
- OpenRouter;
- local Ollama/vLLM;
- enterprise provider later.

Routing criteria:

- task type;
- risk;
- context size;
- price;
- latency;
- model health;
- privacy policy.

Use cheaper models for:

- classification;
- log grouping;
- summarization.

Use strongest allowed models for:

- architecture;
- difficult debugging;
- high-risk code review.

Never couple agent logic to one model vendor.

---

## 16. Memory

Use three types of memory.

### Project Memory

Stable facts:

- architecture;
- conventions;
- commands;
- policies;
- known service boundaries.

### Episodic Memory

Past outcomes:

- previous incidents;
- successful fixes;
- failed approaches;
- review findings.

### Task Memory

Temporary state for current workflow.

Memory must be:

- source-attributed;
- editable;
- scoped by repository/project;
- freshness-aware;
- never treated as more authoritative than current source code.

---

## 17. Data Model — Initial Tables

Suggested core schema:

```text
users
organizations
memberships

github_installations
projects
repositories
project_rules
repository_snapshots

tasks
task_plans
task_nodes
task_dependencies
agent_runs
agent_messages
sandboxes

incidents
incident_events
incident_evidence

reviews
findings

pull_requests
deployments
verifications

integrations
integration_secrets

model_usage
budgets
audit_events
```

Large logs/artifacts should go to object storage rather than bloating Postgres.

---

## 18. Storage

### PostgreSQL

Authoritative relational state.

### Object Storage

S3-compatible storage for:

- compressed logs;
- build artifacts;
- test reports;
- patches;
- large webhook payloads;
- agent transcripts when retention is enabled.

Possible providers:

- Cloudflare R2;
- AWS S3;
- MinIO for self-hosting.

### Redis

Optional operational cache, not source of truth.

---

## 19. Observability

Instrument the platform with OpenTelemetry.

Track:

- workflow duration;
- agent duration;
- token usage;
- cost;
- retry count;
- sandbox startup time;
- test pass/fail;
- repair success rate;
- PR acceptance rate;
- incident false-positive rate;
- time to detect;
- time to PR;
- time to recovery.

Recommended self-hosted observability:

```text
OpenTelemetry
   ├── Prometheus / metrics
   ├── Grafana / dashboards
   ├── Loki / logs
   └── Tempo / traces
```

Every workflow should carry:

```text
trace_id
project_id
task_id
incident_id
agent_run_id
sandbox_id
```

---

## 20. Security Architecture

This product executes code, which makes security a primary architectural requirement.

### Hard rules

- never mount Docker socket into agent containers;
- never expose host filesystem;
- never pass permanent production secrets to coding agents;
- never log raw secret values;
- never trust repository code;
- never execute unverified webhook payloads as instructions;
- treat issue/PR content as untrusted prompt input;
- isolate organization data;
- enforce egress policy;
- encrypt secrets;
- maintain audit logs;
- support kill/cancel for active runs.

### Prompt injection protection

Repository content may contain hostile instructions.

Separate:

```text
SYSTEM POLICY
PROJECT POLICY
USER TASK
REPOSITORY DATA
EXTERNAL LOG DATA
```

Repository data must never override platform policies.

### Secret strategy

MVP:
- encrypted secret references;
- short-lived GitHub installation tokens;
- provider API keys stored server-side only.

Production:
- Vault / cloud KMS;
- short-lived credentials;
- workload identity.

---

## 21. Approval Gates

Possible human gates:

1. plan approval;
2. privileged secret request;
3. dangerous migration approval;
4. PR approval;
5. production rollback approval.

Workflow engine must be able to pause durably while waiting.

---

## 22. Git Strategy

Never commit directly to the protected default branch.

Pattern:

```text
main
 └── agent/task-123-short-description
```

For parallel specialists:

```text
main
 ├── worktree/frontend-T1
 ├── worktree/backend-T2
 └── worktree/db-T3
```

Merge to an integration branch before the final PR when tasks are parallel.

Conflict handling:

1. detect;
2. rebase/merge latest target;
3. route conflict to responsible agent;
4. rerun relevant tests;
5. require review again if semantic changes occur.

---

## 23. CI Integration

The platform should create GitHub Checks for its own validation.

Example:

```text
Autonomous Dev Team / Plan
Autonomous Dev Team / Tests
Autonomous Dev Team / Security
Autonomous Dev Team / Review
Autonomous Dev Team / Policy
```

A PR is considered agent-approved only if required platform checks pass.

GitHub branch protection remains the final repository-level authority.

---

## 24. Failure Handling

### Model failure

- retry;
- switch healthy model;
- resume from durable checkpoint.

### Sandbox failure

- destroy sandbox;
- recreate from clean snapshot;
- replay task.

### Tool timeout

- bounded retry;
- classify deterministic vs transient.

### Agent loop

Stop when:

- max attempts reached;
- no diff improvement;
- same failure repeats;
- cost budget exceeded;
- security policy blocks operation.

Escalate to human with:

- attempts;
- evidence;
- current branch/diff;
- failing command;
- recommended next action.

---

## 25. Multi-Tenant Isolation

Every record carries an organization/project boundary.

Enforce:

- tenant-aware DB queries;
- object-storage prefixes;
- separate sandbox credentials;
- scoped GitHub installations;
- no cross-project memory;
- tenant-specific encryption/context where appropriate.

---

## 26. Reference Deployment Topology

### MVP / Single-node

```text
Docker Compose
│
├── web
├── api
├── temporal
├── temporal-worker
├── postgres
├── redis
├── sandbox-manager
└── object-storage/minio
```

Agents create nested/remote Docker sandboxes through a dedicated sandbox service—not by mounting the host Docker socket into the web/API containers.

### Production

```text
                    CDN / Load Balancer
                           │
                ┌──────────┴──────────┐
                ▼                     ▼
             Next.js               FastAPI
                                      │
                         ┌────────────┼────────────┐
                         ▼            ▼            ▼
                     Postgres      Temporal     Object Store
                                      │
                                      ▼
                               Worker Pool
                                      │
                          ┌───────────┼───────────┐
                          ▼           ▼           ▼
                      Sandbox      Sandbox      Sandbox
                      Pod/VM       Pod/VM       Pod/VM
```

---

## 27. Recommended Technology Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js, React, TypeScript, Tailwind, shadcn/ui |
| API | FastAPI, Python, Pydantic |
| ORM / migrations | SQLAlchemy, Alembic |
| Workflow engine | Temporal |
| Primary DB | PostgreSQL |
| Cache / rate limit | Redis |
| Agent framework/runtime | OpenHands SDK + Agent Server |
| Sandbox MVP | Docker |
| Sandbox production | Kubernetes + stronger runtime isolation as needed |
| Source control | GitHub App + GitHub APIs/webhooks |
| Object storage | S3/R2/MinIO |
| Observability | OpenTelemetry + Prometheus/Grafana/Loki/Tempo |
| Model routing | Internal adapter over OpenAI/Anthropic/Gemini/OpenRouter/Ollama |
| Secrets | encrypted DB refs for MVP; Vault/KMS in production |
| CI | GitHub Actions + GitHub Checks |
| Deployment integration | Vercel first; adapter architecture |
| Monitoring | native health checks + generic webhooks; Sentry/Datadog/OTel adapters |

---

## 28. What We Should Build vs Reuse

### Build ourselves

- product UX;
- project/task/incident model;
- risk engine;
- agent router;
- workflow definitions;
- shared project state;
- GitHub App behavior;
- provider adapters;
- Guardian Mode;
- policy system;
- audit/cost system;
- repair feedback loop.

### Reuse

- OpenHands agent/runtime primitives;
- Temporal durable workflows;
- PostgreSQL;
- Docker/Kubernetes;
- GitHub APIs;
- OpenTelemetry;
- existing test/security tools;
- LLM APIs/local models.

Do **not** build:

- a new Git implementation;
- a new container runtime;
- a new workflow engine;
- a new LLM;
- a new observability protocol.

---

## 29. MVP Architecture Boundary

Version 1 should support:

```text
User task
   ↓
GitHub repository
   ↓
Analyze
   ↓
Plan
   ↓
Approve
   ↓
Single coding agent in sandbox
   ↓
Test
   ↓
Review
   ↓
PR
```

Then add:

```text
Guardian Mode
   ↓
Health / CI / deployment event
   ↓
Incident
   ↓
Repair workflow
   ↓
PR
```

Do not start by implementing twelve simultaneous agents.

The multi-agent system should be introduced after the single-agent execution loop is reliable.

---

## 30. Architecture Decision Summary

1. **GitHub App**, not PAT-based integration.
2. **FastAPI control plane** for AI/backend ecosystem fit.
3. **Next.js dashboard** for the product UI.
4. **Temporal** for durable orchestration.
5. **PostgreSQL** as authoritative state.
6. **OpenHands SDK/Agent Server** for agent execution foundation.
7. **Docker sandbox per task** initially.
8. **Kubernetes/stronger isolation** at production scale.
9. **Risk-based agent routing**, not every-agent-for-every-task.
10. **Human approval before production merge** by default.
11. **Provider-neutral monitoring/deployment adapters**.
12. **Guardian Mode** as a first-class product capability.
13. **OpenTelemetry from day one**.
14. **Structured agent outputs** for routing and auditability.
15. **No production credentials inside general coding sandboxes**.

---

## 31. Success Criteria

The architecture is successful when the platform can reliably do this:

```text
Production problem occurs
        ↓
System detects/correlates it
        ↓
Correct repository + commit identified
        ↓
Failure reproduced in isolation
        ↓
Root cause identified
        ↓
Minimal repair implemented
        ↓
Regression test added
        ↓
Required checks pass
        ↓
PR created with evidence
        ↓
Human merges
        ↓
Deployment observed
        ↓
Production verified healthy
```

without requiring a developer to manually drive the AI through each step.

---

## 32. Current External Capabilities Informing This Design

The architecture deliberately aligns with capabilities available in the ecosystem today:

- GitHub Apps can receive real-time repository events through signed webhooks and act through GitHub APIs.
- GitHub Checks can expose rich CI/check information and enforce protected-branch workflows.
- Vercel exposes deployment/runtime logs, and Log Drains can forward runtime data to external systems/webhooks on supported plans.
- OpenHands provides an agent SDK/server model and supports isolated Docker/Kubernetes-style execution patterns.
- OpenHands separates agent execution, automation state, and sandbox/workspace state, which maps well to the proposed control-plane/runtime split.

These are implementation inputs, not hard vendor dependencies.

---

**End of Architecture Specification**
