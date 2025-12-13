import json
import os
import glob

# Initialize consolidated data
all_products = []
category_mapping = {
    'Medications': 1,
    'Hair Care': 2,
    'Skin Care': 3,
    'Daily Essentials': 4,
    'Mom & Baby': 5,
    'Makeup & Accessories': 6,
    'Medical Supplies': 7,
    'Vitamins & Supplements': 8,
    'Sexual Wellness': 9,
    'Pet Supplies': 10
}

def extract_medications():
    """Extract all medications from individual page files"""
    products = []
    page_files = glob.glob('/workspace/data/medications_page_*.json')
    
    for filepath in sorted(page_files):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'products' in data:
                    for prod in data['products']:
                        products.append({
                            'name_ar': prod.get('product_name', ''),
                            'name_en': prod.get('product_name_english', prod.get('name', '')),
                            'description_ar': prod.get('description', ''),
                            'description_en': prod.get('description', ''),
                            'price': float(prod.get('price_egp', prod.get('price', 0))),
                            'brand': prod.get('brand_name', prod.get('brand', 'Unknown')),
                            'category_id': 1,  # Medications
                            'stock': 'in_stock' if prod.get('availability_status', '').lower().find('stock') >= 0 else 'out_of_stock',
                            'rating': 4.5,
                            'image_url': prod.get('image', ''),
                            'prescription_required': prod.get('prescription_required', True)
                        })
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
    
    print(f"Extracted {len(products)} medications")
    return products

def extract_category(filepath, category_id, category_name):
    """Extract products from a category file"""
    products = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Fix common JSON issues
            content = content.replace('\n}', '\n}')
            data = json.loads(content)
            
            # Different structures for different files
            if 'products' in data and isinstance(data['products'], list):
                for prod in data['products']:
                    products.append(normalize_product(prod, category_id))
            elif 'categories' in data:
                # remaining_categories format
                for cat_key, cat_data in data['categories'].items():
                    if 'products' in cat_data:
                        for prod in cat_data['products']:
                            products.append(normalize_product(prod, category_id))
    except Exception as e:
        print(f"Error processing {category_name}: {e}")
    
    print(f"Extracted {len(products)} {category_name}")
    return products

def normalize_product(prod, category_id):
    """Normalize product data structure"""
    return {
        'name_ar': prod.get('name', prod.get('product_name', prod.get('name_ar', ''))),
        'name_en': prod.get('name_en', prod.get('product_name_english', prod.get('name', ''))),
        'description_ar': prod.get('description', prod.get('desc', '')),
        'description_en': prod.get('description', prod.get('desc', '')),
        'price': float(prod.get('price_egp', prod.get('price', 0))),
        'brand': prod.get('brand', prod.get('brand_name', 'Unknown')),
        'category_id': category_id,
        'stock': 'in_stock' if str(prod.get('stock_status', prod.get('availability_status', ''))).lower().find('stock') >= 0 else 'out_of_stock',
        'rating': 4.5,
        'image_url': prod.get('image', prod.get('image_url', '')),
        'prescription_required': prod.get('prescription_required', False)
    }

# Extract all products
print("Starting product consolidation...")
all_products = []

# Medications
all_products.extend(extract_medications())

# Hair Care
all_products.extend(extract_category('/workspace/data/hair_care/hair_care_products.json', 2, 'Hair Care'))

# Skin Care
all_products.extend(extract_category('/workspace/data/skin_care/skin_care_products.json', 3, 'Skin Care'))

# Daily Essentials
all_products.extend(extract_category('/workspace/data/daily_essentials_products.json', 4, 'Daily Essentials'))

# Mom & Baby
all_products.extend(extract_category('/workspace/data/mom_baby/mom_baby_products.json', 5, 'Mom & Baby'))

# Remaining categories (Makeup, Medical Supplies, etc.)
all_products.extend(extract_category('/workspace/data/remaining_categories/remaining_categories_products.json', 6, 'Remaining Categories'))

# Save consolidated products
output_file = '/workspace/chefaa-clone/public/data/consolidated_products.json'
os.makedirs(os.path.dirname(output_file), exist_ok=True)

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'total_products': len(all_products),
        'products': all_products
    }, f, ensure_ascii=False, indent=2)

print(f"\nTotal products consolidated: {len(all_products)}")
print(f"Saved to: {output_file}")
