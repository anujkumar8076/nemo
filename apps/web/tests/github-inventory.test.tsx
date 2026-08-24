import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { GitHubInventory } from "../components/github-inventory";

const emptyPage = { items: [], next_cursor: null };

describe("GitHubInventory", () => {
  it("shows a truthful disconnected state without an unsafe install action", () => {
    const markup = renderToStaticMarkup(
      <GitHubInventory
        installations={emptyPage}
        repositories={emptyPage}
        installationsError={false}
        repositoriesError={false}
      />,
    );
    expect(markup).toContain("GitHub is not connected");
    expect(markup).not.toContain("Install GitHub App");
  });

  it("renders provider inventory with text-based status evidence", () => {
    const markup = renderToStaticMarkup(
      <GitHubInventory
        installations={{
          items: [
            {
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
            },
          ],
          next_cursor: null,
        }}
        repositories={{
          items: [
            {
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
            },
          ],
          next_cursor: null,
        }}
        installationsError={false}
        repositoriesError={false}
      />,
    );
    expect(markup).toContain("octo-org/nemo");
    expect(markup).toContain("Active");
    expect(markup).toContain("Available");
    expect(markup).toContain("Private");
  });
});
