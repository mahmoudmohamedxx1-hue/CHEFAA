import json
import glob
import requests
import time
from typing import List, Dict

# Supabase configuration
SUPABASE_URL = "https://sggthvsfucciptpgokgk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNnZ3RodnNmdWNjaXB0cGdva2drIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTkzMDcyMCwiZXhwIjoyMDc3NTA2NzIwfQ.wzbtz77OtHcW8Ie6m_mc2On3qumQKJz26x_ygAqluhc"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

def create_slug(name: str) -> str:
    """Create URL-friendly slug from product name"""
    import re
    # Remove special characters and replace spaces with hyphens
    slug = re.sub(r'[^\w\s-]', '', name.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug[:100]  # Limit length

def normalize_product(prod: Dict, category_id: int) -> Dict:
    """Normalize product data for database insertion"""
    name_ar = prod.get('name', prod.get('product_name', prod.get('name_ar', '')))
    name_en = prod.get('name_en', prod.get('product_name_english', name_ar))
    
    return {
        'name': name_en or name_ar,
        'name_ar': name_ar,
        'name_en': name_en,
        'slug': create_slug(name_en or name_ar),
        'description': (prod.get('description', '') or '')[:500],
        'description_ar': (prod.get('description', '') or '')[:500],
        'price': float(prod.get('price_egp', prod.get('price', 0)) or 0),
        'brand': (prod.get('brand', prod.get('brand_name', 'Unknown')) or 'Unknown')[:100],
        'category_id': category_id,
        'stock_quantity': 100 if str(prod.get('stock_status', prod.get('availability_status', ''))).lower().find('stock') >= 0 else 0,
        'rating': 4.5,
        'review_count': 0,
        'images': [],
        'formulation': '',
        'active_ingredient': ''
    }

def batch_insert_products(products: List[Dict], batch_size: int = 100) -> int:
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
                print(f"✓ Inserted batch {i//batch_size + 1}: {len(batch)} products (Total: {total_inserted})")
            else:
                print(f"✗ Error inserting batch {i//batch_size + 1}: {response.status_code} - {response.text[:200]}")
            
            time.sleep(0.1)  # Rate limiting
            
        except Exception as e:
            print(f"✗ Exception in batch {i//batch_size + 1}: {e}")
    
    return total_inserted

def extract_medications() -> List[Dict]:
    """Extract medications from page files"""
    products = []
    page_files = glob.glob('/workspace/data/medications_page_*.json')
    
    for filepath in sorted(page_files)[:50]:  # Limit to first 50 pages for initial import
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'products' in data:
                    for prod in data['products']:
                        products.append(normalize_product(prod, 1))
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
    
    return products

def extract_category_file(filepath: str, category_id: int) -> List[Dict]:
    """Extract products from category file"""
    products = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            if 'products' in data and isinstance(data['products'], list):
                for prod in data['products']:
                    products.append(normalize_product(prod, category_id))
            elif 'categories' in data:
                # remaining_categories format
                for cat_data in data['categories'].values():
                    if isinstance(cat_data, dict) and 'products' in cat_data:
                        for prod in cat_data['products']:
                            products.append(normalize_product(prod, category_id))
    except Exception as e:
        print(f"Error processing category file: {e}")
    
    return products

print("Starting product import...")
print("=" * 60)

# Clear existing products
print("\n1. Clearing existing products...")
delete_response = requests.delete(
    f"{SUPABASE_URL}/rest/v1/products?id=gte.0",
    headers=headers
)
print(f"   Cleared: {delete_response.status_code}")

all_products = []

# Extract from each category
print("\n2. Extracting products from data files...")

print("   - Medications...")
meds = extract_medications()
all_products.extend(meds)
print(f"     Found: {len(meds)} products")

print("   - Hair Care...")
hair = extract_category_file('/workspace/data/hair_care/hair_care_products.json', 2)
all_products.extend(hair)
print(f"     Found: {len(hair)} products")

print("   - Skin Care...")
skin = extract_category_file('/workspace/data/skin_care/skin_care_products.json', 3)
all_products.extend(skin)
print(f"     Found: {len(skin)} products")

print("   - Daily Essentials...")
daily = extract_category_file('/workspace/data/daily_essentials_products.json', 4)
all_products.extend(daily)
print(f"     Found: {len(daily)} products")

print("   - Mom & Baby...")
mom_baby = extract_category_file('/workspace/data/mom_baby/mom_baby_products.json', 5)
all_products.extend(mom_baby)
print(f"     Found: {len(mom_baby)} products")

print(f"\n3. Total products to import: {len(all_products)}")

# Batch insert
print("\n4. Importing products to database...")
imported = batch_insert_products(all_products, batch_size=50)

print("\n" + "=" * 60)
print(f"Import complete! Successfully imported {imported} products")
