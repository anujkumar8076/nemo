# ADR-0008: Provider adapter interfaces

- Status: Accepted
- Date: 2026-08-24

## Decision

Keep source control, deployment, monitoring, model, sandbox, storage, and
notification vendors behind internal typed interfaces.

## Consequences

GitHub and Vercel are initial providers, not domain dependencies. Provider
payloads are normalized before durable workflows consume them.
