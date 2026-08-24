export interface ServerEnvironment {
  apiInternalUrl: string;
}

export function getServerEnvironment(): ServerEnvironment {
  const rawUrl = process.env.AUTODEV_API_INTERNAL_URL;
  if (!rawUrl) throw new Error("AUTODEV_API_INTERNAL_URL is required");
  const parsed = new URL(rawUrl);
  if (parsed.protocol !== "http:" && parsed.protocol !== "https:") {
    throw new Error("AUTODEV_API_INTERNAL_URL must use http or https");
  }
  return { apiInternalUrl: parsed.origin };
}
