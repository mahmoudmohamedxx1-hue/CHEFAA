import { PrismaClient } from "@prisma/client";
import path from "node:path";
import fs from "node:fs";

/**
 * The SQLite catalog lives at <project>/db/custom.db (committed to the repo).
 * Prisma resolves relative `file:` URLs against the process CWD, which breaks
 * in `output: standalone` mode (the server runs from .next/standalone) and in
 * serverless bundles. Probe a few well-known locations and pass an absolute
 * URL via the runtime `datasources` override so every launch mode works:
 * project root, .next/standalone (db copied in by the build script), one or
 * two levels below the root, or derived from the server.js location.
 * An explicit DATABASE_URL from the environment always wins.
 */
function resolveDbUrl(): string {
  if (process.env.DATABASE_URL) return process.env.DATABASE_URL;

  const cwd = process.cwd();
  const argv1 = process.argv[1] ?? "";
  const serverDir = path.dirname(path.resolve(argv1));
  const candidates = [
    path.join(cwd, "db", "custom.db"), // launched from project root
    path.join(cwd, "..", "db", "custom.db"), // launched one level below root
    path.join(cwd, "..", "..", "db", "custom.db"), // launched from .next/standalone
    path.join(serverDir, "..", "..", "db", "custom.db"), // derived from server.js location
  ];
  for (const c of candidates) {
    try {
      if (fs.existsSync(c)) return `file:${c}`;
    } catch {}
  }
  return `file:${candidates[0]}`;
}

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined;
};

export const db =
  globalForPrisma.prisma ??
  new PrismaClient({
    datasources: { db: { url: resolveDbUrl() } },
    // Keep logging minimal — query logging floods dev.log and slows the
    // dev server down with the tee pipeline.
    log: ["error", "warn"],
  });

if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = db;
