import { NextResponse } from 'next/server'
import { getCategories } from '@/lib/catalog'

export async function GET() {
  try {
    const categories = await getCategories()
    return NextResponse.json({ categories })
  } catch (e) {
    console.error('categories error', e)
    return NextResponse.json({ error: 'server_error' }, { status: 500 })
  }
}
