"use client";

import { useActionState } from "react";

import { createTaskAction } from "../app/actions";

export function TaskForm({ projectId, clientRequestId }: { projectId: string; clientRequestId: string }) {
  const [state, action, pending] = useActionState(createTaskAction, { error: null });
  return (
    <form action={action} className="form-stack">
      <input name="projectId" type="hidden" value={projectId} />
      <input name="clientRequestId" type="hidden" value={clientRequestId} />
      <label>Task title<input name="title" maxLength={200} required autoComplete="off" /></label>
      <label>
        What should the engineering team do?
        <textarea name="description" maxLength={20000} rows={7} required />
      </label>
      <p className="field-help">The task will be queued. No code execution or production mutation occurs in Phase 1.</p>
      {state.error ? <p className="form-error" role="alert">{state.error}</p> : null}
      <button className="button button-primary" disabled={pending} type="submit">
        {pending ? "Creating…" : "Create task"}
      </button>
    </form>
  );
}
