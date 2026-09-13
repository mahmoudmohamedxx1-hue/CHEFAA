import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'

export async function GET(
  req: NextRequest,
  ctx: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await ctx.params
    const product = await db.product.findFirst({
      where: { OR: [{ id }, { slug: id }] },
      include: { category: true },
    })
    if (!product) return NextResponse.json({ error: 'not_found' }, { status: 404 })

    const related = await db.product.findMany({
      where: { categoryId: product.categoryId, id: { not: product.id } },
      orderBy: { popularity: 'desc' }, take: 8,
    })

    return NextResponse.json({ product, related })
  } catch (e) {
    console.error('product error', e)
    return NextResponse.json({ error: 'server_error' }, { status: 500 })
  }
}
