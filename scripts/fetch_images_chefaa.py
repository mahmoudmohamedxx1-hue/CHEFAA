#!/usr/bin/env python3
"""Fetch real product images from Chefaa's public search API (by Arabic name).

- Searches chefaa.com/api/products?search=<nameAr>
- Fuzzy-matches candidates against our product name (normalized token overlap)
- Downloads the best match's first image locally
- Resumable via the same scripts/image_manifest.json (source: chefaa.com)
- Polite pacing: ~1.5s between requests
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

BASE = '/home/z/my-project'
IMG_DIR = f'{BASE}/public/images/products'
MANIFEST = f'{BASE}/scripts/image_manifest.json'
EXPORT = f'{BASE}/scripts/products_export.json'

API = 'https://chefaa.com/api/products?search='
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36'
DELAY = 1.5
REQUEST_TIMEOUT = 20

os.makedirs(IMG_DIR, exist_ok=True)

STOPWORDS = {'و', 'في', 'من', 'مع', 'لل', 'مل', 'مللي', 'جم', 'مجم', 'قرص', 'أقراص', 'اقراص',
             'كبسولة', 'كبسولات', 'قطرة', 'شراب', 'امبول', 'انبولة', 'لتر', 'علبة', 'شريط'}


def norm_tokens(s):
    s = str(s or '')
    s = re.sub(r'[\|\–\-—/,]+', ' ', s)
    s = re.sub(r'[۰-۹0-9]+', ' ', s)
    # unify Arabic variants
    s = s.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
    s = s.replace('ى', 'ي').replace('ة', 'ه').replace('ـ', '')
    s = re.sub(r'[^\u0600-\u06FFa-zA-Z\s]', ' ', s)
    toks = [t for t in s.split() if len(t) > 1 and t not in STOPWORDS]
    return toks


def overlap_score(our_toks, their_toks):
    if not our_toks:
        return 0.0
    theirs = set(their_toks)
    hits = sum(1 for t in our_toks if t in theirs)
    return hits / len(our_toks)


def http_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as r:
        return json.loads(r.read().decode('utf-8'))


def http_bytes(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Referer': 'https://chefaa.com/'})
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as r:
        return r.read(12 * 1024 * 1024)


def img_magic_ok(head):
    if head[:3] == b'\xff\xd8\xff':
        return 'jpg'
    if head[:8] == b'\x89PNG\r\n\x1a\n':
        return 'png'
    if head[:4] == b'RIFF' and head[8:12] == b'WEBP':
        return 'webp'
    return None


def main():
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 0
    deadline = time.time() + budget if budget > 0 else None

    products = json.load(open(EXPORT))
    manifest = json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else {}

    def have_img(p):
        m = manifest.get(p['slug'])
        return m and m.get('ok') and os.path.exists(m.get('path', ''))

    todo = [p for p in products if not have_img(p)]
    print(f'products needing images: {len(todo)}', flush=True)

    stats = {'ok': 0, 'nomatch': 0, 'err': 0}
    t0 = time.time()
    for idx, p in enumerate(todo):
        if deadline and time.time() > deadline:
            print('BUDGET REACHED', flush=True)
            break
        slug = p['slug']
        try:
            # Chefaa search is phrase-based: use the descriptive part of the
            # Arabic name (after the brand pipe), never mix in the brand itself
            parts = [x.strip() for x in p['nameAr'].split('|')]
            desc = parts[1] if len(parts) >= 2 else p['nameAr']
            toks = norm_tokens(desc)[:5]
            if not toks:
                toks = norm_tokens(p['nameAr'])[:4]
            if not toks:
                stats['nomatch'] += 1
                continue

            # progressive fallbacks: 5 tokens -> 3 -> 2 -> brand-in-arabic
            items = []
            for qt in (toks, toks[:3], toks[:2]):
                if not qt:
                    continue
                q = urllib.parse.quote(' '.join(qt))
                data = http_json(API + q)
                time.sleep(DELAY)
                items = data.get('data') or []
                if items:
                    break
            if not items and norm_tokens(p.get('brand', '')):
                q = urllib.parse.quote(' '.join(norm_tokens(p['brand'])[:2]))
                data = http_json(API + q)
                time.sleep(DELAY)
                items = data.get('data') or []

            our_toks = norm_tokens(f"{p.get('brand','')} {p['nameAr']}")
            best, best_s = None, 0.0
            second_s = 0.0
            for it in items:
                s = overlap_score(our_toks, norm_tokens(it.get('title', '')))
                if s > best_s:
                    second_s = best_s
                    best_s, best = s, it
                elif s > second_s:
                    second_s = s

            # accept a confident match: decent overlap, or clear winner
            confident = best_s >= 0.55 or (best_s >= 0.4 and best_s - second_s >= 0.2)
            if not best or not confident or not best.get('images'):
                manifest[slug] = {'ok': False, 'source': 'chefaa-api', 'reason': f'no confident match (best={best_s:.2f})'}
                stats['nomatch'] += 1
                continue

            img_url = best['images'][0]
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            data_bytes = http_bytes(img_url)
            time.sleep(0.4)
            if len(data_bytes) < 3000:
                raise ValueError('image too small')
            ext = img_magic_ok(data_bytes[:16])
            if not ext:
                raise ValueError('not an image')
            path = f'{IMG_DIR}/{slug}.{ext}'
            with open(path, 'wb') as f:
                f.write(data_bytes)
            manifest[slug] = {
                'ok': True, 'path': path, 'source': 'chefaa.com',
                'url': img_url, 'match': best_s, 'chefaa_slug': best.get('slug', ''),
            }
            stats['ok'] += 1
        except Exception as e:
            manifest[slug] = {'ok': False, 'source': 'chefaa-api', 'reason': str(e)[:120]}
            stats['err'] += 1
            time.sleep(1.0)

        if (idx + 1) % 10 == 0 or idx + 1 == len(todo):
            print(f'[{idx + 1}/{len(todo)}] ok={stats["ok"]} nomatch={stats["nomatch"]} '
                  f'err={stats["err"]} ({time.time() - t0:.0f}s)', flush=True)
            with open(MANIFEST, 'w') as f:
                json.dump(manifest, f, ensure_ascii=False, indent=1)

    with open(MANIFEST, 'w') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print('DONE', stats, flush=True)


if __name__ == '__main__':
    main()
