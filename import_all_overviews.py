#!/usr/bin/env python3
"""
Comprehensive import script for ALL 850+ product overviews
Handles multiple data formats with robust error handling
"""

import json
import re
from typing import Dict, List, Tuple
from supabase import create_client

# Supabase configuration
SUPABASE_URL = "https://sggthvsfucciptpgokgk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNnZ3RodnNmdWNjaXB0cGdva2drIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTkzMDcyMCwiZXhwIjoyMDc3NTA2NzIwfQ.wzbtz77OtHcW8Ie6m_mc2On3qumQKJz26x_ygAqluhc"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Data file configuration
OVERVIEW_FILES = {
    'medications_batch_1': {
        'path': '/workspace/data/overviews/medications_batch_1/medications_overview_batch_1.json',
        'type': 'medications_v1',
        'key': 'medications'
    },
    'medications_batch_2': {
        'path': '/workspace/data/overviews/medications_batch_2/medications_overview_batch_2.json',
        'type': 'medications_v2',
        'key': 'medication_overviews'
    },
    'medications_batch_3': {
        'path': '/workspace/data/overviews/medications_batch_3/medications_overview_batch_3_comprehensive.json',
        'type': 'medications_v3',
        'key': 'products'
    },
    'medications_batch_4': {
        'path': '/workspace/data/overviews/medications_batch_4/medications_overview_batch_4_real.json',
        'type': 'medications_v4',
        'key': 'products'
    },
    'medications_batch_5': {
        'path': '/workspace/data/overviews/medications_batch_5/medications_overview_batch_5_extracted.json',
        'type': 'medications_v5',
        'key': 'products'
    },
    'medications_batch_6': {
        'path': '/workspace/data/overviews/medications_batch_6/consolidated_all_medications.json',
        'type': 'medications_v6',
        'key': 'products'
    },
    'medications_batch_7': {
        'path': '/workspace/data/overviews/medications_batch_7/medications_overview_batch_7.json',
        'type': 'medications_v7',
        'key': 'pharmaceutical_profiles'
    },
    'hair_care': {
        'path': '/workspace/data/overviews/hair_care/hair_care_overviews.json',
        'type': 'personal_care',
        'key': 'products_processed'
    },
    'skin_care': {
        'path': '/workspace/data/overviews/skin_care_overviews.json',
        'type': 'personal_care',
        'key': 'products_processed'
    },
    'remaining_categories': {
        'path': '/workspace/data/overviews/remaining_categories/remaining_categories_overviews.json',
        'type': 'remaining',
        'key': None
    }
}


def normalize_name(name):
    """Normalize product name for fuzzy matching"""
    if not name:
        return ""
    name = str(name).lower()
    # Remove special characters and normalize spaces
    name = re.sub(r'[|،,؛;()[\]{}]', ' ', name)
    name = re.sub(r'\s+', ' ', name)
    name = re.sub(r'[^\w\s-]', '', name)
    return name.strip()


def fuzzy_match_score(name1, name2):
    """Calculate fuzzy match score between two product names"""
    if not name1 or not name2:
        return 0
    
    norm1 = normalize_name(name1)
    norm2 = normalize_name(name2)
    
    # Exact match
    if norm1 == norm2:
        return 100
    
    # Substring match
    if norm1 in norm2 or norm2 in norm1:
        return 90
    
    # Word overlap scoring
    words1 = set(norm1.split())
    words2 = set(norm2.split())
    
    if not words1 or not words2:
        return 0
    
    # Remove very common words
    common_words = {'mg', 'ml', 'gm', 'tab', 'tablets', 'caps', 'capsules', 'syrup', 'cream'}
    words1 = words1 - common_words
    words2 = words2 - common_words
    
    if not words1 or not words2:
        return 0
    
    overlap = len(words1 & words2)
    total = len(words1 | words2)
    
    score = (overlap / total) * 80 if total > 0 else 0
    
    # Bonus for matching first 2 words
    if len(words1) >= 2 and len(words2) >= 2:
        first_words1 = list(words1)[:2]
        first_words2 = list(words2)[:2]
        if len(set(first_words1) & set(first_words2)) >= 1:
            score += 10
    
    return score


def find_best_match(product_name, products_dict, threshold=50):
    """Find best matching product from database"""
    best_match = None
    best_score = 0
    
    for pid, prod in products_dict.items():
        # Try English name
        score_en = fuzzy_match_score(product_name, prod['name'])
        # Try Arabic name
        score_ar = fuzzy_match_score(product_name, prod.get('name_ar', ''))
        # Try brand
        score_brand = fuzzy_match_score(product_name, prod.get('brand', '')) * 0.5  # Lower weight
        
        max_score = max(score_en, score_ar, score_brand)
        
        if max_score > best_score and max_score >= threshold:
            best_score = max_score
            best_match = pid
    
    return best_match, best_score


def process_medications_v1(item):
    """Process medications format version 1"""
    update_data = {}
    
    # Overview description
    desc = item.get('description', '')
    if isinstance(desc, dict):
        update_data['overview_description'] = (desc.get('english') or desc.get('arabic', ''))[:2000]
    elif desc:
        update_data['overview_description'] = str(desc)[:2000]
    
    # Active ingredients
    if item.get('active_ingredients'):
        update_data['active_ingredients'] = item['active_ingredients']
    
    # Therapeutic indications
    if item.get('therapeutic_indications'):
        indications = item['therapeutic_indications']
        if isinstance(indications, dict):
            update_data['therapeutic_indications'] = indications.get('english', indications.get('arabic', []))
        elif isinstance(indications, list):
            update_data['therapeutic_indications'] = indications
    
    # Dosage
    dosage = item.get('dosage_and_administration', '')
    if isinstance(dosage, dict):
        update_data['dosage_administration'] = (dosage.get('english') or dosage.get('arabic', ''))[:500]
    elif dosage:
        update_data['dosage_administration'] = str(dosage)[:500]
    
    # Specifications
    if item.get('specifications'):
        update_data['product_specifications'] = item['specifications']
    
    # Warnings
    warnings = item.get('contraindications_and_warnings', '')
    if isinstance(warnings, dict):
        update_data['warnings_precautions'] = (warnings.get('english') or warnings.get('arabic', ''))[:500]
    elif warnings:
        update_data['warnings_precautions'] = str(warnings)[:500]
    
    # Storage
    storage = item.get('storage_conditions', '')
    if isinstance(storage, dict):
        update_data['storage_conditions'] = (storage.get('english') or storage.get('arabic', ''))[:300]
    elif storage:
        update_data['storage_conditions'] = str(storage)[:300]
    
    # Extract product name
    product_name = item.get('product_name_english') or item.get('product_name_arabic', '')
    
    return product_name, update_data


def process_medications_v2(item):
    """Process medications format version 2 (batch 2 format)"""
    update_data = {}
    
    # Overview description
    desc = item.get('detailed_description', '')
    if desc:
        update_data['overview_description'] = str(desc)[:2000]
    
    # Active ingredients from ingredients dict
    if item.get('ingredients'):
        ing = item['ingredients']
        if isinstance(ing, dict) and ing.get('active_ingredients'):
            update_data['active_ingredients'] = [{'name': ing['active_ingredients']}]
    
    # Therapeutic uses
    if item.get('therapeutic_uses'):
        update_data['therapeutic_indications'] = item['therapeutic_uses']
    
    # Dosage from dosage_information
    if item.get('dosage_information'):
        dosage_info = item['dosage_information']
        if isinstance(dosage_info, dict):
            dosage_text = f"{dosage_info.get('dosage', '')} {dosage_info.get('frequency', '')} {dosage_info.get('administration', '')}"
            update_data['dosage_administration'] = dosage_text.strip()[:500]
    
    # Specifications
    if item.get('specifications'):
        update_data['product_specifications'] = item['specifications']
    
    # Warnings and precautions
    warnings_list = []
    if item.get('warnings'):
        warnings_list.extend(item['warnings'])
    if item.get('precautions'):
        warnings_list.extend(item['precautions'])
    if item.get('contraindications'):
        warnings_list.extend(item['contraindications'])
    if warnings_list:
        update_data['warnings_precautions'] = ' | '.join([str(w) for w in warnings_list])[:500]
    
    # Storage
    if item.get('storage_requirements'):
        update_data['storage_conditions'] = str(item['storage_requirements'])[:300]
    
    # Extract product name
    if item.get('product_metadata'):
        product_name = item['product_metadata'].get('product_name', '') or item['product_metadata'].get('arabic_name', '')
    else:
        product_name = ''
    
    return product_name, update_data


def process_medications_v3_to_v6(item):
    """Process medications format v3-v6 (products array with various structures)"""
    update_data = {}
    
    # Description
    desc = item.get('full_product_description', '') or item.get('description', '')
    if desc:
        update_data['overview_description'] = str(desc)[:2000]
    
    # Active ingredients
    if item.get('active_ingredients'):
        update_data['active_ingredients'] = item['active_ingredients']
    
    # Therapeutic classifications / indications
    if item.get('therapeutic_classifications'):
        update_data['therapeutic_indications'] = item['therapeutic_classifications']
    elif item.get('indications'):
        update_data['therapeutic_indications'] = item['indications']
    
    # Dosage forms/administration
    dosage_text = ''
    if item.get('dosage_forms_and_strengths'):
        dosage_text = str(item['dosage_forms_and_strengths'])
    elif item.get('dosage_and_administration'):
        dosage_text = str(item['dosage_and_administration'])
    if dosage_text:
        update_data['dosage_administration'] = dosage_text[:500]
    
    # Warnings / contraindications
    warnings_list = []
    if item.get('contraindications'):
        if isinstance(item['contraindications'], list):
            warnings_list.extend(item['contraindications'])
        else:
            warnings_list.append(str(item['contraindications']))
    if item.get('warnings'):
        if isinstance(item['warnings'], list):
            warnings_list.extend(item['warnings'])
        else:
            warnings_list.append(str(item['warnings']))
    if warnings_list:
        update_data['warnings_precautions'] = ' | '.join([str(w) for w in warnings_list])[:500]
    
    # Storage
    if item.get('storage'):
        update_data['storage_conditions'] = str(item['storage'])[:300]
    elif item.get('storage_requirements'):
        update_data['storage_conditions'] = str(item['storage_requirements'])[:300]
    
    # Extract product name
    product_name = (
        item.get('product_name_english', '') or 
        item.get('product_name', '') or 
        item.get('product_name_arabic', '') or 
        item.get('name', '')
    )
    
    return product_name, update_data


def process_medications_v7(item):
    """Process medications format v7 (pharmaceutical_profiles with nested structure)"""
    update_data = {}
    
    # Basic information
    basic_info = item.get('basic_information', {})
    if basic_info.get('description'):
        update_data['overview_description'] = str(basic_info['description'])[:2000]
    
    # Active components
    if basic_info.get('active_components'):
        update_data['active_ingredients'] = basic_info['active_components']
    
    # Therapeutic information
    therapeutic_info = item.get('therapeutic_information', {})
    indications = []
    if therapeutic_info.get('clinical_uses'):
        indications.extend(therapeutic_info['clinical_uses'])
    if therapeutic_info.get('indications'):
        indications.extend(therapeutic_info['indications'])
    if indications:
        update_data['therapeutic_indications'] = indications
    
    # Dosing administration
    dosing_info = item.get('dosing_administration', {})
    dosage_parts = []
    if dosing_info.get('dosage_guidelines'):
        dosage_parts.append(str(dosing_info['dosage_guidelines']))
    if dosing_info.get('frequency'):
        dosage_parts.append(str(dosing_info['frequency']))
    if dosing_info.get('duration_of_treatment'):
        dosage_parts.append(str(dosing_info['duration_of_treatment']))
    if dosage_parts:
        update_data['dosage_administration'] = ' | '.join(dosage_parts)[:500]
    
    # Safety information
    safety_info = item.get('safety_information', {})
    warnings_list = []
    if safety_info.get('contraindications'):
        warnings_list.extend(safety_info['contraindications'])
    if safety_info.get('warnings'):
        warnings_list.extend(safety_info['warnings'])
    if safety_info.get('precautions'):
        warnings_list.extend(safety_info['precautions'])
    if warnings_list:
        update_data['warnings_precautions'] = ' | '.join([str(w) for w in warnings_list])[:500]
    
    # Storage
    storage_info = item.get('storage_handling', {})
    if storage_info.get('storage_conditions'):
        update_data['storage_conditions'] = str(storage_info['storage_conditions'])[:300]
    
    # Extract product name
    product_name = (
        basic_info.get('product_name', '') or 
        basic_info.get('product_name_english', '')
    )
    
    return product_name, update_data


def process_personal_care(item):
    """Process hair/skin care format"""
    update_data = {}
    
    if item.get('product_description'):
        update_data['overview_description'] = str(item['product_description'])[:2000]
    
    if item.get('key_ingredients'):
        update_data['key_ingredients'] = item['key_ingredients']
    
    if item.get('benefits'):
        update_data['benefits'] = item['benefits']
    
    specs = {}
    if item.get('volume'):
        specs['volume'] = item['volume']
    if item.get('hair_type_suitability'):
        specs['hair_type_suitability'] = item['hair_type_suitability']
        update_data['suitability_info'] = str(item['hair_type_suitability'])[:300]
    if item.get('skin_type_suitability'):
        specs['skin_type_suitability'] = item['skin_type_suitability']
        update_data['suitability_info'] = str(item['skin_type_suitability'])[:300]
    if specs:
        update_data['product_specifications'] = specs
    
    if item.get('usage_instructions'):
        update_data['dosage_administration'] = str(item['usage_instructions'])[:500]
    if item.get('warnings'):
        update_data['warnings_precautions'] = str(item['warnings'])[:500]
    if item.get('storage'):
        update_data['storage_conditions'] = str(item['storage'])[:300]
    
    product_name = item.get('product_name', '')
    
    return product_name, update_data


def process_remaining_categories(item):
    """Process remaining categories format"""
    update_data = {}
    
    if item.get('description'):
        update_data['overview_description'] = str(item['description'])[:2000]
    
    # Extract ingredients from dict
    if item.get('ingredients'):
        ing_list = []
        if isinstance(item['ingredients'], dict):
            for key, val in item['ingredients'].items():
                if isinstance(val, dict):
                    ing_list.append(val.get('name', key))
                else:
                    ing_list.append(key)
        update_data['key_ingredients'] = ing_list
    
    if item.get('benefits'):
        update_data['benefits'] = item['benefits']
    
    if item.get('specifications'):
        update_data['product_specifications'] = item['specifications']
    
    if item.get('usage_instructions'):
        update_data['dosage_administration'] = str(item['usage_instructions'])[:500]
    if item.get('warnings'):
        update_data['warnings_precautions'] = str(item['warnings'])[:500]
    
    product_name = item.get('name', '')
    
    return product_name, update_data


# Load all products once
print("=" * 80)
print("COMPREHENSIVE PRODUCT OVERVIEWS IMPORT - ALL 850+ PRODUCTS")
print("=" * 80)
print("\nLoading products from database...")

response = supabase.table('products').select('id, name, name_ar, brand').execute()
products = {p['id']: p for p in response.data}
print(f"✓ Loaded {len(products)} products\n")

stats = {
    'total_processed': 0,
    'total_matched': 0,
    'total_updated': 0,
    'by_source': {},
    'errors': []
}

# Process each overview file
for source_name, config in OVERVIEW_FILES.items():
    print(f"\n{'='*80}")
    print(f"Processing: {source_name}")
    print(f"{'='*80}")
    
    file_path = config['path']
    file_type = config['type']
    data_key = config['key']
    
    source_stats = {'processed': 0, 'matched': 0, 'updated': 0}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        items = []
        
        # Extract items based on file type
        if file_type == 'remaining':
            # Handle remaining categories special format
            for category_key in data.keys():
                if category_key == 'extraction_metadata':
                    continue
                category_data = data[category_key]
                if isinstance(category_data, dict) and 'products' in category_data:
                    items.extend(category_data['products'])
        elif data_key:
            items = data.get(data_key, [])
        
        print(f"Found {len(items)} items in file")
        
        # Process each item
        for item in items:
            stats['total_processed'] += 1
            source_stats['processed'] += 1
            
            # Extract product name and overview data based on type
            if file_type == 'medications_v1':
                product_name, update_data = process_medications_v1(item)
            elif file_type == 'medications_v2':
                product_name, update_data = process_medications_v2(item)
            elif file_type in ['medications_v3', 'medications_v4', 'medications_v5', 'medications_v6']:
                product_name, update_data = process_medications_v3_to_v6(item)
            elif file_type == 'medications_v7':
                product_name, update_data = process_medications_v7(item)
            elif file_type == 'personal_care':
                product_name, update_data = process_personal_care(item)
            elif file_type == 'remaining':
                product_name, update_data = process_remaining_categories(item)
            else:
                continue
            
            if not product_name or not update_data:
                continue
            
            # Find best matching product
            matched_id, match_score = find_best_match(product_name, products, threshold=50)
            
            if matched_id:
                stats['total_matched'] += 1
                source_stats['matched'] += 1
                
                try:
                    # Update product in database
                    supabase.table('products').update(update_data).eq('id', matched_id).execute()
                    stats['total_updated'] += 1
                    source_stats['updated'] += 1
                    
                    if source_stats['updated'] <= 3:
                        print(f"  ✓ Updated: {product_name[:60]} (score: {match_score:.0f})")
                except Exception as e:
                    stats['errors'].append(f"{source_name}: Update failed for {product_name[:40]} - {str(e)[:50]}")
        
        stats['by_source'][source_name] = source_stats
        print(f"\n✓ {source_name}: {source_stats['updated']}/{source_stats['processed']} products updated")
        print(f"  Match rate: {(source_stats['matched']/source_stats['processed']*100) if source_stats['processed'] > 0 else 0:.1f}%")
        
    except FileNotFoundError:
        print(f"  ⚠ File not found: {file_path}")
        stats['errors'].append(f"{source_name}: File not found")
    except json.JSONDecodeError as e:
        print(f"  ⚠ JSON parsing error: {str(e)[:100]}")
        stats['errors'].append(f"{source_name}: JSON error - {str(e)[:50]}")
    except Exception as e:
        print(f"  ⚠ Error: {str(e)[:100]}")
        stats['errors'].append(f"{source_name}: {str(e)[:50]}")

# Final Summary
print("\n" + "=" * 80)
print("IMPORT COMPLETE - FINAL STATISTICS")
print("=" * 80)
print(f"Total products processed: {stats['total_processed']}")
print(f"Total products matched: {stats['total_matched']}")
print(f"Total products updated: {stats['total_updated']}")
print(f"Overall match rate: {(stats['total_matched']/stats['total_processed']*100) if stats['total_processed'] > 0 else 0:.1f}%")
print(f"Overall update rate: {(stats['total_updated']/stats['total_processed']*100) if stats['total_processed'] > 0 else 0:.1f}%")

print("\n" + "-" * 80)
print("BREAKDOWN BY SOURCE:")
print("-" * 80)
for source, source_stats in stats['by_source'].items():
    print(f"{source:30} | Processed: {source_stats['processed']:4} | Updated: {source_stats['updated']:4} | Rate: {(source_stats['updated']/source_stats['processed']*100) if source_stats['processed'] > 0 else 0:5.1f}%")

if stats['errors']:
    print("\n" + "-" * 80)
    print(f"ERRORS ENCOUNTERED ({len(stats['errors'])}):")
    print("-" * 80)
    for error in stats['errors'][:10]:  # Show first 10 errors
        print(f"  • {error}")
    if len(stats['errors']) > 10:
        print(f"  ... and {len(stats['errors']) - 10} more errors")

print("\n" + "=" * 80)
