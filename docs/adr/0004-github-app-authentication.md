# ADR-0004: GitHub App authentication

- Status: Accepted
- Date: 2026-08-24

## Decision

Integrate GitHub through a least-privilege GitHub App and short-lived installation
tokens. Coding agents never receive the App private key.

## Consequences

Webhooks require signature verification, delivery deduplication, persistence,
and replay controls. The control plane owns remote mutations.

The setup callback's `installation_id` is untrusted. A claim is accepted only
after a one-time state value binds the flow to the initiating tenant/user and a
short-lived GitHub user access token proves that the same installation is
accessible to that GitHub user. Only the state digest and non-secret identity
evidence are stored; user and installation access tokens remain ephemeral.

The user authorization adapter is server-only and disabled by default. It uses
the OAuth code once, validates GitHub's typed responses, follows installation
pagination to an exact ID match, and returns only the non-secret proof required
by the claim service. Public setup and callback routes remain unavailable until
the complete redirect and error-handling boundary is tested.

Reference: [GitHub setup URL security guidance](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/about-the-setup-url).
