// Apply real images + rich descriptions to the product DB
// Priority: LLM descriptions (if any) > offline generated
import { PrismaClient } from '@prisma/client'
import { readFileSync, existsSync } from 'fs'

const db = new PrismaClient()

const MANIFEST = '/home/z/my-project/scripts/image_manifest.json'
const DESC_LLM = '/home/z/my-project/scripts/descriptions.json'
const DESC_OFFLINE = '/home/z/my-project/scripts/descriptions_offline.json'

const BRAND_FIX: Record<string, string> = {
  "L'Or": "L'Oréal Paris",
  "L'Oreal": "L'Oréal",
  Loreal: "L'Oréal",
  "L'Oreal Paris": "L'Oréal Paris",
}

async function main() {
  const manifest = existsSync(MANIFEST) ? JSON.parse(readFileSync(MANIFEST, 'utf8')) : {}
  const descLlm = existsSync(DESC_LLM) ? JSON.parse(readFileSync(DESC_LLM, 'utf8')) : {}
  const descOffline = existsSync(DESC_OFFLINE)
    ? JSON.parse(readFileSync(DESC_OFFLINE, 'utf8')) : {}

  let imgUpdated = 0, descUpdated = 0, brandFixed = 0
  const products = await db.product.findMany({ select: { id: true, slug: true, brand: true } })

  for (const p of products) {
    const img = manifest[p.slug]
    const hasImg = img?.ok && existsSync(img.path)
    const llm = descLlm[p.slug]
    const off = descOffline[p.slug]
    const desc = llm?.descEn?.length > 40 ? llm : off
    const newBrand = BRAND_FIX[p.brand] || p.brand

    const data: any = {}
    if (hasImg) data.imageUrl = img.path.replace('/home/z/my-project/public', '')
    if (desc?.descEn) {
      data.descEn = desc.descEn
      data.descAr = desc.descAr
    }
    if (newBrand !== p.brand) data.brand = newBrand

    if (Object.keys(data).length) {
      await db.product.update({ where: { id: p.id }, data })
      if (data.imageUrl) imgUpdated++
      if (data.descEn) descUpdated++
      if (data.brand) brandFixed++
    }
  }

  const stats = await db.product.aggregate({
    _count: { _all: true },
  })
  const withImg = await db.product.count({ where: { imageUrl: { not: '' } } })
  const withDesc = await db.product.count({ where: { descEn: { not: '' } } })

  console.log({
    total: stats._count._all,
    imagesApplied: imgUpdated,
    nowWithImage: withImg,
    descriptionsApplied: descUpdated,
    nowWithDesc: withDesc,
    brandsFixed: brandFixed,
  })
}

main().then(() => db.$disconnect())
