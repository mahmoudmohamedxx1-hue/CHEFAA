'use client'
import { useQuery } from '@tanstack/react-query'

export interface Category { slug: string; nameEn: string; nameAr: string; descEn: string; descAr: string; productCount: number }

export interface Product {
  id: string; slug: string; nameEn: string; nameAr: string; brand: string
  descEn: string; descAr: string; price: number; compareAtPrice: number | null
  stock: number; rating: number; reviewCount: number; popularity: number
  prescriptionRequired: boolean; volume: string; subcategory: string
  category: { slug: string; nameEn: string; nameAr: string }
}

export interface ProductsResponse {
  items: Product[]; total: number; page: number; pages: number
  brands: { brand: string; count: number }[]
}

export function useCategories() {
  return useQuery<Category[]>({
    queryKey: ['categories'],
    queryFn: async () => {
      const res = await fetch('/api/categories')
      const d = await res.json()
      return d.categories
    },
    staleTime: 5 * 60 * 1000,
  })
}

export function useProducts(params: Record<string, string | number | undefined>, enabled = true) {
  const qs = new URLSearchParams()
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== '' && v !== null) qs.set(k, String(v))
  })
  return useQuery<ProductsResponse>({
    queryKey: ['products', qs.toString()],
    queryFn: async () => {
      const res = await fetch(`/api/products?${qs.toString()}`)
      return res.json()
    },
    enabled,
  })
}

export function useProduct(idOrSlug: string | undefined) {
  return useQuery<{ product: Product; related: Product[] }>({
    queryKey: ['product', idOrSlug],
    queryFn: async () => {
      const res = await fetch(`/api/products/${idOrSlug}`)
      if (!res.ok) throw new Error('not found')
      return res.json()
    },
    enabled: !!idOrSlug,
  })
}
