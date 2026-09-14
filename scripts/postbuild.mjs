/**
 * Post-build step for the self-hosted (standalone) flow.
 *
 * `next build` with `output: "standalone"` produces .next/standalone but does
 * NOT copy static assets, public/ or the SQLite catalog into it — the server
 * needs all three at runtime. On Vercel this script is a no-op (Vercel builds
 * its own output format and standalone mode is disabled there).
 */
import { cpSync, existsSync } from "node:fs";
import path from "node:path";

const root = process.cwd();
const standalone = path.join(root, ".next", "standalone");

if (process.env.VERCEL) {
  console.log("postbuild: Vercel detected — skipping standalone packaging");
  process.exit(0);
}

if (!existsSync(standalone)) {
  console.log("postbuild: .next/standalone not found — nothing to package");
  process.exit(0);
}

const copies = [
  [path.join(root, ".next", "static"), path.join(standalone, ".next", "static")],
  [path.join(root, "public"), path.join(standalone, "public")],
  [path.join(root, "db"), path.join(standalone, "db")],
  [path.join(root, "prisma"), path.join(standalone, "prisma")],
];

for (const [from, to] of copies) {
  if (existsSync(from)) {
    cpSync(from, to, { recursive: true });
    console.log(`postbuild: copied ${path.relative(root, from)} -> ${path.relative(root, to)}`);
  }
}

console.log("postbuild: standalone server ready at .next/standalone/server.js");
