#!/usr/bin/env python3
"""Fetch real product photos via z-ai image-search CLI (rate-limit aware).

- 3 workers, per-request stagger
- global cooldown with exponential backoff on HTTP 429
- resumable via manifest
"""
import json
import os
import random
import re
import subprocess
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = '/home/z/my-project'
IMG_DIR = f'{BASE}/public/images/products'
MANIFEST = f'{BASE}/scripts/image_manifest.json'
EXPORT = f'{BASE}/scripts/products_export.json'
TMP = '/tmp/pharm_imgs'
WORKERS = 3
CLI_TIMEOUT = 90

os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

CATEGORY_CTX = {
    'medications': 'medicine box packaging product',
    'vitamins': 'supplement bottle packaging product',
    'skin-care': 'skincare product bottle packaging',
    'hair-care': 'hair care product bottle packaging',
    'mom-baby': 'baby care product packaging',
    'daily-essentials': 'product packaging',
    'makeup': 'makeup product packaging',
    'medical-supplies': 'medical device product packaging',
    'sexual-health': 'product packaging',
    'pet-supplies': 'pet care product packaging',
}
BAD_BRANDS = {'generic', 'no brand', 'unknown', ''}

# global rate-limit state
_lock = threading.Lock()
_cooldown_until = 0.0
_backoff = 20.0


def build_query(p):
    cat = (p.get('category') or {}).get('slug', '')
    name = (p['nameEn'] or '').strip()
    brand = (p['brand'] or '').strip()
    name = re.sub(r'\s*\|\s*', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    brand = re.sub(r'\s*\|\s*', ' ', brand).strip()
    if brand and brand.lower() not in BAD_BRANDS and name.lower().startswith(brand.lower()):
        name = name[len(brand):].strip()
    ctx = CATEGORY_CTX.get(cat, 'product packaging')
    parts = (brand.lower() not in BAD_BRANDS) and [brand] or []
    parts.append(name)
    q = ' '.join(parts) + ' ' + ctx
    return re.sub(r'\s+', ' ', q).strip()


def img_magic_ok(head: bytes):
    if head[:3] == b'\xff\xd8\xff':
        return 'jpg'
    if head[:8] == b'\x89PNG\r\n\x1a\n':
        return 'png'
    if head[:4] == b'RIFF' and head[8:12] == b'WEBP':
        return 'webp'
    return None


def wait_if_cooldown():
    global _cooldown_until
    while True:
        with _lock:
            now = time.time()
            if now >= _cooldown_until:
                return
            remaining = _cooldown_until - now
        time.sleep(min(remaining, 10) + 0.1)


def trigger_cooldown():
    global _cooldown_until, _backoff
    with _lock:
        _cooldown_until = time.time() + _backoff
        _backoff = min(_backoff * 1.6, 120.0)


def reset_backoff():
    global _backoff
    with _lock:
        _backoff = 20.0


def search_once(query: str, tag: str, count=3):
    """Returns (results, was_rate_limited)."""
    out = f'{TMP}/{tag}.json'
    try:
        if os.path.exists(out):
            os.remove(out)
        r = subprocess.run(
            ['z-ai', 'image-search', '-q', query, '--count', str(count),
             '--no-rank', '--gl', 'us', '-o', out],
            capture_output=True, text=True, timeout=CLI_TIMEOUT)
        combined = (r.stdout or '') + (r.stderr or '')
        rate_limited = '429' in combined or 'Too many requests' in combined
        if not os.path.exists(out):
            return [], rate_limited
        with open(out) as f:
            data = json.load(f)
        if not data.get('success'):
            return [], False
        return data.get('results') or [], False
    except Exception:
        return [], False
    finally:
        try:
            if os.path.exists(out):
                os.remove(out)
        except OSError:
            pass


def pick_result(results):
    def score(r):
        try:
            w = int(str(r.get('original_width', '0')).replace('px', '') or 0)
            h = int(str(r.get('original_height', '0')).replace('px', '') or 0)
        except ValueError:
            w = h = 0
        if w and w < 200:
            return -1
        if h and h < 200:
            return -1
        ar = (w / h) if (w and h) else 1.0
        ar_penalty = abs(ar - 1.0)
        size_bonus = min(w, 2000) / 2000.0
        return size_bonus - ar_penalty * 0.5
    ranked = sorted([r for r in results if score(r) >= 0], key=score, reverse=True)
    return ranked[0] if ranked else None


def download(url: str, dest_base: str):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    })
    with urllib.request.urlopen(req, timeout=45) as resp:
        data = resp.read(12 * 1024 * 1024)
    if len(data) < 3000:
        raise ValueError('too small')
    ext = img_magic_ok(data[:16])
    if not ext:
        raise ValueError('not an image')
    path = f'{dest_base}.{ext}'
    with open(path, 'wb') as f:
        f.write(data)
    return path


_manifest_lock = threading.Lock()


def process(p, manifest):
    slug = p['slug']
    prev = manifest.get(slug)
    if prev and prev.get('ok') and os.path.exists(prev.get('path', '')):
        return ('skip', slug, '')
    query = build_query(p)
    tag = re.sub(r'[^a-z0-9-]', '', slug.lower())[:80] or 'q'
    attempts = 0
    rate_hits = 0
    while attempts < 6 and rate_hits < 20:
        wait_if_cooldown()
        results, rate_limited = search_once(query, tag)
        if rate_limited:
            rate_hits += 1
            trigger_cooldown()
            continue
        attempts += 1
        if results:
            best = pick_result(results)
            if best:
                try:
                    path = download(best['original_url'], f'{IMG_DIR}/{slug}')
                    with _manifest_lock:
                        manifest[slug] = {'ok': True, 'path': path,
                                          'source': best.get('source', ''),
                                          'url': best['original_url'], 'query': query}
                    reset_backoff()
                    return ('ok', slug, path)
                except Exception:
                    pass
        # empty results or bad download -> try alternate simplified query once
        if attempts == 3 and p.get('brand', '').lower() not in BAD_BRANDS:
            query = f"{p['brand']} {(p.get('subcategory') or '').replace('-', ' ')} {((p.get('category') or {}).get('slug') or '').replace('-', ' ')} product packaging"
        time.sleep(2 + random.random() * 3)
    with _manifest_lock:
        manifest[slug] = {'ok': False, 'query': query}
    return ('fail', slug, query)


def main():
    import sys as _sys
    budget = float(_sys.argv[1]) if len(_sys.argv) > 1 else 0  # seconds, 0 = unlimited
    deadline = time.time() + budget if budget > 0 else None
    with open(EXPORT) as f:
        products = json.load(f)
    manifest = {}
    if os.path.exists(MANIFEST):
        with open(MANIFEST) as f:
            manifest = json.load(f)
    todo = [p for p in products
            if not (manifest.get(p['slug'], {}).get('ok')
                    and os.path.exists(manifest[p['slug']].get('path', '')))]
    print(f'Total {len(products)} | todo {len(todo)}', flush=True)

    stats = {'ok': 0, 'fail': 0, 'skip': 0}
    t0 = time.time()
    CHUNK = 6
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        start = 0
        while start < len(todo):
            if deadline and time.time() > deadline:
                print('BUDGET REACHED — stopping', flush=True)
                break
            chunk = todo[start:start + CHUNK]
            try:
                for status, slug, info in ex.map(process, chunk, [manifest] * len(chunk)):
                    stats[status] = stats.get(status, 0) + 1
            except Exception as e:
                print('chunk error:', e, flush=True)
            start += CHUNK
            done_so_far = start
            if done_so_far % 18 < CHUNK or done_so_far >= len(todo):
                print(f'[{done_so_far}/{len(todo)}] ok={stats["ok"]} fail={stats["fail"]} '
                      f'({time.time() - t0:.0f}s)', flush=True)
            with _manifest_lock:
                with open(MANIFEST, 'w') as f:
                    json.dump(manifest, f, ensure_ascii=False, indent=1)
    with open(MANIFEST, 'w') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print('DONE', stats, flush=True)


if __name__ == '__main__':
    main()
