# ADR-0001: FastAPI control plane

- Status: Accepted
- Date: 2026-08-24

## Decision

Use Python, FastAPI, Pydantic, SQLAlchemy, and Alembic for the control plane.
Keep routes thin, domain logic in services, persistence behind repositories, and
external inputs validated at the boundary.

## Consequences

This aligns the API with the agent ecosystem and gives explicit typed contracts.
Python dependencies and migrations require a reproducible toolchain.
