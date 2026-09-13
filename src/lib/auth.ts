import { db } from '@/lib/db'
import { cookies } from 'next/headers'
import { scryptSync, randomBytes, timingSafeEqual, randomUUID } from 'crypto'

export function hashPassword(password: string): string {
  const salt = randomBytes(16).toString('hex')
  const hash = scryptSync(password, salt, 64).toString('hex')
  return `${salt}:${hash}`
}

export function verifyPassword(password: string, stored: string): boolean {
  try {
    const [salt, hash] = stored.split(':')
    const derived = scryptSync(password, salt, 64)
    return timingSafeEqual(Buffer.from(hash, 'hex'), derived)
  } catch {
    return false
  }
}

export async function createSession(userId: string) {
  const token = `${randomUUID()}${randomUUID()}`.replace(/-/g, '')
  const expiresAt = new Date(Date.now() + 1000 * 60 * 60 * 24 * 30) // 30 days
  await db.session.create({ data: { token, userId, expiresAt } })
  const jar = await cookies()
  jar.set('tp_session', token, {
    httpOnly: true, sameSite: 'lax', path: '/', expires: expiresAt,
  })
  return token
}

export async function destroySession() {
  const jar = await cookies()
  const token = jar.get('tp_session')?.value
  if (token) await db.session.deleteMany({ where: { token } })
  jar.delete('tp_session')
}

export async function getCurrentUser() {
  const jar = await cookies()
  const token = jar.get('tp_session')?.value
  if (!token) return null
  const session = await db.session.findUnique({
    where: { token },
    include: { user: true },
  })
  if (!session || session.expiresAt < new Date()) return null
  return session.user
}
