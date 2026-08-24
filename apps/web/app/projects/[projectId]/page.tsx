import { randomUUID } from "node:crypto";

import Link from "next/link";

import { StatusBadge } from "../../../components/status-badge";
import { TaskForm } from "../../../components/task-form";
import { loadActivity, loadProject } from "../../../lib/api";

export const dynamic = "force-dynamic";

const eventLabels: Record<string, string> = {
  "project.created": "Project created",
  "project.updated": "Project settings updated",
  "task.created": "Task created",
  "task.cancelled": "Task cancelled",
};

export default async function ProjectPage({ params }: { params: Promise<{ projectId: string }> }) {
  const { projectId } = await params;
  const [project, activity] = await Promise.all([loadProject(projectId), loadActivity(projectId)]);
  return (
    <>
      <Link className="back-link" href="/projects">← Projects</Link>
      <section className="page-heading"><div><p className="eyebrow">PROJECT</p><h1>{project.name}</h1><p>{project.description ?? "No description provided."}</p></div><StatusBadge status={project.status} /></section>
      <section className="detail-grid" aria-label="Project details">
        <div><span>Slug</span><code>{project.slug}</code></div><div><span>Version</span><strong>{project.version}</strong></div><div><span>Repository</span><strong>Not connected</strong></div><div><span>Created</span><time dateTime={project.created_at}>{new Date(project.created_at).toLocaleString()}</time></div>
      </section>
      <div className="two-column wide-left">
        <section className="panel" aria-labelledby="activity-title"><div className="panel-header"><div><p className="eyebrow">AUDIT</p><h2 id="activity-title">Recent activity</h2></div></div>
          {activity.items.length ? <ol className="timeline">{activity.items.map((event) => (
            <li key={event.id}><span className="timeline-marker" aria-hidden="true" /><div><strong>{eventLabels[event.event_type] ?? event.event_type}</strong><time dateTime={event.created_at}>{new Date(event.created_at).toLocaleString()}</time>{event.task_id ? <Link href={`/tasks/${event.task_id}`}>View task</Link> : null}</div></li>
          ))}</ol> : <div className="empty-state"><h3>No activity recorded</h3><p>Auditable project and task changes will appear here.</p></div>}
        </section>
        <section className="panel form-panel" aria-labelledby="new-task-title"><p className="eyebrow">BUILD MODE</p><h2 id="new-task-title">New task</h2><TaskForm projectId={project.id} clientRequestId={randomUUID()} /></section>
      </div>
    </>
  );
}
