#!/usr/bin/env python3
"""Generate a realistic prescription image for testing OCR"""
from PIL import Image, ImageDraw, ImageFont
import random

W, H = 900, 620
img = Image.new('RGB', (W, H), '#fdfdf8')
d = ImageDraw.Draw(img)

def font(size, bold=False):
    try:
        return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf' % ('-Bold' if bold else ''), size)
    except Exception:
        return ImageFont.load_default()

# header
d.rectangle([0, 0, W, 90], fill='#0d9488')
d.text((30, 18), 'DR. AHMED HASSAN, MD', font=font(26, True), fill='white')
d.text((30, 52), 'Internal Medicine Clinic - Cairo      License #22341', font=font(16), fill='#c9f5f0')

# patient info
d.text((30, 110), 'Patient: Mohamed Ali        Age: 34        Date: 10/09/2026', font=font(18), fill='#333')

# Rx symbol
d.text((30, 150), 'Rx', font=font(40, True), fill='#0d9488')

# medicines (slightly random offsets to look handwritten-ish placement)
meds = [
    ('1. Panadol Extra 500mg', '   1 tablet every 8 hours x 5 days'),
    ('2. Augmentin 1g', '   1 tablet every 12 hours x 7 days'),
    ('3. Ventolin inhaler 100mcg', '   2 puffs when needed'),
]
y = 215
for name, dose in meds:
    d.text((60, y), name, font=font(24, True), fill='#1a1a2e')
    d.text((90, y + 34), dose, font=font(19), fill='#555')
    y += 90

# signature
d.text((560, 500), 'Signature:', font=font(18), fill='#777')
# scribble signature
pts = [(660, 545), (680, 510), (700, 550), (720, 515), (745, 545), (770, 520), (800, 548)]
d.line(pts, fill='#22447a', width=3)
for _ in range(14):
    x = random.randint(640, 820); yy = random.randint(505, 555)
    d.line([(x, yy), (x + random.randint(-30, 30), yy + random.randint(-18, 18))], fill='#22447a', width=2)

# footer line
d.line([(30, 585), (W - 30, 585)], fill='#ccc', width=2)

img.save('/home/z/my-project/scripts/test_prescription.png')
print('saved prescription test image')
