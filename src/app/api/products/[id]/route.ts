import { NextRequest, NextResponse } from 'next/server'
import { getProductDetail } from '@/lib/catalog'

export async function GET(
  req: NextRequest,
  ctx: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await ctx.params
    const result = await getProductDetail(id)
    if (!result) return NextResponse.json({ error: 'not_found' }, { status: 404 })
    return NextResponse.json(result)
  } catch (e) {
    console.error('product error', e)
    return NextResponse.json({ error: 'server_error' }, { status: 500 })
  }
}
