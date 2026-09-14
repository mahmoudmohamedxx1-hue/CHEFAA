#!/usr/bin/env python3
"""Apply enrichment: combine Meilisearch + listing-scraper matches,
download real product photos, update DB imageUrls + descriptions."""
import json, os, re, sys, sqlite3, time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

DB = '/home/z/my-project/db/custom.db'
IMG_DIR = '/home/z/my-project/public/images/products'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0 Safari/537.36'

def load(path):
    return json.load(open(path, encoding='utf-8'))

meili = {r['slug']: r for r in load('/home/z/my-project/scripts/meili_matches.json')}
listing = load('/home/z/my-project/scripts/match_report.json')
listing_by_slug = {m['our_slug']: m for m in listing['matched']}

con = sqlite3.connect(DB)
cur = con.cursor()
rows = cur.execute("SELECT id, slug, nameEn, nameAr, descEn, descAr, imageUrl FROM Product").fetchall()
products = {r[1]: {'id': r[0], 'slug': r[1], 'nameEn': r[2], 'nameAr': r[3],
                   'descEn': r[4] or '', 'descAr': r[5] or '', 'imageUrl': r[6] or ''} for r in rows}

def decide_image(p):
    """Return (url, source) for best real image match."""
    slug = p['slug']
    m = meili.get(slug, {}).get('match') if slug in meili else None
    if m and m.get('image') and m['score'] >= 0.52:
        return m['image'], 'chefaa-cdn'
    lm = listing_by_slug.get(slug)
    if lm and lm['score'] >= 0.9:
        return lm['img'], 'chefaa-cdn'
    return None, None

def download(url, dest):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        data = urllib.request.urlopen(req, timeout=30).read()
        if len(data) < 2500:
            return False
        with open(dest, 'wb') as f:
            f.write(data)
        return True
    except Exception:
        return False

def main():
    imageless = [p for p in products.values() if not p['imageUrl']]
    print(f'imageless: {len(imageless)}')
    jobs = []
    for p in imageless:
        url, src = decide_image(p)
        if url:
            ext = os.path.splitext(url.split('?')[0])[1] or '.webp'
            if 'format(webp)' in url: ext = '.webp'
            if ext not in ('.webp', '.png', '.jpg', '.jpeg'):
                ext = '.png'
            dest = os.path.join(IMG_DIR, f"{p['slug']}{ext}")
            jobs.append((p, url, src, dest, f"/images/products/{p['slug']}{ext}"))
    print(f'image jobs: {len(jobs)}')

    ok = fail = 0
    def work(j):
        p, url, src, dest, pub = j
        if os.path.exists(dest) and os.path.getsize(dest) > 2500:
            return (p, pub, src, True)
        return (p, pub, src, download(url, dest))

    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = [ex.submit(work, j) for j in jobs]
        for f in as_completed(futs):
            p, pub, src, success = f.result()
            if success:
                cur.execute("UPDATE Product SET imageUrl=?, imageSource=? WHERE id=?", (pub, src, p['id']))
                ok += 1
            else:
                fail += 1
    con.commit()
    print(f'images downloaded/updated: {ok}, failed: {fail}')

    # descriptions: apply meili real descriptions where ours is thin
    desc_updated = 0
    for slug, r in meili.items():
        m = r.get('match')
        if not m: continue
        p = products.get(slug)
        if not p: continue
        new_en = (m.get('desc_en') or '').strip()
        new_ar = (m.get('desc_ar') or '').strip()
        # use meili desc only if clearly richer than ours
        if len(p['descEn']) < 400 and len(new_en) > 80 and len(new_en) > len(p['descEn']) * 0.7:
            en = new_en if len(new_en) >= len(p['descEn']) else p['descEn']
            ar = new_ar if len(new_ar) >= 60 else p['descAr']
            cur.execute("UPDATE Product SET descEn=?, descAr=? WHERE id=?", (en, ar, p['id']))
            desc_updated += 1
    con.commit()
    print(f'descriptions enriched: {desc_updated}')

    total = cur.execute("SELECT COUNT(*) FROM Product WHERE imageUrl != ''").fetchone()[0]
    rich = cur.execute("SELECT COUNT(*) FROM Product WHERE length(descEn) >= 400").fetchone()[0]
    still = cur.execute("SELECT COUNT(*) FROM Product WHERE imageUrl='' ").fetchone()[0]
    print(f'FINAL: images {total}/496 | rich descriptions {rich} | still imageless {still}')

if __name__ == '__main__':
    main()
