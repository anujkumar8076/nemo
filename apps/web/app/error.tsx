"use client";

export default function ErrorPage({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return <section className="panel error-state"><p className="eyebrow">UNAVAILABLE</p><h1>We could not load this view</h1><p>The control plane did not return usable data. No action was taken.</p><button className="button" onClick={reset} type="button">Try again</button></section>;
}
