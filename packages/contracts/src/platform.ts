export type ProjectStatus = "active" | "archived";
export type TaskStatus =
  | "queued"
  | "planning"
  | "awaiting_approval"
  | "running"
  | "validating"
  | "completed"
  | "failed"
  | "cancelled";

export interface Project {
  id: string;
  organization_id: string;
  client_request_id: string;
  name: string;
  slug: string;
  description: string | null;
  status: ProjectStatus;
  version: number;
  created_by_user_id: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectPage {
  items: Project[];
  next_cursor: string | null;
}

export interface Task {
  id: string;
  organization_id: string;
  project_id: string;
  client_request_id: string;
  title: string;
  description: string;
  mode: "build" | "guardian";
  status: TaskStatus;
  created_by_user_id: string;
  cancelled_by_user_id: string | null;
  cancelled_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface AuditEvent {
  id: string;
  organization_id: string;
  project_id: string;
  task_id: string | null;
  actor_user_id: string | null;
  event_type: string;
  entity_type: string;
  entity_id: string;
  schema_version: number;
  details: Record<string, unknown>;
  created_at: string;
}

export interface ActivityPage {
  items: AuditEvent[];
  next_cursor: string | null;
}

export interface ApiErrorEnvelope {
  error: {
    code: string;
    message: string;
    correlation_id: string;
    details?: unknown;
  };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isNullableString(value: unknown): value is string | null {
  return typeof value === "string" || value === null;
}

export function isProject(value: unknown): value is Project {
  if (!isRecord(value)) return false;
  return (
    typeof value.id === "string" &&
    typeof value.organization_id === "string" &&
    typeof value.client_request_id === "string" &&
    typeof value.name === "string" &&
    typeof value.slug === "string" &&
    isNullableString(value.description) &&
    (value.status === "active" || value.status === "archived") &&
    typeof value.version === "number" &&
    typeof value.created_by_user_id === "string" &&
    typeof value.created_at === "string" &&
    typeof value.updated_at === "string"
  );
}

export function isProjectPage(value: unknown): value is ProjectPage {
  return (
    isRecord(value) &&
    Array.isArray(value.items) &&
    value.items.every(isProject) &&
    isNullableString(value.next_cursor)
  );
}

export function isTask(value: unknown): value is Task {
  if (!isRecord(value)) return false;
  const statuses: readonly unknown[] = [
    "queued",
    "planning",
    "awaiting_approval",
    "running",
    "validating",
    "completed",
    "failed",
    "cancelled",
  ];
  return (
    typeof value.id === "string" &&
    typeof value.organization_id === "string" &&
    typeof value.project_id === "string" &&
    typeof value.client_request_id === "string" &&
    typeof value.title === "string" &&
    typeof value.description === "string" &&
    (value.mode === "build" || value.mode === "guardian") &&
    statuses.includes(value.status) &&
    typeof value.created_by_user_id === "string" &&
    isNullableString(value.cancelled_by_user_id) &&
    isNullableString(value.cancelled_at) &&
    typeof value.created_at === "string" &&
    typeof value.updated_at === "string"
  );
}

export function isActivityPage(value: unknown): value is ActivityPage {
  return (
    isRecord(value) &&
    Array.isArray(value.items) &&
    value.items.every(
      (item) =>
        isRecord(item) &&
        typeof item.id === "string" &&
        typeof item.event_type === "string" &&
        typeof item.entity_type === "string" &&
        typeof item.entity_id === "string" &&
        typeof item.created_at === "string" &&
        isRecord(item.details),
    ) &&
    isNullableString(value.next_cursor)
  );
}

export function isApiErrorEnvelope(value: unknown): value is ApiErrorEnvelope {
  return (
    isRecord(value) &&
    isRecord(value.error) &&
    typeof value.error.code === "string" &&
    typeof value.error.message === "string" &&
    typeof value.error.correlation_id === "string"
  );
}
