#!/usr/bin/env python3
"""The Pharmacy - Platform Status & Competitive Landscape Report (body PDF).

Pipeline: ReportLab body (this script) + HTML/Playwright cover (Template 07
Crystal Blue) merged via pypdf. English document -> FreeSerif family.

Chapter Numbering Plan (Step 3.5):
| Outline | Type    | Chapter # | Title                                          |
|---------|---------|-----------|------------------------------------------------|
| 1       | cover   | -         | Cover (separate HTML/Playwright PDF)           |
| 2       | toc     | -         | Table of Contents                              |
| 3       | content | 1         | Executive Summary                              |
| 4       | content | 2         | What We Got: Platform Inventory                |
| 5       | content | 3         | Market Context: The Egypt E-Pharmacy Opportunity|
| 6       | content | 4         | Competitor Deep-Dive                           |
| 7       | content | 5         | SWOT & Competitive Positioning                 |
| 8       | content | 6         | Where We Are: Gaps, Maturity & Roadmap         |
"""
import os
import sys
import hashlib

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Table, TableStyle, Image, KeepTogether,
                                CondPageBreak, HRFlowable)
from reportlab.platypus.tableofcontents import TableOfContents
from PIL import Image as PILImage

SKILL_SCRIPTS = '/home/z/my-project/skills/pdf/scripts'
sys.path.insert(0, SKILL_SCRIPTS)

# ── Fonts (allowed list only) ────────────────────────────────────────────────
FONT_DIR = '/usr/share/fonts'
pdfmetrics.registerFont(TTFont('FreeSerif', f'{FONT_DIR}/truetype/freefont/FreeSerif.ttf'))
pdfmetrics.registerFont(TTFont('FreeSerif-Bold', f'{FONT_DIR}/truetype/freefont/FreeSerifBold.ttf'))
pdfmetrics.registerFont(TTFont('FreeSerif-Italic', f'{FONT_DIR}/truetype/freefont/FreeSerifItalic.ttf'))
pdfmetrics.registerFont(TTFont('FreeSerif-BoldItalic', f'{FONT_DIR}/truetype/freefont/FreeSerifBoldItalic.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans', f'{FONT_DIR}/truetype/dejavu/DejaVuSansMono.ttf'))
registerFontFamily('FreeSerif', normal='FreeSerif', bold='FreeSerif-Bold',
                   italic='FreeSerif-Italic', boldItalic='FreeSerif-BoldItalic')
registerFontFamily('DejaVuSans', normal='DejaVuSans', bold='DejaVuSans')

from pdf import install_font_fallback  # noqa: E402  (skill helper)
install_font_fallback()

# ── Palette: Template 07 Crystal Blue body subset (fixed by cover.md) ───────
PAGE_BG       = colors.HexColor('#f5f8fc')   # XL
SECTION_BG    = colors.HexColor('#edf2f9')   # XL
CARD_BG       = colors.HexColor('#e4ecf5')   # L
TABLE_STRIPE  = colors.HexColor('#eef3fa')   # L
HEADER_FILL   = colors.HexColor('#1a4a7a')   # M
BORDER        = colors.HexColor('#c0d0e2')   # S
ACCENT        = colors.HexColor('#2d7ab3')   # XS
TEXT_PRIMARY  = colors.HexColor('#142840')
TEXT_MUTED    = colors.HexColor('#5a7a96')

TABLE_HEADER_COLOR = HEADER_FILL
TABLE_HEADER_TEXT  = colors.white
TABLE_ROW_EVEN     = colors.white
TABLE_ROW_ODD      = TABLE_STRIPE

# ── Layout constants ─────────────────────────────────────────────────────────
MARGIN = 1.0 * inch
PAGE_W, PAGE_H = A4
AVAIL_W = PAGE_W - 2 * MARGIN            # ~451pt
AVAIL_H = PAGE_H - 2 * MARGIN
MAX_KEEP_HEIGHT = PAGE_H * 0.4
H1_ORPHAN_THRESHOLD = AVAIL_H * 0.15

ASSETS = '/home/z/my-project/scripts/report_assets'
SHOTS = '/home/z/my-project/scripts'
OUT_PDF = '/home/z/my-project/scripts/report_assets/body.pdf'

DOC_TITLE = 'The Pharmacy - Platform Status & Competitive Landscape Report'
DOC_AUTHOR = 'The Pharmacy Strategy & Product Team'

# ── Styles ───────────────────────────────────────────────────────────────────
S = {}
S['h1'] = ParagraphStyle('H1', fontName='FreeSerif', fontSize=20, leading=25,
                         textColor=HEADER_FILL, spaceBefore=18, spaceAfter=4)
S['h2'] = ParagraphStyle('H2', fontName='FreeSerif', fontSize=14.5, leading=19,
                         textColor=TEXT_PRIMARY, spaceBefore=16, spaceAfter=6)
S['h3'] = ParagraphStyle('H3', fontName='FreeSerif', fontSize=11.5, leading=15,
                         textColor=TEXT_PRIMARY, spaceBefore=12, spaceAfter=5)
S['body'] = ParagraphStyle('Body', fontName='FreeSerif', fontSize=10.5, leading=17,
                           textColor=TEXT_PRIMARY, alignment=TA_JUSTIFY,
                           spaceBefore=0, spaceAfter=9)
S['bullet'] = ParagraphStyle('Bullet', fontName='FreeSerif', fontSize=10.5, leading=16,
                             textColor=TEXT_PRIMARY, alignment=TA_LEFT,
                             leftIndent=14, spaceBefore=0, spaceAfter=5)
S['caption'] = ParagraphStyle('Caption', fontName='FreeSerif', fontSize=8.5, leading=12,
                              textColor=TEXT_MUTED, alignment=TA_CENTER,
                              spaceBefore=3, spaceAfter=6)
S['quote'] = ParagraphStyle('Quote', fontName='FreeSerif-Italic', fontSize=11, leading=17,
                            textColor=HEADER_FILL, alignment=TA_LEFT, leftIndent=24,
                            spaceBefore=6, spaceAfter=10)
S['stat'] = ParagraphStyle('Stat', fontName='FreeSerif', fontSize=19, leading=23,
                           textColor=ACCENT, alignment=TA_CENTER)
S['statlabel'] = ParagraphStyle('StatLabel', fontName='FreeSerif', fontSize=8, leading=11,
                                textColor=TEXT_MUTED, alignment=TA_CENTER)
S['th'] = ParagraphStyle('TH', fontName='FreeSerif', fontSize=9.5, leading=13,
                         textColor=TABLE_HEADER_TEXT, alignment=TA_CENTER)
S['td'] = ParagraphStyle('TD', fontName='FreeSerif', fontSize=9.5, leading=13,
                         textColor=TEXT_PRIMARY, alignment=TA_LEFT, wordWrap='CJK')
S['tdc'] = ParagraphStyle('TDC', fontName='FreeSerif', fontSize=9.5, leading=13,
                          textColor=TEXT_PRIMARY, alignment=TA_CENTER)
S['toc_title'] = ParagraphStyle('TocTitle', fontName='FreeSerif', fontSize=20, leading=25,
                                textColor=HEADER_FILL, spaceAfter=14)
S['src'] = ParagraphStyle('Src', fontName='FreeSerif', fontSize=8.5, leading=12.5,
                          textColor=TEXT_MUTED, alignment=TA_LEFT,
                          leftIndent=24, firstLineIndent=-24, spaceAfter=3)

# ── Helpers ──────────────────────────────────────────────────────────────────

def safe_keep_together(elements):
    total_h = 0
    for el in elements:
        w, h = el.wrap(AVAIL_W, PAGE_H)
        total_h += h
    if total_h <= MAX_KEEP_HEIGHT:
        return [KeepTogether(elements)]
    elif len(elements) >= 2:
        return [KeepTogether(elements[:2])] + list(elements[2:])
    return list(elements)


def heading(text, style, level=0):
    key = 'h_%s' % hashlib.md5(text.encode()).hexdigest()[:8]
    p = Paragraph('<a name="%s"/><b>%s</b>' % (key, text), style)
    p.bookmark_name = key
    p.bookmark_level = level
    p.bookmark_text = text
    p.bookmark_key = key
    return p


def h1(story, text):
    story.append(CondPageBreak(H1_ORPHAN_THRESHOLD))
    hp = heading(text, S['h1'], level=0)
    rule = HRFlowable(width='100%', color=ACCENT, thickness=1.4,
                      spaceBefore=0, spaceAfter=12)
    story.extend(safe_keep_together([hp, rule]))


def h2(story, text, first_para=None):
    hp = heading(text, S['h2'], level=1)
    if first_para is not None:
        story.extend(safe_keep_together([hp, first_para]))
    else:
        story.append(hp)


def body(story, text):
    story.append(Paragraph(text, S['body']))


def bullets(story, items):
    for it in items:
        story.append(Paragraph('•  %s' % it, S['bullet']))
    story.append(Spacer(1, 6))


def embed_image(path, max_width=None, max_height=None):
    if max_width is None:
        max_width = AVAIL_W
    if max_height is None:
        max_height = PAGE_H * 0.35
    pil = PILImage.open(path)
    ow, oh = pil.size
    ratio = min(max_width / ow if ow > max_width else 1.0,
                max_height / oh if oh > max_height else 1.0)
    return Image(path, width=ow * ratio, height=oh * ratio)


def chart(story, png, caption_text, max_h=250):
    img = embed_image(png, max_width=AVAIL_W * 0.96, max_height=max_h)
    img.hAlign = 'CENTER'
    cap = Paragraph(caption_text, S['caption'])
    story.append(Spacer(1, 14))
    story.extend(safe_keep_together([img, Spacer(1, 6), cap]))
    story.append(Spacer(1, 12))


def stat_row(story, stats):
    """stats: list of (value, label). Renders a 1-row callout band."""
    n = len(stats)
    col_w = AVAIL_W / n
    cells = [[Table([[Paragraph('<b>%s</b>' % v, S['stat'])],
                     [Paragraph(l, S['statlabel'])]],
                    colWidths=[col_w - 10])
              for v, l in stats]]
    outer = Table(cells, colWidths=[col_w] * n, hAlign='CENTER')
    inner_style = []
    for i in range(n):
        inner_style.append(('BACKGROUND', (i, 0), (i, 0), CARD_BG))
        inner_style.append(('BOX', (i, 0), (i, 0), 0.75, BORDER))
        inner_style.append(('LINEABOVE', (i, 0), (i, 0), 2, ACCENT))
        inner_style.append(('VALIGN', (i, 0), (i, 0), 'MIDDLE'))
        inner_style.append(('TOPPADDING', (i, 0), (i, 0), 10))
        inner_style.append(('BOTTOMPADDING', (i, 0), (i, 0), 10))
    outer.setStyle(TableStyle(inner_style))
    story.append(Spacer(1, 8))
    story.extend(safe_keep_together([outer]))
    story.append(Spacer(1, 12))


def make_table(story, header_row, rows, ratios, caption_text=None,
               center_cols=None):
    """Standard striped table. All cells wrapped in Paragraph()."""
    center_cols = center_cols or set()
    col_widths = [r * AVAIL_W for r in ratios]
    assert abs(sum(ratios) - 1.0) < 0.01, 'ratios must sum to 1.0'
    data = [[Paragraph('<b>%s</b>' % h, S['th']) for h in header_row]]
    for r in rows:
        cells = []
        for i, c in enumerate(r):
            st = S['tdc'] if i in center_cols else S['td']
            cells.append(Paragraph(str(c), st))
        data.append(cells)
    t = Table(data, colWidths=col_widths, hAlign='CENTER', repeatRows=1)
    style = [
        ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]
    for i in range(1, len(data)):
        bg = TABLE_ROW_ODD if i % 2 == 1 else TABLE_ROW_EVEN
        style.append(('BACKGROUND', (0, i), (-1, i), bg))
    t.setStyle(TableStyle(style))
    story.append(Spacer(1, 16))
    if caption_text:
        cap = Paragraph(caption_text, S['caption'])
        if len(rows) <= 15:
            story.extend(safe_keep_together([t, Spacer(1, 4), cap]))
        else:
            story.append(t)
            story.append(Spacer(1, 4))
            story.append(cap)
    else:
        story.append(t)
    story.append(Spacer(1, 14))


# ── Doc template with TOC support + header/footer ────────────────────────────

class TocDocTemplate(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if hasattr(flowable, 'bookmark_name'):
            level = getattr(flowable, 'bookmark_level', 0)
            text = getattr(flowable, 'bookmark_text', '')
            key = getattr(flowable, 'bookmark_key', '')
            self.notify('TOCEntry', (level, text, self.page, key))


def on_page(canvas, doc):
    canvas.saveState()
    # Header
    canvas.setFont('FreeSerif', 7.5)
    canvas.setFillColor(TEXT_MUTED)
    canvas.drawString(MARGIN, PAGE_H - 42, DOC_TITLE)
    canvas.setStrokeColor(ACCENT)
    canvas.setLineWidth(1.2)
    canvas.line(MARGIN, PAGE_H - 48, PAGE_W - MARGIN, PAGE_H - 48)
    # Footer
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, 46, PAGE_W - MARGIN, 46)
    canvas.setFont('FreeSerif', 7.5)
    canvas.setFillColor(TEXT_MUTED)
    canvas.drawString(MARGIN, 34, 'The Pharmacy · Strategy & Product Team')
    canvas.drawRightString(PAGE_W - MARGIN, 34, 'Page %d' % doc.page)
    canvas.restoreState()


# ── Build story ──────────────────────────────────────────────────────────────
story = []

# TOC page
story.append(Paragraph('<b>Table of Contents</b>', S['toc_title']))
toc = TableOfContents()
toc.levelStyles = [
    ParagraphStyle('TOC1', fontName='FreeSerif', fontSize=11.5, leading=20,
                   leftIndent=16, textColor=TEXT_PRIMARY),
    ParagraphStyle('TOC2', fontName='FreeSerif', fontSize=10, leading=16,
                   leftIndent=34, textColor=TEXT_MUTED),
]
story.append(toc)
story.append(PageBreak())

# ════════════════════════════════ CHAPTER 1 ════════════════════════════════
h1(story, '1. Executive Summary')
body(story, 'The Pharmacy is a complete, ground-up rebuild of the original CHEFAA concept as an '
     'independently owned, production-grade e-pharmacy platform for the Egyptian market. The '
     'legacy prototype lived on a third-party AI-builder platform that the business never truly '
     'owned, and its repository contained no deployable application code. The new platform '
     'corrects that structural weakness at the root: it is a fully owned Next.js 16 codebase with '
     'its own database, authentication, AI services, and admin tooling, ready to deploy to the '
     'operator’s own hosting account. Every layer described in this report was built and '
     'end-to-end verified in this engagement.')
body(story, 'What exists today is a functioning commerce platform, not a mock-up. The catalog '
     'carries 496 products across 10 categories and 187 brands with complete bilingual '
     'Arabic-English content, priced from 10 to 2,450 EGP. Three AI features run against real '
     'models: a prescription reader that photographs-to-cart via OCR, a bilingual health '
     'assistant that recommends catalog products, and a drug interaction checker with severity '
     'grading. The checkout supports 15 Egyptian delivery zones with distance-based fees, '
     'cash-on-delivery, and a six-stage order pipeline that an integrated admin panel manages '
     'end to end. A full browser-based verification pass confirmed the entire journey, from '
     'Arabic-language browsing through AI prescription scanning to a placed order number.')
body(story, 'The market context is unusually favorable for a well-executed new entrant. Egypt’s '
     'e-pharmacy and digital health market is valued at 69 million USD in 2025 and is projected '
     'to reach 236 million USD by 2032, a 19.2 percent compound annual growth rate, inside a '
     'national e-commerce economy heading from 9.1 to 19.6 billion USD. The incumbent leaders '
     'are venture-funded: Yodawy has raised 34.5 million USD and Chefaa 18.3 million USD, yet '
     'Chefaa’s flagship app holds only a 3.7-star rating across roughly 8,500 Google Play '
     'reviews, and our own audit of chefaa.com found a checkout flow that breaks when location '
     'services fail. None of the Egyptian market leaders currently ships genuine AI features '
     'beyond marketing language.')
body(story, 'The strategic verdict of this report: <b>Phase 1 (platform build) is complete and '
     'verified; the venture is pre-launch.</b> The engineering gap to market standard is modest '
     'and closable within 90 days, while the differentiation assets the incumbents lack, real '
     'AI tooling and a bilingual-first experience, are already operational. The critical path '
     'runs through production deployment, online payments, catalog depth, and a licensed '
     'pharmacist partnership, and each is scheduled in the roadmap in Chapter 6.')
stat_row(story, [
    ('496', 'products in catalog, 100% bilingual AR/EN'),
    ('3', 'production AI features, verified end-to-end'),
    ('15', 'Egypt delivery zones, 30-95 EGP fees'),
    ('19.2%', 'market CAGR, 2025-2032 (Ken Research)'),
])
h2(story, '1.1 Key Findings')
bullets(story, [
    '<b>The platform asset is real and owned.</b> Full commerce loop, authentication, AI '
    'services, and admin tooling are built, lint-clean, and browser-verified; no third-party '
    'platform dependency remains.',
    '<b>AI is a genuine differentiator in Egypt.</b> Prescription OCR, a bilingual health '
    'assistant, and an interaction checker are live; no incumbent currently matches this '
    'capability set.',
    '<b>Incumbents are funded but vulnerable on experience.</b> Chefaa’s 3.7-star app '
    'rating, its location-dependent cart, and the absence of AI features leave an opening for '
    'an experience-led entrant.',
    '<b>The market window is open but not indefinite.</b> A 19.2 percent growth market with '
    '78 percent of Cairo health-tech funding concentrated in three players suggests both room '
    'and appetite for credible alternatives.',
    '<b>The binding constraints are operational, not technical.</b> Online payments, catalog '
    'depth, native app presence, and licensed-pharmacist compliance are the four gaps between '
    'the current platform and credible market entry.',
])

# ════════════════════════════════ CHAPTER 2 ════════════════════════════════
h1(story, '2. What We Got: Platform Inventory')
body(story, 'This chapter inventories the platform exactly as it stands on disk and in the '
     'database, with no aspirational items. The original CHEFAA repository contributed two '
     'valuable assets to this rebuild: roughly 335 scraped bilingual product records with '
     'Egyptian market pricing, and a documented category taxonomy mirroring the incumbent’s '
     'merchandising. Everything else was rebuilt from scratch. The sections below quantify the '
     'catalog, the technology stack, the AI capabilities, the commerce machinery, and the '
     'verification evidence.')
h2(story, '2.1 Catalog and Content',
   Paragraph('The live database holds 496 products across 10 categories and 187 distinct '
             'brands, every one carrying a full Arabic name alongside its English name. Prices '
             'span 10 to 2,450 EGP with an average of about 196 EGP, which matches the '
             'price architecture of the incumbent’s mass-market assortment. 21 products are '
             'flagged as prescription-required and routed through the prescription review '
             'queue, 140 carry a discount anchor price, and 37 are merchandised as featured '
             'items on the home page. Category coverage follows the scraped incumbent '
             'taxonomy, extended with curated fills for vitamins, mom and baby, medical '
             'supplies, makeup, sexual health, and pet supplies.', S['body']))
chart(story, f'{ASSETS}/chart_catalog.png',
      'Figure 1: The Pharmacy catalog composition by category (n = 496 products). '
      'Hair care and medications, the two categories with the richest scraped data, '
      'anchor the assortment.')
body(story, 'The assortment’s shape is deliberate rather than accidental. Hair care (223 '
     'products) and medications (104) together account for two-thirds of the catalog because '
     'they are precisely the categories where the scraped incumbent data was deepest and where '
     'Egyptian online pharmacy demand concentrates. The eight remaining categories establish '
     'credible breadth for a launch storefront, so that a first-time visitor perceives a '
     'complete pharmacy rather than a niche shop. The catalog pipeline that consolidated the '
     'scrapes is preserved as a repeatable script, which matters for the Chapter 6 roadmap: '
     'scaling to several thousand SKUs is a data-processing task, not a redesign.')

h2(story, '2.2 Technology Architecture',
   Paragraph('The stack was chosen for ownership, employability, and deployment freedom: '
             'Next.js 16 with TypeScript on the front, Prisma over SQLite in development with '
             'a direct PostgreSQL path for production hosting, and session-cookie '
             'authentication with scrypt password hashing. The user-facing application is a '
             'single-route experience with a hash router, which keeps the Arabic-English '
             'language switch instant and keeps state (cart, wishlist, language, recently '
             'viewed) persisted across visits. Sixteen API endpoints expose auth, catalog, '
             'search, orders, AI services, and admin functions, with role-based access '
             'control separating customer and administrator capabilities.', S['body']))
make_table(story,
           ['Layer', 'Implementation', 'Status'],
           [
            ['Frontend', 'Next.js 16 (App Router), TypeScript, Tailwind 4, shadcn/ui '
             'components, Cairo typeface, instant AR/EN switch with full RTL/LTR mirroring', 'Live'],
            ['State', 'Zustand stores with persistence: cart, wishlist, language, recently '
             'viewed products', 'Live'],
            ['API', '16 endpoints across 6 groups: auth (4), catalog and search (5), '
             'orders (2), AI (2), admin (3), prescriptions (1)', 'Live'],
            ['Data', 'Prisma ORM on SQLite (development) with PostgreSQL migration path for '
             'Vercel deployment', 'Live'],
            ['Auth', 'Scrypt password hashing, HTTP-only session cookies, role-based access '
             '(admin / customer)', 'Live'],
            ['Design', 'Modern Medical teal theme on oklch tokens, mobile-first layouts, '
             'deterministic SVG product artwork (zero image-licensing risk)', 'Live'],
           ],
           [0.14, 0.72, 0.14],
           'Table 1: Platform architecture summary. All layers are implemented, lint-clean, '
           'and running.',
           center_cols={2})

h2(story, '2.3 AI Capabilities',
   Paragraph('Three AI features are wired to real model services and were verified in the '
             'browser during this engagement. They are not UI simulations: each one calls a '
             'backend route that invokes a vision or language model, post-processes the '
             'output, and returns structured data the interface renders. This is the '
             'capability gap that no Egyptian pharmacy competitor currently closes, and it is '
             'the strategic heart of the platform.', S['body']))
make_table(story,
           ['AI Feature', 'How It Works', 'Verified Result'],
           [
            ['Prescription Reader (OCR)',
             'Customer photographs or uploads a prescription; a vision-language model extracts '
             'drug names; fuzzy matching maps them to catalog products with confidence scores',
             'A generated test prescription was uploaded in the browser; Panadol Extra, '
             'Augmentin and Ventolin were detected, matched to catalog items, and added to '
             'the cart in one action'],
            ['AI Health Assistant',
             'Bilingual chat (Arabic and English) grounded in catalog context; returns '
             'guidance plus shoppable product cards',
             'An Arabic symptom query returned a structured advisory reply in Arabic with '
             'matched product recommendations'],
            ['Drug Interaction Checker',
             'Customer enters multiple medications; a language model analyzes pairwise '
             'interactions and returns JSON with severity grading',
             'A multi-drug scenario produced a graded risk analysis with severity badges '
             'rendered in the UI'],
           ],
           [0.22, 0.39, 0.39],
           'Table 2: The three production AI features and their end-to-end verification '
           'outcomes.')

h2(story, '2.4 Commerce and Operations',
   Paragraph('The order pipeline is complete from cart to delivered. Checkout supports 15 '
             'Egyptian delivery zones with fees graded by distance, 30 EGP in core Cairo '
             'districts up to 95 EGP for Aswan, and free delivery above a 500 EGP basket. '
             'Payment is cash-on-delivery, with card and wallet gateway integration '
             'deliberately staged for the launch phase (Chapter 6). Orders move through six '
             'statuses, pending, confirmed, preparing, out for delivery, and delivered, plus '
             'cancelled, each visible to the customer as a timeline and to the administrator '
             'as a management queue.', S['body']))
stat_row(story, [
    ('15', 'delivery zones from Nasr City to Aswan'),
    ('30-95', 'EGP zone fees, same-day Cairo to 3-5 day Upper Egypt'),
    ('500', 'EGP free-delivery threshold'),
    ('6', 'order statuses with customer timeline'),
])
body(story, 'The admin panel closes the operational loop. It presents headline statistics, '
     'manages every order’s status, edits stock and price inline across the catalog, and '
     'reviews uploaded prescriptions with the AI extraction beside them so a pharmacist can '
     'confirm or correct each matched item. This last workflow matters for regulatory '
     'posture: prescription orders are not auto-released, they enter a human review queue, '
     'which is the correct pattern for Egyptian pharmaceutical practice.')

h2(story, '2.5 Verification Evidence',
   Paragraph('The platform was exercised end-to-end in a real browser before this report was '
             'written. The verification matrix below lists every scenario tested and its '
             'result; screenshots of the key views were captured and are embedded in this '
             'chapter. The test coverage deliberately spanned both languages, the full '
             'commerce funnel, both user roles, all three AI features, and a mobile '
             'viewport.', S['body']))
make_table(story,
           ['Verification Scenario', 'Result'],
           [
            ['Home page renders in Arabic (RTL) and English (LTR)', 'Passed'],
            ['Category browsing with price, brand, Rx and stock filters; sorting; pagination', 'Passed'],
            ['Search autocomplete and product detail with related items', 'Passed'],
            ['Add to cart, cart drawer with free-delivery progress bar', 'Passed'],
            ['Full checkout with zone selection, validation, and order placement (TP- order number issued)', 'Passed'],
            ['Customer registration and login (demo account)', 'Passed'],
            ['Admin login and access control (admin-only routes blocked for customers)', 'Passed'],
            ['Order history with status timeline', 'Passed'],
            ['AI health assistant: Arabic query with product matches', 'Passed'],
            ['Drug interaction checker: severity-graded risk analysis', 'Passed'],
            ['Prescription OCR: upload, extraction, catalog match, add-all-to-cart', 'Passed'],
            ['Mobile viewport rendering', 'Passed'],
           ],
           [0.82, 0.18],
           'Table 3: End-to-end verification matrix, executed against the running application.',
           center_cols={1})
chart(story, f'{SHOTS}/shot-home-ar.png',
      'Figure 2: The home view in Arabic with full right-to-left layout, captured during '
      'verification. Category navigation, featured products, and AI tool entry points render '
      'correctly in the RTL locale.', max_h=235)
chart(story, f'{SHOTS}/shot-admin.png',
      'Figure 3: The admin panel with statistics, order management, catalog editing, and the '
      'prescription review queue. All management functions verified with the admin account.',
      max_h=235)

# ════════════════════════════════ CHAPTER 3 ════════════════════════════════
h1(story, '3. Market Context: The Egypt E-Pharmacy Opportunity')
h2(story, '3.1 Market Size and Growth',
   Paragraph('Egypt’s digital pharmacy sector is small in absolute terms and compounding '
             'fast, which is the classic profile of a market where brand positions are still '
             'formable. Ken Research values the Egypt e-pharmacy and digital health market at '
             '69 million USD in 2025, growing at a 19.2 percent compound annual rate to a '
             'projected 236 million USD by 2032. A companion estimate places the country’s '
             'AI-powered e-pharmacy platforms alone at roughly 60 million USD, evidence that '
             'the AI positioning this platform has already built is aligned with where '
             'analysts see the segment heading rather than against it.', S['body']))
chart(story, f'{ASSETS}/chart_market.png',
      'Figure 4: Egypt e-pharmacy and digital health market projection, 2025-2032, in USD '
      'millions at a 19.2 percent CAGR (Ken Research). Endpoint values are analyst '
      'estimates; intermediate years are CAGR interpolation.')
body(story, 'The wider commerce context amplifies the sector number. Egypt’s total '
     'e-commerce market was 9.1 billion USD in 2024 with forecasts reaching 19.6 billion USD '
     'by 2032, and the national internet audience reached 46.3 million users in mid-2025, up '
     '29 percent year on year. Regionally, Middle East and Africa e-pharmacy is forecast to '
     'grow from 2.4 billion USD in 2025 to 5.9 billion USD, while MENA pharmaceutical sales '
     'overall compound near 7 percent, faster than the global market. In plain terms: the '
     'underlying behaviors, connectivity, comfort paying online, and chronic-disease demand, '
     'are all scaling, while the pharmacy-specific online channel remains early enough that '
     'no player has locked the category.')
h2(story, '3.2 Funding Landscape and Competitive Intensity',
   Paragraph('The capital story defines who can outspend whom, and it favors focus over '
             'brute force for a new entrant. StartupBlink tracks 61.1 million USD in funding '
             'across Cairo’s healthcare startups, and 78 percent of it sits with just '
             'three companies: Yodawy, Chefaa, and Dawi Clinics. Yodawy leads at 34.5 '
             'million USD raised, including a 10 million USD round in January 2024, but its '
             'business is pharmacy-benefits infrastructure for insurers and corporates rather '
             'than a consumer storefront. Chefaa, the closest direct comparable, has raised '
             '18.3 million USD, most recently 5.25 million USD in December 2023, and '
             'commercial trackers put its annual recurring revenue at 14.4 million USD in '
             '2023 with later estimates near 29 million USD.', S['body']))
chart(story, f'{ASSETS}/chart_funding.png',
      'Figure 5: Total disclosed funding of the funded Egyptian e-pharmacy players versus '
      'The Pharmacy (PitchBook, Disrupt Africa, company announcements). The Pharmacy enters '
      'with zero external funding and a fully owned codebase.', max_h=175)
body(story, 'Two readings follow from this concentration. The pessimistic one is that '
     'incumbents can outspend a self-funded entrant on marketing indefinitely. The '
     'constructive one, which the evidence in Chapter 4 supports, is that investors '
     'watching this space have already watched three names absorb most of the capital while '
     'consumer satisfaction languished, Chefaa’s app rating is 3.7 stars, so a '
     'differentiated, capital-efficient operator with a working product has a plausible path '
     'to being the credible alternative, and, later, the acquisition or investment target. '
     'The strategic implication is to convert the owned-codebase advantage into launch '
     'velocity before fundraising conversations, not after.')
h2(story, '3.3 Regulatory Environment',
   Paragraph('Egyptian pharmaceutical law requires that medicines be sold by, and under the '
             'supervision of, a licensed pharmacist, and there is not yet a dedicated '
             'e-pharmacy statute; legal analyses published as recently as December 2025 '
             'describe the online sale of medicines as operating in a regulatory gray zone '
             'with no comprehensive official supervision. This is a manageable risk with a '
             'known mitigation pattern: partner with a licensed pharmacy entity, ensure a '
             'pharmacist reviews prescription orders before release, and maintain audit '
             'records of those reviews.', S['body']))
body(story, 'The platform was deliberately engineered for exactly this posture. '
     'Prescription-required products are flagged in the catalog, prescriptions upload into '
     'a review queue rather than auto-processing, and the AI extraction sits beside the '
     'human reviewer’s confirmation step in the admin panel. The remaining compliance '
     'work is operational rather than technical: formalizing the licensed-pharmacist '
     'partnership, publishing the responsible-pharmacist identity, and defining the record '
     'retention policy. These items are scheduled in the 0-30 day roadmap tier, because '
     'regulatory posture should be settled before marketing spend begins.')

# ════════════════════════════════ CHAPTER 4 ════════════════════════════════
h1(story, '4. Competitor Deep-Dive')
body(story, 'This chapter profiles the players an Egyptian customer realistically compares '
     'us against: the venture-backed pure-plays (Chefaa, Vezeeta, Yodawy), the pharmacy '
     'retail chains (El Ezaby, Seif, and the 19011 app), and the horizontal delivery '
     'platforms (Talabat, Amazon Egypt). Profiles combine public funding and product data '
     'with our own first-hand audit of the incumbent’s live website conducted during this '
     'engagement, and close with a capability matrix that positions The Pharmacy against '
     'the field.')
h2(story, '4.1 Chefaa - The Direct Comparable',
   Paragraph('Chefaa, founded in 2017, is Egypt’s most directly comparable online pharmacy: '
             'a GPS-enabled platform that connects patients to partner pharmacies for '
             'medicine and cosmetics delivery in Egypt and Saudi Arabia. It has raised 18.3 '
             'million USD across rounds from Flat6Labs, 500 Startups, M3, and Verod-Kepple '
             'Africa Ventures, including a 5.25 million USD round in December 2023. Its '
             'product emphasizes chronic-patient refill scheduling, prescription upload, and '
             'a bulk-savings program, Super Tawfir, offering up to 15 percent off with a 700 '
             'EGP minimum basket and 1-3 day delivery. Revenue trackers put it at 14.4 '
             'million USD ARR in 2023, with more recent estimates near 29 million USD.', S['body']))
body(story, 'Its weaknesses are experiential and structural. The Google Play listing shows '
     'a 3.7-star rating across roughly 8.5 thousand reviews, well below what a category '
     'leader in a trust-sensitive vertical should command, and our own scrape-based audit '
     'of the live site found the shopping cart functionally dependent on the location '
     'service: when zone resolution fails, the cart flow breaks with a null zone identifier. '
     'The interface itself feels dated relative to modern commerce design standards. Most '
     'significantly for our positioning, Chefaa’s AI narrative is marketing language '
     'around GPS matching and scheduling; there is no prescription OCR, no interaction '
     'checking, and no conversational assistant in the shipped product. A customer who '
     'wants those capabilities today has nowhere to go, which is precisely the wedge this '
     'platform drives.')
h2(story, '4.2 Vezeeta - The Healthcare Super-App',
   Paragraph('Vezeeta is the region’s healthcare super-app: doctor booking, pharmacy '
             'ordering, lab tests, and home visits in one product across Egypt, Saudi '
             'Arabia, Jordan, Lebanon, and Kenya. Its pharmacy vertical, launched in early '
             '2021, is operationally strong: 24/7 ordering with around 60-minute delivery '
             'in major cities, real-time order tracking, e-prescription upload, pharmacist '
             'chat, and insurance integration through the Shamel program advertising up to '
             '80 percent savings. Online payment and cash-on-delivery are both supported.', S['body']))
body(story, 'Vezeeta’s advantage is ecosystem gravity: a patient who books doctors '
     'there has one place to also fill prescriptions, and its multi-country footprint and '
     'marketing budget are beyond a self-funded entrant’s reach. Its constraint is focus. '
     'Pharmacy is one line item in a broad super-app, so the depth of the pharmacy '
     'experience, catalog curation, drug-safety tooling, and category merchandising, '
     'receives super-app priorities rather than pharmacy-specialist priorities. The '
     'head-to-head strategy is therefore depth over breadth: be the specialist experience '
     'for pharmacy-specific journeys, the prescription scan, the interaction check, the '
     'chronic refill, rather than a general healthcare dashboard.')
h2(story, '4.3 Yodawy - The B2B Infrastructure Player',
   Paragraph('Yodawy, with 34.5 million USD raised including its 10 million USD January '
             '2024 round, is the best-funded pharmacy-adjacent company in Egypt, but it '
             'competes in a different arena. Its business is a digital pharmacy marketplace '
             'and pharmacy-benefits-management layer serving insurers, corporates, and '
             'pharmacies: prescription generation integrations, claims processing, and '
             'fulfillment infrastructure. It is not principally a consumer storefront '
             'competing for organic B2C demand, which makes it less of a direct competitor '
             'than a possible future partner or fulfillment backbone for insured segments. '
             'Its fundraising success nevertheless signals that investors regard Egyptian '
             'pharmacy digitization as a fundable thesis, which is favorable context for the '
             'category The Pharmacy is entering.', S['body']))
h2(story, '4.4 Retail Chains - El Ezaby, Seif, and 19011',
   Paragraph('Egypt’s established pharmacy chains bring the strongest trust assets in the '
             'market: physical footprints, licensed pharmacists on staff, decades of brand '
             'recognition, and loyalty programs. El Ezaby operates a national chain with an '
             'app and a 19600 hotline, and both El Ezaby and Seif Pharmacies list their '
             'assortments on Talabat for on-demand delivery; Seif’s own app offers home '
             'delivery with online payment and a 19199 contact line. The 19011 service '
             'similarly aggregates medicine delivery through an app. These players convert '
             'existing store inventory into digital demand rather than building a digital '
             'pharmacy experience from first principles.', S['body']))
body(story, 'Their digital products show chain-retail priorities: store-locator flows, '
     'branch-level inventory, and promotion mechanics, with browsing experiences that lag '
     'modern e-commerce design. None offers AI tooling, and the prescription experience '
     'routes through phone calls or in-store visits rather than an upload-and-review '
     'workflow. For a digital-native customer, the chains are strong on fulfillment '
     'proximity but weak on the convenience layer that motivated online pharmacy in the '
     'first place, which is the gap a focused digital brand can occupy while partnering '
     'with chain inventory later, if needed, for fulfillment scale.')
h2(story, '4.5 Delivery Platforms - Talabat and Amazon Egypt',
   Paragraph('Horizontal platforms are the adjacent threat rather than present competitors '
     'in pharmacy depth. Talabat operates a pharmacy vertical in Egypt promising 24-hour '
     'medicine delivery from nearby pharmacies, and Amazon Egypt, which Euromonitor '
     'credits with roughly 11 percent of national e-commerce, sells over-the-counter health '
     'and wellness products though not prescription medicines. Their strengths are '
     'logistics networks and habitual usage; their pharmacy limitations are regulatory '
     '(prescription handling) and merchandising depth. They matter strategically as a '
     'warning: if a horizontal platform decides to own pharmacy verticals seriously, it '
     'will buy or partner capability rather than build it slowly, which makes building the '
     'defensible specialist experience now, with AI tooling and prescription workflows '
     'already operational, time-sensitive as well as sensible.', S['body']))
h2(story, '4.6 Capability Matrix')
make_table(story,
           ['Capability', 'The Pharmacy', 'Chefaa', 'Vezeeta', 'Retail Chains'],
           [
            ['Catalog depth', '496 SKUs, launch-scale', 'Tens of thousands via partner '
             'pharmacies', 'Large, super-app range', 'Full store inventory'],
            ['Languages', 'Full AR/EN with RTL mirroring', 'AR/EN', 'AR/EN', 'AR/EN'],
            ['AI features', 'Rx OCR, assistant, interaction checker', 'None shipped',
             'None shipped', 'None shipped'],
            ['Prescription handling', 'Upload, AI extraction, pharmacist review queue',
             'Upload with pharmacist callback', 'E-Rx upload with pharmacist chat',
             'Phone or in-store'],
            ['Payments', 'Cash on delivery (gateway staged)', 'Cards, wallets, COD',
             'Cards, wallets, insurance, COD', 'Cards, COD'],
            ['Delivery', '15 zones, 30-95 EGP, same-day Cairo', 'GPS-matched partner '
             'network nationwide', '24/7, about 60 minutes in major cities',
             'Branch-local same-day'],
            ['Mobile apps', 'Responsive web, PWA-ready', 'iOS and Android',
             'iOS and Android', 'iOS and Android'],
            ['Public app rating', 'Not yet launched', '3.7 stars (about 8.5k reviews)',
             'Category-leading', 'Varies by chain'],
            ['Loyalty / insurance', 'Roadmapped', 'Super Tawfir savings program',
             'Shamel insurance discounts', 'Chain points programs'],
            ['Admin tooling', 'Integrated panel: orders, stock, prices, Rx review',
             'Internal systems', 'Internal systems', 'Internal systems'],
           ],
           [0.16, 0.23, 0.21, 0.20, 0.20],
           'Table 4: Capability comparison across the Egyptian online pharmacy field, '
           'September 2026. The Pharmacy column reflects the verified build; competitor '
           'columns reflect public product surfaces.')

# ════════════════════════════════ CHAPTER 5 ════════════════════════════════
h1(story, '5. SWOT and Competitive Positioning')
h2(story, '5.1 Strengths',
   Paragraph('The platform’s strengths concentrate where the incumbents are weakest: '
             'experience quality and intelligent tooling. The codebase is fully owned and '
             'modern, with zero legacy debt and no third-party platform hostage risk, which '
             'is the exact failure mode that stranded the original prototype. The three AI '
             'features are real, verified, and unmatched in the Egyptian market today. The '
             'bilingual Arabic-first experience is not a translation layer but a mirrored '
             'right-to-left design, and in a market where competitors treat Arabic as a '
             'secondary locale, that reads as respect for the customer. Finally, the '
             'operational spine, 15-zone delivery economics, a six-stage order pipeline, and '
             'an integrated admin panel with prescription review, is already functioning '
             'rather than promised.', S['body']))
h2(story, '5.2 Weaknesses',
   Paragraph('The honest gaps are commercial infrastructure, not product quality. Payment '
             'accepts cash on delivery only; competitors already support cards, wallets, '
             'and in Vezeeta’s case insurance billing. The catalog holds 496 SKUs against '
             'incumbent assortments in the tens of thousands, which matters for search '
             'success rate and basket size. There are no native mobile apps, no loyalty '
             'program, no live courier tracking, and no outbound notification channels yet, '
             'and the database runs on development-grade SQLite until the production '
             'deployment lands. None of these is a structural disadvantage; each has a '
             'scheduled remedy in the roadmap, but until they ship, the platform competes '
             'best on experience-led acquisition rather than retention mechanics.', S['body']))
h2(story, '5.3 Opportunities',
   Paragraph('The external environment favors a focused, fast mover. The category is '
             'compounding at 19.2 percent annually while the leader’s app sits at 3.7 '
             'stars, an unusual combination of growing demand and dissatisfied demand. AI '
             'capability, our strongest asset, is also the direction analysts explicitly '
             'forecast for the segment. The chronic-disease refill market that Chefaa '
             'pioneered remains under-served by subscription mechanics, and Arabic-first '
             'search behavior is under-optimized across the field, which rewards a platform '
             'whose bilingual content is complete rather than partial. Longer horizon '
             'options, insurance billing partnerships modeled on Vezeeta’s Shamel, B2B '
             'corporate pharmacy accounts, and licensing the interaction-checking engine to '
             'other regional pharmacies, all build on capabilities already in the '
             'codebase.', S['body']))
h2(story, '5.4 Threats',
   Paragraph('The threats are asymmetry, regulation, and platform ambition. Funded '
             'incumbents can sustain price wars and marketing blitzes that a self-funded '
             'operator cannot match, and Chefaa has already demonstrated willingness to '
             'subsidize baskets through Super Tawfir. The regulatory gray zone could tighten '
             'abruptly; a new e-pharmacy statute requiring specific licensing would raise '
             'the compliance bar for everyone, and the operator prepared for it, with '
             'pharmacist review workflows, would face far less disruption than one that '
             'automated prescription fulfillment. Horizontal platforms are the third force: '
             'Talabat’s pharmacy vertical and Amazon’s wellness assortment signal '
             'appetite for the category, and a decisive horizontal move would compress '
             'independent players’ margins. The consistent mitigation across all three '
             'threats is speed: establish the specialist brand and its AI moat while the '
             'field remains shallow.', S['body']))
make_table(story,
           ['Quadrant', 'Summary'],
           [
            ['Strengths', 'Owned modern codebase; three unmatched AI features; bilingual '
             'RTL-native UX; complete commerce spine; integrated admin with Rx review'],
            ['Weaknesses', 'COD-only payments; 496-SKU catalog; no native apps; no loyalty, '
             'tracking, or notifications; development-grade database'],
            ['Opportunities', '19.2% CAGR market with a 3.7-star incumbent; AI-led '
             'differentiation; chronic refill subscriptions; insurance and B2B extensions'],
            ['Threats', 'Funded price competition; regulatory tightening; horizontal '
             'platforms (Talabat, Amazon) entering the category'],
           ],
           [0.16, 0.84],
           'Table 5: SWOT summary for The Pharmacy, September 2026.')
body(story, 'The positioning statement that follows from this analysis is deliberate and '
     'narrow: <b>The Pharmacy is the AI-first, Arabic-native online pharmacy, clinically '
     'safer by design, with prescription scanning, interaction checking, and a bilingual '
     'experience built as the primary product rather than an afterthought.</b> Every '
     'roadmap decision in the next chapter is evaluated against that sentence; anything '
     'that does not reinforce the specialist, safety-forward, bilingual identity is '
     'deferred in favor of things that do.')

# ════════════════════════════════ CHAPTER 6 ════════════════════════════════
h1(story, '6. Where We Are: Gaps, Maturity and Roadmap')
h2(story, '6.1 Maturity Assessment',
   Paragraph('The venture sits at the boundary between Phase 1 and Phase 2 of a four-phase '
             'lifecycle: the platform is built and verified, but it has not yet served a '
             'paying public customer. That distinction disciplines everything that follows. '
             'The engineering risk that dominates Phase 1 is retired; the commercial risks '
             'of Phase 2, payments, catalog depth, fulfillment partnerships, and regulatory '
             'formalization, are now the critical path, and none of them requires rebuilding '
             'what already works. The table below locates the venture on its lifecycle and '
             'names the exit criteria for each phase.', S['body']))
make_table(story,
           ['Phase', 'Scope', 'Status', 'Exit Criteria'],
           [
            ['1. Build', 'Platform, catalog, AI features, admin, verification', 'Complete',
             'Met: full commerce loop verified end-to-end'],
            ['2. Launch', 'Production hosting, payments, catalog scale, compliance '
             'formalization, first customers', 'Next (0-30 days)',
             'Live domain with PostgreSQL, card payments, about 1,500 SKUs, pharmacist '
             'partnership signed, first 100 orders'],
            ['3. Grow', 'Apps, loyalty, subscriptions, SEO engine, courier tracking',
             'Staged (31-90 days)',
             'App-store presence, repeat-purchase rate above 30 percent, refill '
             'subscriptions active'],
            ['4. Defend', 'Insurance and B2B channels, category expansion, AI moat '
             'deepening', 'Horizon',
             'Insured or corporate revenue line, defensible AI data advantage'],
           ],
           [0.13, 0.34, 0.15, 0.38],
           'Table 6: Four-phase maturity model and current position, September 2026.')
h2(story, '6.2 Gap Analysis',
   Paragraph('The gap table below is the operational core of this report: every capability '
             'where the platform trails the market standard, scored by launch priority. P0 '
             'gaps block credible public launch; P1 gaps weaken competitiveness within the '
             'first quarter; P2 gaps are retention and scale mechanics that matter most '
             'after launch traction exists. The pattern is consistent with the maturity '
             'assessment: the gaps are infrastructure and distribution, not product.', S['body']))
make_table(story,
           ['Capability', 'Today', 'Market Standard', 'Priority'],
           [
            ['Online payments', 'Cash on delivery', 'Cards, wallets, installments',
             'P0'],
            ['Catalog depth', '496 SKUs', 'Tens of thousands of SKUs', 'P0'],
            ['Order notifications', 'None', 'SMS, e-mail, push at every status change',
             'P0'],
            ['Compliance formalization', 'Review workflow built; partnership unsigned',
             'Licensed pharmacy entity, named pharmacist, audit trail', 'P0'],
            ['Production hosting', 'Local development, SQLite', 'Managed hosting, '
             'PostgreSQL, backups, monitoring', 'P0'],
            ['Native apps', 'Responsive web, PWA-ready', 'iOS and Android store presence',
             'P1'],
            ['Live courier tracking', 'Status timeline', 'GPS courier tracking', 'P1'],
            ['Customer support', 'AI assistant', 'Pharmacist chat and call center', 'P1'],
            ['Loyalty program', 'None', 'Points, tiers, refill discounts', 'P2'],
            ['SEO content engine', 'None', 'Condition guides, brand pages, blog', 'P2'],
           ],
           [0.22, 0.26, 0.34, 0.18],
           'Table 7: Capability gaps against market standard, prioritized for launch '
           'planning.',
           center_cols={3})
h2(story, '6.3 The 90-Day Roadmap')
body(story, 'The roadmap sequences the gap closures into three 30-day tiers, each with a '
     'single organizing objective. Tier one is launch readiness: production deployment, '
     'payments, catalog scale, and compliance. Tier two is competitive completeness: '
     'store presence, retention mechanics, and tracking. Tier three is growth '
     'infrastructure: channels beyond organic acquisition and the data assets that deepen '
     'the AI moat. Sequencing matters; payments and compliance precede marketing spend, '
     'and loyalty precedes paid retention, so that every acquired customer lands on a '
     'complete experience.')
make_table(story,
           ['Tier', 'Objective', 'Key Deliverables', 'Success Metric'],
           [
            ['Days 0-30', 'Launch readiness',
             'Vercel deployment with PostgreSQL; payment gateway integration; catalog '
             'expansion to about 1,500 SKUs; SMS and e-mail notifications; licensed '
             'pharmacist partnership and review SLA; analytics instrumentation',
             'Live domain taking card orders with pharmacist-reviewed Rx flow'],
            ['Days 31-60', 'Competitive completeness',
             'PWA and app-store wrappers; loyalty points engine; chronic refill '
             'subscription pilot; courier integration with live tracking; SEO content '
             'engine launch',
             'Store-listed app, 25+ orders per day in Cairo, repeat rate above 20 percent'],
            ['Days 61-90', 'Growth infrastructure',
             'Insurance and corporate account pilots; B2B ordering portal; category '
             'expansion into vitamins and wellness; performance marketing at scale; KPI '
             'dashboards',
             'First insured or corporate account; CAC below 150 EGP; NPS above 50'],
           ],
           [0.12, 0.16, 0.44, 0.28],
           'Table 8: The 90-day launch roadmap with tier objectives and success metrics.')
h2(story, '6.4 Success Metrics and Next Milestones')
body(story, 'The first ninety days after launch should be judged against a compact scorecard '
     'rather than vanity metrics: order volume and repeat-purchase rate for demand '
     'quality, prescription review turnaround and error rate for clinical safety, search '
     'success rate for catalog adequacy, and cost per acquisition against contribution '
     'margin for marketing efficiency. The immediate next milestone, however, is singular '
     'and unambiguous: deploy the verified platform to production hosting with a payment '
     'gateway and a signed pharmacist partnership, and open the doors to the first hundred '
     'customers. Everything this report has inventoried, the owned codebase, the verified '
     'AI features, the bilingual experience, and the complete commerce spine, exists to '
     'make that milestone a deployment exercise rather than a development project, which '
     'is exactly where a pre-launch venture should stand.')
story.append(Spacer(1, 20))
story.append(HRFlowable(width='100%', color=BORDER, thickness=0.6,
                        spaceBefore=0, spaceAfter=10))
story.append(Paragraph('<b>Data sources</b>', S['h3']))
for src in [
    'Ken Research, Egypt E-Pharmacy & Digital Health Market and Egypt AI-Powered '
    'E-Pharmacy Platforms Market reports, 2025-2026.',
    'PitchBook, Crunchbase, Disrupt Africa, Wamda, and Catalyst Africa for company '
    'funding histories (Chefaa, Yodawy), 2019-2026.',
    'GetLatka and Growjo revenue estimates for Chefaa Egypt, 2023-2026.',
    'P&S Market Research, Mordor Intelligence, Euromonitor, and Research and Markets '
    'for Egypt and MENA e-commerce and e-pharmacy market sizing, 2024-2026.',
    'StartupBlink, Top Health Care Startups in Cairo, September 2026.',
    'Adsero legal analysis, E-Pharmacies and Egyptian Law, December 2025.',
    'Google Play and Apple App Store listings for Chefaa, Vezeeta, Seif Pharmacies, and '
    'El Ezaby Pharmacies, accessed September 2026.',
    'Platform database and end-to-end verification logs from this engagement, '
    'September 2026.',
]:
    story.append(Paragraph(src, S['src']))

# ── Build ────────────────────────────────────────────────────────────────────
doc = TocDocTemplate(
    OUT_PDF, pagesize=A4,
    leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN,
    title=DOC_TITLE, author=DOC_AUTHOR, creator='Z.ai',
    subject='Platform status, Egypt e-pharmacy market analysis, competitor deep-dive, '
            'SWOT and 90-day launch roadmap')
doc.multiBuild(story, onFirstPage=on_page, onLaterPages=on_page)
print('Body PDF written:', OUT_PDF)

from pypdf import PdfReader
r = PdfReader(OUT_PDF)
print('Pages:', len(r.pages))
