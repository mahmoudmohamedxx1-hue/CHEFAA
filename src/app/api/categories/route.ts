import { NextResponse } from 'next/server'
import { db } from '@/lib/db'

export async function GET() {
  try {
    const cats = await db.category.findMany({
      orderBy: { sortOrder: 'asc' },
      include: { _count: { select: { products: true } } },
    })

    // cover image: the most popular in-stock product with a real photo in each category
    const covers = await db.product.findMany({
      where: { imageUrl: { not: '' }, stock: { gt: 0 } },
      orderBy: [{ isFeatured: 'desc' }, { popularity: 'desc' }],
      select: { categoryId: true, imageUrl: true, slug: true },
    })
    const coverByCat = new Map<string, string>()
    for (const p of covers) {
      if (!coverByCat.has(p.categoryId)) coverByCat.set(p.categoryId, p.imageUrl)
    }

    return NextResponse.json({
      categories: cats.map((c) => ({
        id: c.id, slug: c.slug, nameEn: c.nameEn, nameAr: c.nameAr,
        descEn: c.descEn, descAr: c.descAr, icon: c.icon,
        productCount: c._count.products,
        coverImage: coverByCat.get(c.id) || '',
      })),
    })
  } catch (e) {
    console.error('categories error', e)
    return NextResponse.json({ error: 'server_error' }, { status: 500 })
  }
}
