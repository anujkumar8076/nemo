import type { DependencyStatus } from "@autodev/contracts";
import React from "react";

interface ServiceStatusProps {
  name: string;
  status: DependencyStatus;
}

export function ServiceStatus({ name, status }: ServiceStatusProps) {
  const available = status.status === "available";
  return (
    <li className="service-row">
      <span className={`status-dot ${available ? "status-ok" : "status-error"}`} aria-hidden />
      <span className="service-name">{name}</span>
      <span className="service-value">{available ? "Available" : "Unavailable"}</span>
      {status.detail ? <code>{status.detail}</code> : null}
    </li>
  );
}
