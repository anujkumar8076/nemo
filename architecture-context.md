# Architecture Context

## System

**Autonomous Dev Team** is an autonomous software-engineering and
maintenance platform.

It supports: - **Build Mode:** task → plan → implementation → validation
→ PR. - **Guardian Mode:** production signal → incident → diagnosis →
repair → validation → PR → deployment verification.

## Architectural Principle

The product is an **orchestration platform**, not a single LLM wrapper.

``` text
User / GitHub / Monitoring
          ↓
    Event Ingestion
          ↓
  Durable Orchestrator
          ↓
     Risk / Triage
          ↓
 Agent Execution Layer
          ↓
 Isolated Sandboxes
          ↓
 Test / Security / Review
          ↓
      GitHub PR
          ↓
   Human Approval
          ↓
      Deployment
          ↓
Production Verification
```

## Core Components

### Web

-   Next.js
-   React
-   TypeScript
-   Tailwind CSS
-   shadcn/ui

Responsibilities: dashboard, projects, tasks, incidents, approvals,
activity, settings, integrations, usage.

### Control Plane

-   Python
-   FastAPI
-   Pydantic
-   SQLAlchemy
-   Alembic

Responsibilities: API, auth/session integration, projects, tasks,
incidents, policies, integrations, workflows, usage, audit.

### Durable Orchestration

**Temporal** is the preferred workflow engine.

Primary workflows: - `BuildTaskWorkflow` - `IncidentRepairWorkflow` -
`PRValidationWorkflow` - `DeploymentVerificationWorkflow` -
`ScheduledMaintenanceWorkflow` - `RepositoryIndexWorkflow`

### Database

**PostgreSQL** is authoritative state.

Redis is limited to cache, transient locks, rate limiting, and live
operational data.

### Agent Runtime

Preferred foundation: - OpenHands SDK - OpenHands Agent Server

Do not rebuild terminal/file/agent primitives unnecessarily.

### Sandbox

MVP: Docker. Production: Kubernetes plus stronger isolation where
required.

Every coding run receives an ephemeral isolated workspace.

### GitHub

Use a GitHub App, not long-lived personal access tokens.

GitHub is responsible for: - repository access; - issues; - branches; -
pull requests; - checks; - CI events; - webhooks.

### Storage

S3-compatible object storage for large logs, artifacts, test reports,
patches, and retained transcripts.

### Observability

OpenTelemetry first. Target stack: Prometheus + Grafana + Loki + Tempo.

## Agent Roles

Initial: - Triage - Planner - General Developer - Test - Review

Later/high-risk: - Project Manager - Architect - Frontend - Backend -
Database - Security - Infrastructure

Agents are invoked based on risk and need. Every task must not pass
through every agent.

## Risk Routing

### Low

`Developer → Test → Review → PR`

### Medium

`Planner → Developer/Specialist → Test → Review → PR`

### High

`Architect → Planner → Specialists → Test → Security → Review → PR`

### Critical

Constrained diagnosis/planning plus explicit human gates.

## Shared State

Core entities: - User - Organization - Project - Repository -
RepositorySnapshot - ProjectRule - Task - TaskPlan - TaskNode -
AgentRun - Sandbox - Incident - IncidentEvidence - Finding - Review -
PullRequest - Deployment - Verification - Integration - UsageRecord -
AuditEvent

## Event Architecture

Inbound events are normalized before workflow execution.

Sources: - dashboard; - GitHub; - Vercel; - health checks; - generic
webhooks; - monitoring providers.

Requirements: - signature validation; - idempotency; - delivery
deduplication; - event persistence; - schema versioning; - replay
support.

Long AI work must never execute inside webhook requests.

## Guardian Mode

``` text
Production
   ↓
Health / CI / Deployment / Runtime Signals
   ↓
Normalization
   ↓
Correlation + Thresholding
   ↓
Incident
   ↓
Triage
   ↓
Evidence Collection
   ↓
Sandbox at failing commit
   ↓
Reproduction
   ↓
Repair
   ↓
Regression Test
   ↓
Review/Security
   ↓
PR
   ↓
Human Merge
   ↓
Deployment Verification
```

## Security Boundaries

Hard constraints: - no host Docker socket; - no host filesystem
exposure; - no unrestricted production credentials; - no default
auto-merge; - short-lived GitHub credentials; - encrypted secret
references; - tenant isolation; - network/egress controls; - audit
logging; - cancellation/kill switch; - repository content treated as
untrusted.

## Provider Abstractions

Do not tightly couple core logic to one vendor.

Interfaces: - `SourceControlProvider` - `DeploymentProvider` -
`MonitoringProvider` - `LLMProvider` - `SandboxProvider` -
`NotificationProvider`

Vercel and GitHub are initial integrations, not permanent architecture
dependencies.

## Monorepo Direction

``` text
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

## Architecture Rule

Before adding a new service, database, queue, framework, or agent role,
demonstrate why the existing architecture cannot meet the requirement.
