/**
 * Generate professional bilingual (EN/AR) pharmacy product descriptions
 * for all products with thin descriptions, via z-ai-web-dev-sdk LLM.
 * Batches of 8, 3 concurrent workers, resumable via progress file.
 */
import { Database } from 'bun:sqlite';
import ZAI from 'z-ai-web-dev-sdk';

const DB_PATH = '/home/z/my-project/db/custom.db';
const PROGRESS = '/home/z/my-project/scripts/desc_progress.json';

const db = new Database(DB_PATH);
const rows = db
  .query(
    `SELECT p.slug, p.nameEn, p.nameAr, p.brand, p.descEn, p.descAr, p.volume,
            p.prescriptionRequired, c.nameEn as catEn
     FROM Product p JOIN Category c ON p.categoryId = c.id
     WHERE length(p.descEn) < 400 OR length(p.descAr) < 250`
  )
  .all() as any[];

console.log(`products needing descriptions: ${rows.length}`);

let progress: Record<string, { en: string; ar: string }> = {};
try {
  progress = JSON.parse(await Bun.file(PROGRESS).text());
} catch {}
const todo = rows.filter((r) => !progress[r.slug]);
console.log(`to generate: ${todo.length} (already done: ${rows.length - todo.length})`);

const SYSTEM = `You are a senior copywriter for "The Pharmacy", a licensed Egyptian online pharmacy. Write product descriptions in the style of leading pharmacy e-commerce sites (Boots, Watsons, Chefaa).

Rules:
- English description (descEn): 55-85 words, 2 short paragraphs max. Cover: what the product is, its key benefits/uses, brief usage guidance.
- Arabic description (descAr): Modern Standard Arabic with Egyptian retail warmth, equivalent content to the English (not a literal translation), 50-80 words.
- Use established OTC/pharmacy language. No exaggerated medical claims. For prescription items, mention that a prescription is required and to consult a doctor or pharmacist.
- Rely on the product name, brand, category, and existing notes. If a detail is unknown, write generically — never invent specific clinical statistics.
- Do NOT repeat the product name more than once. No markdown, no bullet points, no emojis.
- Respond with STRICT JSON only: an array of objects [{"slug":"...","descEn":"...","descAr":"..."}]. No commentary, no code fences.`;

function buildBatch(batch: any[]): string {
  const items = batch
    .map(
      (r) =>
        `slug: ${r.slug}\nname: ${r.nameEn} | ${r.nameAr}\nbrand: ${r.brand}\ncategory: ${r.catEn}\nvolume: ${r.volume || 'n/a'}\nprescription: ${r.prescriptionRequired ? 'yes' : 'no'}\nexisting notes: ${(r.descEn || '').slice(0, 220)}`
    )
    .join('\n---\n');
  return `Write descriptions for these ${batch.length} products:\n\n${items}`;
}

function parseJSON(text: string): any[] {
  let t = text.trim();
  t = t.replace(/^```(?:json)?\s*/i, '').replace(/```\s*$/, '');
  const start = t.indexOf('[');
  const end = t.lastIndexOf(']');
  if (start >= 0 && end > start) t = t.slice(start, end + 1);
  return JSON.parse(t);
}

async function processBatch(zai: any, batch: any[]): Promise<number> {
  let lastErr: any;
  let wait = 45_000; // patient: 429 likely service-wide; wait and retry
  for (let attempt = 0; attempt < 8; attempt++) {
    try {
      const completion = await zai.chat.completions.create({
        messages: [
          { role: 'assistant', content: SYSTEM },
          { role: 'user', content: buildBatch(batch) },
        ],
        thinking: { type: 'disabled' },
      });
      const raw = completion.choices[0]?.message?.content || '';
      const arr = parseJSON(raw);
      let n = 0;
      for (const item of arr) {
        if (item?.slug && typeof item.descEn === 'string' && typeof item.descAr === 'string'
            && item.descEn.length > 120 && item.descAr.length > 80) {
          progress[item.slug] = { en: item.descEn.trim(), ar: item.descAr.trim() };
          n++;
        }
      }
      if (n > 0) return n;
      throw new Error('no valid items in response');
    } catch (e: any) {
      lastErr = e;
      const is429 = String(e?.message || '').includes('429');
      if (is429) {
        console.log(`429 rate-limited, waiting ${wait / 1000}s...`);
        await new Promise((r) => setTimeout(r, wait));
        wait = Math.min(wait * 1.5, 240_000);
        attempt--; // 429 doesn't count as a failed attempt (capped by wall time)
        continue;
      }
      await new Promise((r) => setTimeout(r, 2000 * (attempt + 1)));
    }
  }
  console.error('batch failed:', lastErr?.message);
  return 0;
}

// run 3 concurrent workers over batches of 8
const BATCH = 8;
const batches: any[][] = [];
for (let i = 0; i < todo.length; i += BATCH) batches.push(todo.slice(i, i + BATCH));

let done = 0;
const queue = [...batches];
const workers = Array.from({ length: 3 }, async () => {
  const zai = await ZAI.create();
  while (queue.length) {
    const b = queue.shift()!;
    const n = await processBatch(zai, b);
    done++;
    if (done % 5 === 0) {
      console.log(`${done}/${batches.length} batches, ${Object.keys(progress).length} descriptions`);
      await Bun.write(PROGRESS, JSON.stringify(progress));
    }
  }
});
await Promise.all(workers);
await Bun.write(PROGRESS, JSON.stringify(progress));
console.log(`generated: ${Object.keys(progress).length} descriptions`);

// write to DB
const stmt = db.query('UPDATE Product SET descEn = ?, descAr = ? WHERE slug = ?');
let updated = 0;
db.transaction(() => {
  for (const [slug, d] of Object.entries(progress)) {
    if (d.en.length > 120 && d.ar.length > 80) {
      stmt.run(d.en, d.ar, slug);
      updated++;
    }
  }
})();
console.log(`DB updated: ${updated}`);
