#!/usr/bin/env python3
"""Charts for The Pharmacy competitive analysis report.
Follows typesetting/charts.md: no top/right spines, dashed grid 20% opacity,
horizontal bars for long labels, value labels, legend outside, Template 07 palette.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os

fm.fontManager.addfont('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 11

# Template 07 body palette (fixed)
ACCENT = '#2d7ab3'
HEADER_FILL = '#1a4a7a'
BORDER = '#c0d0e2'
TEXT_PRIMARY = '#142840'
TEXT_MUTED = '#5a7a96'

OUT = '/home/z/my-project/scripts/report_assets'
os.makedirs(OUT, exist_ok=True)


def style_ax(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(BORDER)
    ax.spines['bottom'].set_color(BORDER)
    ax.tick_params(colors=TEXT_MUTED, labelsize=10)
    ax.grid(True, linestyle='--', alpha=0.2, linewidth=0.5, color=TEXT_MUTED)
    ax.set_axisbelow(True)


# ── Chart 1: Egypt E-Pharmacy & Digital Health market projection ──
years = [2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032]
vals = [69, 82, 98, 117, 139, 166, 198, 236]

fig, ax = plt.subplots(figsize=(8.0, 3.4), dpi=200, constrained_layout=True)
style_ax(ax)
ax.plot(years, vals, color=ACCENT, linewidth=2.5, solid_capstyle='round', zorder=3)
ax.fill_between(years, vals, 0, color=ACCENT, alpha=0.14, zorder=2)
# Label first and last points only (first/last/max/min rule)
ax.scatter([years[0], years[-1]], [vals[0], vals[-1]], color=HEADER_FILL, s=28, zorder=4)
ax.annotate('$69M', (years[0], vals[0]), textcoords='offset points', xytext=(2, 10),
            fontsize=10.5, color=TEXT_PRIMARY, fontweight='bold')
ax.annotate('$236M', (years[-1], vals[-1]), textcoords='offset points', xytext=(-30, 10),
            fontsize=10.5, color=TEXT_PRIMARY, fontweight='bold')
ax.set_xticks(years)
ax.set_ylabel('USD millions', color=TEXT_MUTED, fontsize=10)
ax.set_ylim(0, 270)
ax.set_xlim(2024.7, 2032.3)
fig.savefig(f'{OUT}/chart_market.png', facecolor='white')
plt.close(fig)

# ── Chart 2: Disclosed funding of Egyptian e-pharmacy players ──
players = ['Yodawy', 'Chefaa', 'The Pharmacy']
funding = [34.5, 18.3, 0.0]
labels = ['$34.5M', '$18.3M', 'Self-funded\n(owned codebase)']
bar_colors = [BORDER, '#7fa8c9', ACCENT]

fig, ax = plt.subplots(figsize=(7.6, 2.5), dpi=200, constrained_layout=True)
style_ax(ax)
bars = ax.barh(players, funding, color=bar_colors, height=0.52, edgecolor='none', zorder=3)
ax.set_xlim(0, 44)
ax.invert_yaxis()
for i, (b, lab) in enumerate(zip(bars, labels)):
    ax.annotate(lab, (b.get_width(), b.get_y() + b.get_height() / 2),
                textcoords='offset points', xytext=(8, 0), va='center',
                fontsize=10, color=TEXT_PRIMARY, fontweight='bold')
ax.set_xlabel('Total disclosed funding (USD millions)', color=TEXT_MUTED, fontsize=10)
ax.set_xticks([0, 10, 20, 30, 40])
fig.savefig(f'{OUT}/chart_funding.png', facecolor='white')
plt.close(fig)

# ── Chart 3: The Pharmacy catalog composition ──
cats = ['Hair Care', 'Medications', 'Skin Care', 'Daily Essentials', 'Mom & Baby',
        'Medical Supplies', 'Vitamins & Supplements', 'Makeup', 'Sexual Health', 'Pet Supplies']
counts = [223, 104, 50, 49, 15, 15, 14, 12, 8, 6]

fig, ax = plt.subplots(figsize=(7.6, 3.9), dpi=200, constrained_layout=True)
style_ax(ax)
y = np.arange(len(cats))
shades = [ACCENT if c >= 50 else '#7fa8c9' for c in counts]
bars = ax.barh(y, counts, color=shades, height=0.6, edgecolor='none', zorder=3)
ax.set_yticks(y)
ax.set_yticklabels(cats, fontsize=10, color=TEXT_PRIMARY)
ax.invert_yaxis()
ax.set_xlim(0, 250)
for b, c in zip(bars, counts):
    ax.annotate(str(c), (b.get_width(), b.get_y() + b.get_height() / 2),
                textcoords='offset points', xytext=(6, 0), va='center',
                fontsize=9.5, color=TEXT_PRIMARY, fontweight='bold')
ax.set_xlabel('Products in catalog (n = 496)', color=TEXT_MUTED, fontsize=10)
ax.set_xticks([0, 50, 100, 150, 200, 250])
fig.savefig(f'{OUT}/chart_catalog.png', facecolor='white')
plt.close(fig)

print('Charts generated:')
for f in sorted(os.listdir(OUT)):
    print(' -', f, os.path.getsize(os.path.join(OUT, f)), 'bytes')
