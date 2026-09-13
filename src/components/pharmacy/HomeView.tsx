'use client'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import { Pill, Zap, Sparkles, Waves, Baby, Droplets, Palette, Stethoscope, Heart, PawPrint, ScanText, MessageCircleHeart, ShieldAlert, ArrowRight, Truck, BadgeCheck, Cross, Clock } from 'lucide-react'
import { useLang } from './LangContext'
import { useCategories, useProducts, type Product } from './hooks'
import { ProductCard } from './ProductCard'
import { go } from '@/lib/router'
import { motion } from 'framer-motion'

const CAT_ICONS: Record<string, any> = {
  pill: Pill, zap: Zap, sparkles: Sparkles, waves: Waves, baby: Baby,
  droplets: Droplets, palette: Palette, stethoscope: Stethoscope, heart: Heart, paw: PawPrint,
}
const CAT_TINTS: Record<string, string> = {
  'medications': 'bg-teal-50 text-teal-600', 'vitamins': 'bg-yellow-50 text-yellow-600',
  'skin-care': 'bg-pink-50 text-pink-600', 'hair-care': 'bg-violet-50 text-violet-600',
  'mom-baby': 'bg-cyan-50 text-cyan-600', 'daily-essentials': 'bg-emerald-50 text-emerald-600',
  'makeup': 'bg-rose-50 text-rose-600', 'medical-supplies': 'bg-slate-100 text-slate-600',
  'sexual-health': 'bg-red-50 text-red-500', 'pet-supplies': 'bg-amber-50 text-amber-600',
}
const SLUG_ICON: Record<string, string> = {
  'medications': 'pill', 'vitamins': 'zap', 'skin-care': 'sparkles', 'hair-care': 'waves',
  'mom-baby': 'baby', 'daily-essentials': 'droplets', 'makeup': 'palette',
  'medical-supplies': 'stethoscope', 'sexual-health': 'heart', 'pet-supplies': 'paw',
}

const fade = {
  initial: { opacity: 0, y: 16 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: '-60px' },
  transition: { duration: 0.45 },
}

export function HomeView() {
  const { lang, t } = useLang()
  const { data: categories = [] } = useCategories()
  const { data: featured } = useProducts({ featured: 'true', limit: 8 })
  const { data: popular } = useProducts({ sort: 'rating', limit: 8 })

  const featuredItems: Product[] = featured?.items?.length ? featured.items : popular?.items || []

  return (
    <div className="flex flex-col gap-14 pb-14">
      {/* ===== HERO ===== */}
      <section className="relative overflow-hidden -mt-0">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-primary/5" />
        <svg className="absolute -top-24 -end-24 w-[420px] h-[420px] opacity-[0.07] text-primary" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="48" fill="currentColor" />
          <circle cx="50" cy="50" r="34" fill="white" />
          <rect x="46" y="26" width="8" height="48" rx="2" fill="currentColor" />
          <rect x="26" y="46" width="48" height="8" rx="2" fill="currentColor" />
        </svg>

        <div className="relative max-w-7xl mx-auto px-4 lg:px-6 pt-12 pb-10 lg:pt-20 lg:pb-16 grid lg:grid-cols-2 gap-10 items-center">
          <div className="flex flex-col gap-5">
            <Badge className="w-fit gap-1.5 bg-primary/10 text-primary hover:bg-primary/10 border border-primary/20 px-3.5 py-1.5 text-xs font-bold">
              <Sparkles className="w-3.5 h-3.5 tp-pulse" /> {t('hero_badge')}
            </Badge>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-[1.1] text-balance">
              {t('hero_title_1')}
              <span className="block text-primary mt-1">{t('hero_title_2')}</span>
            </h1>
            <p className="text-base sm:text-lg text-muted-foreground leading-relaxed max-w-xl">{t('hero_sub')}</p>
            <div className="flex flex-wrap items-center gap-3 pt-2">
              <Button size="lg" onClick={() => go('/c/medications')} className="rounded-2xl h-12 px-7 text-base font-bold gap-2 shadow-lg shadow-primary/25">
                {t('hero_cta_shop')} <ArrowRight className="w-4 h-4 flip-x rtl:rotate-180" />
              </Button>
              <Button size="lg" variant="outline" onClick={() => go('/prescription')} className="rounded-2xl h-12 px-7 text-base font-bold gap-2 border-primary/40 text-primary hover:bg-primary/5 hover:text-primary">
                <ScanText className="w-5 h-5" /> {t('hero_cta_rx')}
              </Button>
            </div>
            <div className="flex items-center gap-5 pt-4 text-sm">
              <span className="flex flex-col">
                <span className="text-2xl font-black text-primary">488+</span>
                <span className="text-xs text-muted-foreground">{lang === 'ar' ? 'منتج أصلي' : 'genuine products'}</span>
              </span>
              <span className="w-px h-8 bg-border" />
              <span className="flex flex-col">
                <span className="text-2xl font-black text-primary">3</span>
                <span className="text-xs text-muted-foreground">{lang === 'ar' ? 'أدوات ذكاء اصطناعي' : 'AI health tools'}</span>
              </span>
              <span className="w-px h-8 bg-border" />
              <span className="flex flex-col">
                <span className="text-2xl font-black text-primary">15</span>
                <span className="text-xs text-muted-foreground">{lang === 'ar' ? 'منطقة توصيل' : 'delivery zones'}</span>
              </span>
            </div>
          </div>

          {/* hero visual: AI tools cards */}
          <div className="hidden lg:grid grid-cols-1 gap-4">
            {[
              { icon: ScanText, title: t('ai_rx_title'), desc: t('ai_rx_desc'), color: 'text-primary bg-primary/10' },
              { icon: MessageCircleHeart, title: t('ai_chat_title'), desc: t('ai_chat_desc'), color: 'text-emerald-600 bg-emerald-50' },
              { icon: ShieldAlert, title: t('ai_ddi_title'), desc: t('ai_ddi_desc'), color: 'text-red-500 bg-red-50' },
            ].map((f, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: 30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.15 * i, duration: 0.5 }}
              >
                <Card className="p-5 flex items-center gap-4 hover:shadow-lg hover:border-primary/30 transition-all cursor-pointer" onClick={() => go(['/prescription', '/assistant', '/interactions'][i])}>
                  <span className={`w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 ${f.color}`}>
                    <f.icon className="w-6 h-6" />
                  </span>
                  <div>
                    <p className="font-bold">{f.title}</p>
                    <p className="text-sm text-muted-foreground leading-snug">{f.desc}</p>
                  </div>
                  <ArrowRight className="w-4 h-4 ms-auto shrink-0 text-muted-foreground flip-x rtl:rotate-180" />
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== CATEGORIES ===== */}
      <section className="max-w-7xl mx-auto w-full px-4 lg:px-6">
        <motion.div {...fade} className="flex items-end justify-between mb-6">
          <div>
            <h2 className="text-2xl sm:text-3xl font-black tracking-tight">{t('shop_by_category')}</h2>
          </div>
        </motion.div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
          {categories.map((c, i) => {
            const Icon = CAT_ICONS[SLUG_ICON[c.slug]] || Pill
            return (
              <motion.button
                key={c.slug}
                initial={{ opacity: 0, scale: 0.92 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.04, duration: 0.35 }}
                onClick={() => go(`/c/${c.slug}`)}
                className={`group flex flex-col items-center gap-3 p-5 rounded-3xl border bg-card hover:border-primary/40 hover:shadow-lg hover:-translate-y-0.5 transition-all ${CAT_TINTS[c.slug] || 'bg-accent text-primary'}`}
              >
                <span className={`w-12 h-12 rounded-2xl flex items-center justify-center ${CAT_TINTS[c.slug] || 'bg-primary/10 text-primary'} group-hover:scale-110 transition-transform`}>
                  <Icon className="w-6 h-6" />
                </span>
                <span className="text-sm font-bold text-center leading-tight">{lang === 'ar' ? c.nameAr : c.nameEn}</span>
                <span className="text-[11px] text-muted-foreground">{c.productCount} {lang === 'ar' ? 'منتج' : 'items'}</span>
              </motion.button>
            )
          })}
        </div>
      </section>

      {/* ===== FEATURED PRODUCTS ===== */}
      <section className="max-w-7xl mx-auto w-full px-4 lg:px-6">
        <motion.div {...fade} className="flex items-end justify-between mb-6">
          <h2 className="text-2xl sm:text-3xl font-black tracking-tight">{t('featured_products')}</h2>
          <Button variant="ghost" onClick={() => go('/c/medications')} className="text-primary font-bold gap-1.5">
            {t('view_all')} <ArrowRight className="w-4 h-4 flip-x rtl:rotate-180" />
          </Button>
        </motion.div>
        {featuredItems.length === 0 ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="aspect-[3/4] rounded-2xl bg-muted animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {featuredItems.map((p) => <ProductCard key={p.id} p={p} />)}
          </div>
        )}
      </section>

      {/* ===== AI TOOLS ===== */}
      <section className="max-w-7xl mx-auto w-full px-4 lg:px-6">
        <motion.div {...fade} className="rounded-3xl bg-gradient-to-br from-foreground to-slate-800 text-white p-8 sm:p-12 relative overflow-hidden">
          <svg className="absolute -top-20 -end-20 w-72 h-72 opacity-10 text-primary" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="48" fill="currentColor" />
          </svg>
          <div className="relative flex flex-col gap-2 mb-8">
            <Badge className="w-fit bg-primary/20 text-primary-foreground border-primary/40 gap-1.5">
              <Sparkles className="w-3.5 h-3.5" /> {t('ai_tools_sub')}
            </Badge>
            <h2 className="text-3xl font-black tracking-tight">{t('ai_power_tools')}</h2>
          </div>
          <div className="relative grid sm:grid-cols-3 gap-4">
            {[
              { icon: ScanText, title: t('ai_rx_title'), desc: t('ai_rx_desc'), to: '/prescription' },
              { icon: MessageCircleHeart, title: t('ai_chat_title'), desc: t('ai_chat_desc'), to: '/assistant' },
              { icon: ShieldAlert, title: t('ai_ddi_title'), desc: t('ai_ddi_desc'), to: '/interactions' },
            ].map((f) => (
              <button key={f.to} onClick={() => go(f.to)} className="group flex flex-col gap-3 p-6 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 hover:border-primary/50 text-start transition-all backdrop-blur">
                <span className="w-12 h-12 rounded-2xl bg-primary flex items-center justify-center group-hover:scale-110 transition-transform">
                  <f.icon className="w-6 h-6 text-white" />
                </span>
                <p className="font-bold text-lg">{f.title}</p>
                <p className="text-sm text-white/60 leading-relaxed">{f.desc}</p>
                <span className="mt-auto text-sm font-bold text-primary inline-flex items-center gap-1.5 pt-2">
                  {t('try_now')} <ArrowRight className="w-4 h-4 flip-x rtl:rotate-180" />
                </span>
              </button>
            ))}
          </div>
        </motion.div>
      </section>

      {/* ===== HOW IT WORKS ===== */}
      <section className="max-w-7xl mx-auto w-full px-4 lg:px-6">
        <motion.h2 {...fade} className="text-2xl sm:text-3xl font-black tracking-tight mb-8 text-center">{t('how_it_works')}</motion.h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { icon: Sparkles, label: t('step_1') },
            { icon: BadgeCheck, label: t('step_2') },
            { icon: Cross, label: t('step_3') },
            { icon: Truck, label: t('step_4') },
          ].map((s, i) => (
            <motion.div key={i} {...fade} transition={{ ...fade.transition, delay: i * 0.08 }} className="relative flex flex-col items-center gap-3 p-6 rounded-3xl border bg-card text-center">
              <span className="absolute top-4 start-4 text-xs font-black text-primary/30">{`0${i + 1}`}</span>
              <span className="w-12 h-12 rounded-2xl bg-primary/10 text-primary flex items-center justify-center">
                <s.icon className="w-6 h-6" />
              </span>
              <p className="text-sm font-semibold leading-snug max-w-[180px]">{s.label}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ===== TRUST ===== */}
      <section className="max-w-7xl mx-auto w-full px-4 lg:px-6">
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { icon: BadgeCheck, title: t('trust_genuine'), desc: t('trust_genuine_d') },
            { icon: Truck, title: t('trust_fast'), desc: t('trust_fast_d') },
            { icon: Cross, title: t('trust_pharmacist'), desc: t('trust_pharmacist_d') },
            { icon: Sparkles, title: t('trust_ai'), desc: t('trust_ai_d') },
          ].map((b, i) => (
            <motion.div key={i} {...fade} transition={{ ...fade.transition, delay: i * 0.06 }} className="flex gap-3.5 p-5 rounded-2xl bg-accent/50">
              <span className="w-10 h-10 rounded-xl bg-white text-primary flex items-center justify-center shrink-0 shadow-sm">
                <b.icon className="w-5 h-5" />
              </span>
              <div>
                <p className="font-bold text-sm">{b.title}</p>
                <p className="text-xs text-muted-foreground leading-relaxed mt-0.5">{b.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  )
}
