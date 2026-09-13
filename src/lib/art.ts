// Deterministic product artwork - no external images needed
const PALETTES: Record<string, [string, string]> = {
  'medications': ['#0d9488', '#14b8a6'],
  'vitamins': ['#ca8a04', '#eab308'],
  'skin-care': ['#db2777', '#f472b6'],
  'hair-care': ['#7c3aed', '#a78bfa'],
  'mom-baby': ['#0891b2', '#22d3ee'],
  'daily-essentials': ['#059669', '#34d399'],
  'makeup': ['#be185d', '#ec4899'],
  'medical-supplies': ['#475569', '#64748b'],
  'sexual-health': ['#e11d48', '#fb7185'],
  'pet-supplies': ['#d97706', '#fbbf24'],
}

function hashCode(s: string): number {
  let h = 0
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0
  return Math.abs(h)
}

export function productArt(slug: string, category: string, brand: string): { from: string; to: string; initials: string; angle: number; pattern: number } {
  const [from, to] = PALETTES[category] || ['#0d9488', '#14b8a6']
  const h = hashCode(slug)
  const initials = brand
    .split(/\s+/)
    .filter((w) => /^[A-Za-z0-9]/.test(w))
    .slice(0, 2)
    .map((w) => w[0].toUpperCase())
    .join('') || 'TP'
  return { from, to, initials, angle: (h % 4) * 90, pattern: h % 3 }
}
