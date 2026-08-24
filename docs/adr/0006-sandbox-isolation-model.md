# ADR-0006: Sandbox isolation model

- Status: Accepted
- Date: 2026-08-24

## Decision

Use disposable, non-root Docker sandboxes for MVP and Kubernetes workloads with
stronger isolation for production. Deny host filesystem and Docker socket access,
constrain resources and egress, sanitize environments, and support kill.

## Consequences

Trusted API and worker services do not create arbitrary nested containers. A
dedicated sandbox provider and adversarial isolation tests are required.
