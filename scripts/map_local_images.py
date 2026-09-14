#!/usr/bin/env python3
"""Map unmapped local product images to DB products by slug, and list products missing images by priority."""
import sqlite3, os, glob, json, re

DB = '/home/z/my-project/db/custom.db'
IMG_DIR = '/home/z/my-project/public/images/products'

con = sqlite3.connect(DB)
cur = con.cursor()
rows = cur.execute("SELECT id, slug, nameEn, nameAr, brand, imageUrl, popularity, isFeatured, categoryId, descEn FROM Product").fetchall()
cats = dict(cur.execute("SELECT id, slug FROM Category").fetchall())
cat_order = {cid: cats[cid] for cid in cats}

# slug -> (id, imageUrl)
by_slug = {r[1]: r for r in rows}

# Existing files on disk
files = {}
for f in glob.glob(os.path.join(IMG_DIR, '*.*')):
    base = os.path.splitext(os.path.basename(f))[0]
    ext = os.path.splitext(f)[1]
    files[base] = ext

# 1) Map files not referenced in DB
mapped_urls = {r[5] for r in rows if r[5]}
unmapped_files, remapped = [], 0
for base, ext in files.items():
    url = f'/images/products/{base}{ext}'
    if url not in mapped_urls:
        unmapped_files.append((base, ext))

new_mappings = []
for base, ext in unmapped_files:
    # try exact slug
    if base in by_slug and not by_slug[base][5]:
        new_mappings.append((f'/images/products/{base}{ext}', base))
    else:
        # try slug prefix match (file names sometimes truncated)
        cands = [s for s in by_slug if not by_slug[s][5] and (s.startswith(base) or base.startswith(s))]
        if cands:
            best = max(cands, key=len)
            new_mappings.append((f'/images/products/{base}{ext}', best))

print(f'Unmapped files on disk: {len(unmapped_files)}')
print(f'New slug mappings found: {len(new_mappings)}')

for url, slug in new_mappings:
    cur.execute("UPDATE Product SET imageUrl=?, imageSource='chefaa-scrape' WHERE slug=?", (url, slug))
con.commit()

# 2) Products still missing images, priority-sorted
missing = [r for r in cur.execute("SELECT id, slug, nameEn, nameAr, brand, popularity, isFeatured, categoryId, descEn FROM Product WHERE imageUrl='' OR imageUrl IS NULL").fetchall()]
def prio(r):
    return (not r[6], -r[5])  # featured first, then popularity desc
missing.sort(key=prio)

print(f'Still missing images: {len(missing)}')
by_cat = {}
for r in missing:
    c = cats.get(r[7], '?')
    by_cat[c] = by_cat.get(c, 0) + 1
print('Missing by category:', json.dumps(by_cat, indent=1))

out = [{'id': r[0], 'slug': r[1], 'nameEn': r[2], 'nameAr': r[3], 'brand': r[4], 'popularity': r[5],
        'featured': bool(r[6]), 'cat': cats.get(r[7], '?'), 'descLen': len(r[8] or '')} for r in missing]
with open('/home/z/my-project/scripts/missing_images.json', 'w') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

# also export thin descriptions (<400 chars) for enrichment
thin = [r for r in cur.execute("SELECT id, slug, nameEn, nameAr, brand, descEn, descAr, volume, categoryId FROM Product WHERE length(descEn) < 400").fetchall()]
print(f'Thin descriptions (<400 chars EN): {len(thin)}')
thin_out = [{'id': r[0], 'slug': r[1], 'nameEn': r[2], 'nameAr': r[3], 'brand': r[4], 'descEn': r[5], 'descAr': r[6], 'volume': r[7], 'cat': cats.get(r[8], '?')} for r in thin]
with open('/home/z/my-project/scripts/thin_descriptions.json', 'w') as f:
    json.dump(thin_out, f, ensure_ascii=False, indent=1)
print('Wrote scripts/missing_images.json and scripts/thin_descriptions.json')
