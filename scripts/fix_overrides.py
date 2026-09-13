#!/usr/bin/env python3
"""Correct wrong override picks + retry Mustela with alternate URL form."""
import os, sys, sqlite3
sys.path.insert(0, '/home/z/my-project/scripts')
from enrich_round2 import post, MEILI, IMG_DIR
import urllib.request

DB = '/home/z/my-project/db/custom.db'
con = sqlite3.connect(DB)
cur = con.cursor()
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0'

def rollback(slug):
    cur.execute("UPDATE Product SET imageUrl='', imageSource='' WHERE slug=?", (slug,))
    for ext in ('.webp', '.png', '.jpg'):
        f = os.path.join(IMG_DIR, slug + ext)
        if os.path.exists(f):
            os.remove(f)
    print(f'rolled back {slug}')

def apply(slug, title_must, query, title_must_not=()):
    row = cur.execute("SELECT id FROM Product WHERE slug=?", (slug,)).fetchone()
    if not row:
        return
    res = post(MEILI, {'q': query, 'limit': 10})
    for h in (res or {}).get('hits', []):
        t = h.get('title_en', '') or ''
        if all(m.lower() in t.lower() for m in title_must) and not any(m.lower() in t.lower() for m in title_must_not):
            img = (h.get('image') or '').replace('/public/uploads/', '/filters:format(webp)/public/uploads/')
            if not img:
                continue
            ext = '.webp' if 'format(webp)' in img else '.png'
            dest = os.path.join(IMG_DIR, f'{slug}{ext}')
            ok = False
            if os.path.exists(dest) and os.path.getsize(dest) > 2500:
                ok = True
            else:
                for u in (img, img.replace('/filters:format(webp)/', '/')):
                    try:
                        req = urllib.request.Request(u, headers={'User-Agent': UA})
                        data = urllib.request.urlopen(req, timeout=30).read()
                        if len(data) > 2500:
                            open(dest, 'wb').write(data)
                            ok = True
                            break
                    except Exception:
                        continue
            if ok:
                cur.execute("UPDATE Product SET imageUrl=?, imageSource='chefaa-cdn' WHERE id=?",
                            (f'/images/products/{slug}{ext}', row[0]))
                print(f'OK {slug} <- {t[:55]}')
                return
    print(f'FAIL {slug}')

# wrong picks -> rollback
rollback('amoxicillin-500mg-16-capsules')   # Curam is amox+clav, not plain amoxicillin
rollback('redoxon-double-action-30-tablets')  # plain Vit C 1000, not Double Action
rollback('starville-screen-professional-white-top')  # acne cream, not sunscreen

# re-pick correctly
apply('antinal-capsules-20', ['200mg', 'cap'], 'Antinal 200mg', title_must_not=['syrup', 'ml'])
apply('bepanthen-ointment-100g', ['ointment'], 'Bepanthen ointment', title_must_not=['cream', 'lotion'])
apply('mustela-hydra-bebe-body-lotion-300ml', ['body lotion', '300'], 'Mustela baby hydra bebe body lotion 300ml')

con.commit()
total = cur.execute("SELECT COUNT(*) FROM Product WHERE imageUrl != ''").fetchone()[0]
still = cur.execute("SELECT COUNT(*) FROM Product WHERE imageUrl=''").fetchone()[0]
print(f'\nimages: {total}/496 | still imageless: {still}')
