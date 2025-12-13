import json
import glob
import requests
import re
from typing import Dict, List, Any

SUPABASE_URL = "https://sggthvsfucciptpgokgk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNnZ3RodnNmdWNjaXB0cGdva2drIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTkzMDcyMCwiZXhwIjoyMDc3NTA2NzIwfQ.wzbtz77OtHcW8Ie6m_mc2On3qumQKJz26x_ygAqluhc"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

def normalize_product_name(name: str) -> str:
    """Normalize product name for matching"""
    if not name:
        return ""
    name = name.lower().strip()
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'\s+', ' ', name)
    return name

def load_medications_overview(file_path: str) -> List[Dict]:
    """Load medication overview data"""
    overviews = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        medications = data.get('medications', [])
        for med in medications:
            desc = med.get('description', '')
            if isinstance(desc, dict):
                desc_text = desc.get('english', '') or desc.get('arabic', '')
            else:
                desc_text = str(desc) if desc else ''
            
            dosage = med.get('dosage_and_administration', '')
            if isinstance(dosage, dict):
                dosage_text = dosage.get('english', '') or dosage.get('arabic', '')
            else:
                dosage_text = str(dosage) if dosage else ''
            
            warnings = med.get('contraindications_and_warnings', '')
            if isinstance(warnings, dict):
                warnings_text = warnings.get('english', '') or warnings.get('arabic', '')
            else:
                warnings_text = str(warnings) if warnings else ''
            
            storage = med.get('storage_conditions', '')
            if isinstance(storage, dict):
                storage_text = storage.get('english', '') or storage.get('arabic', '')
            else:
                storage_text = str(storage) if storage else ''
            
            overview = {
                'product_name': med.get('product_name_english') or med.get('product_name_arabic', ''),
                'product_name_ar': med.get('product_name_arabic', ''),
                'overview_description': desc_text,
                'active_ingredients': med.get('active_ingredients', []),
                'therapeutic_indications': med.get('therapeutic_indications', {}),
                'dosage_administration': dosage_text,
                'product_specifications': med.get('specifications', {}),
                'warnings_precautions': warnings_text,
                'storage_conditions': storage_text
            }
            overviews.append(overview)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
    
    return overviews

def load_personal_care_overview(file_path: str) -> List[Dict]:
    """Load hair/skin care overview data"""
    overviews = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        products = data.get('products_processed', data.get('products', []))
        for prod in products:
            key_ingredients = prod.get('key_ingredients', [])
            if isinstance(key_ingredients, str):
                key_ingredients = [key_ingredients]
                
            overview = {
                'product_name': prod.get('product_name', prod.get('name', '')),
                'overview_description': prod.get('product_description', prod.get('description', '')),
                'key_ingredients': key_ingredients,
                'benefits': prod.get('benefits', []),
                'suitability_info': prod.get('hair_type_suitability', prod.get('skin_type_suitability', '')),
                'usage_instructions': prod.get('usage_instructions', ''),
                'warnings_precautions': prod.get('warnings', ''),
                'storage_conditions': prod.get('storage', '')
            }
            overviews.append(overview)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
    
    return overviews

def match_and_update_product(overview: Dict, products: List[Dict]) -> bool:
    """Match overview with product and update"""
    normalized_overview_name = normalize_product_name(overview.get('product_name', ''))
    normalized_overview_name_ar = normalize_product_name(overview.get('product_name_ar', ''))
    
    for product in products:
        product_name = normalize_product_name(product.get('name', ''))
        product_name_ar = normalize_product_name(product.get('name_ar', ''))
        
        # Match by name (English or Arabic)
        if (normalized_overview_name and normalized_overview_name in product_name) or \
           (product_name and product_name in normalized_overview_name) or \
           (normalized_overview_name_ar and normalized_overview_name_ar in product_name_ar) or \
           (product_name_ar and product_name_ar in normalized_overview_name_ar):
            
            # Prepare update data
            update_data = {}
            
            if overview.get('overview_description'):
                update_data['overview_description'] = overview['overview_description'][:1000]
            
            if overview.get('key_ingredients'):
                update_data['key_ingredients'] = overview['key_ingredients'][:20]
            
            if overview.get('benefits'):
                update_data['benefits'] = overview['benefits'][:15]
            
            if overview.get('active_ingredients'):
                update_data['active_ingredients'] = overview['active_ingredients']
            
            if overview.get('therapeutic_indications'):
                indications = overview['therapeutic_indications']
                if isinstance(indications, dict):
                    # Extract just the English or Arabic list
                    update_data['therapeutic_indications'] = indications.get('english', indications.get('arabic', []))
                elif isinstance(indications, list):
                    update_data['therapeutic_indications'] = indications
            
            if overview.get('dosage_administration'):
                update_data['dosage_administration'] = overview['dosage_administration'][:500]
            
            if overview.get('product_specifications'):
                update_data['product_specifications'] = overview['product_specifications']
            
            if overview.get('suitability_info'):
                update_data['suitability_info'] = overview['suitability_info'][:300]
            
            if overview.get('usage_instructions'):
                update_data['usage_instructions'] = overview['usage_instructions'][:500]
            
            if overview.get('warnings_precautions'):
                update_data['warnings_precautions'] = overview['warnings_precautions'][:500]
            
            if overview.get('storage_conditions'):
                update_data['storage_conditions'] = overview['storage_conditions'][:300]
            
            # Update product
            if update_data:
                try:
                    response = requests.patch(
                        f"{SUPABASE_URL}/rest/v1/products?id=eq.{product['id']}",
                        headers=headers,
                        json=update_data
                    )
                    if response.status_code in [200, 204]:
                        return True
                except Exception as e:
                    print(f"Error updating product {product['id']}: {e}")
            
            return False
    
    return False

# Main execution
print("=" * 70)
print("CHEFAA COMPREHENSIVE OVERVIEW DATA INTEGRATION")
print("=" * 70)

# Get all products from database
print("\n1. Loading products from database...")
response = requests.get(
    f"{SUPABASE_URL}/rest/v1/products?select=id,name,name_ar",
    headers=headers
)
products = response.json()
print(f"   Loaded {len(products)} products")

# Load all overview files
overview_files = {
    'medications': [
        '/workspace/data/overviews/medications_batch_1/medications_overview_batch_1.json',
        '/workspace/data/overviews/medications_batch_2/medications_overview_batch_2.json',
        '/workspace/data/overviews/medications_batch_3/medications_overview_batch_3.json',
        '/workspace/data/overviews/medications_batch_4/medications_overview_batch_4.json',
        '/workspace/data/overviews/medications_batch_5/medications_overview_batch_5.json',
        '/workspace/data/overviews/medications_batch_6/medications_overview_batch_6.json',
        '/workspace/data/overviews/medications_batch_7/medications_overview_batch_7.json',
    ],
    'hair_care': [
        '/workspace/data/overviews/hair_care/hair_care_overviews_final_v2.json'
    ],
    'skin_care': [
        '/workspace/data/overviews/skin_care_overviews.json'
    ],
    'remaining': [
        '/workspace/data/overviews/remaining_categories/remaining_categories_overviews.json'
    ]
}

print("\n2. Processing overview data files...")
total_overviews = 0
total_matched = 0

# Process medications
print("\n   Medications:")
for file_path in overview_files['medications']:
    try:
        overviews = load_medications_overview(file_path)
        print(f"   - {file_path.split('/')[-1]}: {len(overviews)} products")
        
        for overview in overviews:
            total_overviews += 1
            if match_and_update_product(overview, products):
                total_matched += 1
                if total_matched <= 10:
                    print(f"      ✓ Matched: {overview.get('product_name', '')[:50]}")
    except FileNotFoundError:
        pass

# Process hair care
print("\n   Hair Care:")
for file_path in overview_files['hair_care']:
    try:
        overviews = load_personal_care_overview(file_path)
        print(f"   - {file_path.split('/')[-1]}: {len(overviews)} products")
        
        for overview in overviews:
            total_overviews += 1
            if match_and_update_product(overview, products):
                total_matched += 1
                if total_matched <= 15:
                    print(f"      ✓ Matched: {overview.get('product_name', '')[:50]}")
    except FileNotFoundError:
        pass

# Process skin care
print("\n   Skin Care:")
for file_path in overview_files['skin_care']:
    try:
        overviews = load_personal_care_overview(file_path)
        print(f"   - {file_path.split('/')[-1]}: {len(overviews)} products")
        
        for overview in overviews:
            total_overviews += 1
            if match_and_update_product(overview, products):
                total_matched += 1
    except FileNotFoundError:
        pass

# Process remaining categories
print("\n   Remaining Categories:")
for file_path in overview_files.get('remaining', []):
    try:
        overviews = load_personal_care_overview(file_path)
        print(f"   - {file_path.split('/')[-1]}: {len(overviews)} products")
        
        for overview in overviews:
            total_overviews += 1
            if match_and_update_product(overview, products):
                total_matched += 1
                if total_matched % 10 == 0:
                    print(f"      ✓ Matched {total_matched} products so far...")
    except FileNotFoundError:
        print(f"      File not found: {file_path}")
        pass

print("\n" + "=" * 70)
print(f"COMPLETE: Processed {total_overviews} overviews")
print(f"Successfully matched and updated {total_matched} products")
print(f"Match rate: {(total_matched/total_overviews*100) if total_overviews > 0 else 0:.1f}%")
print("=" * 70)
