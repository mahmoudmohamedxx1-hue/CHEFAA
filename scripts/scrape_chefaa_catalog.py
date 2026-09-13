#!/usr/bin/env python3
"""Scrape Chefaa category listing pages (server-rendered) to build a catalog map:
slug -> {name_ar, price, image_url}. Resumable JSONL cache.

Polite: 4 workers, 0.4s delay, retry with backoff.
"""
import re, json, os, time, sys
import urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = 'https://chefaa.com/eg-ar/now/category/{cat}?page={n}'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
CACHE = '/home/z/my-project/scripts/chefaa_catalog_cache.jsonl'
CATS = ['medications', 'skin-care', 'hair-care', 'daily-essentials', 'mom-baby',
        'makeup-accessories', 'sexual-welness', 'vitamins-supplements', 'health-care-devices']
MAX_PAGES = {c: 120 for c in CATS}

# card pattern: link slug + image content + name content
CARD = re.compile(
    r'nowProduct/([a-z0-9\-]+).*?itemprop="image"\s+content="(https://cdn\.chefaa\.com/[^"]+)".*?itemprop="name"\s+content="([^"]*)"',
    re.S)
PAGELINK = re.compile(r'\?page=(\d+)')

def fetch(url, tries=4):
    for t in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'ar,en;q=0.8'})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode('utf-8', 'ignore')
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503):
                time.sleep(2 * (t + 1)); continue
            if e.code == 404: return ''
            raise
        except Exception:
            time.sleep(1.5 * (t + 1))
    return None

def parse(html):
    out = {}
    for m in CARD.finditer(html):
        slug, img, name = m.group(1), m.group(2), m.group(3)
        img = img.replace('fit-in/220x194/', '').replace('fit-in/330x330/', '')
        out[slug] = {'slug': slug, 'name': name.strip(), 'img': img}
    return out

def last_page(html):
    pages = [int(x) for x in PAGELINK.findall(html)]
    return max(pages) if pages else 1

def load_cache():
    seen_pages, products = set(), {}
    if os.path.exists(CACHE):
        for line in open(CACHE, encoding='utf-8'):
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if rec.get('type') == 'page':
                seen_pages.add((rec['cat'], rec['page']))
                products.update(rec.get('products', {}))
            elif rec.get('type') == 'catinfo':
                pass
    return seen_pages, products

def main():
    seen_pages, products = load_cache()
    print(f'cache: {len(seen_pages)} pages, {len(products)} products')
    lock_write = open(CACHE, 'a', encoding='utf-8')

    # discover page counts
    tasks = []
    for cat in CATS:
        url = BASE.format(cat=cat, n=1)
        html = fetch(url)
        if html is None:
            print(f'FAIL cat {cat}'); continue
        lp = min(last_page(html), MAX_PAGES[cat])
        print(f'{cat}: {lp} pages, page1 products: {len(parse(html))}')
        if (cat, 1) not in seen_pages:
            prods = parse(html)
            lock_write.write(json.dumps({'type': 'page', 'cat': cat, 'page': 1, 'products': prods}, ensure_ascii=False) + '\n')
            lock_write.flush()
            products.update(prods)
            seen_pages.add((cat, 1))
        for p in range(2, lp + 1):
            if (cat, p) not in seen_pages:
                tasks.append((cat, p))
    print(f'pages to fetch: {len(tasks)}')

    def work(t):
        cat, p = t
        html = fetch(BASE.format(cat=cat, n=p))
        if html is None:
            return (cat, p, None)
        return (cat, p, parse(html))

    done = 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = [ex.submit(work, t) for t in tasks]
        for f in as_completed(futs):
            cat, p, prods = f.result()
            done += 1
            if prods is None:
                print(f'FAIL {cat} p{p}')
            elif prods:
                lock_write.write(json.dumps({'type': 'page', 'cat': cat, 'page': p, 'products': prods}, ensure_ascii=False) + '\n')
                if done % 20 == 0:
                    lock_write.flush()
                    print(f'{done}/{len(tasks)} pages, last: {cat} p{p} ({len(prods)} items)')
            if done % 40 == 0:
                lock_write.flush()
    lock_write.flush()
    lock_write.close()
    print(f'DONE. fetched {done} pages')

if __name__ == '__main__':
    main()
