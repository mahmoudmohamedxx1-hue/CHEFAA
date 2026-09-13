// Export product list for image fetching + description generation
import { PrismaClient } from '@prisma/client'
import { writeFileSync } from 'fs'

const db = new PrismaClient()

async function main() {
  const products = await db.product.findMany({
    select: {
      id: true, slug: true, nameEn: true, nameAr: true, brand: true,
      subcategory: true, volume: true, price: true, descEn: true, descAr: true,
      popularity: true, isFeatured: true,
      category: { select: { slug: true, nameEn: true } },
    },
    // most visible products first: featured, then popular
    orderBy: [{ isFeatured: 'desc' }, { popularity: 'desc' }],
  })
  writeFileSync('/home/z/my-project/scripts/products_export.json', JSON.stringify(products, null, 1))
  console.log(`Exported ${products.length} products`)
  console.log('Sample:', JSON.stringify(products[0], null, 1))
}

main().then(() => db.$disconnect())
