import {
  isActivityPage,
  isApiErrorEnvelope,
  isApiHealth,
  isGitHubInstallationPage,
  isGitHubRepositoryPage,
  isProject,
  isProjectPage,
  isTask,
  type ActivityPage,
  type ApiHealth,
  type GitHubInstallationPage,
  type GitHubRepositoryPage,
  type Project,
  type ProjectPage,
  type Task,
} from "@autodev/contracts";

import { getServerEnvironment } from "./environment";

export interface HealthResult {
  health: ApiHealth | null;
  error: string | null;
}

export class ApiRequestError extends Error {
  constructor(
    message: string,
    readonly code: string,
    readonly correlationId: string | null,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiRequestError";
  }
}

type Validator<T> = (value: unknown) => value is T;

async function apiRequest<T>(
  path: string,
  validator: Validator<T>,
  init?: RequestInit,
): Promise<T> {
  const { apiInternalUrl, bootstrapApiToken } = getServerEnvironment();
  const response = await fetch(`${apiInternalUrl}${path}`, {
    ...init,
    cache: "no-store",
    headers: {
      Authorization: `Bearer ${bootstrapApiToken}`,
      ...(init?.body ? { "Content-Type": "application/json" } : {}),
      ...init?.headers,
    },
    signal: AbortSignal.timeout(5000),
  });
  const value: unknown = await response.json();
  if (!response.ok) {
    if (isApiErrorEnvelope(value)) {
      throw new ApiRequestError(
        value.error.message,
        value.error.code,
        value.error.correlation_id,
        response.status,
      );
    }
    throw new ApiRequestError("The API request failed.", "invalid_error_response", null, response.status);
  }
  if (!validator(value)) {
    throw new ApiRequestError("The API returned an invalid response.", "invalid_response", null, 502);
  }
  return value;
}

export async function loadApiHealth(): Promise<HealthResult> {
  const { apiInternalUrl } = getServerEnvironment();
  try {
    const response = await fetch(`${apiInternalUrl}/health/ready`, {
      cache: "no-store",
      signal: AbortSignal.timeout(5000),
    });
    const value: unknown = await response.json();
    if (!isApiHealth(value)) return { health: null, error: "Invalid API response" };
    return { health: value, error: response.ok ? null : "Dependencies are unavailable" };
  } catch (error: unknown) {
    const detail = error instanceof Error ? error.name : "UnknownError";
    return { health: null, error: `API unavailable (${detail})` };
  }
}

export async function loadProjects(): Promise<ProjectPage> {
  return apiRequest("/v1/projects", isProjectPage);
}

export async function loadGitHubInstallations(): Promise<GitHubInstallationPage> {
  return apiRequest("/v1/github/installations?limit=100", isGitHubInstallationPage);
}

export async function loadGitHubRepositories(): Promise<GitHubRepositoryPage> {
  return apiRequest("/v1/github/repositories?limit=100", isGitHubRepositoryPage);
}

export async function loadProject(projectId: string): Promise<Project> {
  return apiRequest(`/v1/projects/${encodeURIComponent(projectId)}`, isProject);
}

export async function loadTask(taskId: string): Promise<Task> {
  return apiRequest(`/v1/tasks/${encodeURIComponent(taskId)}`, isTask);
}

export async function loadActivity(projectId: string): Promise<ActivityPage> {
  return apiRequest(`/v1/projects/${encodeURIComponent(projectId)}/activity`, isActivityPage);
}

export async function createProject(input: {
  clientRequestId: string;
  name: string;
  slug: string;
  description: string | null;
}): Promise<Project> {
  return apiRequest("/v1/projects", isProject, {
    method: "POST",
    body: JSON.stringify({
      client_request_id: input.clientRequestId,
      name: input.name,
      slug: input.slug,
      description: input.description,
    }),
  });
}

export async function createTask(
  projectId: string,
  input: { clientRequestId: string; title: string; description: string },
): Promise<Task> {
  return apiRequest(`/v1/projects/${encodeURIComponent(projectId)}/tasks`, isTask, {
    method: "POST",
    body: JSON.stringify({
      client_request_id: input.clientRequestId,
      title: input.title,
      description: input.description,
    }),
  });
}

export async function cancelTask(taskId: string): Promise<Task> {
  return apiRequest(`/v1/tasks/${encodeURIComponent(taskId)}/cancel`, isTask, { method: "POST" });
}
