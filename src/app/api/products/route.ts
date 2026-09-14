import { NextRequest, NextResponse } from 'next/server'
import { getProducts } from '@/lib/catalog'

export async function GET(req: NextRequest) {
  try {
    const sp = req.nextUrl.searchParams
    const num = (v: string | null) => (v ? Number(v) : undefined)

    const result = await getProducts({
      category: sp.get('category') || undefined,
      q: (sp.get('q') || '').trim(),
      sort: sp.get('sort') || undefined,
      min: num(sp.get('min')),
      max: num(sp.get('max')),
      brand: sp.get('brand') || undefined,
      rx: (sp.get('rx') as 'true' | 'false' | null) || undefined,
      inStock: sp.get('inStock') === 'true',
      featured: sp.get('featured') === 'true',
      ids: (sp.get('ids') || '').split(',').filter(Boolean),
      page: num(sp.get('page')),
      limit: num(sp.get('limit')),
    })

    return NextResponse.json(result)
  } catch (e) {
    console.error('products error', e)
    return NextResponse.json({ error: 'server_error' }, { status: 500 })
  }
}
