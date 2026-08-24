# Code Standards

## Purpose

Mandatory engineering standards for Autonomous Dev Team.

## General Principles

1.  Correctness before cleverness.
2.  Readability before premature optimization.
3.  Small, focused modules.
4.  Explicit contracts.
5.  Secure defaults.
6.  Deterministic behavior where possible.
7.  Every production path must be observable.
8.  Every meaningful change must be testable.

## TypeScript / Frontend

-   TypeScript strict mode.
-   Avoid `any`; use explicit types or `unknown` with narrowing.
-   Prefer named types/interfaces for public contracts.
-   Functional React components.
-   Avoid unnecessary client components in Next.js.
-   Keep server-only code out of client bundles.
-   Validate external data at boundaries.
-   Reuse design-system components.
-   Avoid business logic inside presentation components.
-   Extract complex state into hooks/services.
-   Use semantic HTML and keyboard-accessible controls.
-   Handle loading, empty, error, disabled, and success states.

## Python / Backend

-   Python type hints on public functions.
-   Pydantic models for API/event boundaries.
-   SQLAlchemy models/repositories separated from API schemas.
-   Alembic for schema migrations.
-   Async only where it provides actual I/O benefit.
-   No broad `except Exception` without re-raising/logging/context.
-   Use domain-specific exceptions.
-   Never return internal stack traces to clients.
-   Keep route handlers thin.
-   Business logic belongs in services/domain modules.
-   External providers must be behind adapters.

## Naming

Use names that communicate intent.

Good: - `create_repair_workflow` - `github_installation_id` -
`incident_fingerprint`

Avoid: - `data` - `temp` - `thing` - `helper2` - `doStuff`

## Functions

A function should have one primary responsibility.

Prefer:

``` text
receive_event
normalize_event
persist_event
start_workflow
```

over one 300-line webhook handler.

## API Standards

-   Version public APIs: `/v1/...`.
-   Use consistent error envelopes.
-   Use UUID/ULID-style opaque public IDs.
-   Validate every external input.
-   Paginate collections.
-   Support idempotency where mutation may be retried.
-   Never expose internal secrets or raw provider credentials.
-   Use proper HTTP status codes.

## Event Standards

Every normalized event should include: - event ID; - schema version; -
source; - type; - project; - timestamp; - correlation metadata; -
payload reference or safe payload.

Consumers must be idempotent.

## Database Standards

-   PostgreSQL is source of truth.
-   Migrations must be reversible where practical.
-   Add indexes intentionally.
-   Avoid N+1 queries.
-   Use transactions for multi-record invariants.
-   Store large artifacts in object storage.
-   Do not put raw unbounded logs in relational rows.
-   Tenant ownership must be explicit on tenant-scoped records.

## Security Standards

-   Secrets only through approved secret/config systems.
-   No secrets in source, fixtures, screenshots, logs, or prompts.
-   Verify webhook signatures.
-   Use least privilege.
-   Treat repository data as untrusted.
-   Sanitize filenames/paths.
-   Prevent traversal and symlink escapes.
-   Use short-lived credentials.
-   Redact sensitive values in logs.
-   Never mount `/var/run/docker.sock` into agent workloads.

## Logging

Use structured logs.

Include when available: - trace ID; - project ID; - task ID; - incident
ID; - workflow ID; - agent run ID; - sandbox ID.

Do not log: - API keys; - auth tokens; - cookies; - full sensitive
webhook payloads; - secret environment variables.

## Errors

Errors must answer: 1. What failed? 2. Where? 3. Is it retryable? 4.
What correlation ID identifies it?

Separate: - validation error; - policy violation; - transient provider
error; - permanent provider error; - agent failure; - sandbox failure; -
budget exceeded; - user cancellation.

## Testing

### Backend

-   unit tests for deterministic domain logic;
-   integration tests for DB/workflows/adapters;
-   contract tests for provider payloads.

### Frontend

-   component tests for behavior;
-   e2e tests for critical workflows.

### Agent System

Maintain benchmark fixture repositories with known expected outcomes.

### Guardian

Use fault injection and incident fixtures.

Tests must not depend on arbitrary sleep durations where event
synchronization is possible.

## Pull Request Quality

Each PR should: - solve one coherent problem; - contain focused
changes; - include tests; - avoid unrelated formatting churn; - describe
risk; - document migrations/config changes; - provide verification
commands.

## Dependency Rules

Before adding a dependency: - confirm existing stack cannot reasonably
solve it; - check maintenance/activity; - check license; - check
security posture; - pin appropriately; - document why it exists.

## Configuration

-   typed configuration validation;
-   `.env.example` contains fake values only;
-   no secret values in `NEXT_PUBLIC_*`;
-   fail fast when required server configuration is missing.

## Formatting / Tooling

Recommended baseline:

Frontend: - ESLint - Prettier - TypeScript - Vitest - Playwright

Backend: - Ruff - mypy or Pyright - pytest

Security: - Semgrep - Trivy - secret scanning - package-manager audit
tools

## Documentation

Update documentation when changing: - architecture; - public APIs; -
configuration; - setup; - deployment; - workflow behavior; - project
rules.

Important architectural decisions should receive an ADR.

## Forbidden Shortcuts

Do not: - comment out failing tests; - add `@ts-ignore` as a default
fix; - add broad lint disables; - catch and ignore exceptions; -
hard-code fake success responses; - claim functionality is implemented
when only UI exists; - bypass authorization for convenience; - disable
TLS/certificate checks; - expose internal admin endpoints publicly.

## Definition of Code Complete

Code is complete only when:
`implementation + tests + validation + security considerations + documentation + tracking`
are complete.
