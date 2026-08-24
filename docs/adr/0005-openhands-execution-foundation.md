# ADR-0005: OpenHands execution foundation

- Status: Accepted
- Date: 2026-08-24

## Decision

Evaluate and reuse pinned, license-reviewed OpenHands SDK and Agent Server
components instead of rebuilding terminal and file tooling.

## Consequences

Integration begins after the sandbox boundary exists. OpenHands stays behind an
internal adapter so workflows do not depend on its vendor API.
