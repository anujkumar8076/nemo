import type { ProjectStatus, TaskStatus } from "@autodev/contracts";
import React from "react";

const labels: Record<ProjectStatus | TaskStatus, string> = {
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
};

export function StatusBadge({ status }: { status: ProjectStatus | TaskStatus }) {
  const tone = status === "completed" || status === "active"
    ? "badge-ok"
    : status === "failed"
      ? "badge-danger"
      : status === "archived" || status === "cancelled"
        ? "badge-neutral"
        : "badge-info";
  return <span className={`badge ${tone}`}>{labels[status]}</span>;
}
