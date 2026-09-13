import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { getCurrentUser } from '@/lib/auth'

export async function GET(_req: NextRequest, ctx: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await ctx.params
    const order = await db.order.findFirst({
      where: { OR: [{ id }, { orderNumber: id }] },
      include: { items: true },
    })
    if (!order) return NextResponse.json({ error: 'not_found' }, { status: 404 })
    // guests can only see orders by orderNumber (random), users must own the order or be admin
    const user = await getCurrentUser()
    const isOwner = user && (order.userId === user.id || user.isAdmin)
    const byRandomNumber = id === order.orderNumber
    if (!isOwner && !byRandomNumber) {
      return NextResponse.json({ error: 'forbidden' }, { status: 403 })
    }
    return NextResponse.json({ order })
  } catch (e) {
    console.error('order get error', e)
    return NextResponse.json({ error: 'server_error' }, { status: 500 })
  }
}
