# Autonomous Dev Team

Autonomous Dev Team turns engineering tasks and production incidents into
isolated, tested, reviewable GitHub pull requests while preserving human control
over high-risk and production changes.

The product is built in evidence-gated phases. Current progress is recorded in
`progress-tracker.md`.

## Repository

- `apps/web`: Next.js dashboard
- `apps/api`: FastAPI control plane
- `apps/worker`: Temporal worker
- `packages/contracts`: shared public TypeScript contracts
- `packages/github`: source-control provider boundary
- `packages/agent-core`: agent contracts and policies
- `packages/integrations`: deployment and monitoring provider boundaries
- `packages/ui`: shared UI primitives
- `services/sandbox-manager`: isolated execution service (Phase 4)
- `infra/docker`: local development topology
- `docs/adr`: architecture decision records

## Prerequisites

- Node.js 22+
- pnpm 11
- Docker with Compose v2

Python runs inside the API and worker containers in the default workflow.
For host-side Python checks, create and activate Python 3.12 virtual environment,
then install `apps/api[dev]`, `apps/worker[dev]`, and `alembic==1.16.5` as editable
packages. The `.venv` directory is ignored.

## Local development

1. Copy `.env.example` to `.env`.
2. Run `pnpm dev`.
3. Open `http://localhost:3000`, API health at `http://localhost:8000/health`,
   and Temporal UI at `http://localhost:8080`.
4. Stop with `pnpm dev:down`.

Run `pnpm check` for local quality gates and `pnpm security` for dependency
auditing. CI additionally validates Python, migrations, containers, and secrets.
Database integration checks can use `infra/docker/compose.test.yaml`, which
publishes an ephemeral PostgreSQL instance on loopback port 55432 without
changing the development stack.

## Development authentication

Phase 1 uses a server-side bootstrap bearer token to exercise tenant isolation
before the production identity provider is selected. The API creates exactly
one configured development user, organization, and owner membership. The token
is server-only and must never use a `NEXT_PUBLIC_*` name. Bootstrap mode fails
configuration validation when `AUTODEV_ENVIRONMENT=production`; a production
deployment therefore cannot accidentally ship with this temporary auth mode.

All values in `.env.example` are intentionally fake local defaults. Replace the
bootstrap token in any shared development environment.

## GitHub webhook ingress

Phase 2 begins with a disabled-by-default webhook trust boundary at
`POST /webhooks/github`. When enabled, it verifies `X-Hub-Signature-256` over
the untouched request body, accepts only the documented initial event set,
persists the delivery ID and payload digest, and deduplicates redeliveries at
the database constraint. Set a unique `AUTODEV_GITHUB_WEBHOOK_SECRET` of at
least 32 characters in the receiving environment; the example value is fake.

Installation claiming, short-lived installation tokens, repository sync, and
remote repository writes are not enabled by this ingress slice. They require a
real GitHub App and verification against a dedicated test repository.

The control plane contains a server-only GitHub App client for RSA-signed App
JWTs, opaque one-hour installation tokens, paginated repository discovery, and
rate-limit retry signals. Remote actions remain independently disabled through
`AUTODEV_GITHUB_REMOTE_ACTIONS_ENABLED`. Enabling them also requires an App ID
and private key; neither credential is exposed through public API contracts or
passed to agent execution.

Installation claiming now has a durable, tenant/user-bound one-time state
machine, but no public claim action is enabled. Raw state is never stored, setup
identifiers cannot change after first observation, expired/replayed state is
rejected, and completion requires typed proof from the server-only GitHub user
authorization adapter. That adapter exchanges the one-time OAuth code, verifies
the authenticated user and exact accessible installation, and discards the
access token without returning or persisting it. Both user authorization and
the public claim flow remain disabled until explicitly configured and tested
with a real GitHub App.

## Safety defaults

The platform may analyze repositories, modify isolated workspaces, run checks,
and prepare pull requests. It does not auto-merge or directly modify production.
Sandboxes never receive the host Docker socket, control-plane secrets, or
unrestricted production credentials.
