'use client'
import { Button } from '@/components/ui/button'
import { Heart } from 'lucide-react'
import { useLang } from './LangContext'
import { useProductsByIds, type Product } from './hooks'
import { ProductCard } from './ProductCard'
import { go } from '@/lib/router'
import { useWishlist } from '@/lib/store'

export function WishlistView() {
  const { lang, t } = useLang()
  const ids = useWishlist((s) => s.ids)
  const { data, isLoading } = useProductsByIds(ids, ids.length > 0)

  const items: Product[] = isLoading ? [] : (data?.items || [])

  return (
    <div className="max-w-7xl mx-auto w-full px-4 lg:px-6 py-8 pb-16">
      <div className="flex items-center gap-2.5 mb-6">
        <span className="w-10 h-10 rounded-2xl bg-red-50 text-red-500 flex items-center justify-center shrink-0">
          <Heart className="w-5 h-5 fill-red-500" />
        </span>
        <div>
          <h1 className="text-2xl font-black tracking-tight">{t('wishlist')}</h1>
          <p className="text-sm text-muted-foreground">
            {ids.length > 0 ? `${items.length} ${lang === 'ar' ? 'منتج' : 'items'}` : (lang === 'ar' ? 'احفظ منتجاتك المفضلة' : 'Save your favorite products')}
          </p>
        </div>
      </div>

      {ids.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-3 py-20 text-center">
          <span className="w-16 h-16 rounded-full bg-accent flex items-center justify-center">
            <Heart className="w-7 h-7 text-red-400" />
          </span>
          <p className="font-bold text-lg">{t('wishlist_empty')}</p>
          <p className="text-sm text-muted-foreground max-w-sm">{t('wishlist_empty_sub')}</p>
          <Button onClick={() => go('/')} className="mt-2 rounded-xl">
            {t('continue_shopping')}
          </Button>
        </div>
      ) : isLoading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {ids.slice(0, 8).map((id) => (
            <div key={id} className="aspect-[3/4] rounded-2xl bg-muted animate-pulse" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <div className="flex flex-col items-center gap-3 py-20 text-center">
          <p className="font-bold">{t('no_results')}</p>
          <Button onClick={() => go('/')} className="rounded-xl">{t('continue_shopping')}</Button>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {items.map((p) => <ProductCard key={p.id} p={p} />)}
        </div>
      )}
    </div>
  )
}
