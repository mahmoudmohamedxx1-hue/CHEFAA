#!/usr/bin/env python3
"""Round 2 enrichment: shorter Meili queries (brand + key tokens), brand-required
matching, and retry of failed downloads. Fills remaining imageless products."""
import json, os, re, sys, sqlite3, time, unicodedata
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

MEILI = 'https://meilisearch.chefaa.com/indexes/products_eg/search'
KEY = 'd63cccef2eeacd2734bef1c445980b5720de94f5f161bf9d8322a377a0b03536'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0 Safari/537.36'
DB = '/home/z/my-project/db/custom.db'
IMG_DIR = '/home/z/my-project/public/images/products'
OUT2 = '/home/z/my-project/scripts/meili_round2.json'

STOP = {'for', 'and', 'with', 'the', 'of', 'to', 'new', 'best', 'sale', 'tabs', 'tab',
        'tablets', 'tablet', 'caps', 'capsules', 'pcs', 'pack', 'ml', 'mg', 'gm'}

def post(url, body, tries=3):
    for t in range(tries):
        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                         headers={'Authorization': f'Bearer {KEY}',
                                                  'Content-Type': 'application/json',
                                                  'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.loads(r.read().decode())
        except Exception:
            if t == tries - 1: return None
            time.sleep(1.5 * (t + 1))

def norm(s):
    s = (s or '').lower()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))  # fold accents: é -> e
    s = re.sub(r"['’`]", '', s)  # l'oreal -> loreal (apostrophes only)
    s = re.sub(r'[^a-z0-9\u0600-\u06ff]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

NUMUNIT = re.compile(r'^((?:\d+)?(?:\.\d+)?)((?:mg|ml|gm|gr|g|mcg|iu|%)?)$')

def toks(s):
    """Tokenize; expand fused number-unit tokens (180mg -> 180, mg)."""
    out = set()
    for t in norm(s).split():
        m = NUMUNIT.match(t)
        if m and m.group(1):
            num, unit = m.group(1), m.group(2)
            if num not in STOP:
                out.add(num)
            if unit and len(unit) > 1 and unit not in STOP:
                out.add(unit)
            continue
        if len(t) > 1 and t not in STOP:
            out.add(t)
    return out

GENERIC_BRANDS = {'generic', 'natural', 'none', '', 'various'}

def key_query(name, brand):
    """brand + first significant tokens of name (not already in brand)"""
    bt = toks(brand)
    nt = [t for t in norm(name).split() if t not in STOP and t not in bt and len(t) > 1]
    if norm(brand) in GENERIC_BRANDS:
        return ' '.join(nt[:4]).strip()  # generic brand: query by name only
    return (brand + ' ' + ' '.join(nt[:3])).strip()

UNIT_CANON = {'gm': 'g', 'gr': 'g', 'g': 'g', 'mg': 'mg', 'ml': 'ml', 'mcg': 'mcg', 'iu': 'iu', '%': '%'}

def strength_nums(s):
    """Canonicalized strength markers: 1gm == 1g. Bare pack counts excluded."""
    t = norm(s)
    out = set()
    for m in re.finditer(r'(\d+(?:\.\d+)?)\s*(mg|ml|gm|gr|g|mcg|iu|%)', t):
        out.add(f'{m.group(1)}{UNIT_CANON[m.group(2)]}')
    for m in re.finditer(r'\b(\d\.\d{1,2})\b', t):  # dye shade codes 5.13 / 4.15
        out.add(m.group(1))
    return out

def match_ok(p, h, strict=True):
    """Brand must match (brands field OR brand token in hit title);
    distinguishing name tokens must appear in hit; STRENGTH numbers must agree
    (bare pack counts may differ — same product, same photo)."""
    our = toks(p['nameEn']) | toks(p['brand'])
    hb = (h.get('brands') or {})
    hit_t = toks(h.get('title_en', '') + ' ' + h.get('title_ar', '') + ' ' + hb.get('title_en', '') + ' ' + hb.get('title_ar', ''))
    bt = toks(p['brand'])
    hbt = toks((hb.get('title_en') or '') + ' ' + (hb.get('title_ar') or ''))
    if norm(p['brand']) in GENERIC_BRANDS:
        brand_ok = True  # generic brand: no brand evidence possible; rely on dist tokens (2+ required below)
    else:
        # brand evidence: brands field, brand token in title, OR our product's
        # own name-word in title (unbranded listing of same product, e.g. Bayer
        # Aspirin -> "Aspirin Protect 100mg"); strength check still guards this.
        name_words = [t for t in norm(p['nameEn']).split() if len(t) > 1 and t not in STOP]
        first_word = {name_words[0]} if name_words else set()
        brand_ok = (bool(bt & hbt) or bool(bt & hit_t) or bool(first_word & hit_t)) if bt else False
    if not brand_ok:
        return False
    # distinguishing tokens from our name (excluding brand)
    dist = toks(p['nameEn']) - bt
    if not dist:
        return False
    hits_int = dist & hit_t
    # require at least half of distinguishing tokens (min 1), and never match on 0
    if len(hits_int) < max(1, min(2, len(dist) // 2 + (1 if len(dist) == 1 else 0))):
        return False
    if not hits_int:
        return False
    # strength agreement: canonicalized units must not conflict. Soft rule:
    # reject only when NO number matches at all (e.g. 625 vs 1); if the bare
    # number matches but the unit differs (50ml vs 50gm), accept — same photo.
    our_s = strength_nums(p['nameEn'])
    hit_s = strength_nums(h.get('title_en', '') + ' ' + h.get('title_ar', ''))
    if our_s and hit_s and not (our_s & hit_s):
        our_n = {v.rstrip('mgliu%') for v in our_s}
        hit_n = {v.rstrip('mgliu%') for v in hit_s}
        if not (our_n & hit_n):
            return False
    # generic-brand products: require 2+ distinguishing token matches for safety
    if norm(p['brand']) in GENERIC_BRANDS:
        if len(hits_int) < 2:
            return False
    return True

def name_only_query(p):
    bt = toks(p['brand'])
    nt = [t for t in norm(p['nameEn']).split() if t not in STOP and t not in bt and len(t) > 1]
    return ' '.join(nt[:4]).strip()

def search(p):
    queries = [key_query(p['nameEn'], p['brand']), name_only_query(p), p['nameAr'], toks_str(p['brand'] + ' ' + p['nameEn'])]
    seen = set()
    for q in queries:
        if not q or q in seen: continue
        seen.add(q)
        res = post(MEILI, {'q': q, 'limit': 10})
        if not res or not res.get('hits'): continue
        for h in res['hits']:
            if match_ok(p, h):
                img = (h.get('image') or '').replace('/public/uploads/', '/filters:format(webp)/public/uploads/')
                if img:
                    return {'slug': p['slug'], 'query': q, 'image': img,
                            'title_en': h.get('title_en', ''), 'title_ar': h.get('title_ar', ''),
                            'desc_en': (h.get('meta_description_en') or '').strip(),
                            'desc_ar': (h.get('meta_description_ar') or '').strip(),
                            'price': h.get('price')}
    return {'slug': p['slug'], 'image': None}

def toks_str(s):
    return ' '.join(sorted(toks(s))[:6])

def download(url, dest):
    for u in ([url, url.replace('/filters:format(webp)/', '/')] if 'format(webp)' in url else [url]):
        try:
            req = urllib.request.Request(u, headers={'User-Agent': UA})
            data = urllib.request.urlopen(req, timeout=30).read()
            if len(data) > 2500:
                with open(dest, 'wb') as f: f.write(data)
                return True
        except Exception:
            continue
    return False

def main():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    rows = cur.execute("SELECT id, slug, nameEn, nameAr, brand FROM Product WHERE imageUrl='' OR imageUrl IS NULL").fetchall()
    products = [{'id': r[0], 'slug': r[1], 'nameEn': r[2], 'nameAr': r[3], 'brand': r[4]} for r in rows]
    print(f'imageless to fill: {len(products)}')

    done = {}
    if os.path.exists(OUT2):
        done = {r['slug']: r for r in json.load(open(OUT2)) if not r.get('image')}
        done = {r['slug']: r for r in json.load(open(OUT2))}
    todo = [p for p in products if p['slug'] not in done]
    print(f'to search: {len(todo)}')

    results = []
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs = [ex.submit(search, p) for p in todo]
        for i, f in enumerate(as_completed(futs)):
            results.append(f.result())
            if (i + 1) % 25 == 0: print(f'{i+1}/{len(todo)}')
    allr = list(done.values()) + results
    json.dump(allr, open(OUT2, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    matched = [r for r in allr if r.get('image')]
    print(f'round2 matched: {len(matched)}')

    ok = fail = 0
    for r in matched:
        p = next((x for x in products if x['slug'] == r['slug']), None)
        if not p:
            cur2 = con.cursor()
            row = cur2.execute("SELECT id FROM Product WHERE slug=?", (r['slug'],)).fetchone()
            if not row: continue
            p = {'id': row[0]}
        ext = '.webp' if 'format(webp)' in r['image'] else (os.path.splitext(r['image'])[1] or '.png')
        dest = os.path.join(IMG_DIR, f"{r['slug']}{ext}")
        if (os.path.exists(dest) and os.path.getsize(dest) > 2500) or download(r['image'], dest):
            cur.execute("UPDATE Product SET imageUrl=?, imageSource='chefaa-cdn' WHERE id=?",
                        (f"/images/products/{r['slug']}{ext}", p['id']))
            # also apply real description if notably richer than nothing
            cur.execute("UPDATE Product SET descEn=CASE WHEN length(descEn)<150 AND length(?)>80 THEN ? ELSE descEn END, descAr=CASE WHEN length(descAr)<150 AND length(?)>60 THEN ? ELSE descAr END WHERE id=?",
                        (r.get('desc_en', ''), r.get('desc_en', ''), r.get('desc_ar', ''), r.get('desc_ar', ''), p['id']))
            ok += 1
        else:
            fail += 1
    con.commit()
    still = cur.execute("SELECT COUNT(*) FROM Product WHERE imageUrl=''").fetchone()[0]
    total = cur.execute("SELECT COUNT(*) FROM Product WHERE imageUrl != ''").fetchone()[0]
    print(f'downloaded: {ok}, failed: {fail} | images now {total}/496, still imageless: {still}')

if __name__ == '__main__':
    main()
