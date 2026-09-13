// Add key common medicines missing from catalog (from original CHEFAA seed data)
import { PrismaClient } from '@prisma/client'
const db = new PrismaClient()

const EXTRA = [
  { nameEn: 'Augmentin 1g 14 Tablets', nameAr: 'أوجمنتين 1 جم 14 قرص', brand: 'Augmentin', price: 145, sub: 'antibiotics', vol: '14 tablets', rx: true,
    dEn: 'Broad-spectrum amoxicillin/clavulanate antibiotic for bacterial infections. Prescription required.',
    dAr: 'مضاد حيوي واسع المجال أموكسيسيلين/كلافولانات للعدوى البكتيرية. يتطلب روشتة طبية.' },
  { nameEn: 'Augmentin 625mg 14 Tablets', nameAr: 'أوجمنتين 625 مجم 14 قرص', brand: 'Augmentin', price: 105, sub: 'antibiotics', vol: '14 tablets', rx: true,
    dEn: 'Amoxicillin/clavulanate antibiotic for respiratory and urinary infections. Prescription required.',
    dAr: 'مضاد حيوي للعدوى التنفسية والبولية. يتطلب روشتة طبية.' },
  { nameEn: 'Aspirin 100mg 30 Tablets', nameAr: 'أسبرين 100 مجم 30 قرص', brand: 'Bayer', price: 32.5, sub: 'chronic-care', vol: '30 tablets', rx: false,
    dEn: 'Low-dose aspirin as blood thinner for heart health and stroke prevention.',
    dAr: 'أسبرين بجرعة منخفضة كمضاد للتجلط لصحة القلب والوقاية من الجلطات.' },
  { nameEn: 'Brufen 600mg 20 Tablets', nameAr: 'بروفين 600 مجم 20 قرص', brand: 'Brufen', price: 55, sub: 'pain-relief', vol: '20 tablets', rx: false,
    dEn: 'Ibuprofen anti-inflammatory for pain, fever and inflammation relief.',
    dAr: 'إيبوبروفين مضاد للالتهاب لتخفيف الألم والحرارة والالتهاب.' },
  { nameEn: 'Omeprazole 20mg 14 Capsules', nameAr: 'أوميبرازول 20 مجم 14 كبسولة', brand: 'Generic', price: 65, sub: 'stomach', vol: '14 capsules', rx: false,
    dEn: 'Proton pump inhibitor for acid reflux, heartburn and gastric protection.',
    dAr: 'مثبط مضخة البروتون للارتجاع الحمضي والحرقة وحماية المعدة.' },
  { nameEn: 'Amoxicillin 500mg 16 Capsules', nameAr: 'أموكسيسيلين 500 مجم 16 كبسولة', brand: 'Generic', price: 85, sub: 'antibiotics', vol: '16 capsules', rx: true,
    dEn: 'Penicillin antibiotic for bacterial infections. Prescription required.',
    dAr: 'مضاد حيوي بنسليني للعدوى البكتيرية. يتطلب روشتة طبية.' },
  { nameEn: 'Concor 5mg 30 Tablets', nameAr: 'كونكور 5 مجم 30 قرص', brand: 'Concor', price: 95, sub: 'chronic-care', vol: '30 tablets', rx: true,
    dEn: 'Bisoprolol beta-blocker for hypertension and heart conditions. Prescription required.',
    dAr: 'بيسوبرولول حاصر بيتا لارتفاع ضغط الدم وأمراض القلب. يتطلب روشتة طبية.' },
  { nameEn: 'Panadol Advance 500mg 24 Tablets', nameAr: 'بانادول أدفانس 500 مجم 24 قرص', brand: 'Panadol', price: 48, sub: 'pain-relief', vol: '24 tablets', rx: false,
    dEn: 'Paracetamol 500mg tablets with Optizorb for faster pain and fever relief.',
    dAr: 'أقراص باراسيتامول 500 مجم بتقنية أوبتيزورب لتخفيف أسرع للألم والحرارة.' },
]

function slugify(s: string) {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 70)
}

async function main() {
  const cats = await db.category.findMany()
  const map = new Map(cats.map((c) => [c.slug, c.id]))
  let added = 0
  for (const m of EXTRA) {
    const slug = slugify(m.nameEn)
    const exists = await db.product.findUnique({ where: { slug } })
    if (exists) continue
    await db.product.create({
      data: {
        slug, nameEn: m.nameEn, nameAr: m.nameAr, brand: m.brand,
        descEn: m.dEn, descAr: m.dAr, price: m.price,
        categoryId: map.get('medications')!, subcategory: m.sub, volume: m.vol,
        prescriptionRequired: m.rx, stock: 40 + added * 7, rating: 4.6,
        reviewCount: 150 + added * 37, popularity: 95 - added, isFeatured: added < 2,
      },
    })
    added++
  }
  console.log(`Added ${added} medicines`)
  const total = await db.product.count()
  console.log(`Total products: ${total}`)
}

main().catch(console.error).finally(() => db.$disconnect())
