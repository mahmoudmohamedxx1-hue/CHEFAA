'use client'
import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Star, ShoppingCart, Heart, FileText } from 'lucide-react'
import { useCart, useWishlist } from '@/lib/store'
import { useLang } from './LangContext'
import { ProductImage } from './ProductImage'
import { go } from '@/lib/router'
import { useToast } from '@/hooks/use-toast'
import type { Lang } from '@/lib/i18n'

export interface P {
  id: string; slug: string; nameEn: string; nameAr: string; brand: string
  price: number; compareAtPrice?: number | null; stock: number; rating: number
  reviewCount: number; prescriptionRequired: boolean; category: { slug: string } | string
  volume?: string
}

export function fmtPrice(v: number, lang: Lang) {
  const n = v % 1 === 0 ? v.toLocaleString('en-US') : v.toFixed(2)
  return lang === 'ar' ? `${n} جنيه` : `EGP ${n}`
}

export function ProductCard({ p }: { p: P }) {
  const { lang } = useLang()
  const add = useCart((s) => s.add)
  const wishlist = useWishlist()
  const { toast } = useToast()
  const catSlug = typeof p.category === 'string' ? p.category : p.category?.slug
  const name = lang === 'ar' ? p.nameAr : p.nameEn
  const discount = p.compareAtPrice && p.compareAtPrice > p.price
    ? Math.round((1 - p.price / p.compareAtPrice) * 100) : 0

  const onAdd = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (p.stock <= 0) return
    add({
      productId: p.id, slug: p.slug, nameEn: p.nameEn, nameAr: p.nameAr,
      price: p.price, stock: p.stock, prescriptionRequired: p.prescriptionRequired,
    })
    toast({ description: `${name} — ${lang === 'ar' ? 'تمت الإضافة للعربة' : 'Added to cart'}` })
  }

  const onWish = (e: React.MouseEvent) => {
    e.stopPropagation()
    const addedNow = wishlist.toggle(p.id)
    toast({ description: addedNow
      ? (lang === 'ar' ? 'أضيف للمفضلة' : 'Added to wishlist')
      : (lang === 'ar' ? 'أُزيل من المفضلة' : 'Removed from wishlist') })
  }

  return (
    <Card
      onClick={() => go(`/p/${p.slug}`)}
      className="group cursor-pointer overflow-hidden border-border/70 hover:border-primary/40 hover:shadow-lg transition-all duration-300 flex flex-col p-3 gap-3"
    >
      <div className="relative">
        <ProductImage slug={p.slug} category={catSlug} brand={p.brand} className="w-full aspect-square" />
        {discount > 0 && (
          <Badge className="absolute top-2 start-2 bg-red-500 hover:bg-red-500 text-[11px] font-bold">
            -{discount}%
          </Badge>
        )}
        {p.prescriptionRequired && (
          <Badge variant="secondary" className="absolute top-2 end-2 gap-1 text-[11px] bg-amber-100 text-amber-800 hover:bg-amber-100">
            <FileText className="w-3 h-3" /> {lang === 'ar' ? 'روشتة' : 'Rx'}
          </Badge>
        )}
        <button
          onClick={onWish}
          aria-label="wishlist"
          className="absolute bottom-2 start-2 z-10 bg-white/90 backdrop-blur rounded-full p-2.5 shadow-sm hover:scale-110 active:scale-95 transition-transform min-w-11 min-h-11 flex items-center justify-center"
        >
          <Heart className={`w-4 h-4 ${wishlist.has(p.id) ? 'fill-red-500 text-red-500' : 'text-muted-foreground'}`} />
        </button>
        {p.stock === 0 && (
          <div className="absolute inset-0 bg-white/60 backdrop-blur-[1px] flex items-center justify-center">
            <span className="bg-foreground/80 text-white text-xs font-bold px-3 py-1.5 rounded-full">
              {lang === 'ar' ? 'غير متوفر' : 'Out of stock'}
            </span>
          </div>
        )}
      </div>

      <div className="flex flex-col gap-1.5 flex-1">
        <span className="text-[11px] font-semibold text-primary/80 uppercase tracking-wide">{p.brand}</span>
        <h3 className="text-sm font-semibold leading-snug line-clamp-2 group-hover:text-primary transition-colors min-h-[2.5rem]">
          {name}
        </h3>
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
          <span className="font-semibold text-foreground">{p.rating.toFixed(1)}</span>
          <span>({p.reviewCount})</span>
          {p.stock > 0 && p.stock <= 10 && (
            <span className="ms-auto text-[11px] font-bold text-amber-600">{lang === 'ar' ? 'كمية محدودة' : `Only ${p.stock} left`}</span>
          )}
        </div>
        <div className="mt-auto flex items-end justify-between gap-2 pt-1">
          <div className="flex flex-col">
            <span className="text-base font-extrabold text-foreground">{fmtPrice(p.price, lang)}</span>
            {discount > 0 && p.compareAtPrice && (
              <span className="text-xs text-muted-foreground line-through">{fmtPrice(p.compareAtPrice, lang)}</span>
            )}
          </div>
          <Button
            size="icon"
            onClick={onAdd}
            disabled={p.stock <= 0}
            aria-label={lang === 'ar' ? 'أضف للعربة' : 'Add to cart'}
            className="rounded-xl h-10 w-10 shrink-0"
          >
            <ShoppingCart className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </Card>
  )
}
