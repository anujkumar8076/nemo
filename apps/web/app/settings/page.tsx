export default function SettingsPage() {
  return (
    <><section className="page-heading"><div><p className="eyebrow">ADMINISTRATION</p><h1>Settings</h1><p>Security-sensitive integrations remain unavailable until their documented phases.</p></div></section><section className="panel"><h2>Development authentication</h2><div className="policy-note"><strong>Bootstrap mode is active</strong><p>This local-only identity mechanism is rejected by the API in production. A production authentication provider remains an explicit open decision.</p></div></section></>
  );
}
