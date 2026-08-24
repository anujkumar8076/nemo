import Link from "next/link";

import { ServiceStatus } from "../components/service-status";
import { StatusBadge } from "../components/status-badge";
import { loadApiHealth, loadProjects } from "../lib/api";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const [health, projectsResult] = await Promise.all([loadApiHealth(), loadProjects().catch(() => null)]);
  const dependencies = Object.entries(health.health?.dependencies ?? {});
  const ready = health.health?.status === "healthy" && !health.error;
  const projects = projectsResult?.items ?? [];

  return (
    <>
      <section className="page-heading">
        <div><p className="eyebrow">OVERVIEW</p><h1>Engineering control plane</h1></div>
        <Link className="button button-primary" href="/projects#new-project">New project</Link>
      </section>
      <section className="summary-grid" aria-label="Platform summary">
        <article><span>Projects</span><strong>{projects.length}</strong><small>Persisted workspaces</small></article>
        <article><span>Active runs</span><strong>0</strong><small>Execution starts in Phase 5</small></article>
        <article><span>Production actions</span><strong>Disabled</strong><small>Human control enforced</small></article>
      </section>
      <div className="two-column">
        <section className="panel" aria-labelledby="projects-title">
          <div className="panel-header"><div><p className="eyebrow">PROJECTS</p><h2 id="projects-title">Recent workspaces</h2></div><Link href="/projects">View all</Link></div>
          {!projectsResult ? <p className="notice" role="status">Projects are temporarily unavailable.</p> : projects.length ? (
            <ul className="record-list">
              {projects.slice(0, 5).map((project) => (
                <li key={project.id}><div><Link href={`/projects/${project.id}`}>{project.name}</Link><code>{project.slug}</code></div><StatusBadge status={project.status} /></li>
              ))}
            </ul>
          ) : <div className="empty-state"><h3>No projects yet</h3><p>Create a project to establish a durable workspace for engineering tasks.</p></div>}
        </section>
        <section className="panel" aria-labelledby="status-title">
          <div className="panel-header"><div><p className="eyebrow">SYSTEM STATUS</p><h2 id="status-title">Local services</h2></div><span className={`badge ${ready ? "badge-ok" : "badge-warning"}`}>{ready ? "Ready" : "Not ready"}</span></div>
          {health.error ? <p className="notice" role="status">{health.error}</p> : null}
          {dependencies.length ? <ul className="service-list">{dependencies.map(([name, status]) => <ServiceStatus key={name} name={name} status={status} />)}</ul> : <p className="empty">No dependency status is available.</p>}
        </section>
      </div>
    </>
  );
}
