import type { Metadata } from "next";
import Link from "next/link";
import type { ReactNode } from "react";

import "./styles.css";

export const metadata: Metadata = {
  title: "Autonomous Dev Team",
  description: "Verified autonomous engineering with human production control",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <header className="topbar">
          <Link className="brand" href="/">Autonomous Dev Team</Link>
          <div className="identity" aria-label="Current session">
            <span>Development workspace</span>
            <span className="badge badge-warning">Bootstrap access</span>
          </div>
        </header>
        <div className="app-shell">
          <nav className="sidebar" aria-label="Primary navigation">
            <Link href="/">Overview</Link>
            <Link href="/projects">Projects</Link>
            <span aria-disabled="true">Incidents <small>Later</small></span>
            <span aria-disabled="true">Deployments <small>Later</small></span>
            <span aria-disabled="true">Integrations <small>Phase 2</small></span>
            <Link href="/settings">Settings</Link>
          </nav>
          <main className="content">{children}</main>
        </div>
      </body>
    </html>
  );
}
