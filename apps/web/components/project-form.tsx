"use client";

import { useActionState } from "react";

import { createProjectAction } from "../app/actions";

export function ProjectForm({ clientRequestId }: { clientRequestId: string }) {
  const [state, action, pending] = useActionState(createProjectAction, { error: null });
  return (
    <form action={action} className="form-stack">
      <input name="clientRequestId" type="hidden" value={clientRequestId} />
      <div className="field-grid">
        <label>Name<input name="name" maxLength={120} required autoComplete="off" /></label>
        <label>Slug<input name="slug" maxLength={63} pattern="[a-z0-9]+(?:-[a-z0-9]+)*" required autoComplete="off" /></label>
      </div>
      <label>Description<textarea name="description" maxLength={5000} rows={4} /></label>
      {state.error ? <p className="form-error" role="alert">{state.error}</p> : null}
      <button className="button button-primary" disabled={pending} type="submit">
        {pending ? "Creating…" : "Create project"}
      </button>
    </form>
  );
}
