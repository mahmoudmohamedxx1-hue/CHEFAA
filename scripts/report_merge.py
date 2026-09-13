#!/usr/bin/env python3
"""Merge cover + body into the final report PDF (normalized to A4)."""
from pypdf import PdfReader, PdfWriter

A4_W, A4_H = 595.28, 841.89

COVER = '/home/z/my-project/scripts/report_assets/cover.pdf'
BODY = '/home/z/my-project/scripts/report_assets/body.pdf'
OUT = '/home/z/my-project/download/The_Pharmacy_Competitive_Landscape_Report.pdf'


def normalize_page_to_a4(page):
    box = page.mediabox
    w, h = float(box.width), float(box.height)
    if abs(w - A4_W) > 0.1 or abs(h - A4_H) > 0.1:
        page.scale_to(A4_W, A4_H)
    return page


writer = PdfWriter()
writer.add_page(normalize_page_to_a4(PdfReader(COVER).pages[0]))
for page in PdfReader(BODY).pages:
    writer.add_page(normalize_page_to_a4(page))
writer.add_metadata({
    '/Title': 'The Pharmacy - Platform Status & Competitive Landscape Report',
    '/Author': 'The Pharmacy Strategy & Product Team',
    '/Creator': 'Z.ai',
    '/Subject': 'Egypt e-pharmacy market analysis, competitor deep-dive, SWOT and '
                '90-day launch roadmap',
})
import os
os.makedirs('/home/z/my-project/download', exist_ok=True)
with open(OUT, 'wb') as f:
    writer.write(f)

r = PdfReader(OUT)
sizes = {(round(float(p.mediabox.width)), round(float(p.mediabox.height))) for p in r.pages}
print('Final PDF:', OUT)
print('Pages:', len(r.pages), '| page sizes:', sizes)
print('Size on disk: %.1f KB' % (os.path.getsize(OUT) / 1024))
