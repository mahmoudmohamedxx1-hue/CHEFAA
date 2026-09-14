#!/usr/bin/env python3
"""Final targeted overrides for products the automated matcher missed:
same-product variants (pack size / plaster=patch / 1g=1000mg / typo'd titles).
Plus retry of failed downloads (Mustela)."""
import json, os, sys, sqlite3
sys.path.insert(0, '/home/z/my-project/scripts')
from enrich_round2 import post, MEILI, download, IMG_DIR

DB = '/home/z/my-project/db/custom.db'
con = sqlite3.connect(DB)
cur = con.cursor()

# our_slug -> meili query expected to return the same product
OVERRIDES = {
    'antinal-capsules-20': 'Antinal diarrhea capsules',
    'kefentech-back-patch-for-pain-relief': 'Kefentech plaster',
    'vitacid-c-1000mg-effervescent-20': 'Vitacid C effervescent',
    'bepanthen-ointment-100g': 'Bepanthen protective baby ointment',
    'mustela-hydra-bebe-body-lotion-300ml': 'Mustela baby hydra bebe body lotion',
    'amoxicillin-500mg-16-capsules': 'Amoxicillin 500mg capsules',
    'redoxon-double-action-30-tablets': 'Redoxon double action',
    'freedent-baby-toothpaste-75ml': 'Freedent baby toothpaste',
    'personal-lubricant-water-based-100ml': 'personal lubricant gel',
    'pregnancy-test-midstream-2-pack': 'pregnancy test midstream',
    'starville-screen-professional-white-top': 'Starville screen sunscreen',
}

UA_OK = 0
for slug, q in OVERRIDES.items():
    row = cur.execute("SELECT id, imageUrl FROM Product WHERE slug=?", (slug,)).fetchone()
    if not row or row[1]:
        continue
    res = post(MEILI, {'q': q, 'limit': 5})
    hits = (res or {}).get('hits', [])
    if not hits:
        print(f'no hits: {slug} ({q})')
        continue
    h = hits[0]
    img = (h.get('image') or '').replace('/public/uploads/', '/filters:format(webp)/public/uploads/')
    if not img:
        print(f'no img: {slug}')
        continue
    ext = '.webp' if 'format(webp)' in img else '.png'
    dest = os.path.join(IMG_DIR, f'{slug}{ext}')
    if (os.path.exists(dest) and os.path.getsize(dest) > 2500) or download(img, dest):
        cur.execute("UPDATE Product SET imageUrl=?, imageSource='chefaa-cdn' WHERE id=?",
                    (f'/images/products/{slug}{ext}', row[0]))
        UA_OK += 1
        print(f'OK {slug} <- {h.get("title_en","")[:50]}')
    else:
        print(f'DOWNLOAD FAIL {slug}')

con.commit()
total = cur.execute("SELECT COUNT(*) FROM Product WHERE imageUrl != ''").fetchone()[0]
still = cur.execute("SELECT COUNT(*) FROM Product WHERE imageUrl=''").fetchone()[0]
print(f'\nimages: {total}/496 | still imageless: {still}')
