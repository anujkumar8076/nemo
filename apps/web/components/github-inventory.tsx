import type { GitHubInstallationPage, GitHubRepositoryPage } from "@autodev/contracts";
import React from "react";

import { StatusBadge } from "./status-badge";

interface GitHubInventoryProps {
  installations: GitHubInstallationPage | null;
  repositories: GitHubRepositoryPage | null;
  installationsError: boolean;
  repositoriesError: boolean;
}

function formattedTime(value: string | null): string {
  if (value === null) return "Never synchronized";
  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "UTC",
  }).format(new Date(value));
}

export function GitHubInventory({
  installations,
  repositories,
  installationsError,
  repositoriesError,
}: GitHubInventoryProps) {
  if (installationsError || installations === null) {
    return (
      <section className="panel error-state" role="alert">
        <p className="eyebrow">GITHUB · UNAVAILABLE</p>
        <h2>Repository connection state could not be loaded</h2>
        <p>The control plane returned no usable installation data. No action was taken.</p>
      </section>
    );
  }

  return (
    <section className="integration-stack" aria-labelledby="github-integration-title">
      <section className="panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">SOURCE CONTROL</p>
            <h2 id="github-integration-title">GitHub App</h2>
          </div>
          <span className="count">{installations.items.length} installations</span>
        </div>
        {installations.items.length === 0 ? (
          <div className="empty-state">
            <h3>GitHub is not connected</h3>
            <p>
              Installation remains unavailable until the control plane can verify GitHub identity
              and bind the installation to this workspace safely.
            </p>
          </div>
        ) : (
          <ul className="record-list">
            {installations.items.map((installation) => (
              <li key={installation.id}>
                <div>
                  <strong>{installation.account_login}</strong>
                  <p>
                    {installation.account_type} · {installation.repository_selection} repositories
                  </p>
                  <code>Last synchronized: {formattedTime(installation.last_synced_at)} UTC</code>
                </div>
                <StatusBadge status={installation.status} />
              </li>
            ))}
          </ul>
        )}
        {installations.next_cursor !== null ? (
          <p className="notice" role="status">Showing the first 100 installations.</p>
        ) : null}
      </section>

      {installations.items.length > 0 ? (
        <section className="panel" aria-labelledby="repository-inventory-title">
          <div className="panel-header">
            <div>
              <p className="eyebrow">AVAILABLE TO THE APP</p>
              <h2 id="repository-inventory-title">Repository inventory</h2>
            </div>
            <span className="count">{repositories?.items.length ?? 0} repositories</span>
          </div>
          {repositoriesError || repositories === null ? (
            <p className="notice" role="status">
              Installations loaded, but repository inventory is temporarily unavailable.
            </p>
          ) : repositories.items.length === 0 ? (
            <div className="empty-state">
              <h3>No repositories are currently available</h3>
              <p>GitHub may not have synchronized yet, or access has been removed.</p>
            </div>
          ) : (
            <ul className="record-list">
              {repositories.items.map((repository) => (
                <li key={repository.id}>
                  <div>
                    <strong>{repository.full_name}</strong>
                    <p>
                      {repository.private ? "Private" : "Public"} · default branch {repository.default_branch}
                      {repository.archived ? " · Archived" : ""}
                      {repository.disabled ? " · Disabled" : ""}
                    </p>
                    <code>Observed {formattedTime(repository.last_seen_at)} UTC</code>
                  </div>
                  <span className="badge badge-ok">Available</span>
                </li>
              ))}
            </ul>
          )}
          {repositories !== null && repositories.next_cursor !== null ? (
            <p className="notice" role="status">Showing the first 100 available repositories.</p>
          ) : null}
        </section>
      ) : null}
    </section>
  );
}
