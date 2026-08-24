# Autonomous Dev Team --- Project Overview

## What Is It?

Autonomous Dev Team is an AI-powered software engineering and
maintenance platform that can understand a GitHub repository, implement
engineering tasks, validate changes, create pull requests, monitor
deployed applications, investigate failures, and prepare repairs.

It is designed to act like an **autonomous engineering team with human
production control**, rather than a chat-based code generator.

## Core Product Loop

### Build Mode

``` text
User asks for work
       ↓
Repository analyzed
       ↓
Risk classified
       ↓
Plan created
       ↓
Implementation
       ↓
Tests
       ↓
Security / Review
       ↓
Pull Request
       ↓
Human merge
```

### Guardian Mode

``` text
Application is live
       ↓
Failure detected
       ↓
Incident correlated
       ↓
Evidence collected
       ↓
Failure reproduced
       ↓
Root cause identified
       ↓
Repair implemented
       ↓
Regression test
       ↓
Review
       ↓
Pull Request
       ↓
Human merge
       ↓
Deployment verified
```

## Product Vision

A developer should be able to connect a repository and say:

> Build what I request, follow this project's rules, watch the deployed
> application, and when something breaks, investigate it and prepare a
> safe verified fix.

The user should not need to manually select individual agents.

## Target Users

-   solo developers;
-   indie hackers;
-   startups;
-   small engineering teams;
-   agencies;
-   open-source maintainers;
-   teams managing many GitHub repositories.

## Core Features

### Repository Intelligence

-   detect stack/framework;
-   map source structure;
-   detect install/build/test/lint commands;
-   understand CI;
-   identify deployment configuration;
-   read project rules;
-   maintain repository snapshots.

### Autonomous Tasks

Tasks can originate from: - web dashboard; - GitHub issue; - API; -
monitoring incident; - scheduled maintenance.

### Planning

Medium/high-risk work receives structured planning before
implementation.

### Autonomous Coding

Agents can: - inspect files; - search code; - edit files; - run shell
commands; - install allowed dependencies; - run tests; - debug
failures; - create a focused patch.

### Validation

-   format;
-   lint;
-   typecheck;
-   unit tests;
-   integration tests;
-   e2e where applicable;
-   build;
-   independent review;
-   security checks for risky changes.

### Pull Requests

The platform can: - create branch; - commit; - push; - create PR; -
attach evidence; - create GitHub checks; - link task/incident.

### Guardian Mode

-   HTTP health monitoring;
-   CI failure events;
-   deployment failure events;
-   generic monitoring webhooks;
-   incident correlation;
-   automatic diagnosis;
-   repair PRs;
-   post-deployment verification.

### Multi-Agent Engineering

Roles may include: - Triage; - Project Manager; - Architect; -
Planner; - Developer; - Frontend; - Backend; - Database; - Test; -
Security; - Review.

Agents are invoked based on task risk, not all at once.

## Safety Model

By default AI may: - inspect; - plan; - edit isolated workspaces; -
test; - review; - push agent branches; - create PRs.

By default AI may not: - merge protected production branches; - directly
change production; - obtain unrestricted production secrets; - bypass
required checks.

## Technology Stack

### Frontend

-   Next.js
-   React
-   TypeScript
-   Tailwind CSS
-   shadcn/ui

### Backend

-   FastAPI
-   Python
-   Pydantic
-   SQLAlchemy
-   Alembic

### Infrastructure

-   PostgreSQL
-   Temporal
-   Redis
-   S3-compatible object storage
-   Docker
-   Kubernetes later

### Agent Runtime

-   OpenHands SDK
-   OpenHands Agent Server

### Integrations

-   GitHub App
-   Vercel initially
-   generic webhooks
-   monitoring providers later

### Observability

-   OpenTelemetry
-   Prometheus
-   Grafana
-   Loki
-   Tempo

### AI

Provider-neutral model router: - OpenAI - Anthropic - Gemini -
OpenRouter - Ollama/local models

## Main Entities

-   User
-   Organization
-   Project
-   Repository
-   ProjectRule
-   RepositorySnapshot
-   Task
-   Plan
-   TaskNode
-   AgentRun
-   Sandbox
-   Incident
-   Evidence
-   Finding
-   Review
-   PullRequest
-   Deployment
-   Verification
-   Integration
-   UsageRecord
-   AuditEvent

## Recommended Repository Structure

``` text
autonomous-dev-team/
├── apps/
│   ├── web/
│   ├── api/
│   └── worker/
├── packages/
│   ├── contracts/
│   ├── github/
│   ├── agent-core/
│   ├── integrations/
│   └── ui/
├── services/
│   └── sandbox-manager/
├── infra/
│   ├── docker/
│   ├── kubernetes/
│   └── terraform/
├── docs/
├── AGENTS.md
└── README.md
```

## MVP

First prove:

``` text
GitHub Repository
       ↓
User Task
       ↓
Repository Analysis
       ↓
Plan
       ↓
One Coding Agent
       ↓
Sandbox
       ↓
Tests + Review
       ↓
Automatic PR
```

Then prove:

``` text
Production/CI Failure
       ↓
Incident
       ↓
Same Repair Engine
       ↓
Automatic PR
```

Only then expand into sophisticated multi-agent orchestration.

## Product Differentiator

Traditional assistant: `Prompt → Code suggestion`

Cloud coding agent: `Task → Code → PR`

Autonomous Dev Team:
`Build → Verify → Deploy → Observe → Diagnose → Repair → Verify`

## North-Star Outcome

The ideal notification is:

> Production began failing. The system identified the failing deployment
> and root cause, reproduced the issue, added a regression test,
> prepared a repair, passed required validation, and opened a pull
> request for your review.

## Engineering Principle

The project optimizes for **verified autonomous outcomes**, not maximum
autonomous activity.
