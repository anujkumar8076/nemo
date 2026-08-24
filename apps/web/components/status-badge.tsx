import type { GitHubInstallationStatus, ProjectStatus, TaskStatus } from "@autodev/contracts";
import React from "react";

const labels: Record<ProjectStatus | TaskStatus | GitHubInstallationStatus, string> = {
  active: "Active",
  archived: "Archived",
  queued: "Queued",
  planning: "Planning",
  awaiting_approval: "Waiting for approval",
  running: "Executing",
  validating: "Testing",
  completed: "Completed",
  failed: "Failed",
  cancelled: "Cancelled",
  suspended: "Suspended",
  revoked: "Revoked",
};

export function StatusBadge({ status }: { status: ProjectStatus | TaskStatus | GitHubInstallationStatus }) {
  const tone = status === "completed" || status === "active"
    ? "badge-ok"
    : status === "failed" || status === "revoked"
      ? "badge-danger"
      : status === "archived" || status === "cancelled" || status === "suspended"
        ? "badge-neutral"
        : "badge-info";
  return <span className={`badge ${tone}`}>{labels[status]}</span>;
}
