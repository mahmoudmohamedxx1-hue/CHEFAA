import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { Prisma } from '@prisma/client'

export async function GET(req: NextRequest) {
  try {
    const sp = req.nextUrl.searchParams
    const category = sp.get('category') || undefined
    const q = (sp.get('q') || '').trim()
    const sort = sp.get('sort') || 'popular'
    const min = sp.get('min') ? Number(sp.get('min')) : undefined
    const max = sp.get('max') ? Number(sp.get('max')) : undefined
    const brand = sp.get('brand') || undefined
    const rx = sp.get('rx') // 'true' | 'false' | undefined
    const inStock = sp.get('inStock') === 'true'
    const featured = sp.get('featured') === 'true'
    const ids = (sp.get('ids') || '').split(',').filter(Boolean)
    const page = Math.max(1, Number(sp.get('page') || 1))
    const limit = Math.min(60, Math.max(1, Number(sp.get('limit') || 24)))

    const where: Prisma.ProductWhereInput = {}
    if (ids.length) where.id = { in: ids }
    if (category) where.category = { slug: category }
    if (featured) where.isFeatured = true
    if (brand) where.brand = { equals: brand }
    if (rx === 'true') where.prescriptionRequired = true
    if (rx === 'false') where.prescriptionRequired = false
    if (inStock) where.stock = { gt: 0 }
    if (min !== undefined || max !== undefined) {
      where.price = {}
      if (min !== undefined && !Number.isNaN(min)) where.price.gte = min
      if (max !== undefined && !Number.isNaN(max)) where.price.lte = max
    }
    if (q) {
      where.OR = [
        { nameEn: { contains: q } },
        { nameAr: { contains: q } },
        { brand: { contains: q } },
        { descEn: { contains: q } },
        { subcategory: { contains: q } },
      ]
    }

    let orderBy: Prisma.ProductOrderByWithRelationInput
    switch (sort) {
      case 'price-asc': orderBy = { price: 'asc' }; break
      case 'price-desc': orderBy = { price: 'desc' }; break
      case 'rating': orderBy = { rating: 'desc' }; break
      case 'newest': orderBy = { createdAt: 'desc' }; break
      default: orderBy = { popularity: 'desc' }
    }

    const [items, total, brandAgg] = await Promise.all([
      db.product.findMany({
        where, orderBy,
        skip: (page - 1) * limit, take: limit,
        include: { category: { select: { slug: true, nameEn: true, nameAr: true } } },
      }),
      db.product.count({ where }),
      db.product.groupBy({
        by: ['brand'], where, _count: { _all: true },
        orderBy: { _count: { brand: 'desc' } }, take: 24,
      }),
    ])

    return NextResponse.json({
      items, total, page, pages: Math.ceil(total / limit) || 1,
      brands: brandAgg.map((b) => ({ brand: b.brand, count: b._count._all })),
    })
  } catch (e) {
    console.error('products error', e)
    return NextResponse.json({ error: 'server_error' }, { status: 500 })
  }
}
