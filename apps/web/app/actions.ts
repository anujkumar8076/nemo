"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { ApiRequestError, cancelTask, createProject, createTask } from "../lib/api";

export interface ActionState {
  error: string | null;
}

function requiredText(formData: FormData, key: string, maxLength: number): string {
  const value = formData.get(key);
  if (typeof value !== "string" || value.trim().length === 0) {
    throw new Error(`${key} is required.`);
  }
  const normalized = value.trim();
  if (normalized.length > maxLength) throw new Error(`${key} is too long.`);
  return normalized;
}

function actionError(error: unknown): ActionState {
  if (error instanceof ApiRequestError) {
    return { error: `${error.message} Reference: ${error.correlationId ?? "unavailable"}` };
  }
  return { error: error instanceof Error ? error.message : "The request could not be completed." };
}

export async function createProjectAction(
  _state: ActionState,
  formData: FormData,
): Promise<ActionState> {
  let projectId: string;
  try {
    const name = requiredText(formData, "name", 120);
    const slug = requiredText(formData, "slug", 63);
    const clientRequestId = requiredText(formData, "clientRequestId", 36);
    if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)) {
      throw new Error("slug must use lowercase letters, numbers, and single hyphens.");
    }
    const rawDescription = formData.get("description");
    const description = typeof rawDescription === "string" && rawDescription.trim()
      ? rawDescription.trim()
      : null;
    if (description && description.length > 5000) throw new Error("description is too long.");
    projectId = (await createProject({ clientRequestId, name, slug, description })).id;
  } catch (error: unknown) {
    return actionError(error);
  }
  revalidatePath("/");
  revalidatePath("/projects");
  redirect(`/projects/${projectId}`);
}

export async function createTaskAction(
  _state: ActionState,
  formData: FormData,
): Promise<ActionState> {
  let taskId: string;
  try {
    const projectId = requiredText(formData, "projectId", 36);
    const clientRequestId = requiredText(formData, "clientRequestId", 36);
    const title = requiredText(formData, "title", 200);
    const description = requiredText(formData, "description", 20_000);
    taskId = (await createTask(projectId, { clientRequestId, title, description })).id;
  } catch (error: unknown) {
    return actionError(error);
  }
  revalidatePath(`/projects/${String(formData.get("projectId"))}`);
  redirect(`/tasks/${taskId}`);
}

export async function cancelTaskAction(
  _state: ActionState,
  formData: FormData,
): Promise<ActionState> {
  let taskId: string;
  try {
    taskId = requiredText(formData, "taskId", 36);
    await cancelTask(taskId);
  } catch (error: unknown) {
    return actionError(error);
  }
  revalidatePath(`/tasks/${taskId}`);
  return { error: null };
}
