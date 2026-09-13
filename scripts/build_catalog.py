#!/usr/bin/env python3
"""Consolidate scraped CHEFAA data + curated products into unified catalog.json"""
import json, re, hashlib

SRC = '/home/z/my-project/chefaa-source'
OUT = '/home/z/my-project/scripts/catalog.json'

def h(s): return int(hashlib.md5(s.encode()).hexdigest()[:8], 16)

def clean_brand(b):
    if not b: return 'Generic'
    b = str(b).strip()
    m = re.search(r'\(([^()]+)\)\s*$', b)
    if m and re.match(r'^[A-Za-z]', m.group(1)):
        return m.group(1).strip()
    if re.search(r'[A-Za-z]', b):
        parts = re.split(r'[|/]', b)
        for p in parts:
            p = p.strip()
            if re.match(r"^[A-Za-z][A-Za-z0-9&'\.\- ]*$", p) and len(p) > 1:
                return p
        m2 = re.search(r"([A-Za-z][A-Za-z0-9&'\.\-]*(?: [A-Za-z0-9&'\.\-]+)*)", b)
        if m2: return m2.group(1).strip()
    return b

def slugify(s):
    s = str(s).lower()
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    s = re.sub(r'-{2,}', '-', s)
    return s[:70].rstrip('-')

def norm_price(p):
    try: return round(float(str(p).replace(',', '').replace('EGP', '').strip()), 2)
    except: return None

def clean_name_en(s):
    s = str(s).strip()
    s = re.sub(r'\s*\|\s*', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    s = s.replace('...', '')
    return s.strip(' .|-')

products = []
seen_slugs = set()

def add(name_en, name_ar, brand, price, category, subcategory, volume='', rx=False, desc_en='', desc_ar=''):
    name_en = clean_name_en(name_en)
    if not name_en or not name_ar or not price or price < 5: return
    slug = slugify(name_en)
    if not slug or slug in seen_slugs: return
    seen_slugs.add(slug)
    seed = h(slug)
    rating = round(3.8 + (seed % 12) / 10.0, 1)
    if rating > 4.9: rating = 4.9
    reviews = 5 + seed % 950
    stock = 0 if seed % 17 == 0 else (3 + seed % 8 if seed % 11 == 0 else 25 + seed % 180)
    compare = None
    if seed % 10 < 3:
        compare = round(price * (1.08 + (seed % 18) / 100.0), 2)
    products.append({
        'slug': slug, 'nameEn': name_en, 'nameAr': name_ar,
        'brand': clean_brand(brand), 'price': price, 'compareAtPrice': compare,
        'category': category, 'subcategory': subcategory, 'volume': volume,
        'prescriptionRequired': bool(rx), 'stock': stock, 'rating': rating,
        'reviewCount': reviews, 'popularity': seed % 100,
        'descEn': desc_en, 'descAr': desc_ar
    })

# ---------- 1. Hair treatments (140) ----------
with open(f'{SRC}/chefaa_hair_treatment_products_data.json') as f:
    d = json.load(f)
for p in d['products']:
    vol = p.get('volume') or ''
    tt = p.get('treatment_type') or 'Treatment'
    tgt = p.get('target') or ''
    b = clean_brand(p['brand'])
    add(p['english_name'], p['arabic_name'], p['brand'], p.get('price_egp'), 'hair-care', 'treatments', vol,
        False, f"{tt} by {b}. {('Suitable for ' + tgt + '. ') if tgt else ''}Professional hair care treatment{(' ' + vol) if vol else ''} for healthier, stronger hair.",
        f"منتج علاجي للشعر من {b}، {tt}. {('مناسب لـ ' + tgt + '. ') if tgt else ''}يعزز صحة الشعر وقوته.")

# ---------- 2. Hair coloring (47) ----------
with open(f'{SRC}/chefaa_hair_coloring_products_data.json') as f:
    d = json.load(f)
for p in d['products']:
    sf = p.get('special_features') or ''
    if sf in ('Not specified', 'N/A'): sf = ''
    b = clean_brand(p['brand'])
    add(p['english_name'], p['arabic_name'], p['brand'], p.get('price_egp'), 'hair-care', 'coloring', p.get('volume_size') or '',
        False, f"Professional hair coloring product by {b}. {sf} Delivers rich, long-lasting color with radiant shine.",
        f"صبغة شعر احترافية من {b}. {sf} تمنح شعرك لوناً غنياً يدوم طويلاً بلمعة رائعة.")

# ---------- 3. Shampoo & conditioner (40) ----------
with open(f'{SRC}/chefaa_shampoo_conditioner_complete_data.json') as f:
    d = json.load(f)
for p in d['products']:
    hc = p.get('hair_concern') or ''
    b = clean_brand(p['brand'])
    add(p['english_name'], p['arabic_name'], p['brand'], p.get('price_egp'), 'hair-care', 'shampoo-conditioner', p.get('volume') or '',
        False, f"{p.get('type','Shampoo')} by {b} for {hc.lower() if hc else 'daily'} hair care{(' ' + str(p.get('volume',''))) if p.get('volume') else ''}. Gentle formula for clean, healthy hair.",
        f"{p.get('type','شامبو')} من {b} للعناية {('بـ' + hc) if hc else 'اليومية'} بالشعر{(' ' + str(p.get('volume',''))) if p.get('volume') else ''}. تركيبة لطيفة لشعر نظيف وصحي.")

# ---------- 4. Daily essentials (49) ----------
with open(f'{SRC}/chefaa_daily_essentials_phase1_comprehensive_updated.json') as f:
    d = json.load(f)
for p in d['products']:
    desc = p.get('description') or ''
    b = clean_brand(p['brand'])
    add(p['english_name'], p['arabic_name'], p['brand'], norm_price(p.get('price')), 'daily-essentials', 'personal-care', p.get('specifications') or '',
        False, (f"{desc}. Trusted personal care essential by {b} for your daily routine." if desc else f"Daily essential by {b}. Quality personal care product for everyday use."),
        f"من أساسيات العناية اليومية من {b}. منتج عالي الجودة للاستخدام اليومي.")

# ---------- 5. Skin care (54) ----------
with open(f'{SRC}/chefaa_skin_care_consolidated_products.json') as f:
    d = json.load(f)
for pg in d['consolidated_chefaa_skin_care_products']['products_by_page'].values():
    for p in pg.get('products', []):
        pt = p.get('product_type') or 'Skin care'
        b = clean_brand(p['brand'])
        add(p['product_name_english'], p['product_name_arabic'], p['brand'], p.get('price_egp'), 'skin-care', slugify(pt) or 'care', p.get('size_volume') or '',
        False, f"{pt} by {b}{(' ' + str(p.get('size_volume',''))) if p.get('size_volume') else ''}. Dermatologist-trusted skin care for a healthy, radiant complexion.",
        f"{pt} من {b}{(' ' + str(p.get('size_volume',''))) if p.get('size_volume') else ''}. عناية موثوقة بالبشرة لإطلالة صحية ومشرقة.")

# ---------- 6. Pain relief (58) ----------
with open(f'{SRC}/pain_relief_all_products_consolidated.json') as f:
    d = json.load(f)
for pg in d['all_products']:
    for p in pg.get('products', []):
        rx = str(p.get('prescription_required', 'No')).lower() == 'yes'
        b = clean_brand(p.get('brand'))
        add(p['english_name'], p['product_name'], p.get('brand'), p.get('price_egp'), 'medications', 'pain-relief', p.get('specifications') or '',
            rx, f"Analgesic and fever reducer by {b}. {p.get('dosage_information','')}. Effective relief from headaches, muscle pain and fever.",
            f"مسكن فعال وخافض للحرارة من {b}. {p.get('dosage_information','')}. يسكن الصداع وآلام العضلات والحمى.")

# ---------- 7. Medications extracted (12) ----------
with open(f'{SRC}/medications_products_extracted.json') as f:
    d = json.load(f)
for p in d['products']:
    cat = p.get('category', '')
    sub = 'stomach' if 'stomach' in cat.lower() or 'acid' in cat.lower() else 'general'
    rx = str(p.get('prescription_required', '')).lower() in ('yes', 'true', 'required')
    b = clean_brand(p.get('brand'))
    add(p['english_name'], p['product_name'], p.get('brand'), p.get('price_egp'), 'medications', sub, p.get('dosage_info') or '',
        rx, f"{p.get('description','')}. Quality medication available at The Pharmacy." if p.get('description') else f"Medication by {b} available at The Pharmacy.",
        f"{p.get('description','')}. دواء متوفر في ذا فارميسي." if p.get('description') else f"دواء من {b} متوفر في ذا فارميسي.")

# ---------- 8. Curated products ----------
CURATED = [
    ('Strepsils Honey & Lemon Lozenges 36', 'ستريبسلز أقراص استحلاب عسل وليمون 36', 'Strepsils', 95, 'medications', 'cough-cold', '36 lozenges', False, 'Soothing antiseptic lozenges for sore throat and mouth infections with honey and lemon.', 'أقراص استحلاب مطهرة لالتهاب الحلق والفم بنكهة العسل والليمون.'),
    ('Vicks VapoRub 50ml', 'فيكس فابوراب 50 مل', 'Vicks', 80, 'medications', 'cough-cold', '50ml jar', False, 'Topical cough suppressant with menthol and eucalyptus for fast relief from cough and congestion.', 'مرهم موضعي للكحة يحتوي على المنثول والأوكاليبتوس لتخفيف سريع من الاحتقان.'),
    ('Bronchicum Syrup 100ml', 'برونشيكم شراب 100 مل', 'Bronchicum', 68, 'medications', 'cough-cold', '100ml syrup', False, 'Herbal expectorant syrup for productive cough and bronchial congestion relief.', 'شراب عشبي طارد للبلغم لعلاج الكحة المصحوبة بالبلغم والاحتقان الشعبي.'),
    ('Congestal Tablets 20', 'كونجستال أقراص 20', 'Congestal', 42, 'medications', 'cough-cold', '20 tablets', False, 'Cold and flu relief tablets for congestion, runny nose and sinus pressure.', 'أقراص لعلاج نزلات البرد والإنفلونزا والاحتقان وسيلان الأنف.'),
    ('Antinal Capsules 20', 'أنتينال كبسولات 20', 'Antinal', 45, 'medications', 'stomach', '20 capsules', False, 'Antidiarrheal capsules for acute bacterial diarrhea and intestinal infections.', 'كبسولات لعلاج الإسهال الحاد البكتيري والالتهابات المعوية.'),
    ('Buscopan 10mg 20 Tablets', 'بوسكوبان 10 مجم 20 قرص', 'Buscopan', 58, 'medications', 'stomach', '20 tablets', False, 'Antispasmodic tablets for abdominal cramps and irritable bowel syndrome relief.', 'أقراص مضادة للتشنج لتقلصات البطن ومتلازمة القولون العصبي.'),
    ('Motilium 10mg 30 Tablets', 'موتيليوم 10 مجم 30 قرص', 'Motilium', 72, 'medications', 'stomach', '30 tablets', True, 'Prokinetic tablets for nausea, vomiting and delayed stomach emptying. Prescription required.', 'أقراص للغثيان والقيء وتحسين حركة المعدة. يتطلب روشتة طبية.'),
    ('Nexium 40mg 14 Tablets', 'نيكسيوم 40 مجم 14 قرص', 'Nexium', 165, 'medications', 'stomach', '14 tablets', True, 'Esomeprazole tablets for GERD, acid reflux and gastric ulcer treatment. Prescription required.', 'أقراص إيزوميبرازول لعلاج الارتجاع المريئي وقرحة المعدة. يتطلب روشتة طبية.'),
    ('Aerius 5mg 30 Tablets', 'إيريوس 5 مجم 30 قرص', 'Aerius', 118, 'medications', 'allergy', '30 tablets', False, 'Non-drowsy antihistamine for allergies, hay fever and chronic urticaria. Once daily.', 'مضاد هيستامين غير مسبب للنعاس للحساسية والحمى القشعية. جرعة يومية واحدة.'),
    ('Claritine 10mg 20 Tablets', 'كلاريتين 10 مجم 20 قرص', 'Claritine', 88, 'medications', 'allergy', '20 tablets', False, 'Loratadine tablets providing 24-hour non-drowsy relief from allergy symptoms.', 'أقراص لوراتادين لتخفيف أعراض الحساسية على مدار 24 ساعة دون نعاس.'),
    ('Zyrtec 10mg 20 Tablets', 'زيرتك 10 مجم 20 قرص', 'Zyrtec', 96, 'medications', 'allergy', '20 tablets', False, 'Cetirizine antihistamine for fast relief from sneezing, itching and hives.', 'سيتيريزين لتخفيف سريع من العطاس والحكة والشرى.'),
    ('Telfast 180mg 15 Tablets', 'تلفاست 180 مجم 15 قرص', 'Telfast', 105, 'medications', 'allergy', '15 tablets', False, 'Fexofenadine tablets for powerful non-drowsy seasonal allergy relief.', 'أقراص فيكسوفينادين لتخفيف قوي من حساسية الموسم دون نعاس.'),
    ('Zithromax 500mg 6 Tablets', 'زيثروماكس 500 مجم 6 أقراص', 'Zithromax', 190, 'medications', 'antibiotics', '6 tablets', True, 'Azithromycin antibiotic for respiratory, skin and ear infections. Prescription required.', 'مضاد حيوي أزيثرومايسين لالتهابات الجهاز التنفسي والجلد والأذن. يتطلب روشتة.'),
    ('Ciprofloxacin 500mg 10 Tablets', 'سيبروفلوكساسين 500 مجم 10 أقراص', 'Generic', 95, 'medications', 'antibiotics', '10 tablets', True, 'Broad-spectrum antibiotic for urinary and gastrointestinal infections. Prescription required.', 'مضاد حيوي واسع المجال لالتهابات المسالك البولية. يتطلب روشتة طبية.'),
    ('Flagyl 500mg 20 Tablets', 'فلاجيل 500 مجم 20 قرص', 'Flagyl', 85, 'medications', 'antibiotics', '20 tablets', True, 'Metronidazole tablets for anaerobic bacterial and protozoal infections. Prescription required.', 'ميترونيدازول للعدوى البكتيرية اللاهوائية والطفيلية. يتطلب روشتة.'),
    ('Glucophage 1000mg 30 Tablets', 'جلوكوفاج 1000 مجم 30 قرص', 'Glucophage', 110, 'medications', 'chronic-care', '30 tablets', True, 'Metformin for type 2 diabetes management. Prescription required.', 'ميتفورمين لعلاج السكري من النوع الثاني. يتطلب روشتة طبية.'),
    ('Janumet 50/1000mg 56 Tablets', 'جانوميت 50/1000 مجم 56 قرص', 'Janumet', 520, 'medications', 'chronic-care', '56 tablets', True, 'Sitagliptin/Metformin combination for type 2 diabetes control. Prescription required.', 'مركب سيتاجلبتين وميتفورمين للتحكم في السكري. يتطلب روشتة طبية.'),
    ('Lipitor 20mg 30 Tablets', 'ليبيتور 20 مجم 30 قرص', 'Lipitor', 175, 'medications', 'chronic-care', '30 tablets', True, 'Atorvastatin for lowering cholesterol and cardiovascular protection. Prescription required.', 'أتورفاستاتين لخفض الكوليسترول وحماية القلب. يتطلب روشتة طبية.'),
    ('Euthyrox 50mcg 100 Tablets', 'يوثيروكس 50 ميكروجرام 100 قرص', 'Euthyrox', 95, 'medications', 'chronic-care', '100 tablets', True, 'Levothyroxine for hypothyroidism management. Prescription required.', 'ليفوثيروكسين لعلاج قصور الغدة الدرقية. يتطلب روشتة طبية.'),
    ('Amlor 5mg 30 Capsules', 'أملور 5 مجم 30 كبسولة', 'Amlor', 105, 'medications', 'chronic-care', '30 capsules', True, 'Amlodipine capsules for hypertension and angina. Prescription required.', 'أملوديبين لعلاج ارتفاع ضغط الدم والذبحة الصدرية. يتطلب روشتة.'),
    ('Ventolin Evohaler 200 Doses', 'فنتولين بخاخ 200 جرعة', 'Ventolin', 130, 'medications', 'respiratory', '200 doses', True, 'Salbutamol inhaler for rapid asthma relief and bronchospasm prevention. Prescription required.', 'بخاخ سالبوتامول لتخفيف نوبة الربو بسرعة. يتطلب روشتة طبية.'),
    ('Singulair 10mg 28 Tablets', 'سينجولير 10 مجم 28 قرص', 'Singulair', 210, 'medications', 'respiratory', '28 tablets', True, 'Montelukast for asthma prevention and allergic rhinitis. Prescription required.', 'مونتيلوكاست للوقاية من الربو وحساسية الأنف. يتطلب روشتة.'),
    ('Clexane 40mg Syringes', 'كليكسان 40 مجم حقن', 'Clexane', 350, 'medications', 'chronic-care', 'prefilled syringes', True, 'Enoxaparin injections for blood clot prevention. Prescription required.', 'حقن إينوكسابارين للوقاية من تجلط الدم. يتطلب روشتة طبية.'),
    ('Doliprane 1000mg 16 Tablets', 'دوليبران 1000 مجم 16 قرص', 'Doliprane', 60, 'medications', 'pain-relief', '16 tablets', False, 'Paracetamol 1000mg tablets for headache, dental pain and fever.', 'باراسيتامول 1000 مجم للصداع وآلام الأسنان والحمى.'),
    ('Cataflam 50mg 20 Tablets', 'كاتافلام 50 مجم 20 قرص', 'Cataflam', 55, 'medications', 'pain-relief', '20 tablets', False, 'Diclofenac potassium fast-acting anti-inflammatory for acute pain and dysmenorrhea.', 'ديكلوفيناك بوتاسيوم سريع المفعول للآلام الحادة وعسر الطمث.'),
    ('Voltaren Emulgel 100g', 'فولتارين إيملجيل 100 جرام', 'Voltaren', 145, 'medications', 'pain-relief', '100g tube', False, 'Topical anti-inflammatory gel for muscle, joint and back pain relief.', 'جل مضاد للالتهاب موضعي لآلام العضلات والمفاصل والظهر.'),
    ('Centrum Adults 100 Tablets', 'سنتروم للبالغين 100 قرص', 'Centrum', 380, 'vitamins', 'multivitamins', '100 tablets', False, 'Complete daily multivitamin with 24 essential nutrients for overall health and immunity.', 'مكمل فيتامينات يومي شامل مع 24 عنصراً غذائياً أساسياً للصحة والمناعة.'),
    ('Centrum Women 60 Tablets', 'سنتروم للنساء 60 قرص', 'Centrum', 320, 'vitamins', 'multivitamins', '60 tablets', False, 'Multivitamin tailored for women with biotin, iron and vitamin D for energy and beauty.', 'فيتامينات مصممة للنساء مع البيوتين والحديد وفيتامين د للطاقة والجمال.'),
    ('Devarol-S 200000 IU Ampoule', 'ديفارول إس 200000 وحدة', 'Devarol', 65, 'vitamins', 'vitamin-d', 'ampoule', False, 'High-strength vitamin D3 ampoule for deficiency treatment and bone health.', 'أمبولة فيتامين د3 عالية التركيز لعلاج النقص وصحة العظام.'),
    ('Vitamin D3 5000 IU 60 Capsules', 'فيتامين د3 5000 وحدة 60 كبسولة', 'Natural', 180, 'vitamins', 'vitamin-d', '60 capsules', False, 'Daily vitamin D3 supplement supporting bones, muscles and immune function.', 'مكمل فيتامين د3 اليومي لدعم العظام والعضلات والمناعة.'),
    ('Omega-3 Plus 60 Capsules', 'أوميجا 3 بلس 60 كبسولة', 'Natural', 220, 'vitamins', 'supplements', '60 capsules', False, 'Fish oil omega-3 with EPA and DHA for heart, brain and joint health.', 'زيت سمك أوميجا 3 مع EPA و DHA لصحة القلب والدماغ والمفاصل.'),
    ('Vitacid C 1000mg Effervescent 20', 'فيتاسيد سي 1000 مجم فوارة 20', 'Vitacid', 75, 'vitamins', 'vitamin-c', '20 tablets', False, 'Effervescent vitamin C 1000mg for immune support and antioxidant protection.', 'فوار فيتامين سي 1000 مجم لدعم المناعة والحماية من الأكسدة.'),
    ('Redoxon Double Action 30 Tablets', 'ريدوكسون دبل أكشن 30 قرص', 'Redoxon', 120, 'vitamins', 'vitamin-c', '30 tablets', False, 'Vitamin C + Zinc effervescent for double immune system support.', 'فيتامين سي مع الزنك فوارة لدعم مزدوج لجهاز المناعة.'),
    ('Zinc 50mg 100 Tablets', 'زنك 50 مجم 100 قرص', 'Natural', 95, 'vitamins', 'supplements', '100 tablets', False, 'Essential zinc supplement for immunity, wound healing and skin health.', 'مكمل الزنك الأساسي للمناعة والتئام الجروح وصحة الجلد.'),
    ('Magnesium 500mg 90 Tablets', 'ماغنسيوم 500 مجم 90 قرص', 'Natural', 165, 'vitamins', 'supplements', '90 tablets', False, 'Magnesium supplement for muscle relaxation, sleep quality and nerve function.', 'مكمل الماغنسيوم لاسترخاء العضلات وجودة النوم ووظائف الأعصاب.'),
    ('B-Complex Forte 60 Tablets', 'بي كومبلكس فورت 60 قرص', 'Natural', 110, 'vitamins', 'supplements', '60 tablets', False, 'Vitamin B complex for energy metabolism, stress relief and nervous system health.', 'مركب فيتامينات ب لطاقة الجسم وتخفيف التوتر وصحة الجهاز العصبي.'),
    ('Cal-Mag 100 Tablets', 'كال ماج 100 قرص', 'Natural', 140, 'vitamins', 'supplements', '100 tablets', False, 'Calcium and magnesium combination for strong bones and teeth.', 'تركيبة الكالسيوم والماغنسيوم لعظام وأسنان قوية.'),
    ('Iron + Folic Acid 60 Tablets', 'حديد مع حمض فوليك 60 قرص', 'Natural', 85, 'vitamins', 'supplements', '60 tablets', False, 'Iron with folic acid for anemia prevention, pregnancy support and energy.', 'حديد مع حمض الفوليك للوقاية من الأنيميا ودعم الحمل والطاقة.'),
    ('Collagen + Vitamin C 300g Powder', 'كولاجين مع فيتامين سي 300 جرام', 'Natural', 450, 'vitamins', 'supplements', '300g powder', False, 'Hydrolyzed collagen powder with vitamin C for skin elasticity, hair and joints.', 'بودرة كولاجين مع فيتامين سي لمرونة الجلد والشعر والمفاصل.'),
    ('Probiotic 10 Billion 30 Capsules', 'بروبيوتيك 10 مليار 30 كبسولة', 'Natural', 260, 'vitamins', 'supplements', '30 capsules', False, '10 billion CFU probiotic for gut health, digestion and immunity.', 'بروبيوتيك 10 مليار وحدة لصحة الأمعاء والهضم والمناعة.'),
    ('Pampers Baby Dry Size 4 Mega 56', 'بامبرز بيبي دراي مقاس 4 ميجا 56', 'Pampers', 340, 'mom-baby', 'diapers', '56 diapers', False, 'Up to 12 hours of dryness with triple absorbent channels for comfortable nights.', 'جفاف يصل إلى 12 ساعة مع قنوات امتصاص ثلاثية لليالي مريحة.'),
    ('Pampers Premium Care Size 3 Jumbo 68', 'بامبرز بريميوم كير مقاس 3 جامبو 68', 'Pampers', 545, 'mom-baby', 'diapers', '68 diapers', False, 'Premium ultra-soft diapers with breathable layers and wetness indicator.', 'حفاضات فائقة النعومة مع طبقات تتنفس ومؤشر البلل.'),
    ("Johnson's Baby Shampoo 500ml", 'جونسون بيبي شامبو 500 مل', "Johnson's", 150, 'mom-baby', 'bath', '500ml', False, 'No-more-tears formula gently cleanses delicate baby hair and scalp.', 'تركيبة بدون دموع تنظف شعر وفروة رأس الطفل بلطف.'),
    ("Johnson's Baby Lotion 500ml", 'جونسون بيبي لوشن 500 مل', "Johnson's", 165, 'mom-baby', 'skin', '500ml', False, 'Moisturizing baby lotion for soft, smooth and protected skin all day.', 'لوشن مرطب للطفل لبشرة ناعمة ومحمية طوال اليوم.'),
    ('Bepanthen Ointment 100g', 'بيبانثين مرهم 100 جرام', 'Bepanthen', 240, 'mom-baby', 'skin', '100g tube', False, 'Provitamin B5 ointment protecting delicate skin and treating diaper rash.', 'مرهم ببروفيتامين ب5 يحمي البشرة الحساسة ويعالج التسلخات.'),
    ('Mustela Hydra Bebe Body Lotion 300ml', 'مستيلا هيدرا بيبي لوشن 300 مل', 'Mustela', 385, 'mom-baby', 'skin', '300ml', False, 'Hypoallergenic baby body lotion for immediate and long-lasting hydration.', 'لوشن جسم للأطفال مضاد للحساسية بترطيب فوري ودائم.'),
    ('Cerelac Wheat & Honey 400g', 'سيرلاك قمح وعسل 400 جرام', 'Cerelac', 125, 'mom-baby', 'food', '400g box', False, 'Iron-fortified infant cereal for babies from 6 months with wheat and honey.', 'حبوب أطفال مدعمة بالحديد من عمر 6 أشهر بالقمح والعسل.'),
    ('Nan 1 Optipro 400g', 'نان 1 أوبتي برو 400 جرام', 'Nan', 210, 'mom-baby', 'formula', '400g tin', False, 'Starter infant formula with optimized protein for babies from birth to 6 months.', 'لبن أطفال بروتين محسن من الولادة حتى 6 أشهر.'),
    ('Nan 2 Optipro Follow-up 400g', 'نان 2 أوبتي برو 400 جرام', 'Nan', 215, 'mom-baby', 'formula', '400g tin', False, 'Follow-up formula with optimized protein for babies from 6 to 12 months.', 'لبن تابع بروتين محسن من 6 إلى 12 شهراً.'),
    ('Pigeon Baby Wipes 80 Sheets', 'بيجن منادلات أطفال 80 منديل', 'Pigeon', 95, 'mom-baby', 'essentials', '80 wipes', False, 'Alcohol-free gentle wipes for delicate baby skin cleaning.', 'منادلات لطيفة خالية من الكحول لبشرة الطفل الحساسة.'),
    ('Sudocrem Antiseptic 60g', 'سودوكريم مطهر 60 جرام', 'Sudocrem', 130, 'mom-baby', 'skin', '60g jar', False, 'Antiseptic healing cream for diaper rash, eczema and minor skin irritations.', 'كريم مطهر شافي للتسلخات والإكزيما وتهيج الجلد البسيط.'),
    ('Chicco Natural Feeling Bottle 150ml', 'كيكو زجاجة رضاعة 150 مل', 'Chicco', 195, 'mom-baby', 'feeding', '150ml bottle', False, 'Anti-colic feeding bottle with physiological teat for newborns.', 'زجاجة رضاعة مضادة للغازات بحلمة فسيولوجية لحديثي الولادة.'),
    ('Freedent Baby Toothpaste 75ml', 'فريدينت معجون أسنان أطفال 75 مل', 'Freedent', 68, 'mom-baby', 'essentials', '75ml', False, 'Fluoride-safe training toothpaste for babies and toddlers.', 'معجون أسنان تدريبي آمن بالفلورايد للأطفال والرضع.'),
    ('Babyife Nasal Aspirator', 'بيبيفاي شفاط أنف', 'Babyife', 145, 'mom-baby', 'essentials', 'device', False, 'Gentle nasal aspirator for safe mucus removal in babies.', 'شفاط أنف لطيف لإزالة المخاط بأمان للأطفال.'),
    ('Mustela Stelatopia Bath Oil 200ml', 'مستيلا ستيلاتوبيا زيت حمام 200 مل', 'Mustela', 420, 'mom-baby', 'bath', '200ml', False, 'Relipidizing bath oil for very dry and eczema-prone baby skin.', 'زيت حمام معالج للبشرة الجافة جداً والمصابة بالإكزيما.'),
    ('Maybelline Lash Sensational Mascara', 'مايبيلين لاش سينسيشنال ماسكارا', 'Maybelline', 320, 'makeup', 'eyes', 'Black', False, 'Fan-effect volumizing mascara for full, sensational lashes without clumping.', 'ماسكارا مكثفة بتأثير المروحة لرموش كاملة مبهرة دون تكتل.'),
    ('Maybelline Fit Me Foundation SPF 15', 'مايبيلين فيت مي فاونديشن SPF 15', 'Maybelline', 295, 'makeup', 'face', '30ml', False, 'Natural, breathable foundation matching your skin tone with sun protection.', 'فاونديشن طبيعي يتنفس مع حماية من الشمس يناسب لون بشرتك.'),
    ("L'Oreal Infallible Lipstick 24H", 'لوريال إنفوليبل أحمر شفاه 24 ساعة', "L'Oreal", 340, 'makeup', 'lips', 'Various shades', False, 'Long-lasting 24-hour liquid lipstick with intense color payoff.', 'أحمر شفاه سائل يدوم 24 ساعة بلون كثيف وثابت.'),
    ('Essence Lash Princess Mascara', 'إيسنس لاش برنسيس ماسكارا', 'Essence', 150, 'makeup', 'eyes', 'Black', False, 'Cult-favorite volumizing mascara with conic shaped brush for dramatic lashes.', 'ماسكارا مكثفة أيقونية بفرشاة مخروطية لرموش درامية.'),
    ('NYX Soft Matte Lip Cream', 'نيكس سوفت مات ليب كريم', 'NYX', 210, 'makeup', 'lips', 'Various shades', False, 'Velvet matte lip cream with buttery smooth application.', 'كريم شفاه مطفي مخملي بملمس ناعم حريري.'),
    ('Revlon ColorStay Foundation', 'ريفلون كولورستاي فاونديشن', 'Revlon', 365, 'makeup', 'face', '30ml', False, 'Transfer-resistant foundation with up to 24 hours wear.', 'فاونديشن مقاوم للانحلال يدوم حتى 24 ساعة.'),
    ('Maybelline Super Stay Concealer', 'مايبيلين سوبر ستاي كونسيلر', 'Maybelline', 245, 'makeup', 'face', 'Various shades', False, 'Full coverage concealer for dark circles and imperfections, 24H wear.', 'كونسيلر بتغطية كاملة للهالات والعيوب يدوم 24 ساعة.'),
    ('Essence Eyebrow Pencil', 'إيسنس قلم حواجب', 'Essence', 85, 'makeup', 'eyes', 'Various shades', False, 'Precise eyebrow pencil for natural-looking, defined brows.', 'قلم حواجب دقيق لحواجب محددة بمظهر طبيعي.'),
    ('NYX Born To Glow Highlighter', 'نيكس بورن تو جلو هايلايتر', 'NYX', 235, 'makeup', 'face', 'Powder', False, 'Luminous highlighter for a natural, glowing complexion.', 'هايلايتر مضيء لإشراقة طبيعية مشرقة.'),
    ("L'Oreal Voluminous Mascara", 'لوريال فوليومينوس ماسكارا', "L'Oreal", 280, 'makeup', 'eyes', 'Black', False, 'Volume-building mascara for bold, thick lashes.', 'ماسكارا لبناء كثافة الرموش بشكل جريء.'),
    ('Essence Nail Polish 60+ Shades', 'إيسنس طلاء أظافر 60+ لون', 'Essence', 65, 'makeup', 'nails', 'Various shades', False, 'Quick-drying, chip-resistant nail polish in vibrant colors.', 'طلاء أظافر سريع الجفاف ومقاوم للتقصف بألوان زاهية.'),
    ('FENTY Gloss Bomb Universal', 'فينتي جلوس بومب', 'Fenty Beauty', 480, 'makeup', 'lips', 'Various shades', False, 'Universal lip gloss with shimmer for plump, juicy lips.', 'جلوس شفاه عام مع لمعان لشفاه ممتلئة وحيوية.'),
    ('Omron M2 Blood Pressure Monitor', 'أومرون إم2 جهاز قياس ضغط الدم', 'Omron', 1650, 'medical-supplies', 'devices', 'Upper arm', False, 'Clinically validated automatic BP monitor with hypertension indicator.', 'جهاز ضغط أوتوماتيكي معتمد طبياً مع مؤشر ارتفاع الضغط.'),
    ('Omron M3 IT BP Monitor with App', 'أومرون إم3 آي تي مع تطبيق', 'Omron', 2450, 'medical-supplies', 'devices', 'Bluetooth', False, 'Smart blood pressure monitor syncing readings to your smartphone.', 'جهاز ضغط ذكي يزامن القراءات مع هاتفك الذكي.'),
    ('Accu-Chek Performa Glucometer Kit', 'أكووتش بيرفورما جهاز سكر', 'Accu-Chek', 550, 'medical-supplies', 'devices', 'Kit + strips', False, 'Complete blood glucose monitoring kit with fast, accurate readings.', 'جهاز قياس سكر دم كامل مع نتائج سريعة ودقيقة.'),
    ('Accu-Chek Performa Strips 50', 'أكووتش بيرفورما شرائط 50', 'Accu-Chek', 320, 'medical-supplies', 'consumables', '50 strips', False, 'Glucose test strips compatible with Performa meters.', 'شرائط فحص السكر المتوافقة مع أجهزة بيرفورما.'),
    ('OneTouch Select Plus Meter', 'وان تاتش سيليكت بلس', 'OneTouch', 480, 'medical-supplies', 'devices', 'Kit', False, 'Color-coded glucose meter making readings easy to understand.', 'جهاز سكر بترميز لوني يسهل فهم النتائج.'),
    ('Beurer Thermometer FT09', 'بورير ترمومتر FT09', 'Beurer', 180, 'medical-supplies', 'devices', 'Digital', False, 'Fast 10-second digital thermometer with fever alarm.', 'ترمومتر رقمي سريع في 10 ثوانٍ مع تنبيه الحمى.'),
    ('Infrared Forehead Thermometer', 'ترمومتر جبلي بالأشعة تحت الحمراء', 'Generic', 350, 'medical-supplies', 'devices', 'Non-contact', False, 'Contactless forehead thermometer for hygienic temperature measurement.', 'ترمومتر بدون تلامس لقياس حرارة صحي وسريع.'),
    ('Compressor Nebulizer Kit', 'جهاز بخار نيبيولايزر', 'Generic', 750, 'medical-supplies', 'devices', 'Compressor', False, 'Home nebulizer for asthma and respiratory medication delivery.', 'جهاز بخار منزلي لأدوية الربو والجهاز التنفسي.'),
    ('Surgical Face Masks 50pcs', 'كمامات طبية 50 قطعة', 'Generic', 75, 'medical-supplies', 'consumables', '50 masks', False, '3-ply disposable surgical masks with 95% bacterial filtration.', 'كمامات طبية 3 طبقات بفلترة بكتيرية 95%.'),
    ('First Aid Kit Home 42 Pieces', 'حقيبة إسعافات أولية 42 قطعة', 'Generic', 280, 'medical-supplies', 'essentials', '42 pieces', False, 'Complete home first aid kit with bandages, antiseptics and tools.', 'حقيبة إسعاف منزلية كاملة مع الشاش والمطهرات والأدوات.'),
    ('Elastic Bandage 10cm', 'رباط ضاغط 10 سم', 'Generic', 35, 'medical-supplies', 'consumables', '10cm roll', False, 'Stretchable elastic bandage for support and compression.', 'رباط مطاطي قابل للمد للدعم والضغط.'),
    ('Digital Body Weight Scale', 'ميزان رقمي لوزن الجسم', 'Generic', 290, 'medical-supplies', 'devices', 'Glass', False, 'Tempered glass digital scale with precise step-on technology.', 'ميزان رقمي بزجاج مقوى بتقنية الدقة الفورية.'),
    ('Hot Water Bag 2L', 'كيس ماء ساخن 2 لتر', 'Generic', 60, 'medical-supplies', 'essentials', '2L', False, 'Classic hot water bottle for pain relief and warmth therapy.', 'كيس ماء ساخن كلاسيكي لتخفيف الألم والعلاج الحراري.'),
    ('Wheelchair Foldable Standard', 'كرسي متحرك قابل للطي', 'Generic', 2200, 'medical-supplies', 'mobility', 'Standard', False, 'Foldable steel wheelchair with removable armrests and brakes.', 'كرسي متحرك فولاذي قابل للطي بمساند قابلة للإزالة.'),
    ('Walking Stick Height Adjustable', 'عصا مشي قابلة للتعديل', 'Generic', 220, 'medical-supplies', 'mobility', 'Aluminum', False, 'Lightweight aluminum cane with ergonomic handle.', 'عصا ألومنيوم خفيفة بمقبض مريح.'),
    ('Durex Classic Condoms 12', 'ديريكس كوندوم كلاسيك 12', 'Durex', 110, 'sexual-health', 'contraception', '12 condoms', False, 'Natural-feel latex condoms with extra lubrication for safety and comfort.', 'كوندومات لاتكس طبيعية الملمس مع تشحيم إضافي للأمان والراحة.'),
    ('Durex Intimate Gel 10ml', 'ديريكس جل حميمي 10 مل', 'Durex', 175, 'sexual-health', 'wellness', '10ml', False, 'Stimulating gel designed to enhance intimacy and sensation.', 'جل محفز لتعزيز العلاقة الحميمة والإحساس.'),
    ('Pregnancy Test Midstream 2 Pack', 'اختبار حمل 2 اختبار', 'Generic', 55, 'sexual-health', 'tests', '2 tests', False, 'Rapid hCG pregnancy tests with 99% accuracy from first day of missed period.', 'اختبارات حمل سريعة بدقة 99% من أول يوم تأخر.'),
    ('Ovulation Test Strips 5 Pack', 'شرائط اختبار التبويض 5', 'Generic', 60, 'sexual-health', 'tests', '5 strips', False, 'LH ovulation predictor strips for family planning.', 'شرائط تنبؤ بالتبويض لتنظيم الأسرة.'),
    ('Viagra 100mg 4 Tablets', 'فياجرا 100 مجم 4 أقراص', 'Pfizer', 260, 'sexual-health', 'medications', '4 tablets', True, 'Sildenafil for erectile dysfunction. Prescription required and pharmacist consultation.', 'سيلدينافيل لعلاج ضعف الانتصاب. يتطلب روشتة واستشارة صيدلي.'),
    ('Cialis 20mg 4 Tablets', 'سياليس 20 مجم 4 أقراص', 'Lilly', 320, 'sexual-health', 'medications', '4 tablets', True, 'Tadalafil long-acting tablets for erectile dysfunction. Prescription required.', 'تادالافيل طويل المفعول. يتطلب روشتة طبية.'),
    ('Personal Lubricant Water-Based 100ml', 'مزلق شخصي قاعدة مائية 100 مل', 'Generic', 95, 'sexual-health', 'wellness', '100ml', False, 'Dermatologically tested water-based lubricant, condom compatible.', 'مزلق مائي مختبر جلدياً ومتوافق مع الكوندوم.'),
    ('Femina Vaginal Ovules 6', 'فيمينا لبوس مهبلي 6', 'Femina', 120, 'sexual-health', 'medications', '6 ovules', True, 'Antifungal vaginal ovules for candida infections. Ask our pharmacist.', 'لبوس مهبلي مضاد للفطريات. استشر الصيدلي.'),
    ('Frontline Plus Dog Large 3 Pipettes', 'فرونت لاين بلس للكلاب 3 أمبولات', 'Frontline', 420, 'pet-supplies', 'health', '3 pipettes', False, 'Flea and tick spot-on treatment for large dogs over 20kg.', 'علاج البراغيث والقراد للكلاب كبيرة الحجم فوق 20 كجم.'),
    ('Frontline Plus Cat 3 Pipettes', 'فرونت لاين بلس للقطط 3 أمبولات', 'Frontline', 380, 'pet-supplies', 'health', '3 pipettes', False, 'Flea and tick spot-on protection for cats and kittens.', 'حماية من البراغيث والقراد للقطط والقطط الصغيرة.'),
    ('Pet Shampoo Anti-Itch 250ml', 'شامبو حيوانات مضاد للحكة 250 مل', 'Generic', 85, 'pet-supplies', 'grooming', '250ml', False, 'Soothing medicated pet shampoo for itchy and sensitive skin.', 'شامبو طبي مهدئ للحيوانات للبشرة المتهيجة والحساسة.'),
    ('Pet Vitamin Supplement 60 Tablets', 'فيتامينات حيوانات 60 قرص', 'Generic', 130, 'pet-supplies', 'health', '60 tablets', False, 'Daily multivitamin tablets for dogs and cats vitality.', 'فيتامينات يومية لنشاط وحيوية الكلاب والقطط.'),
    ('Cat Litter Premium Bentonite 10L', 'فضلات قطط بنتونيت 10 لتر', 'Generic', 145, 'pet-supplies', 'essentials', '10L bag', False, 'Clumping bentonite cat litter with odor control.', 'فضلات قطط متكتلة مع تحكم في الروائح.'),
    ('Dog Dental Chews Medium 14', 'مضغات أسنان للكلاب 14', 'Generic', 110, 'pet-supplies', 'food', '14 chews', False, 'Dental care chews reducing tartar and freshening breath.', 'مضغات للعناية بأسنان الكلاب وتقليل الجير.'),
]
for c in CURATED:
    add(*c)

# save
cats = {}
for p in products:
    cats.setdefault(p['category'], set()).add(p['subcategory'])

stats = {k: len([p for p in products if p['category'] == k]) for k in cats}
out = {'products': products, 'stats': stats, 'subcategories': {k: sorted(v) for k, v in cats.items()}}
with open(OUT, 'w') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

print('TOTAL PRODUCTS:', len(products))
print('BY CATEGORY:')
for k, v in stats.items(): print(f'  {k}: {v}')
rx_count = sum(1 for p in products if p['prescriptionRequired'])
print('RX products:', rx_count)
print('Out of stock:', sum(1 for p in products if p['stock'] == 0))
