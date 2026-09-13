import { NextResponse } from 'next/server'
import { db } from '@/lib/db'

export async function GET() {
  try {
    const cats = await db.category.findMany({
      orderBy: { sortOrder: 'asc' },
      include: { _count: { select: { products: true } } },
    })
    return NextResponse.json({
      categories: cats.map((c) => ({
        id: c.id, slug: c.slug, nameEn: c.nameEn, nameAr: c.nameAr,
        descEn: c.descEn, descAr: c.descAr, icon: c.icon,
        productCount: c._count.products,
      })),
    })
  } catch (e) {
    console.error('categories error', e)
    return NextResponse.json({ error: 'server_error' }, { status: 500 })
  }
}
