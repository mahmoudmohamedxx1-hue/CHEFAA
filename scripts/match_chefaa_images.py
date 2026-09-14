#!/usr/bin/env python3
"""Match our products missing images against scraped Chefaa catalog by normalized Arabic name.
Dry-run mode prints match stats; --apply downloads images and updates DB.
"""
import re, json, os, sys, sqlite3, unicodedata
import urllib.request

CACHE = '/home/z/my-project/scripts/chefaa_catalog_cache.jsonl'
DB = '/home/z/my-project/db/custom.db'
IMG_DIR = '/home/z/my-project/public/images/products'

AR_DIAC = re.compile(r'[\u064B-\u0652\u0640]')
def norm(s):
    if not s: return ''
    s = unicodedata.normalize('NFKC', s)
    s = AR_DIAC.sub('', s)
    s = s.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
    s = s.replace('ة', 'ه').replace('ى', 'ي').replace('ؤ', 'و').replace('ئ', 'ي')
    s = re.sub(r'[^\w\sآا-ي]', ' ', s, flags=re.UNICODE)
    s = re.sub(r'\s+', ' ', s).strip().lower()
    return s

def tokens(s):
    stop = {'و', 'من', 'لل', 'مع', 'في', 'علي', 'على', 'الي', 'الى'}
    return {t for t in norm(s).split() if len(t) > 1 and t not in stop}

def load_catalog():
    prods = {}
    for line in open(CACHE, encoding='utf-8'):
        try:
            rec = json.loads(line)
        except Exception:
            continue
        if rec.get('type') == 'page':
            for slug, p in rec.get('products', {}).items():
                prods[slug] = p
    return prods

def main(apply=False):
    catalog = load_catalog()
    print(f'catalog: {len(catalog)} unique products')
    # index by normalized name
    by_norm = {}
    for slug, p in catalog.items():
        by_norm.setdefault(norm(p['name']), []).append(slug)

    con = sqlite3.connect(DB)
    cur = con.cursor()
    missing = cur.execute("SELECT id, slug, nameEn, nameAr, brand, categoryId FROM Product WHERE imageUrl='' OR imageUrl IS NULL").fetchall()
    print(f'our products missing images: {len(missing)}')

    results, unmatched = [], []
    for pid, slug, ne, na, brand, cid in missing:
        n = norm(na)
        best = None
        # tier 1: exact
        if n and n in by_norm:
            cands = by_norm[n]
            best = (1.0, cands[0])
        else:
            # tier 2: startswith / token overlap
            nt = tokens(na)
            best_score, best_slug = 0.0, None
            for cn, slugs in by_norm.items():
                ct = set(cn.split())
                if not ct or not nt: continue
                # quick filter: share >= 2 tokens or first token
                inter = nt & ct
                if not inter: continue
                if na and cn.startswith(n[:12]) or n.startswith(cn[:12]):
                    score = 0.9
                else:
                    score = len(inter) / max(1, len(nt | ct))
                if score > best_score:
                    best_score, best_slug = score, slugs[0]
            if best_score >= 0.55:
                best = (best_score, best_slug)
        if best:
            results.append((pid, slug, best[1], best[0], catalog[best[1]]['img']))
        else:
            unmatched.append((slug, ne, na, brand))

    print(f'matched: {len(results)}  unmatched: {len(unmatched)}')
    scores = [r[3] for r in results]
    from collections import Counter
    print('score buckets:', Counter(round(s, 1) for s in scores))

    # save match report
    with open('/home/z/my-project/scripts/match_report.json', 'w', encoding='utf-8') as f:
        json.dump({'matched': [{'our_slug': r[1], 'chefaa_slug': r[2], 'score': round(r[3], 2), 'img': r[4]} for r in results],
                   'unmatched': [{'slug': u[0], 'nameEn': u[1], 'nameAr': u[2], 'brand': u[3]} for u in unmatched]},
                  f, ensure_ascii=False, indent=1)

    if not apply:
        for u in unmatched[:25]:
            print('UNMATCHED:', u[1], '|', u[2][:50], '|', u[3])
        return

    # download images + update DB
    UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0 Safari/537.36'
    ok = fail = 0
    for pid, slug, cslug, score, img in results:
        if score < 0.99 and score < 0.55:
            continue
        ext = '.webp' if 'format(webp)' in img or img.endswith('.webp') else os.path.splitext(img)[1] or '.png'
        dest = os.path.join(IMG_DIR, f'{slug}{ext}')
        if not os.path.exists(dest):
            try:
                req = urllib.request.Request(img, headers={'User-Agent': UA})
                data = urllib.request.urlopen(req, timeout=30).read()
                if len(data) < 3000:
                    fail += 1; continue
                with open(dest, 'wb') as f:
                    f.write(data)
            except Exception as e:
                print(f'DL FAIL {slug}: {e}')
                fail += 1
                continue
        ok += 1
        cur.execute("UPDATE Product SET imageUrl=?, imageSource='chefaa-cdn' WHERE id=?",
                    (f'/images/products/{slug}{ext}', pid))
        if ok % 40 == 0:
            con.commit()
    con.commit()
    print(f'downloaded {ok}, failed {fail}')
    total = cur.execute("SELECT COUNT(*) FROM Product WHERE imageUrl != ''").fetchone()[0]
    print(f'products with images now: {total}/496')

if __name__ == '__main__':
    main('--apply' in sys.argv)
