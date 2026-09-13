#!/usr/bin/env python3
"""Enrich products via Chefaa's public Meilisearch API (products_eg):
- real product photos (downloaded locally as webp)
- real descriptions (meta_description_en/ar) for thin descriptions

Matching: search by English name; score hits on token-set Jaccard of
(nameEn + brand) vs (title_en + brand), numeric tokens (mg/counts) weighted.
Resumable: scripts/meili_matches.json
"""
import json, os, re, sys, time, sqlite3, unicodedata
import urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

MEILI = 'https://meilisearch.chefaa.com/indexes/products_eg/search'
KEY = 'd63cccef2eeacd2734bef1c445980b5720de94f5f161bf9d8322a377a0b03536'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0 Safari/537.36'
DB = '/home/z/my-project/db/custom.db'
IMG_DIR = '/home/z/my-project/public/images/products'
OUT = '/home/z/my-project/scripts/meili_matches.json'

def post(url, body, tries=3):
    for t in range(tries):
        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                         headers={'Authorization': f'Bearer {KEY}',
                                                  'Content-Type': 'application/json',
                                                  'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            if t == tries - 1:
                return None
            time.sleep(1.5 * (t + 1))

AR_DIAC = re.compile(r'[\u064B-\u0652\u0640]')
def norm(s):
    if not s: return ''
    s = unicodedata.normalize('NFKC', s)
    s = AR_DIAC.sub('', s)
    for a, b in [('أ', 'ا'), ('إ', 'ا'), ('آ', 'ا'), ('ة', 'ه'), ('ى', 'ي'), ('ؤ', 'و'), ('ئ', 'ي')]:
        s = s.replace(a, b)
    s = s.lower()
    s = re.sub(r'[^a-z0-9\u0600-\u06ff]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

def toks(s):
    return {t for t in norm(s).split() if len(t) > 1}

def nums(s):
    out = set()
    for m in re.finditer(r'(\d+)\s*(mg|ml|gm|g|gr|mcg|tab|tabs|tablet|tablets|amp|ampoules|caps|count|ملجم|قرص|كبسولة)?', norm(s)):
        n, unit = m.group(1), m.group(2) or ''
        if n in ('0', '1'):
            continue
        out.add(f'{n}{unit}')
    return out

def score(ours, hit):
    """ours: dict(nameEn, nameAr, brand); hit: meili hit"""
    our_nt = toks(ours['nameEn'] + ' ' + ours['brand'])
    hit_nt = toks(hit.get('title_en', '') + ' ' + (hit.get('brands') or {}).get('title_en', ''))
    if not our_nt or not hit_nt:
        return 0.0
    jac = len(our_nt & hit_nt) / len(our_nt | hit_nt)
    # brand must match (both directions) for a strong score
    ob = toks(ours['brand'])
    hb = toks((hit.get('brands') or {}).get('title_en', '') + ' ' + (hit.get('brands') or {}).get('title_ar', ''))
    brand_ok = bool(ob & hb) if ob else True
    # numeric/strength tokens must not conflict
    on, hn = nums(ours['nameEn']), nums(hit.get('title_en', ''))
    num_conflict = bool(on and hn and not (on & hn))
    if num_conflict:
        jac *= 0.45
    if not brand_ok:
        jac *= 0.5
    # arabic name bonus
    oat, hat = toks(ours['nameAr']), toks(hit.get('title_ar', ''))
    if oat and hat:
        aj = len(oat & hat) / len(oat | hat)
        jac = max(jac, 0.6 * jac + 0.4 * aj)
    return jac

def search_and_match(p):
    q = p['nameEn']
    res = post(MEILI, {'q': q, 'limit': 8})
    if res is None or not res.get('hits'):
        # fallback: arabic query
        res = post(MEILI, {'q': p['nameAr'], 'limit': 8})
    if res is None or not res.get('hits'):
        return {**p, 'match': None}
    best, best_s = None, 0.0
    for h in res['hits']:
        s = score(p, h)
        if s > best_s:
            best, best_s = h, s
    if best and best_s >= 0.52:
        img = best.get('image') or ''
        if img:
            img = img.replace('/public/uploads/', '/filters:format(webp)/public/uploads/')
        return {**p, 'match': {
            'slug': best.get('slug'), 'score': round(best_s, 3), 'image': img,
            'title_en': best.get('title_en', ''), 'title_ar': best.get('title_ar', ''),
            'desc_en': (best.get('meta_description_en') or '').strip(),
            'desc_ar': (best.get('meta_description_ar') or '').strip(),
            'price': best.get('price'),
        }}
    return {**p, 'match': None}

def main():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    # ALL products (images for missing; descriptions where thin) — search once, use everywhere
    rows = cur.execute("SELECT id, slug, nameEn, nameAr, brand, imageUrl, descEn, descAr FROM Product").fetchall()
    products = [{'id': r[0], 'slug': r[1], 'nameEn': r[2], 'nameAr': r[3], 'brand': r[4],
                 'imageUrl': r[5] or '', 'descEn': r[6] or '', 'descAr': r[7] or ''} for r in rows]
    need = [p for p in products if not p['imageUrl'] or len(p['descEn']) < 400]
    print(f'products needing enrichment: {len(need)} / {len(products)}')

    done = {}
    if os.path.exists(OUT):
        done = {r['slug']: r for r in json.load(open(OUT))}
    todo = [p for p in need if p['slug'] not in done]
    print(f'already matched: {len(done)}, to search: {len(todo)}')

    results = []
    def work(p):
        r = search_and_match(p)
        return r

    n = 0
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs = {ex.submit(work, p): p['slug'] for p in todo}
        for f in as_completed(futs):
            r = f.result()
            results.append(r)
            n += 1
            if n % 30 == 0:
                print(f'{n}/{len(todo)} searched')
    allr = list(done.values()) + results
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(allr, f, ensure_ascii=False, indent=1)
    m = [r for r in allr if r.get('match')]
    print(f'matched total: {len(m)} / {len(allr)}')
    from collections import Counter
    print('score buckets:', Counter(round(r['match']['score'], 1) for r in m))

if __name__ == '__main__':
    main()
