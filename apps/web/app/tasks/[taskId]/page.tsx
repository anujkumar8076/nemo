import Link from "next/link";

import { CancelTaskForm } from "../../../components/cancel-task-form";
import { StatusBadge } from "../../../components/status-badge";
import { loadTask } from "../../../lib/api";

export const dynamic = "force-dynamic";

export default async function TaskPage({ params }: { params: Promise<{ taskId: string }> }) {
  const { taskId } = await params;
  const task = await loadTask(taskId);
  const cancellable = !["completed", "failed", "cancelled"].includes(task.status);
  return (
    <>
      <Link className="back-link" href={`/projects/${task.project_id}`}>← Project</Link>
      <section className="page-heading"><div><p className="eyebrow">TASK · {task.id.slice(0, 8)}</p><h1>{task.title}</h1></div><StatusBadge status={task.status} /></section>
      <div className="two-column wide-left">
        <section className="panel"><p className="eyebrow">OBJECTIVE</p><h2>Requested change</h2><p className="task-description">{task.description}</p><div className="policy-note"><strong>Current capability boundary</strong><p>This task is persisted and auditable. Repository analysis and code execution are intentionally unavailable until later safety phases.</p></div></section>
        <aside className="panel"><p className="eyebrow">CONTROL</p><h2>Human controls</h2><dl className="metadata"><div><dt>Mode</dt><dd>{task.mode}</dd></div><div><dt>Created</dt><dd><time dateTime={task.created_at}>{new Date(task.created_at).toLocaleString()}</time></dd></div></dl>{cancellable ? <CancelTaskForm taskId={task.id} /> : <p className="empty">This task is in a terminal state.</p>}</aside>
      </div>
    </>
  );
}
