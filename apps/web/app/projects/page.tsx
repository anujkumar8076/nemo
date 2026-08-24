import { randomUUID } from "node:crypto";

import Link from "next/link";

import { ProjectForm } from "../../components/project-form";
import { StatusBadge } from "../../components/status-badge";
import { loadProjects } from "../../lib/api";

export const dynamic = "force-dynamic";

export default async function ProjectsPage() {
  const projects = await loadProjects();
  return (
    <>
      <section className="page-heading"><div><p className="eyebrow">WORKSPACES</p><h1>Projects</h1><p>Durable boundaries for repositories, rules, tasks, and audit history.</p></div></section>
      <section className="panel">
        <div className="panel-header"><h2>All projects</h2><span className="count">{projects.items.length}</span></div>
        {projects.items.length ? <ul className="record-list">{projects.items.map((project) => (
          <li key={project.id}><div><Link href={`/projects/${project.id}`}>{project.name}</Link><p>{project.description ?? "No description"}</p><code>{project.slug}</code></div><StatusBadge status={project.status} /></li>
        ))}</ul> : <div className="empty-state"><h3>No projects yet</h3><p>The first project creates the tenant-scoped boundary for future automation.</p></div>}
      </section>
      <section className="panel form-panel" id="new-project" aria-labelledby="new-project-title"><p className="eyebrow">CREATE</p><h2 id="new-project-title">New project</h2><ProjectForm clientRequestId={randomUUID()} /></section>
    </>
  );
}
