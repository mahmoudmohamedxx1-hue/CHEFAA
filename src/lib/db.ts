import path from 'path'
import { PrismaClient } from '@prisma/client'

// Default database location so the app also works when no .env is present
// (e.g. on Vercel, where the seeded db/custom.db is committed to the repo).
// An explicit DATABASE_URL from the environment always wins.
if (!process.env.DATABASE_URL) {
  process.env.DATABASE_URL = `file:${path.join(process.cwd(), 'db', 'custom.db')}`
}

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined
}

export const db =
  globalForPrisma.prisma ??
  new PrismaClient({
    // Query logging is useful locally but far too noisy on hosted platforms
    log: process.env.NODE_ENV === 'production' ? ['error'] : ['query'],
  })

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = db
