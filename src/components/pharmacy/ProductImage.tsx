'use client'
import { productArt } from '@/lib/art'
import { Pill, Zap, Sparkles, Waves, Baby, Droplets, Palette, Stethoscope, Heart, PawPrint } from 'lucide-react'

const ICONS: Record<string, any> = {
  pill: Pill, zap: Zap, sparkles: Sparkles, waves: Waves, baby: Baby,
  droplets: Droplets, palette: Palette, stethoscope: Stethoscope, heart: Heart, paw: PawPrint,
}

const CATEGORY_ICON: Record<string, string> = {
  'medications': 'pill', 'vitamins': 'zap', 'skin-care': 'sparkles', 'hair-care': 'waves',
  'mom-baby': 'baby', 'daily-essentials': 'droplets', 'makeup': 'palette',
  'medical-supplies': 'stethoscope', 'sexual-health': 'heart', 'pet-supplies': 'paw',
}

export function ProductImage({
  slug, category, brand, className = '', rounded = 'rounded-2xl',
}: { slug: string; category: string; brand: string; className?: string; rounded?: string }) {
  const { from, to, initials, angle } = productArt(slug, category, brand)
  const Icon = ICONS[CATEGORY_ICON[category] || 'pill'] || Pill

  return (
    <div
      className={`relative overflow-hidden flex items-center justify-center ${rounded} ${className}`}
      style={{ background: `linear-gradient(${angle + 120}deg, ${from}18, ${to}32, ${from}12)` }}
      aria-hidden="true"
    >
      <svg className="absolute inset-0 w-full h-full opacity-[0.14]" viewBox="0 0 100 100" preserveAspectRatio="none">
        <circle cx={angle % 2 === 0 ? 25 : 75} cy="30" r="34" fill={to} />
        <circle cx={angle % 2 === 0 ? 78 : 22} cy="78" r="26" fill={from} />
      </svg>

      <span
        className="relative z-10 font-black tracking-tight select-none leading-none"
        style={{ color: from, fontSize: 'clamp(1.5rem, 45%, 3rem)' }}
      >
        {initials}
      </span>

      <span className="absolute z-10 bottom-2 end-2 flex items-center justify-center rounded-xl w-9 h-9 shadow-sm bg-white">
        <Icon className="w-4 h-4" style={{ color: from }} strokeWidth={2.2} />
      </span>
    </div>
  )
}

export function categoryIconName(slug: string): string {
  return CATEGORY_ICON[slug] || 'pill'
}
