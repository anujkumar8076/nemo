import { GitHubInventory } from "../../components/github-inventory";
import { loadGitHubInstallations, loadGitHubRepositories } from "../../lib/api";

export const dynamic = "force-dynamic";

export default async function SettingsPage() {
  const [installationsResult, repositoriesResult] = await Promise.allSettled([
    loadGitHubInstallations(),
    loadGitHubRepositories(),
  ]);

  return (
    <>
      <section className="page-heading">
        <div>
          <p className="eyebrow">ADMINISTRATION</p>
          <h1>Settings</h1>
          <p>Review identity and source-control boundaries for this workspace.</p>
        </div>
      </section>
      <div className="integration-stack">
        <section className="panel">
          <h2>Development authentication</h2>
          <div className="policy-note">
            <strong>Bootstrap mode is active</strong>
            <p>
              This local-only identity mechanism is rejected by the API in production. A production
              authentication provider remains an explicit open decision.
            </p>
          </div>
        </section>
        <GitHubInventory
          installations={installationsResult.status === "fulfilled" ? installationsResult.value : null}
          repositories={repositoriesResult.status === "fulfilled" ? repositoriesResult.value : null}
          installationsError={installationsResult.status === "rejected"}
          repositoriesError={repositoriesResult.status === "rejected"}
        />
      </div>
    </>
  );
}
