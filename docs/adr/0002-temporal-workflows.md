# ADR-0002: Temporal for durable workflows

- Status: Accepted
- Date: 2026-08-24

## Decision

Use Temporal for long-running build, repair, validation, indexing, approval, and
deployment-verification workflows. State must survive worker restarts.

## Consequences

Workflow code remains deterministic. External I/O belongs in activities;
approval waits, cancellation, retry limits, and cleanup are explicit.
