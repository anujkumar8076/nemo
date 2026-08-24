# ADR-0004: GitHub App authentication

- Status: Accepted
- Date: 2026-08-24

## Decision

Integrate GitHub through a least-privilege GitHub App and short-lived installation
tokens. Coding agents never receive the App private key.

## Consequences

Webhooks require signature verification, delivery deduplication, persistence,
and replay controls. The control plane owns remote mutations.
