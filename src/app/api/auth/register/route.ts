import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { hashPassword, createSession } from '@/lib/auth'

export async function POST(req: NextRequest) {
  try {
    const body = await req.json()
    const { email, password, name, phone } = body || {}
    const cleanEmail = String(email || '').trim().toLowerCase()
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(cleanEmail)) {
      return NextResponse.json({ error: 'invalid_email' }, { status: 400 })
    }
    if (!password || String(password).length < 6) {
      return NextResponse.json({ error: 'weak_password' }, { status: 400 })
    }
    const exists = await db.user.findUnique({ where: { email: cleanEmail } })
    if (exists) {
      return NextResponse.json({ error: 'email_taken' }, { status: 409 })
    }
    const user = await db.user.create({
      data: {
        email: cleanEmail,
        passwordHash: hashPassword(String(password)),
        name: String(name || '').trim() || null,
        phone: String(phone || '').trim() || null,
      },
    })
    await createSession(user.id)
    return NextResponse.json({
      user: { id: user.id, email: user.email, name: user.name, phone: user.phone, isAdmin: user.isAdmin },
    })
  } catch (e) {
    console.error('register error', e)
    return NextResponse.json({ error: 'server_error' }, { status: 500 })
  }
}
