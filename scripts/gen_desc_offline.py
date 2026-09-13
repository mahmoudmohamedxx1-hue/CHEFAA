#!/usr/bin/env python3
"""Offline bilingual product description generator (no API needed).

Produces scripts/descriptions_offline.json: {slug: {descEn, descAr}}
Quality: professional pharmacy copy, 3-5 sentences, varied via hash rotation.
Incorporates real scraped one-liners where names match.
"""
import json
import re
import glob
import os

BASE = '/home/z/my-project'
EXPORT = f'{BASE}/scripts/products_export.json'
OUT = f'{BASE}/scripts/descriptions_offline.json'

# ---------------- knowledge bases ----------------

DRUGS = [
    (r'panadol|paracetamol|acetaminophen|adol|abimol|cetal',
     'paracetamol-based analgesic and antipyretic',
     'مسكّن للألم وخافض للحرارة يعتمد على الباراسيتامول',
     'works effectively against headaches, muscle pain, toothache, period pain and fever',
     'فعّال للصداع وآلام العضلات والأسنان وآلام الدورة الشهرية والحرارة'),
    (r'brufen|ibuprofen|advil|profen|flamar| cataflam|diclofenac|voltaren|ketolac|ketofan',
     'non-steroidal anti-inflammatory (NSAID)',
     'مضاد التهاب غير ستيرويدي',
     'relieves pain, inflammation and fever, ideal for joint and muscle pain',
     'يخفف الألم والالتهاب والحرارة، مثالي لآلام المفاصل والعضلات'),
    (r'aspirin|asperine|aspro',
     'acetylsalicylic acid tablet', 'أقراص حمض أسيتيل ساليسيليك',
     'used for pain relief, fever and low-dose cardiovascular protection',
     'يُستخدم لتخفيف الألم والحرارة ووقاية القلب بجرعات منخفضة'),
    (r'augmentin|amoxicillin| curam|hibiotic|amoclav',
     'penicillin-class antibiotic', 'مضاد حيوي من فئة البنسلين',
     'fights a wide range of bacterial infections of the respiratory tract, sinuses, skin and urinary system',
     'يحارب مجموعة واسعة من العدوى البكتيرية في الجهاز التنفسي والجيوب والجلد والمسالك البولية'),
    (r'zithromax|azithromycin|azrolid|zetamax',
     'macrolide antibiotic', 'مضاد حيوي ماكروليدي',
     'treats respiratory, skin and ear infections with a short convenient course',
     'يعالج التهابات الجهاز التنفسي والجلد والأذن بكورة علاجية قصيرة'),
    (r'omeprazole|prazole|controloc|pantoprazole|nexium|esomeprazole|zollinger',
     'proton pump inhibitor', 'مثبط لمضخة البروتون',
     'reduces stomach acid to relieve heartburn, reflux and gastric ulcers',
     'يقلل حموضة المعدة لتخفيف الحرقان والارتجاع وقرح المعدة'),
    (r'cetirizine|zyrtec|allerg|loratadine|claritine|claritin|telfast|fexofenadine|histafree|ahist',
     'non-drowsy antihistamine', 'مضاد هيستامين غير مسبب للنعاس',
     'controls allergy symptoms such as sneezing, runny nose, itchy eyes and skin rashes',
     'يضبط أعراض الحساسية مثل العطس وسيلان الأنف وحكة العين والطفح الجلدي'),
    (r'ventolin|salbutamol|farcolin|inhaler|pulmicort|budesonide',
     'bronchodilator inhaler', 'بخاخ موسّع للشعب الهوائية',
     'opens the airways quickly to relieve wheezing, cough and shortness of breath in asthma',
     'يفتح الشعب الهوائية بسرعة لتخفيف الأزيز والكحة وضيق النفس في حالات الربو'),
    (r'concor|bisoprolol|atenolol|concour|betaloc|metoprolol',
     'beta-blocker', 'حاصر بيتا',
     'helps control high blood pressure and supports heart rhythm stability',
     'يساعد في ضبط ضغط الدم المرتفع واستقرار نظم القلب'),
    (r'glucophage|metformin|amaryl|glimepiride|januvia|sitagliptin',
     'oral antidiabetic', 'خافض سكر عن طريق الفم',
     'helps manage blood sugar levels in type 2 diabetes as part of your treatment plan',
     'يساعد في ضبط مستوى السكر في الدم لمرضى السكري من النوع الثاني ضمن خطة العلاج'),
    (r'lipitor|atorvastatin|crestor|rosuvastatin|statin',
     'cholesterol-lowering statin', 'ستاتين خافض للكوليسترول',
     'lowers LDL cholesterol to protect the heart and blood vessels',
     'يخفض الكوليسترول الضار لحماية القلب والأوعية الدموية'),
    (r'antinal|nifuroxazide|streptoquin|entero|buscopan|spasmo|coloverin|colona',
     'gastrointestinal relief treatment', 'علاج لمشكلات الجهاز الهضمي',
     'eases stomach cramps, diarrhea and intestinal discomfort',
     'يخفف تقلصات المعدة والإسهال واضطرابات الأمعاء'),
    (r'motilium|domperidone|metoclopramide|nausea|vomistop',
     'anti-nausea prokinetic', 'علاج للغثيان وتنظيم حركة المعدة',
     'relieves nausea, vomiting and bloating by restoring normal stomach movement',
     'يخفف الغثيان والقيء والانتفاخ بإعادة حركة المعدة الطبيعية'),
    (r'viagra|sildenafil|cialis|tadalafil|vardenafil',
     'men\'s wellness medication', 'دواء صحة الرجال',
     'supports men\'s intimate health as prescribed by a physician',
     'يدعم الصحة الجنسية للرجال حسب إرشادات الطبيب'),
]

VITAMINS = [
    (r'vitamin c|ascorbic', 'Vitamin C', 'فيتامين سي',
     'acts as a powerful antioxidant, supporting immunity, collagen production and brighter skin',
     'مضاد أكسدة قوي يدعم المناعة وإنتاج الكولاجين ونضارة البشرة'),
    (r'vitamin d|calcium|osteo', 'bone-health nutrients', 'عناصر صحة العظام',
     'supports strong bones, teeth and healthy calcium absorption',
     'يدعم صحة العظام والأسنان وامتصاص الكالسيوم'),
    (r'omega|fish oil|salmon oil', 'Omega-3 fatty acids', 'أحماض أوميغا 3',
     'supports heart health, brain function and joint flexibility',
     'يدعم صحة القلب ووظائف المخ ومرونة المفاصل'),
    (r'multivitamin|multi-vitamin|centrum|supradyn|vitamax|perfectil',
     'comprehensive daily multivitamin', 'فيتامينات متعددة يومية شاملة',
     'fills nutritional gaps to sustain daily energy, immunity and vitality',
     'يسد الفجوات الغذائية لدعم الطاقة اليومية والمناعة والحيوية'),
    (r'zinc', 'Zinc', 'الزنك',
     'supports immune defense, skin healing and healthy hair',
     'يدعم جهاز المناعة وشفاء البشرة وصحة الشعر'),
    (r'iron|ferrous', 'Iron', 'الحديد',
     'helps prevent iron deficiency and supports healthy red blood cells',
     'يساعد في الوقاية من نقص الحديد ويدعم كريات الدم الحمراء'),
    (r'magnesium', 'Magnesium', 'المغنيسيوم',
     'supports muscle relaxation, nerve function and better sleep quality',
     'يدعم استرخاء العضلات ووظائف الأعصاب وجودة النوم'),
    (r'biotin|hair vitamin|hairburst', 'Biotin', 'البيوتين',
     'nourishes hair from within for stronger strands and healthy growth',
     'يغذي الشعر من الداخل لخصلات أقوى ونمو صحي'),
    (r'probiotic|lactobacillus|acidophilus', 'probiotics', 'البروبيوتيك',
     'restores the natural balance of gut flora for better digestion and immunity',
     'يعيد التوازن الطبيعي لبكتيريا الأمعاء لهضم أفضل ومناعة أقوى'),
    (r'collagen', 'collagen', 'الكولاجين',
     'promotes skin elasticity, hydrated glow and joint comfort',
     'يعزز مرونة البشرة ونضارتها وراحة المفاصل'),
    (r'panax|ginseng|gingko|energy', 'energizing herbal complex', 'مركب أعشاب منشطة',
     'naturally boosts energy, focus and physical endurance',
     'يعزز الطاقة والتركيز والقدرة على التحمل بشكل طبيعي'),
]

SKIN_ACTIVES = [
    (r'hyaluronic|hydra|aquaboost|moistur', 'deep hydration with hyaluronic acid', 'ترطيب عميق بحمض الهيالورونيك'),
    (r'niacinamide', 'visible pore refinement and even tone with niacinamide', 'تنقيح المسام وتوحيد اللون بالنياسيناميد'),
    (r'retinol|retinal', 'skin renewal and anti-aging action with retinol', 'تجديد البشرة ومقاومة التجاعيد بالريتينول'),
    (r'vitamin c|ascorbic|brighten|lighten|whitening|glow', 'antioxidant brightening for a more radiant, even complexion', 'تفتيح مضاد للأكسدة لبشرة أكثر إشراقاً وتوحيداً'),
    (r'acne|acne|salicylic|benzoyl| breakout|pimple', 'targeted blemish and acne control', 'استهداف الحبوب والتحكم في حب الشباب'),
    (r'spf|sun|sunscreen|sunblock|eclat solaire', 'broad-spectrum sun protection against UVA/UVB rays', 'حماية واسعة من أشعة الشمس UVA/UVB'),
    (r'aloe|sooth|calm|sensitive', 'gentle soothing care for sensitive skin', 'عناية لطيفة مهدئة للبشرة الحساسة'),
    (r'charcoal|clay|purify|detox|mask', 'purifying detox that draws out impurities and excess oil', 'تنقية تسحب الشوائب والزيوت الزائدة'),
    (r'shea|butter|ceramide|barrier|repair|bepanthen|panthenol', 'barrier-repairing moisture for stressed skin', 'ترطيب مثبّت للبشرة المرهقة وإصلاح حاجزها الوقائي'),
    (r'snail|mucin', 'regenerating snail extract for repair and glow', 'خلاصة الحلزون لتجديد البشرة وإشراقها'),
    (r'anti.?aging|wrinkle|firm|lift|age', 'firming anti-wrinkle care for a youthful look', 'عناية مشدودة مقاومة للتجاعيد لمظهر شبابي'),
    (r'eye|contour|dark circle', 'targeted eye-contour care for dark circles and puffiness', 'عناية مركزة لمنطقة العين للهالات والانتفاخات'),
    (r'hand|body|foot|heel', 'rich nourishing care for dry, rough skin', 'عناية مغذية غنية للبشرة الجافة والمتشققة'),
    (r'lip', 'softening lip care for smooth, supple lips', 'عناية ملينة للشفاه لنعومة فورية'),
    (r'scrub|exfoliat|peeling', 'gentle exfoliation that renews skin texture', 'تقشير لطيف يجدد ملمس البشرة'),
    (r'cleans|wash|gel wash|foam|micellar', 'effective yet gentle cleansing', 'تنظيف فعّال ولطيف في آن واحد'),
]

HAIR_ACTIVES = [
    (r'anti.?dandruff|dandruff|قشرة', 'anti-dandruff action that calms flaking and itch', 'مفعول مضاد للقشرة يهدئ التسلخات والحكة'),
    (r'hair loss|hairloss|anti.?hairloss|fall|فقدان الشعر|grow', 'anti-hair-loss support that strengthens roots', 'دعم ضد تساقط الشعر يقوي الجذور'),
    (r'keratin', 'keratin smoothing and strengthening', 'تنعيم وتقوي بالكيراتين'),
    (r'argan|moroccan|elvive|marula', 'argan-oil nourishment for silky, frizz-free hair', 'تغذية بزيت الأرجان لشعر حريري بدون هيشان'),
    (r'collagen|protein|bond|repair|damage|treatment', 'deep repair for damaged and chemically-treated hair', 'إصلاح عميق للشعر التالف والمعالج كيميائياً'),
    (r'color|colour|dye|صبغة|castings', 'color-protecting care that keeps shades vibrant', 'عناية حافظة للون تحافظ على حيوية الدرجات'),
    (r'curl|curly|كيرلي', 'curl definition and bounce', 'تحديد الكيرل ومنحه ارتداداً صحياً'),
    (r'straight|smooth|relax', 'sleek smoothing for manageable hair', 'تنعيم فائق لشعر سهل التصفيف'),
    (r'volume|thickening|dense', 'body-boosting volume from the roots', 'كثافة وامتلاء من الجذور'),
    (r'oily|grease|sebum|oil control', 'sebum-regulating freshness', 'ضبط الإفرازات الدهنية وانتعاش فوري'),
    (r'dry|hydrat|moistur|شعر جاف', 'intensive moisture for thirsty strands', 'ترطيب مكثف للخصلات العطشى'),
    (r'kids|baby|children|أطفال', 'tear-free gentle care for kids', 'عناية لطيفة بدون دموع للأطفال'),
    (r'serum|oil|ampoule|elixir', 'concentrated treatment for intensive results', 'علاج مركز لنتائج مكثفة'),
    (r'shampoo', 'gentle daily cleansing', 'تنظيف يومي لطيف'),
    (r'conditioner|balm|mask', 'softening care for easy detangling', 'عناية ملينة تسهّل فك التشابك'),
]

FORM_MAP = [
    (r'tablet|tab\b|قرص', 'tablets', 'أقراص'),
    (r'capsule|cap\b|كبسولة', 'capsules', 'كبسولات'),
    (r'syrup|شراب|elixir', 'syrup', 'شراب'),
    (r'drops|قطرات|eye drop', 'drops', 'قطرات'),
    (r'inhaler|بخاخ', 'inhaler', 'بخاخ'),
    (r'spray|سبراي', 'spray', 'سبراي'),
    (r'serum|سيروم', 'serum', 'سيروم'),
    (r'cream|كريم', 'cream', 'كريم'),
    (r'gel\b|\bجل\b', 'gel', 'جل'),
    (r'oil|زيت', 'oil', 'زيت'),
    (r'mask|ماسك', 'mask', 'ماسك'),
    (r'shampoo|شامبو', 'shampoo', 'شامبو'),
    (r'conditioner|بلسم', 'conditioner', 'بلسم'),
    (r'stick|ستيك', 'stick', 'ستيك'),
    (r'roll.?on|رول', 'roll-on', 'رول أون'),
    (r'soap|صابون', 'bar', 'بار صابون'),
    (r'ointment|مرهم', 'ointment', 'مرهم'),
    (r'suppository|لبوس', 'suppository', 'لبوس'),
]

RX_EN = 'Dispensed with a valid prescription only — always follow your doctor\'s instructions and read the leaflet before use.'
RX_AR = 'يصرف بروشتة طبية فقط — يرجى اتباع إرشادات الطبيب وقراءة النشرة الداخلية قبل الاستخدام.'

USAGE = {
    'medications': ('Take exactly as directed on the package or as advised by your doctor or pharmacist.',
                    'يُستخدم حسب الجرعة الموضحة على العلبة أو حسب إرشادات الطبيب أو الصيدلي.'),
    'vitamins': ('Take one serving daily with a meal, or as recommended by your healthcare provider.',
                 'تناول جرعة واحدة يومياً مع الطعام أو حسب توصية مقدم الرعاية الصحية.'),
    'skin-care': ('Apply to clean skin morning and/or evening, massaging gently until fully absorbed.',
                  'يُوضع على بشرة نظيفة صباحاً و/أو مساءً مع تدليك لطيف حتى الامتصاص الكامل.'),
    'hair-care': ('Apply to wet hair, massage into scalp and strands, then rinse thoroughly; for leave-ins, apply to damp hair.',
                  'يُوزع على الشعر المبلل مع تدليك فروة الرأس والخصلات ثم يشطف جيداً؛ وإن كان من نوع بدون شطف يوضع على الشعر الرطب.'),
    'mom-baby': ('Gently apply or use as needed, ideal for daily baby-care routines.',
                 'يُستخدم برفق عند الحاجة، مثالي لروتين العناية اليومي بالطفل.'),
    'daily-essentials': ('Use daily as part of your personal-care routine for best results.',
                         'يُستخدم يومياً ضمن روتين العناية الشخصية لأفضل النتائج.'),
    'makeup': ('Apply and blend evenly; remove at the end of the day with a gentle cleanser.',
               'يُوضع ويوزع بالتساوي، ويزال في نهاية اليوم بمنظف لطيف.'),
    'medical-supplies': ('Use as directed, following the instructions on the package.',
                         'يُستخدم حسب التعليمات الموضحة على العلبة.'),
    'sexual-health': ('Use as directed on the package; consult a pharmacist if you have questions.',
                      'يُستخدم حسب التعليمات على العلبة واستشر الصيدلي عند وجود أي استفسار.'),
    'pet-supplies': ('Use as directed for your pet\'s size and needs.',
                     'يُستخدم حسب حجم حيوانك الأليف واحتياجاته.'),
}


BRAND_FIX = {
    "L'Or": "L'Oréal Paris",
    "L'Oreal": "L'Oréal",
    'Loreal': "L'Oréal",
    "L'Oreal Paris": "L'Oréal Paris",
}

GENERIC_BRANDS = {'generic', 'natural', 'no brand', 'unknown', 'other', 'none'}


def clean_brand(b):
    b = (b or '').strip()
    return BRAND_FIX.get(b, b)


def h(s):
    x = 0
    for ch in s:
        x = (x * 31 + ord(ch)) & 0xffffffff
    return x


def pick(lst, seed):
    return lst[h(seed) % len(lst)]


def find(patterns, text):
    for pat, *rest in patterns:
        if re.search(pat, text, re.I):
            return rest
    return None


def load_scraped():
    """Index of scraped one-line descriptions keyed by normalized english name."""
    idx = {}
    files = [
        'chefaa_daily_essentials_phase1_comprehensive_updated.json',
        'chefaa_daily_essentials_phase1_comprehensive.json',
        'chefaa_hair_coloring_products_data.json',
        'medications_products_extracted.json',
    ]
    for fn in files:
        p = os.path.join(BASE, 'chefaa-source', fn)
        if not os.path.exists(p):
            continue
        try:
            data = json.load(open(p))
        except Exception:
            continue
        items = data if isinstance(data, list) else (data.get('products') or [])
        for it in items:
            if not isinstance(it, dict):
                continue
            en = it.get('english_name') or ''
            desc = it.get('description') or it.get('special_features') or ''
            if en and desc and len(desc) > 25:
                key = re.sub(r'[^a-z0-9]', '', en.lower())[:40]
                idx[key] = re.sub(r'\s+', ' ', desc).strip()
    return idx


def gen(p, scraped_idx):
    cat = p['category']['slug']
    sub = p.get('subcategory') or ''
    name_en, name_ar = p['nameEn'], p['nameAr']
    brand = p['brand']
    vol = p.get('volume') or ''
    text = f"{name_en} {name_ar} {sub} {brand}"

    # scraped real line?
    key = re.sub(r'[^a-z0-9]', '', name_en.lower())[:40]
    scraped = scraped_idx.get(key) or scraped_idx.get(key[:30]) or None

    # find actives
    drug = find(DRUGS, text)
    vit = find(VITAMINS, text)
    skin = find(SKIN_ACTIVES, text)
    hair = find(HAIR_ACTIVES, text)
    # form must come from the product NAME only (subcategory text like
    # "shampoo-conditioner" would wrongly match "shampoo" for a conditioner)
    name_text = f'{name_en} {name_ar}'
    form = find(FORM_MAP, name_text) or find(FORM_MAP, text) or ('product', 'منتج')

    rx = p.get('prescriptionRequired')
    if rx is None:
        rx = bool(re.search(r'augmentin|amoxicillin|zithromax|concor|glucophage|viagra|sildenafil|cialis|insulin', text, re.I))

    what_en = what_ar = benefit_en = benefit_ar = None
    brand = clean_brand(brand)

    if drug:
        what_en, what_ar, benefit_en, benefit_ar = drug
    elif cat == 'vitamins' and vit:
        en_name, ar_name, benefit_en, benefit_ar = vit
        if brand.lower() in GENERIC_BRANDS:
            what_en, what_ar = f'{en_name} supplement', f'مكمل {ar_name}'
        else:
            what_en, what_ar = f'{en_name} supplement from {brand}', f'مكمل {ar_name} من {brand}'
    elif cat == 'skin-care' and skin:
        what_en = pick([f'{brand} skincare {form[0]}', f'{brand} {form[0]} for daily skincare'],
                       name_en + 'w')
        what_ar = pick([f'{form[1]} من {brand} للعناية بالبشرة', f'منتج {brand} للعناية اليومية بالبشرة'],
                       name_ar + 'w')
        benefit_en, benefit_ar = f'Delivers {skin[0]}', f'يمنح بشرتك {skin[1]}'
    elif cat == 'hair-care' and hair:
        what_en = pick([f'{brand} hair care {form[0]}', f'{brand} professional {form[0]}'],
                       name_en + 'w')
        what_ar = pick([f'{form[1]} للشعر من {brand}', f'منتج {brand} الاحترافي للعناية بالشعر'],
                       name_ar + 'w')
        benefit_en, benefit_ar = f'Provides {hair[0]}', f'يمنح شعرك {hair[1]}'
    elif cat == 'hair-care':
        what_en, what_ar = f'{brand} hair care {form[0]}', f'{form[1]} للشعر من {brand}'
        benefit_en = 'keeps hair clean, soft and manageable with every use'
        benefit_ar = 'يحافظ على شعر نظيف وناعم وسهل التصفيف مع كل استخدام'
    elif cat == 'skin-care':
        what_en, what_ar = f'{brand} skincare {form[0]}', f'{form[1]} للعناية بالبشرة من {brand}'
        benefit_en = 'supports healthy, comfortable and radiant-looking skin'
        benefit_ar = 'يدعم بشرة صحية ومريحة ومشرقة'
    elif cat == 'medications':
        what_en, what_ar = f'{brand} {form[0]}', f'{form[1]} من {brand}'
        benefit_en = 'serves as a trusted pharmacy staple for everyday family care'
        benefit_ar = 'منتج موثوق في الصيدليات للعناية اليومية بالأسرة'
    elif cat == 'vitamins':
        what_en, what_ar = f'{brand} daily supplement', f'مكمل غذائي يومي من {brand}'
        benefit_en = 'helps fill daily nutritional gaps and keeps you at your best'
        benefit_ar = 'يسد الاحتياجات الغذائية اليومية ويحافظ على أفضل حالاتك'
    elif cat == 'mom-baby':
        what_en, what_ar = f'{brand} baby care {form[0]}', f'{form[1]} للعناية بالطفل من {brand}'
        benefit_en = 'provides gentle, trusted care developed with your little one\'s comfort in mind'
        benefit_ar = 'عناية لطيفة وموثوقة صُممت مع مراعاة راحة طفلك'
    elif cat == 'daily-essentials':
        what_en, what_ar = f'{brand} personal care {form[0]}', f'{form[1]} للعناية الشخصية من {brand}'
        benefit_en = 'gives you reliable freshness and everyday comfort'
        benefit_ar = 'أساسي يومي يمنحك انتعاشاً وراحة تدوم'
    elif cat == 'makeup':
        what_en, what_ar = f'{brand} makeup {form[0]}', f'منتج مكياج {form[1]} من {brand}'
        benefit_en = 'adds effortless color and definition with a smooth, long-wearing finish'
        benefit_ar = 'يضيف لوناً وتحديداً بسهولة بلمسة نهائية ناعمة تدوم طويلاً'
    elif cat == 'medical-supplies':
        what_en, what_ar = f'{brand} medical supply', f'مستلزم طبي من {brand}'
        benefit_en = 'offers reliable home-care quality you can depend on'
        benefit_ar = 'جودة موثوقة للرعاية المنزلية يمكنك الاعتماد عليها'
    elif cat == 'sexual-health':
        what_en, what_ar = f'{brand} wellness product', f'منتج صحة عائلية من {brand}'
        benefit_en = 'delivers discreet, reliable personal wellness care'
        benefit_ar = 'عناية شخصية موثوقة وبخصوصية تامة'
    else:  # pet-supplies
        what_en, what_ar = f'{brand} pet care {form[0]}', f'{form[1]} للعناية بالحيوانات الأليفة من {brand}'
        benefit_en = 'keeps your pet healthy, clean and happy'
        benefit_ar = 'يحافظ على صحة حيوانك الأليف ونظافته وسعادته'

    # name descriptor (strip brand, but keep full name if remainder is too bare)
    desc_name = name_en
    for b in {brand, p.get('brand', '')}:
        if b and desc_name.lower().startswith(b.lower()):
            candidate = desc_name[len(b):].strip(' |-–')
            letters = re.sub(r'[^a-zA-Z]', '', candidate)
            if len(letters) >= 8:
                desc_name = candidate
            break

    art = 'an' if form[0][0].lower() in 'aeiou' else 'a'
    open_en = pick([
        f'{what_en.capitalize()} — {desc_name}.',
        f'{desc_name} by {brand}: {art} {form[0]} designed for daily use.',
        f'{what_en.capitalize()} ({desc_name}).',
    ], p['slug'])
    open_ar = pick([
        f'{what_ar} — {name_ar}.',
        f'{name_ar} من {brand}: {form[1]} مصمم للاستخدام اليومي.',
        f'{what_ar} ({name_ar}).',
    ], p['slug'] + 'a')

    # scraped line as extra detail (clean Arabic segments for EN)
    if scraped:
        scraped = re.sub(r'\([^\)]*[\u0600-\u06FF][^\)]*\)', '', scraped)
        scraped = re.sub(r'[\u0600-\u06FF]+', ' ', scraped)
        scraped = re.sub(r'\s+', ' ', scraped).strip(' ,|')
    scrap_en = f' {scraped.rstrip(".")}.' if scraped and len(scraped) > 25 else ''

    mid_en = f'It {benefit_en}.' if not benefit_en.startswith(('Delivers', 'Provides')) else f'{benefit_en}.'
    mid_ar = f'{benefit_ar}.'

    usage_en, usage_ar = USAGE.get(cat, USAGE['medical-supplies'])

    def size_like(v):
        v = (v or '').strip().lower()
        if not v or v in ('not specified', 'n/a'):
            return False
        return bool(re.search(r'\d|ml|gm|gr|gram|kg|oz|piece|pc|sachet|tablet|capsul|pipette|diaper|condom|pack|strip|vial|sheet|tissue|roll', v))

    vol_en = f' Pack size: {vol}.' if size_like(vol) else ''
    vol_ar = f' الحجم: {vol}.' if size_like(vol) else ''

    tail_en = pick([
        'From The Pharmacy, delivered fast to your door anywhere in Egypt.',
        'Order now from The Pharmacy for quick, careful delivery across Egypt.',
        'Brought to you by The Pharmacy — genuine products, pharmacist-checked.',
    ], p['slug'] + 't')
    tail_ar = pick([
        'من ذا فارميسي، يوصل سريعاً حتى باب منزلك في كل أنحاء مصر.',
        'اطلبه الآن من ذا فارميسي ليصلك بسرعة وعناية في جميع أنحاء مصر.',
        'من ذا فارميسي — منتجات أصلية بمراجعة صيدلي.',
    ], p['slug'] + 't' + 'a')

    desc_en = f'{open_en}{scrap_en} {mid_en} {usage_en}{vol_en} {tail_en}'
    if rx:
        desc_en += f' {RX_EN}'
    desc_ar = f'{open_ar} {mid_ar} {usage_ar}{vol_ar} {tail_ar}'
    if rx:
        desc_ar += f' {RX_AR}'

    desc_en = re.sub(r'\s+', ' ', desc_en).replace(' .', '.').strip()
    desc_ar = re.sub(r'\s+', ' ', desc_ar).replace(' .', '.').replace('،.', '،').strip()
    return {'descEn': desc_en, 'descAr': desc_ar}


def main():
    products = json.load(open(EXPORT))
    scraped_idx = load_scraped()
    print(f'scraped descriptions indexed: {len(scraped_idx)}')
    out = {}
    for p in products:
        out[p['slug']] = gen(p, scraped_idx)
    json.dump(out, open(OUT, 'w'), ensure_ascii=False, indent=1)
    print(f'generated {len(out)} descriptions -> {OUT}')
    # print samples
    import random
    for slug in random.sample(list(out), 5):
        d = out[slug]
        print('---', slug)
        print('EN:', d['descEn'])
        print('AR:', d['descAr'])


if __name__ == '__main__':
    main()
