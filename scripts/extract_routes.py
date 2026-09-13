#!/usr/bin/env python3
import re

html = open('/tmp/search.html').read()
m = re.search(r'var Ziggy = (\{.*?\});', html, re.S)
if not m:
    print('no ziggy')
else:
    raw = m.group(1)
    # find route names + uris
    for mm in re.finditer(r'"([\w.\-]+)":\{"uri":"([^"]+)"', raw):
        n, u = mm.group(1), mm.group(2)
        u = u.replace('\\/', '/')
        if any(k in n.lower() for k in ['search', 'product', 'now', 'api', 'categor', 'filter']):
            print(f'{n} -> {u}')
    # also print first 15 routes overall
    print('--- sample ---')
    cnt = 0
    for mm in re.finditer(r'"([\w.\-]+)":\{"uri":"([^"]+)"', raw):
        print(f'{mm.group(1)} -> {mm.group(2).replace(chr(92) + "/", "/")}')
        cnt += 1
        if cnt > 20: break
