import { ServiceStatus } from "../components/service-status";
import { loadApiHealth } from "../lib/api";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const result = await loadApiHealth();
  const dependencies = Object.entries(result.health?.dependencies ?? {});
  const ready = result.health?.status === "healthy" && !result.error;

  return (
    <main>
      <header className="topbar">
        <div className="brand">Autonomous Dev Team</div>
        <span className="phase">Foundation · Phase 0</span>
      </header>
      <section className="hero" aria-labelledby="page-title">
        <p className="eyebrow">CONTROL PLANE</p>
        <h1 id="page-title">Build safely. Verify everything.</h1>
        <p className="lede">
          The platform foundation is being established. Production mutations and automatic
          merges remain disabled by policy.
        </p>
      </section>
      <section className="panel" aria-labelledby="status-title">
        <div className="panel-header">
          <div>
            <p className="eyebrow">SYSTEM STATUS</p>
            <h2 id="status-title">Local control plane</h2>
          </div>
          <span className={`badge ${ready ? "badge-ok" : "badge-warning"}`}>
            {ready ? "Ready" : "Not ready"}
          </span>
        </div>
        {result.error ? <p className="notice" role="status">{result.error}</p> : null}
        {dependencies.length ? (
          <ul className="service-list">
            {dependencies.map(([name, status]) => (
              <ServiceStatus key={name} name={name} status={status} />
            ))}
          </ul>
        ) : (
          <p className="empty">No dependency status is available yet.</p>
        )}
      </section>
      <section className="principles" aria-label="Platform guarantees">
        <article><strong>Human-controlled</strong><span>No production merge by default</span></article>
        <article><strong>Evidence-first</strong><span>Tests and audit data over AI theater</span></article>
        <article><strong>Isolated</strong><span>Untrusted code stays outside the control plane</span></article>
      </section>
    </main>
  );
}
