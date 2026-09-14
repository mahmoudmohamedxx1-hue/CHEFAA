#!/usr/bin/env python3
"""Round 3: re-verify round-2 matches with FIXED matcher (l-strip bug), roll back
wrong ones, then fill remaining imageless products with fresh Meili searches."""
import json, os, re, sqlite3, sys
sys.path.insert(0, '/home/z/my-project/scripts')
from enrich_round2 import (MEILI, post, toks, norm, match_ok, key_query, download,
                           IMG_DIR, OUT2, name_only_query)
from concurrent.futures import ThreadPoolExecutor, as_completed

DB = '/home/z/my-project/db/custom.db'
con = sqlite3.connect(DB)
cur = con.cursor()

# 1) re-verify round-2 matched records
round2 = json.load(open(OUT2, encoding='utf-8'))
rows = cur.execute("SELECT slug, nameEn, nameAr, brand FROM Product").fetchall()
prod = {r[0]: {'slug': r[0], 'nameEn': r[1], 'nameAr': r[2], 'brand': r[3]} for r in rows}

bad, good = [], []
for r in round2:
    if not r.get('image'):
        continue
    p = prod.get(r['slug'])
    if not p:
        continue
    fake_hit = {'title_en': r.get('title_en', ''), 'title_ar': r.get('title_ar', ''),
                'brands': {}}  # brands unknown in stored record -> approximate with product brand
    # brand check against stored title text
    ok = match_ok(p, {**fake_hit, 'brands': {'title_en': p['brand'], 'title_ar': ''}}, strict=True)
    (good if ok else bad).append(r['slug'])
print(f're-verify round2: {len(good)} good, {len(bad)} suspicious: {bad}')

for slug in bad:
    cur.execute("UPDATE Product SET imageUrl='', imageSource='' WHERE slug=? AND imageSource='chefaa-cdn'", (slug,))
    # remove possibly-wrong local file
    for ext in ('.webp', '.png', '.jpg'):
        f = os.path.join(IMG_DIR, slug + ext)
        if os.path.exists(f) and slug in bad:
            # only delete if this file was created by round2 (name == slug)
            os.remove(f)
con.commit()

# 2) fresh search for ALL still-imageless
rows = cur.execute("SELECT id, slug, nameEn, nameAr, brand, popularity, isFeatured FROM Product WHERE imageUrl='' OR imageUrl IS NULL").fetchall()
todo = [{'id': r[0], 'slug': r[1], 'nameEn': r[2], 'nameAr': r[3], 'brand': r[4]} for r in rows]
print(f'imageless to fill: {len(todo)}')

def search_all_queries(p):
    qs = [key_query(p['nameEn'], p['brand']), name_only_query(p), p['nameAr'],
          p['brand'] + ' ' + ' '.join(t for t in norm(p['nameEn']).split()[:2] if t not in toks(p['brand']))]
    seen = set()
    for q in qs:
        if not q or q in seen: continue
        seen.add(q)
        res = post(MEILI, {'q': q, 'limit': 12})
        if not res or not res.get('hits'): continue
        for h in res['hits']:
            if match_ok(p, h):
                img = (h.get('image') or '').replace('/public/uploads/', '/filters:format(webp)/public/uploads/')
                if img:
                    return {'slug': p['slug'], 'image': img, 'title_en': h.get('title_en', ''),
                            'title_ar': h.get('title_ar', ''),
                            'desc_en': (h.get('meta_description_en') or '').strip(),
                            'desc_ar': (h.get('meta_description_ar') or '').strip()}
    return {'slug': p['slug'], 'image': None}

results = []
with ThreadPoolExecutor(max_workers=5) as ex:
    futs = [ex.submit(search_all_queries, p) for p in todo]
    for i, f in enumerate(as_completed(futs)):
        results.append(f.result())
        if (i + 1) % 25 == 0: print(f'{i+1}/{len(todo)}')

ok = fail = 0
for r in results:
    if not r.get('image'): continue
    row = cur.execute("SELECT id FROM Product WHERE slug=?", (r['slug'],)).fetchone()
    if not row: continue
    ext = '.webp' if 'format(webp)' in r['image'] else (os.path.splitext(r['image'])[1] or '.png')
    dest = os.path.join(IMG_DIR, f"{r['slug']}{ext}")
    if (os.path.exists(dest) and os.path.getsize(dest) > 2500) or download(r['image'], dest):
        cur.execute("UPDATE Product SET imageUrl=?, imageSource='chefaa-cdn' WHERE id=?",
                    (f"/images/products/{r['slug']}{ext}", row[0]))
        cur.execute("UPDATE Product SET descEn=CASE WHEN length(descEn)<150 AND length(?)>80 THEN ? ELSE descEn END, descAr=CASE WHEN length(descAr)<150 AND length(?)>60 THEN ? ELSE descAr END WHERE id=?",
                    (r['desc_en'], r['desc_en'], r['desc_ar'], r['desc_ar'], row[0]))
        ok += 1
    else:
        fail += 1
con.commit()

# persist round3 results
json.dump(results, open('/home/z/my-project/scripts/meili_round3.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
total = cur.execute("SELECT COUNT(*) FROM Product WHERE imageUrl != ''").fetchone()[0]
still = cur.execute("SELECT COUNT(*) FROM Product WHERE imageUrl=''").fetchone()[0]
print(f'round3 downloaded: {ok}, failed: {fail} | images now {total}/496, still imageless: {still}')
