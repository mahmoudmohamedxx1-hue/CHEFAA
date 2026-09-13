// The Pharmacy - database seeder
import { PrismaClient } from '@prisma/client'
import { scryptSync, randomBytes } from 'crypto'
import { readFileSync } from 'fs'

const db = new PrismaClient()

function hashPassword(password: string): string {
  const salt = randomBytes(16).toString('hex')
  const hash = scryptSync(password, salt, 64).toString('hex')
  return `${salt}:${hash}`
}

const CATEGORIES = [
  { slug: 'medications', nameEn: 'Medications', nameAr: 'الأدوية', icon: 'pill', sortOrder: 1,
    descEn: 'Prescription and OTC medicines: pain relief, cold & flu, allergy, antibiotics and chronic care.',
    descAr: 'أدوية بروشتة ودون وصفة: مسكنات، البرد والإنفلونزا، الحساسية، المضادات الحيوية ورعاية الأمراض المزمنة.' },
  { slug: 'vitamins', nameEn: 'Vitamins & Supplements', nameAr: 'الفيتامينات والمكملات', icon: 'zap', sortOrder: 2,
    descEn: 'Multivitamins, immunity boosters and supplements for energy, beauty and wellness.',
    descAr: 'فيتامينات متعددة ومعززات المناعة ومكملات للطاقة والجمال والعافية.' },
  { slug: 'skin-care', nameEn: 'Skin Care', nameAr: 'العناية بالبشرة', icon: 'sparkles', sortOrder: 3,
    descEn: 'Dermatologist-trusted moisturizers, sunscreens, cleansers and treatments.',
    descAr: 'مرطبات وواقيات شمس ومنظفات وعلاجات موثوقة من أطباء الجلدية.' },
  { slug: 'hair-care', nameEn: 'Hair Care', nameAr: 'العناية بالشعر', icon: 'waves', sortOrder: 4,
    descEn: 'Shampoos, conditioners, treatments and coloring for every hair type.',
    descAr: 'شامبو وبلسم وعلاجات وصبغات لكل أنواع الشعر.' },
  { slug: 'mom-baby', nameEn: 'Mom & Baby', nameAr: 'الأم والطفل', icon: 'baby', sortOrder: 5,
    descEn: 'Diapers, formula, baby skincare and feeding essentials from trusted brands.',
    descAr: 'حفاضات ولبن أطفال ومستحضرات العناية بالطفل وأساسيات التغذية من ماركات موثوقة.' },
  { slug: 'daily-essentials', nameEn: 'Daily Essentials', nameAr: 'العناية اليومية', icon: 'droplets', sortOrder: 6,
    descEn: 'Personal hygiene, dental care and everyday essentials for the whole family.',
    descAr: 'النظافة الشخصية والعناية بالأسنان والأساسيات اليومية لكل الأسرة.' },
  { slug: 'makeup', nameEn: 'Makeup', nameAr: 'المكياج', icon: 'palette', sortOrder: 7,
    descEn: 'Face, eyes, lips and nails cosmetics from global brands.',
    descAr: 'مستحضرات تجميل للوجه والعيون والشفاه والأظافر من ماركات عالمية.' },
  { slug: 'medical-supplies', nameEn: 'Medical Supplies', nameAr: 'المستلزمات الطبية', icon: 'stethoscope', sortOrder: 8,
    descEn: 'Blood pressure monitors, glucometers, thermometers and home care devices.',
    descAr: 'أجهزة قياس الضغط والسكر والحرارة وأجهزة الرعاية المنزلية.' },
  { slug: 'sexual-health', nameEn: 'Sexual Health', nameAr: 'الصحة الجنسية', icon: 'heart', sortOrder: 9,
    descEn: 'Discreet wellness products, tests and treatments with pharmacist support.',
    descAr: 'منتجات واختبارات وعلاجات العافية بسرية تامة مع دعم الصيدلي.' },
  { slug: 'pet-supplies', nameEn: 'Pet Supplies', nameAr: 'مستلزمات الحيوانات', icon: 'paw', sortOrder: 10,
    descEn: 'Flea treatments, grooming and nutrition for dogs and cats.',
    descAr: 'علاجات البراغيث والعناية والتغذية للكلاب والقطط.' },
]

async function main() {
  console.log('Seeding The Pharmacy database...')

  // wipe in dependency order
  await db.orderItem.deleteMany()
  await db.order.deleteMany()
  await db.prescription.deleteMany()
  await db.session.deleteMany()
  await db.product.deleteMany()
  await db.category.deleteMany()
  await db.user.deleteMany()

  // categories
  const catMap: Record<string, string> = {}
  for (const c of CATEGORIES) {
    const cat = await db.category.create({ data: c })
    catMap[c.slug] = cat.id
  }
  console.log(`Created ${CATEGORIES.length} categories`)

  // products
  const catalog = JSON.parse(readFileSync('/home/z/my-project/scripts/catalog.json', 'utf8'))
  const products = catalog.products as any[]
  let featured = 0
  for (const p of products) {
    const isFeatured = p.popularity > 90 && p.stock > 0
    if (isFeatured) featured++
    await db.product.create({
      data: {
        slug: p.slug, nameEn: p.nameEn, nameAr: p.nameAr, brand: p.brand,
        descEn: p.descEn || '', descAr: p.descAr || '',
        price: p.price, compareAtPrice: p.compareAtPrice ?? null,
        categoryId: catMap[p.category], subcategory: p.subcategory || '',
        volume: p.volume || '', prescriptionRequired: !!p.prescriptionRequired,
        stock: p.stock, rating: p.rating, reviewCount: p.reviewCount,
        popularity: p.popularity, isFeatured,
      },
    })
  }
  console.log(`Created ${products.length} products (${featured} featured)`)

  // users
  const admin = await db.user.create({
    data: {
      email: 'admin@thepharmacy.com',
      passwordHash: hashPassword('Admin@2026'),
      name: 'Pharmacy Admin', phone: '+201000000001', isAdmin: true,
    },
  })
  const demo = await db.user.create({
    data: {
      email: 'demo@thepharmacy.com',
      passwordHash: hashPassword('Demo@2026'),
      name: 'Demo Customer', phone: '+201000000002', isAdmin: false,
    },
  })
  console.log('Created admin + demo users')

  // demo orders for admin dashboard & order history
  const sample = await db.product.findMany({ take: 8, orderBy: { popularity: 'desc' } })
  const statuses = ['delivered', 'out_for_delivery', 'preparing', 'confirmed']
  let orderNo = 100241
  for (let i = 0; i < 4; i++) {
    const items = sample.slice(i, i + 3).map((p) => ({
      productId: p.id, nameEn: p.nameEn, nameAr: p.nameAr,
      price: p.price, quantity: 1 + (i % 3),
    }))
    const subtotal = items.reduce((s, it) => s + it.price * it.quantity, 0)
    const deliveryFee = subtotal >= 500 ? 0 : 35
    await db.order.create({
      data: {
        orderNumber: `TP-${orderNo + i}`,
        userId: demo.id, status: statuses[i],
        subtotal: Math.round(subtotal * 100) / 100, deliveryFee, total: Math.round((subtotal + deliveryFee) * 100) / 100,
        paymentMethod: 'cod', zone: 'nasr-city',
        address: 'Demo address, Nasr City, Cairo', phone: '+201000000002',
        notes: '', items: { create: items },
      },
    })
  }
  console.log('Created 4 demo orders')

  // demo prescription
  await db.prescription.create({
    data: {
      userId: demo.id, imageData: '',
      extractedText: 'Rx: Panadol Extra 500mg x24, Augmentin 1g x14, Ventolin inhaler',
      detectedMedicines: JSON.stringify(['Panadol Extra', 'Augmentin 1g', 'Ventolin Inhaler']),
      status: 'reviewed', address: 'Demo address, Maadi, Cairo',
      phone: '+201000000002', notes: 'Sample uploaded prescription',
    },
  })
  console.log('Created demo prescription')
}

main().catch((e) => { console.error(e); process.exit(1) }).finally(() => db.$disconnect())
