# UI Context

## Product UI Goal

The interface should make an advanced autonomous engineering system feel
**calm, professional, trustworthy, and understandable**.

The user should feel that they are assigning work to an engineering
team---not configuring an AI research experiment.

## Design Principles

### 1. Hide Agent Complexity by Default

Normal users see:

``` text
Analyzing → Planning → Implementing → Testing → Reviewing → PR Ready
```

They should not need to manage:

``` text
Frontend Agent
Backend Agent
Database Agent
Security Agent
```

Advanced execution details belong behind expandable views.

### 2. Evidence Over AI Theater

Avoid UI whose main purpose is animated "AI thinking."

Prioritize: - actual status; - changed files; - test results; -
findings; - cost; - PR; - incident evidence; - timestamps.

### 3. Human Control Must Be Obvious

Important controls: - Approve Plan - Reject/Edit Plan - Cancel Run -
Stop Sandbox - Retry - Open PR - Enable/Disable Guardian Mode

Dangerous actions require clear confirmation.

### 4. Status Must Be Unambiguous

Use consistent states:

``` text
Queued
Analyzing
Planning
Waiting for Approval
Executing
Testing
Reviewing
Blocked
Failed
PR Ready
Completed
Cancelled
```

Do not display "success" before validation completes.

## Visual Direction

Professional developer/SaaS product.

Characteristics: - clean; - restrained; - information-dense without
clutter; - strong typography; - subtle borders; - clear hierarchy; -
minimal decorative gradients; - excellent dark mode; - responsive; -
accessible.

Avoid: - excessive glassmorphism; - neon AI visuals; - giant empty hero
areas inside the app; - excessive rounded cards; - random colors; -
constant animations; - fake terminal decoration.

## Application Shell

``` text
┌──────────────────────────────────────────────────────────┐
│ Logo     Project Switcher                    User / Org   │
├──────────────┬───────────────────────────────────────────┤
│ Overview     │                                           │
│ Tasks        │               Page                        │
│ Incidents    │                                           │
│ Deployments  │                                           │
│ Integrations │                                           │
│ Usage        │                                           │
│ Audit        │                                           │
│ Settings     │                                           │
└──────────────┴───────────────────────────────────────────┘
```

## Core Screens

### Dashboard

Show: - active tasks; - open incidents; - PRs ready for review; -
Guardian health; - recent deployments; - recent activity; - usage/budget
summary.

Do not overload with vanity metrics.

### Projects

Each project card/row: - name; - repository; - production environment; -
Guardian status; - open tasks; - open incidents; - latest deployment
health.

### Project Overview

Sections: - current health; - repository; - detected stack; - active
work; - incidents; - deployments; - project rules; - integrations.

Primary CTA: `New Task`

### Create Task

Main input should be simple:

``` text
What should the engineering team do?

[ Describe the feature, bug, or change... ]

Attach issue/context (optional)

[Create Task]
```

Advanced options: - branch; - budget; - risk override request; - model
policy; - plan approval preference.

Keep advanced settings collapsed.

### Task Detail

Header:

``` text
TASK-142 · Add Google OAuth
In Progress · High Risk
```

Main timeline:

``` text
✓ Repository analyzed
✓ Architecture reviewed
✓ Plan approved
● Implementing
○ Testing
○ Security
○ Review
○ Pull request
```

Secondary panels: - Plan - Changes - Tests - Findings - Activity - Agent
Details - Cost

### Plan Approval

Show: - objective; - affected systems; - tasks; - risk; - protected
files; - validation plan.

Actions: `Approve Plan` `Request Changes`

### Incident List

Prioritize: - severity; - status; - project; - environment; - first
seen; - duration; - deployment; - repair status.

### Incident Detail

Header:

``` text
INC-1024 · Authentication API failures
HIGH · Production · Repairing
```

Show: - impact; - detection source; - error fingerprint; - affected
endpoint/service; - deployment; - commit; - timeline; - evidence; -
root-cause hypothesis; - repair progress; - linked PR.

### Guardian Mode

Use a clear state:

``` text
Guardian Mode
● Enabled

Production: Healthy
Last check: 14 seconds ago
```

Configuration: - environments; - health checks; - failure threshold; -
monitoring integrations; - auto-create repair PR; - notifications.

Do not enable auto-merge by default.

### Pull Request Ready State

Provide a concise engineering summary:

``` text
Repair Ready

PR #219
Tests        Passed
Build        Passed
Security     Passed
Review       Passed
Risk         High

[Open Pull Request]
```

## Activity Timeline

Use human-readable events:

``` text
14:02 Repository analyzed
14:03 Plan generated
14:05 Plan approved
14:06 Sandbox started
14:09 Backend implementation completed
14:11 Test failed
14:13 Failure repaired
14:15 Tests passed
14:17 Review passed
14:18 Pull request created
```

Raw logs belong in expandable detail.

## Agent Details

Advanced view only.

``` text
Backend Agent
Status: Working

Current action:
Running authentication integration tests

Changed:
- api/auth/oauth.py
- api/routes/auth.py

Last command:
pytest tests/auth -q
```

Never expose hidden chain-of-thought. Show tool activity, structured
summaries, decisions, evidence, and results instead.

## Color Semantics

Use the design system's semantic tokens rather than hard-coded feature
colors.

Meanings: - neutral = normal; - success = passed/healthy; - warning =
attention; - destructive = failed/high danger; - info/accent = active
work.

Do not communicate status by color alone. Include icon/text.

## Typography

Use a modern, highly readable sans-serif.

Recommended: - Inter; - Geist; - system fallback.

Use monospace for: - commit SHA; - commands; - paths; - IDs; - code.

## Components

Build reusable primitives: - `StatusBadge` - `RiskBadge` -
`TaskTimeline` - `IncidentTimeline` - `EvidencePanel` - `TestResult` -
`FindingCard` - `DiffSummary` - `RepositoryBadge` - `DeploymentStatus` -
`ApprovalPanel` - `CostSummary` - `ActivityFeed` - `EmptyState` -
`ErrorState`

## Accessibility

Required: - keyboard navigation; - visible focus; - semantic HTML; -
ARIA only where needed; - sufficient contrast; - status text in addition
to color; - reduced-motion support; - accessible dialogs; - accessible
data tables.

## Responsive Behavior

Desktop is primary because this is an engineering tool.

Tablet/mobile must still support: - incident review; - task status; -
plan approval; - opening PR; - Guardian health.

Complex diffs/logs may use optimized mobile layouts rather than desktop
tables squeezed onto small screens.

## Loading / Empty / Error States

Every data screen must explicitly design: - loading; - empty; - error; -
partial data; - stale data; - disconnected integration; - permission
denied.

Never show fabricated placeholder production data as real data.

## Trust UX

Whenever the AI proposes an action, show: - what it intends to change; -
why; - risk; - validation; - whether human approval is required.

For incidents, distinguish: - observed evidence; - inferred root
cause; - confirmed reproduction.

## UI Definition of Done

A screen is complete only when: - real backend state is connected; -
loading/empty/error states exist; - responsive behavior works; -
keyboard access works; - no fake success states remain; - destructive
actions are protected; - relevant tests pass.
