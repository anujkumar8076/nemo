export type Availability = "available" | "unavailable";

export interface DependencyStatus {
  status: Availability;
  detail?: string | null;
}

export interface ApiHealth {
  service: "api";
  status: "healthy" | "degraded";
  dependencies?: Record<string, DependencyStatus> | null;
}

export function isApiHealth(value: unknown): value is ApiHealth {
  if (typeof value !== "object" || value === null) return false;
  const candidate = value as Record<string, unknown>;
  return (
    candidate.service === "api" &&
    (candidate.status === "healthy" || candidate.status === "degraded")
  );
}
