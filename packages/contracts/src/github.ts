export type GitHubInstallationStatus = "active" | "suspended" | "revoked";

export interface GitHubInstallation {
  id: string;
  external_id: number;
  account_external_id: number;
  account_login: string;
  account_type: "Organization" | "User";
  repository_selection: "all" | "selected";
  permissions: Record<string, unknown>;
  status: GitHubInstallationStatus;
  suspended_at: string | null;
  last_synced_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface GitHubInstallationPage {
  items: GitHubInstallation[];
  next_cursor: string | null;
}

export interface GitHubRepository {
  id: string;
  installation_id: string;
  external_id: number;
  owner: string;
  name: string;
  full_name: string;
  private: boolean;
  default_branch: string;
  html_url: string;
  archived: boolean;
  disabled: boolean;
  available: boolean;
  last_seen_at: string;
  removed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface GitHubRepositoryPage {
  items: GitHubRepository[];
  next_cursor: string | null;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isNullableString(value: unknown): value is string | null {
  return typeof value === "string" || value === null;
}

export function isGitHubInstallation(value: unknown): value is GitHubInstallation {
  if (!isRecord(value)) return false;
  return (
    typeof value.id === "string" &&
    typeof value.external_id === "number" &&
    typeof value.account_external_id === "number" &&
    typeof value.account_login === "string" &&
    (value.account_type === "Organization" || value.account_type === "User") &&
    (value.repository_selection === "all" || value.repository_selection === "selected") &&
    isRecord(value.permissions) &&
    (value.status === "active" || value.status === "suspended" || value.status === "revoked") &&
    isNullableString(value.suspended_at) &&
    isNullableString(value.last_synced_at) &&
    typeof value.created_at === "string" &&
    typeof value.updated_at === "string"
  );
}

export function isGitHubInstallationPage(value: unknown): value is GitHubInstallationPage {
  return (
    isRecord(value) &&
    Array.isArray(value.items) &&
    value.items.every(isGitHubInstallation) &&
    isNullableString(value.next_cursor)
  );
}

export function isGitHubRepository(value: unknown): value is GitHubRepository {
  if (!isRecord(value)) return false;
  return (
    typeof value.id === "string" &&
    typeof value.installation_id === "string" &&
    typeof value.external_id === "number" &&
    typeof value.owner === "string" &&
    typeof value.name === "string" &&
    typeof value.full_name === "string" &&
    typeof value.private === "boolean" &&
    typeof value.default_branch === "string" &&
    typeof value.html_url === "string" &&
    typeof value.archived === "boolean" &&
    typeof value.disabled === "boolean" &&
    typeof value.available === "boolean" &&
    typeof value.last_seen_at === "string" &&
    isNullableString(value.removed_at) &&
    typeof value.created_at === "string" &&
    typeof value.updated_at === "string"
  );
}

export function isGitHubRepositoryPage(value: unknown): value is GitHubRepositoryPage {
  return (
    isRecord(value) &&
    Array.isArray(value.items) &&
    value.items.every(isGitHubRepository) &&
    isNullableString(value.next_cursor)
  );
}
