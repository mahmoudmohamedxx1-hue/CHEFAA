import type { NextConfig } from "next";

// `output: standalone` is used for self-hosting (VPS/bun). Vercel builds its
// own output format, so standalone mode is disabled there automatically.
const isVercel = Boolean(process.env.VERCEL);

const nextConfig: NextConfig = {
  ...(isVercel ? {} : { output: "standalone" as const }),
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
