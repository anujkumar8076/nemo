# GitHub provider package

Phase 2 will implement the `SourceControlProvider` boundary, signed webhook
normalization, and short-lived GitHub App installation-token service here.
Agents must not receive GitHub App private keys.

The first Phase 2 slice is implemented in the FastAPI control plane because it
owns inbound trust verification and durable delivery persistence. This package
remains reserved for provider-neutral TypeScript contracts; it must never
become a client-side credential holder.
