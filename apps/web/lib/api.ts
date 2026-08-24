import { isApiHealth, type ApiHealth } from "@autodev/contracts";

import { getServerEnvironment } from "./environment";

export interface HealthResult {
  health: ApiHealth | null;
  error: string | null;
}

export async function loadApiHealth(): Promise<HealthResult> {
  const { apiInternalUrl } = getServerEnvironment();
  try {
    const response = await fetch(`${apiInternalUrl}/health/ready`, {
      cache: "no-store",
      signal: AbortSignal.timeout(2500),
    });
    const value: unknown = await response.json();
    if (!isApiHealth(value)) return { health: null, error: "Invalid API response" };
    return { health: value, error: response.ok ? null : "Dependencies are unavailable" };
  } catch (error: unknown) {
    const detail = error instanceof Error ? error.name : "UnknownError";
    return { health: null, error: `API unavailable (${detail})` };
  }
}
