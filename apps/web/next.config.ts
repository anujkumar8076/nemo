import type { NextConfig } from "next";

const standaloneOutput = process.env.AUTODEV_STANDALONE === "true";

const nextConfig: NextConfig = {
  ...(standaloneOutput ? { output: "standalone" as const } : {}),
  poweredByHeader: false,
  reactStrictMode: true,
  transpilePackages: ["@autodev/contracts"],
};

export default nextConfig;
