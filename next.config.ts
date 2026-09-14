import type { NextConfig } from "next";

// `output: standalone` is ONLY for self-hosting (VPS / this sandbox's bun
// runtime) and is opt-in via SELF_HOST=1. Vercel, v0 and plain `next start`
// all use the standard build output, which is what those platforms expect.
const isSelfHost = process.env.SELF_HOST === "1";

const nextConfig: NextConfig = {
  ...(isSelfHost ? { output: "standalone" as const } : {}),
  /* config options here */
  typescript: {
    ignoreBuildErrors: true,
  },
  reactStrictMode: false,
  // Ship the committed SQLite catalog + prisma engine inside every serverless
  // function that reads the database (catalog APIs, SSR product pages, sitemap).
  outputFileTracingIncludes: {
    "/api/**/*": ["./db/custom.db", "./node_modules/.prisma/**/*"],
    "/product/[slug]": ["./db/custom.db", "./node_modules/.prisma/**/*"],
    "/category/[slug]": ["./db/custom.db", "./node_modules/.prisma/**/*"],
    "/sitemap.xml": ["./db/custom.db", "./node_modules/.prisma/**/*"],
  },
  async headers() {
    return [
      {
        // The service worker must always be revalidated so updates land quickly
        source: "/sw.js",
        headers: [
          { key: "Cache-Control", value: "no-cache, no-store, must-revalidate" },
          { key: "Service-Worker-Allowed", value: "/" },
        ],
      },
      {
        source: "/manifest.webmanifest",
        headers: [{ key: "Cache-Control", value: "public, max-age=3600" }],
      },
    ];
  },
};

export default nextConfig;
