"use client";

import { useActionState } from "react";

import { cancelTaskAction } from "../app/actions";

export function CancelTaskForm({ taskId }: { taskId: string }) {
  const [state, action, pending] = useActionState(cancelTaskAction, { error: null });
  return (
    <form action={action}>
      <input name="taskId" type="hidden" value={taskId} />
      {state.error ? <p className="form-error" role="alert">{state.error}</p> : null}
      <button className="button button-danger" disabled={pending} type="submit">
        {pending ? "Cancelling…" : "Cancel task"}
      </button>
    </form>
  );
}
