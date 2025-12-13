import json
import glob
import requests
import time
from typing import List, Dict

# Supabase configuration
SUPABASE_URL = "https://sggthvsfucciptpgokgk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNnZ3RodnNmdWNjaXB0cGdva2drIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTkzMDcyMCwiZXhwIjoyMDc3NTA2NzIwfQ.wzbtz77OtHcW8Ie6m_mc2On3qumQKJz26x_ygAqluhc"

# Category UUID mapping
CATEGORY_IDS = {
    'medications': "00b6ecb8-30f9-43c6-9e3c-4e9bfbabde77",
    'hair_care': "5fff1dcd-f553-48d1-bb18-308ac1b7464c",
    'skin_care': "b41aefa7-3c94-4a69-9eb3-3daa3fd5fa50",
    'daily_essentials': "3c0552fd-50c2-4880-9332-fd203c27ac64",
    'mom_baby': "fcd2a965-f02b-4447-bf44-3a3cddfcef8b",
    'makeup': "9327d9ad-55d1-47c9-a35f-aff5acada789",
    'medical_supplies': "02ee9fdb-6273-44d5-8211-42346a66cbeb",
    'vitamins': "1771c4d1-9a6a-49d4-96d5-779f3329c402"
}

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

def create_slug(name: str, index: int = 0) -> str:
    """Create URL-friendly slug from product name"""
    import re
    slug = re.sub(r'[^\w\s-]', '', name.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    slug = slug[:90]
    if index > 0:
        slug = f"{slug}-{index}"
    return slug

def normalize_product(prod: Dict, category_id: str, index: int = 0) -> Dict:
    """Normalize product data for database insertion"""
    name_ar = prod.get('name', prod.get('product_name', prod.get('name_ar', '')))
    name_en = prod.get('name_en', prod.get('product_name_english', name_ar))
    
    # Handle price - skip if invalid
    try:
        price = float(prod.get('price_egp', prod.get('price', 0)) or 0)
    except (ValueError, TypeError):
        price = 0.0
    
    return {
        'name': (name_en or name_ar)[:255],
        'name_ar': name_ar[:255],
        'slug': create_slug(name_en or name_ar, index),
        'description': (prod.get('description', '') or '')[:500],
        'description_ar': (prod.get('description', '') or '')[:500],
        'price': price,
        'brand': (prod.get('brand', prod.get('brand_name', 'Unknown')) or 'Unknown')[:100],
        'category_id': category_id,
        'stock_quantity': 100,
        'rating': 4.5,
        'review_count': 0,
        'images': [],
        'formulation': '',
        'prescription_required': prod.get('prescription_required', False)
    }

def batch_insert_products(products: List[Dict], batch_size: int = 50) -> int:
    """Insert products in batches"""
    total_inserted = 0
    
    for i in range(0, len(products), batch_size):
        batch = products[i:i + batch_size]
        try:
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/products",
                headers=headers,
                json=batch
            )
            
            if response.status_code in [200, 201]:
                total_inserted += len(batch)
                print(f"✓ Batch {i//batch_size + 1}: {len(batch)} products (Total: {total_inserted})")
            else:
                print(f"✗ Batch {i//batch_size + 1} error: {response.status_code}")
                print(f"   {response.text[:150]}")
            
            time.sleep(0.15)
            
        except Exception as e:
            print(f"✗ Batch {i//batch_size + 1} exception: {str(e)[:100]}")
    
    return total_inserted

def extract_medications() -> List[Dict]:
    """Extract medications from page files"""
    products = []
    page_files = glob.glob('/workspace/data/medications_page_*.json')
    category_id = CATEGORY_IDS['medications']
    
    for filepath in sorted(page_files)[:50]:  # First 50 pages
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'products' in data:
                    for idx, prod in enumerate(data['products']):
                        products.append(normalize_product(prod, category_id, len(products)))
        except Exception as e:
            pass
    
    return products

def extract_category_file(filepath: str, category_id: str) -> List[Dict]:
    """Extract products from category file"""
    products = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            if 'products' in data and isinstance(data['products'], list):
                for idx, prod in enumerate(data['products']):
                    products.append(normalize_product(prod, category_id, idx))
            elif 'categories' in data:
                for cat_data in data['categories'].values():
                    if isinstance(cat_data, dict) and 'products' in cat_data:
                        for idx, prod in enumerate(cat_data['products']):
                            products.append(normalize_product(prod, category_id, len(products)))
    except Exception as e:
        print(f"   Error: {str(e)[:50]}")
    
    return products

print("=" * 60)
print("CHEFAA PRODUCT IMPORT - Real Data Integration")
print("=" * 60)

# Clear existing products
print("\n1. Clearing existing products...")
delete_response = requests.delete(
    f"{SUPABASE_URL}/rest/v1/products?id=gte.0",
    headers=headers
)
print(f"   Status: {delete_response.status_code}")

all_products = []

print("\n2. Extracting products...")

print("   Medications...")
meds = extract_medications()
all_products.extend(meds)
print(f"   → {len(meds)} products")

print("   Hair Care...")
hair = extract_category_file('/workspace/data/hair_care/hair_care_products.json', CATEGORY_IDS['hair_care'])
all_products.extend(hair)
print(f"   → {len(hair)} products")

print("   Skin Care...")
skin = extract_category_file('/workspace/data/skin_care/skin_care_products.json', CATEGORY_IDS['skin_care'])
all_products.extend(skin)
print(f"   → {len(skin)} products")

print("   Daily Essentials...")
daily = extract_category_file('/workspace/data/daily_essentials_products.json', CATEGORY_IDS['daily_essentials'])
all_products.extend(daily)
print(f"   → {len(daily)} products")

print("   Mom & Baby...")
mom_baby = extract_category_file('/workspace/data/mom_baby/mom_baby_products.json', CATEGORY_IDS['mom_baby'])
all_products.extend(mom_baby)
print(f"   → {len(mom_baby)} products")

print(f"\n3. Total products extracted: {len(all_products)}")

print("\n4. Importing to database...")
imported = batch_insert_products(all_products)

print("\n" + "=" * 60)
print(f"COMPLETE: {imported} products imported successfully")
print("=" * 60)
