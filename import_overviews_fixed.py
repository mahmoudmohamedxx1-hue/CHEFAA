#!/usr/bin/env python3
"""
Fixed import script for product overviews
Handles multiple data formats from different extraction batches
"""

import json
import re
from supabase import create_client

# Supabase configuration
SUPABASE_URL = "https://sggthvsfucciptpgokgk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNnZ3RodnNmdWNjaXB0cGdva2drIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTkzMDcyMCwiZXhwIjoyMDc3NTA2NzIwfQ.wzbtz77OtHcW8Ie6m_mc2On3qumQKJz26x_ygAqluhc"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def normalize_name(name):
    """Normalize product name for fuzzy matching"""
    if not name:
        return ""
    # Convert to lowercase, remove special chars, normalize spaces
    name = str(name).lower()
    name = re.sub(r'[|،,؛;]', ' ', name)
    name = re.sub(r'\s+', ' ', name)
    name = re.sub(r'[^\w\s-]', '', name)
    return name.strip()

def fuzzy_match(name1, name2):
    """Check if two product names are similar enough"""
    if not name1 or not name2:
        return False
    
    norm1 = normalize_name(name1)
    norm2 = normalize_name(name2)
    
    # Extract first 3-4 words as key identifier
    words1 = norm1.split()[:4]
    words2 = norm2.split()[:4]
    
    # Check if significant words overlap
    if len(words1) >= 2 and len(words2) >= 2:
        overlap = sum(1 for w in words1 if w in norm2)
        return overlap >= 2
    
    return False

# Get all products
print("Loading products from database...")
response = supabase.table('products').select('id, name, name_ar, brand').execute()
products = {p['id']: p for p in response.data}
print(f"Loaded {len(products)} products\n")

stats = {'processed': 0, 'matched': 0, 'updated': 0}

# Process Hair Care
print("=" * 70)
print("HAIR CARE PRODUCTS")
print("=" * 70)
try:
    with open('/workspace/data/overviews/hair_care/hair_care_overviews.json', 'r') as f:
        data = json.load(f)
    
    for item in data.get('products_processed', []):
        stats['processed'] += 1
        name = item.get('product_name', '')
        
        # Find matching product
        matched_id = None
        for pid, prod in products.items():
            if fuzzy_match(name, prod['name']) or fuzzy_match(name, prod.get('name_ar', '')):
                matched_id = pid
                break
        
        if matched_id:
            stats['matched'] += 1
            update_data = {}
            
            if item.get('product_description'):
                update_data['overview_description'] = item['product_description'][:2000]
            
            if item.get('key_ingredients'):
                update_data['key_ingredients'] = item['key_ingredients']
            
            if item.get('benefits'):
                update_data['benefits'] = item['benefits']
            
            specs = {}
            if item.get('volume'):
                specs['volume'] = item['volume']
            if item.get('hair_type_suitability'):
                specs['hair_type_suitability'] = item['hair_type_suitability']
                update_data['suitability_info'] = item['hair_type_suitability'][:300]
            if specs:
                update_data['product_specifications'] = specs
            
            if item.get('usage_instructions'):
                usage = item['usage_instructions']
                update_data['dosage_administration'] = str(usage)[:500] if usage else ''
            if item.get('warnings'):
                warnings = item['warnings']
                update_data['warnings_precautions'] = str(warnings)[:500] if warnings else ''
            if item.get('storage'):
                storage = item['storage']
                update_data['storage_conditions'] = str(storage)[:300] if storage else ''
            
            if update_data:
                supabase.table('products').update(update_data).eq('id', matched_id).execute()
                stats['updated'] += 1
                if stats['updated'] <= 5:
                    print(f"✓ Updated: {name[:60]}")
    
    print(f"Hair Care: {stats['updated']} products updated from {stats['processed']} processed\n")
except Exception as e:
    print(f"Error processing hair care: {e}\n")

# Process Medications Batch 1
print("=" * 70)
print("MEDICATIONS BATCH 1")
print("=" * 70)
initial_updated = stats['updated']
try:
    with open('/workspace/data/overviews/medications_batch_1/medications_overview_batch_1.json', 'r') as f:
        data = json.load(f)
    
    for med in data.get('medications', []):
        stats['processed'] += 1
        name = med.get('product_name_english') or med.get('product_name_arabic', '')
        
        matched_id = None
        for pid, prod in products.items():
            if fuzzy_match(name, prod['name']) or fuzzy_match(name, prod.get('name_ar', '')):
                matched_id = pid
                break
        
        if matched_id:
            stats['matched'] += 1
            update_data = {}
            
            desc = med.get('description', '')
            if isinstance(desc, dict):
                update_data['overview_description'] = (desc.get('english') or desc.get('arabic', ''))[:2000]
            
            if med.get('active_ingredients'):
                update_data['active_ingredients'] = med['active_ingredients']
            
            if med.get('therapeutic_indications'):
                indications = med['therapeutic_indications']
                if isinstance(indications, dict):
                    update_data['therapeutic_indications'] = indications.get('english', indications.get('arabic', []))
            
            dosage = med.get('dosage_and_administration', '')
            if isinstance(dosage, dict):
                update_data['dosage_administration'] = (dosage.get('english') or dosage.get('arabic', ''))[:500]
            
            if med.get('specifications'):
                update_data['product_specifications'] = med['specifications']
            
            warnings = med.get('contraindications_and_warnings', '')
            if isinstance(warnings, dict):
                update_data['warnings_precautions'] = (warnings.get('english') or warnings.get('arabic', ''))[:500]
            
            storage = med.get('storage_conditions', '')
            if isinstance(storage, dict):
                update_data['storage_conditions'] = (storage.get('english') or storage.get('arabic', ''))[:300]
            
            if update_data:
                supabase.table('products').update(update_data).eq('id', matched_id).execute()
                stats['updated'] += 1
                if stats['updated'] - initial_updated <= 5:
                    print(f"✓ Updated: {name[:60]}")
    
    print(f"Medications Batch 1: {stats['updated'] - initial_updated} products updated\n")
except Exception as e:
    print(f"Error processing medications batch 1: {e}\n")

# Process Remaining Categories
print("=" * 70)
print("REMAINING CATEGORIES (Daily Essentials, Mom & Baby, etc.)")
print("=" * 70)
initial_updated = stats['updated']
try:
    with open('/workspace/data/overviews/remaining_categories/remaining_categories_overviews.json', 'r') as f:
        data = json.load(f)
    
    for category_key in data.keys():
        if category_key == 'extraction_metadata':
            continue
        
        category_data = data[category_key]
        if isinstance(category_data, dict) and 'products' in category_data:
            for prod in category_data['products']:
                stats['processed'] += 1
                name = prod.get('name', '')
                
                matched_id = None
                for pid, p in products.items():
                    if fuzzy_match(name, p['name']) or fuzzy_match(name, p.get('name_ar', '')):
                        matched_id = pid
                        break
                
                if matched_id:
                    stats['matched'] += 1
                    update_data = {}
                    
                    if prod.get('description'):
                        update_data['overview_description'] = prod['description'][:2000]
                    
                    # Extract ingredients from dict
                    if prod.get('ingredients'):
                        ing_list = []
                        if isinstance(prod['ingredients'], dict):
                            for key, val in prod['ingredients'].items():
                                if isinstance(val, dict):
                                    ing_list.append(val.get('name', key))
                                else:
                                    ing_list.append(key)
                        update_data['key_ingredients'] = ing_list
                    
                    if prod.get('benefits'):
                        update_data['benefits'] = prod['benefits']
                    
                    if prod.get('specifications'):
                        update_data['product_specifications'] = prod['specifications']
                    
                    if prod.get('usage_instructions'):
                        usage = prod['usage_instructions']
                        update_data['dosage_administration'] = str(usage)[:500] if usage else ''
                    if prod.get('warnings'):
                        warnings = prod['warnings']
                        update_data['warnings_precautions'] = str(warnings)[:500] if warnings else ''
                    
                    if update_data:
                        supabase.table('products').update(update_data).eq('id', matched_id).execute()
                        stats['updated'] += 1
                        if stats['updated'] - initial_updated <= 5:
                            print(f"✓ Updated: {name[:60]}")
    
    print(f"Remaining Categories: {stats['updated'] - initial_updated} products updated\n")
except Exception as e:
    print(f"Error processing remaining categories: {e}\n")

# Final Summary
print("\n" + "=" * 70)
print("IMPORT COMPLETE")
print("=" * 70)
print(f"Total products processed: {stats['processed']}")
print(f"Products matched: {stats['matched']}")
print(f"Products updated: {stats['updated']}")
print(f"Match rate: {(stats['matched']/stats['processed']*100) if stats['processed'] > 0 else 0:.1f}%")
print("=" * 70)
