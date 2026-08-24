import { describe, expect, it } from "vitest";

import { isGitHubInstallationPage, isGitHubRepositoryPage } from "../src/github";
import { isProjectPage } from "../src/platform";

describe("platform contracts", () => {
  it("rejects malformed project pages at the service boundary", () => {
    expect(isProjectPage({ items: [{ id: "only-an-id" }], next_cursor: null })).toBe(false);
  });

  it("validates GitHub inventory pages without trusting malformed provider data", () => {
    const installation = {
      id: "installation-id",
      external_id: 123,
      account_external_id: 456,
      account_login: "octo-org",
      account_type: "Organization",
      repository_selection: "selected",
      permissions: { metadata: "read" },
      status: "active",
      suspended_at: null,
      last_synced_at: "2026-08-24T12:00:00Z",
      created_at: "2026-08-24T11:00:00Z",
      updated_at: "2026-08-24T12:00:00Z",
    };
    expect(isGitHubInstallationPage({ items: [installation], next_cursor: null })).toBe(true);
    expect(
      isGitHubInstallationPage({
        items: [{ ...installation, status: "unknown" }],
        next_cursor: null,
      }),
    ).toBe(false);

    const repository = {
      id: "repository-id",
      installation_id: "installation-id",
      external_id: 789,
      owner: "octo-org",
      name: "nemo",
      full_name: "octo-org/nemo",
      private: true,
      default_branch: "main",
      html_url: "https://github.com/octo-org/nemo",
      archived: false,
      disabled: false,
      available: true,
      last_seen_at: "2026-08-24T12:00:00Z",
      removed_at: null,
      created_at: "2026-08-24T11:00:00Z",
      updated_at: "2026-08-24T12:00:00Z",
    };
    expect(isGitHubRepositoryPage({ items: [repository], next_cursor: null })).toBe(true);
    expect(
      isGitHubRepositoryPage({
        items: [{ ...repository, private: "yes" }],
        next_cursor: null,
      }),
    ).toBe(false);
  });
});
