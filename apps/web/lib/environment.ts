export interface ServerEnvironment {
  apiInternalUrl: string;
  bootstrapApiToken: string;
}

export function getServerEnvironment(): ServerEnvironment {
  const rawUrl = process.env.AUTODEV_API_INTERNAL_URL;
  if (!rawUrl) throw new Error("AUTODEV_API_INTERNAL_URL is required");
  const parsed = new URL(rawUrl);
  if (parsed.protocol !== "http:" && parsed.protocol !== "https:") {
    throw new Error("AUTODEV_API_INTERNAL_URL must use http or https");
  }
  const bootstrapApiToken = process.env.AUTODEV_BOOTSTRAP_API_TOKEN;
  if (!bootstrapApiToken || bootstrapApiToken.length < 32) {
    throw new Error("AUTODEV_BOOTSTRAP_API_TOKEN must contain at least 32 characters");
  }
  return { apiInternalUrl: parsed.origin, bootstrapApiToken };
}
