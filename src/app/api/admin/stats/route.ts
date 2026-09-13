import { NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { getCurrentUser } from '@/lib/auth'

export async function GET() {
  const user = await getCurrentUser()
  if (!user?.isAdmin) return NextResponse.json({ error: 'forbidden' }, { status: 403 })
  try {
    const [products, lowStock, orders, users, prescriptions, revenueAgg, statusAgg, topProducts] = await Promise.all([
      db.product.count(),
      db.product.count({ where: { stock: { lte: 10 } } }),
      db.order.count(),
      db.user.count({ where: { isAdmin: false } }),
      db.prescription.count(),
      db.order.aggregate({ _sum: { total: true }, where: { status: { not: 'cancelled' } } }),
      db.order.groupBy({ by: ['status'], _count: { _all: true } }),
      db.orderItem.groupBy({
        by: ['nameEn', 'nameAr'], _sum: { quantity: true },
        orderBy: { _sum: { quantity: 'desc' } }, take: 5,
      }),
    ])
    return NextResponse.json({
      stats: {
        products, lowStock, orders, users, prescriptions,
        revenue: revenueAgg._sum.total || 0,
        statusCounts: Object.fromEntries(statusAgg.map((s) => [s.status, s._count._all])),
      },
      topProducts: topProducts.map((t) => ({ nameEn: t.nameEn, nameAr: t.nameAr, qty: t._sum.quantity || 0 })),
    })
  } catch (e) {
    console.error('admin stats error', e)
    return NextResponse.json({ error: 'server_error' }, { status: 500 })
  }
}
