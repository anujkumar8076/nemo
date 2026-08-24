# ADR-0003: PostgreSQL is authoritative state

- Status: Accepted
- Date: 2026-08-24

## Decision

Persist product, audit, event, and workflow-linked metadata in PostgreSQL. Use
Redis only for caches, rate limits, short locks, and transient fan-out.

## Consequences

Tenant ownership is explicit in records and queries. Large artifacts belong in
object storage; schema changes use reviewed Alembic migrations.
