// Generate rich bilingual product descriptions via LLM (z-ai-web-dev-sdk)
// Resumable: checkpoints to scripts/descriptions.json after each batch.
import ZAI from 'z-ai-web-dev-sdk'
import { readFileSync, writeFileSync, existsSync } from 'fs'

const EXPORT = '/home/z/my-project/scripts/products_export.json'
const OUT = '/home/z/my-project/scripts/descriptions.json'
const BATCH = 12
const DELAY_MS = 1200

interface P {
  slug: string; nameEn: string; nameAr: string; brand: string
  subcategory: string; volume: string; price: number
  category: { slug: string; nameEn: string }
}
interface Desc { slug: string; descEn: string; descAr: string }

function lenientJson(text: string): any {
  let t = text.trim()
  t = t.replace(/^```(?:json)?/i, '').replace(/```$/, '').trim()
  const start = t.indexOf('[')
  const end = t.lastIndexOf(']')
  if (start >= 0 && end > start) t = t.slice(start, end + 1)
  return JSON.parse(t)
}

async function genBatch(zai: any, products: P[]): Promise<Desc[]> {
  const sys = `You are a professional bilingual copywriter for a licensed Egyptian online pharmacy (e-commerce store).
Write product descriptions that a real pharmacy would show on its product page.

STRICT RULES:
- Ground your text ONLY in the product name, brand, category, subcategory and size given. Use your general knowledge of well-known brands/products when the name clearly identifies them (e.g. Panadol = paracetamol).
- NEVER invent dosage instructions, contraindications, or medical claims for unknown products. For OTC/Rx medicines keep it general: what it is typically used for, and advise following the package instructions or consulting a doctor/pharmacist.
- For prescription items, end the Arabic description with "يصرف بروشتة طبية." and the English with "Prescription required." when rx=true.
- descEn: 3-4 sentences, professional pharmacy e-commerce tone (like Boots/WebMD product pages): what it is, key benefits/features, how to use (general), pack size.
- descAr: Natural Modern Standard Arabic with Egyptian retail warmth (like صيدليات أنافبي), 3-4 جمل, NOT a literal translation — idiomatic and fluent.
- No marketing fluff like "best product ever", no emoji, no markdown, no quotes inside the strings.

OUTPUT: ONLY a valid JSON array, no markdown fences, exactly:
[{"slug":"<slug>","descEn":"...","descAr":"..."}]
One object per input product, same order, same slugs. Every input product MUST appear.`

  const list = products.map((p) => ({
    slug: p.slug,
    nameEn: p.nameEn,
    nameAr: p.nameAr,
    brand: p.brand,
    category: p.category?.nameEn,
    subcategory: p.subcategory,
    size: p.volume,
    priceEgp: p.price,
    rxHint: /tablet|capsule|mg|inhaler|syrup|ampoule|injection|drops|spray/i.test(p.nameEn) ? 'possibly medicine' : '',
  }))

  const completion = await zai.chat.completions.create({
    messages: [
      { role: 'assistant', content: sys },
      { role: 'user', content: `Products:\n${JSON.stringify(list, null, 1)}` },
    ],
    thinking: { type: 'disabled' },
  })
  const raw = completion.choices[0]?.message?.content || ''
  const parsed = lenientJson(raw) as Desc[]
  if (!Array.isArray(parsed)) throw new Error('not an array')
  const bySlug = new Map(parsed.map((d) => [d.slug, d]))
  return products.map((p) => {
    const d = bySlug.get(p.slug)
    return {
      slug: p.slug,
      descEn: (d?.descEn || '').trim(),
      descAr: (d?.descAr || '').trim(),
    }
  }).filter((d) => d.descEn.length > 40 && d.descAr.length > 40)
}

async function main() {
  const BUDGET_SEC = Number(process.env.BUDGET_SEC || 0)
  const deadline = Date.now() + BUDGET_SEC * 1000
  const products: P[] = JSON.parse(readFileSync(EXPORT, 'utf8'))
  const done: Record<string, Desc> = existsSync(OUT)
    ? JSON.parse(readFileSync(OUT, 'utf8')) : {}
  const todo = products.filter((p) => !(done[p.slug]?.descEn?.length > 40))
  console.log(`total=${products.length} done=${Object.keys(done).length} todo=${todo.length}`)

  const zai = await ZAI.create()
  let ok = 0, fail = 0
  outer:
  for (let i = 0; i < todo.length; i += BATCH) {
    const batch = todo.slice(i, i + BATCH)
    let attempt = 0
    let rateWaits = 0
    while (attempt < 4) {
      // stop if budget exhausted before starting a new retry round
      if (BUDGET_SEC && Date.now() > deadline) {
        console.log('BUDGET REACHED — exiting gracefully')
        break outer
      }
      try {
        const res = await genBatch(zai, batch)
        if (res.length < batch.length * 0.6) throw new Error(`only ${res.length}/${batch.length} valid`)
        for (const d of res) done[d.slug] = d
        ok += res.length
        break
      } catch (e: any) {
        const msg = String(e?.message || '')
        const is429 = msg.includes('429') || msg.toLowerCase().includes('too many')
        if (is429) {
          rateWaits++
          if (rateWaits > 10) {
            console.error(`batch ${i / BATCH}: giving up after ${rateWaits} rate waits`)
            fail += batch.length
            for (const p of batch) if (!done[p.slug]) done[p.slug] = { slug: p.slug, descEn: '', descAr: '' }
            break
          }
          const wait = Math.min(30000 + rateWaits * 15000, 120000)
          console.error(`batch ${i / BATCH}: 429 — waiting ${wait / 1000}s (${rateWaits})`)
          await new Promise((r) => setTimeout(r, wait))
          continue // retry same batch without consuming attempt
        }
        attempt++
        console.error(`batch ${i / BATCH}: attempt ${attempt} failed: ${msg}`)
        if (attempt >= 4) {
          fail += batch.length
          for (const p of batch) if (!done[p.slug]) done[p.slug] = { slug: p.slug, descEn: '', descAr: '' }
        }
        await new Promise((r) => setTimeout(r, 2500 * attempt))
      }
    }
    writeFileSync(OUT, JSON.stringify(done, null, 1))
    console.log(`[${Math.min(i + BATCH, todo.length)}/${todo.length}] ok=${ok} fail=${fail}`)
    if (BUDGET_SEC && Date.now() > deadline) {
      console.log('BUDGET REACHED — exiting gracefully')
      break outer
    }
    await new Promise((r) => setTimeout(r, DELAY_MS))
  }
  writeFileSync(OUT, JSON.stringify(done, null, 1))
  console.log('DONE', { ok, fail })
}

main().catch((e) => { console.error(e); process.exit(1) })
