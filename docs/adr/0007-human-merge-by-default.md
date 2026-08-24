# ADR-0007: Human merge by default

- Status: Accepted
- Date: 2026-08-24

## Decision

Agents may prepare branches, checks, and pull requests but may not merge protected
branches or mutate production by default. High-risk plans and restricted changes
require durable human approval.

## Consequences

Approval is a first-class audited state. Any future auto-merge is explicit opt-in
policy for narrowly defined low-risk changes.
