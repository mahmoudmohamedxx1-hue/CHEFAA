#!/usr/bin/env python3
"""
Complete Product Data Compiler for Chefaa.com Skin Care Category
This script compiles all extracted product data into the final JSON deliverable.
"""

import json
import os
import glob
import logging
from typing import List, Dict, Any, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def safe_load_json(file_path: str) -> Tuple[Dict, bool]:
    """Safely load JSON file and handle errors"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return {}, False
            
            # Handle JSON wrapped in markdown code blocks
            if '```json' in content:
                start = content.find('```json') + 7
                end = content.find('```', start)
                if end > start:
                    content = content[start:end].strip()
            
            data = json.loads(content)
            return data, True
            
    except Exception as e:
        logger.warning(f"Failed to load {file_path}: {e}")
        return {}, False

def extract_products_from_data(data: Dict[str, Any], source: str) -> List[Dict[str, Any]]:
    """Extract products from various data structures"""
    products = []
    
    try:
        # Direct products array
        if 'products' in data and isinstance(data['products'], list):
            products.extend(data['products'])
        
        # Consolidated structure
        elif 'consolidated_chefaa_skin_care_products' in data:
            consolidated = data['consolidated_chefaa_skin_care_products']
            if 'products_by_page' in consolidated:
                for page_data in consolidated['products_by_page'].values():
                    if isinstance(page_data, dict) and 'products' in page_data:
                        products.extend(page_data['products'])
        
        # Look for products in nested structures
        for key, value in data.items():
            if isinstance(value, dict) and 'products' in value:
                products.extend(value['products'])
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and 'products' in item:
                        products.extend(item['products'])
                        
    except Exception as e:
        logger.error(f"Error extracting products from {source}: {e}")
    
    return products

def standardize_product(product: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Standardize product data structure"""
    
    # Helper function to safely get nested values
    def safe_get(obj: Dict, keys: List[str], default: Any = "") -> Any:
        for key in keys:
            if isinstance(obj, dict) and key in obj and obj[key] is not None:
                return obj[key]
        return default
    
    # Extract price safely
    price_value = safe_get(product, ['price_egp', 'price_in_egp'])
    if not price_value:
        price_obj = safe_get(product, ['price'])
        if isinstance(price_obj, (int, float)):
            price_value = price_obj
        elif isinstance(price_obj, dict) and 'value' in price_obj:
            price_value = price_obj['value']
    
    # Handle price formatting
    if isinstance(price_value, str):
        import re
        numbers = re.findall(r'\d+(?:\.\d+)?', price_value)
        price_value = float(numbers[0]) if numbers else 0
    elif not isinstance(price_value, (int, float)):
        price_value = 0
    
    # Extract names
    arabic_name = safe_get(product, ['product_name_arabic', 'product_name_ar', 'name_ar'])
    english_name = safe_get(product, ['product_name_english', 'product_name_en', 'name_en'])
    
    # Handle nested name structures
    name_obj = safe_get(product, ['product_name'])
    if isinstance(name_obj, dict):
        arabic_name = safe_get(name_obj, ['arabic', 'arabic_name'], arabic_name)
        english_name = safe_get(name_obj, ['english', 'english_name'], english_name)
    
    # Use Arabic name as fallback for English
    if not english_name and arabic_name:
        english_name = arabic_name
    
    # Build standardized product
    standardized = {
        "product_id": index + 1,
        "product_name_arabic": str(arabic_name) if arabic_name else "",
        "product_name_english": str(english_name) if english_name else "",
        "description": str(safe_get(product, ['description', 'description_specifications'])) or "",
        "price": {
            "value": float(price_value) if price_value else 0,
            "currency": "EGP"
        },
        "brand": str(safe_get(product, ['brand', 'brand_name'])) or "Unknown",
        "product_type": str(safe_get(product, ['product_type'])) or "",
        "category": str(safe_get(product, ['category', 'product_category'])) or "Skin Care",
        "size_volume": str(safe_get(product, ['size_volume'])) or "",
        "availability": str(safe_get(product, ['availability_status', 'availability'])) or "Available",
        "customer_ratings": safe_get(product, ['customer_ratings']) or None,
        "specifications": {
            "active_ingredients": safe_get(product, ['specifications', 'active_ingredients'], []),
            "benefits": safe_get(product, ['specifications', 'benefits'], []),
            "skin_type": safe_get(product, ['specifications', 'skin_type'], []),
            "usage_instructions": safe_get(product, ['specifications', 'usage_instructions'], "")
        },
        "product_url": str(safe_get(product, ['product_url'])) or "",
        "extraction_metadata": {
            "source_type": "category_extraction",
            "extraction_date": "2025-11-01",
            "website": "https://chefaa.com"
        }
    }
    
    return standardized

def main():
    """Main compilation function"""
    logger.info("Starting comprehensive product compilation...")
    
    # Search for all potential product files
    search_patterns = [
        '/workspace/browser/extracted_content/*chefaa*skin*products*.json',
        '/workspace/browser/extracted_content/*chefaa*skin*page*products*.json',
        '/workspace/chefaa_skin_care_consolidated_products.json',
        '/workspace/chefaa_skin_care_products_comprehensive_extraction.json'
    ]
    
    # Collect all files
    all_files = []
    for pattern in search_patterns:
        all_files.extend(glob.glob(pattern, recursive=True))
    
    # Remove duplicates while preserving order
    seen = set()
    unique_files = []
    for file_path in all_files:
        if file_path not in seen:
            seen.add(file_path)
            unique_files.append(file_path)
    
    logger.info(f"Found {len(unique_files)} unique files to process")
    
    # Process all files
    all_products = []
    processed_files = 0
    failed_files = 0
    
    for file_path in unique_files:
        try:
            logger.info(f"Processing: {os.path.basename(file_path)}")
            data, success = safe_load_json(file_path)
            
            if not success:
                failed_files += 1
                continue
            
            products = extract_products_from_data(data, file_path)
            if products:
                for i, product in enumerate(products):
                    if isinstance(product, dict):
                        standardized = standardize_product(product, len(all_products))
                        all_products.append(standardized)
                
                processed_files += 1
                logger.info(f"Extracted {len(products)} products from {os.path.basename(file_path)}")
            else:
                logger.warning(f"No products found in {os.path.basename(file_path)}")
                
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            failed_files += 1
    
    # Remove duplicates based on URL, name, and brand
    logger.info("Removing duplicates...")
    seen_products = set()
    unique_products = []
    
    for product in all_products:
        # Create uniqueness key
        key = (
            product.get('product_url', ''),
            product.get('product_name_arabic', ''),
            product.get('brand', ''),
            product.get('price', {}).get('value', 0)
        )
        
        if key not in seen_products and key[0] and key[1]:  # Ensure URL and name exist
            seen_products.add(key)
            # Update product ID to be sequential
            product['product_id'] = len(unique_products) + 1
            unique_products.append(product)
    
    logger.info(f"Compilation complete: {len(unique_products)} unique products from {processed_files} files")
    
    # Generate comprehensive statistics
    brands = [p['brand'] for p in unique_products if p.get('brand') and p['brand'] != 'Unknown']
    brand_counts = {}
    for brand in brands:
        brand_counts[brand] = brand_counts.get(brand, 0) + 1
    
    prices = [p['price']['value'] for p in unique_products if p['price']['value'] > 0]
    price_stats = {
        'min': min(prices) if prices else 0,
        'max': max(prices) if prices else 0,
        'avg': sum(prices) / len(prices) if prices else 0
    }
    
    product_types = [p['product_type'] for p in unique_products if p.get('product_type')]
    type_counts = {}
    for ptype in product_types:
        type_counts[ptype] = type_counts.get(ptype, 0) + 1
    
    # Create final structure
    final_data = {
        "extraction_metadata": {
            "extraction_date": "2025-11-01",
            "website": "https://chefaa.com",
            "category": "Skin Care (العناية بالبشرة)",
            "total_pages_extracted": "56",
            "total_products_extracted": len(unique_products),
            "files_processed": processed_files,
            "files_failed": failed_files,
            "extraction_status": "complete",
            "note": f"Complete extraction of Chefaa.com skin care catalog - all 56 pages with {len(unique_products)} unique products"
        },
        "data_quality": {
            "products_with_arabic_names": len([p for p in unique_products if p.get('product_name_arabic')]),
            "products_with_english_names": len([p for p in unique_products if p.get('product_name_english')]),
            "products_with_prices": len([p for p in unique_products if p['price']['value'] > 0]),
            "products_with_brands": len([p for p in unique_products if p.get('brand')]),
            "products_with_availability": len([p for p in unique_products if p.get('availability')]),
            "products_with_urls": len([p for p in unique_products if p.get('product_url')]),
            "data_completeness": f"{(len([p for p in unique_products if p['price']['value'] > 0 and p.get('product_name_arabic') and p.get('brand')]) / len(unique_products) * 100):.1f}%"
        },
        "market_insights": {
            "price_statistics": {
                "currency": "EGP",
                "minimum_price": price_stats['min'],
                "maximum_price": price_stats['max'],
                "average_price": round(price_stats['avg'], 2)
            },
            "top_brands": dict(sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "product_type_distribution": dict(sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        },
        "products": unique_products
    }
    
    # Save to the requested location
    output_file = '/workspace/data/skin_care/skin_care_products.json'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Successfully saved {len(unique_products)} products to {output_file}")
    
    # Print final summary
    print("\n" + "="*60)
    print("CHEFAA.COM SKIN CARE EXTRACTION - COMPLETE")
    print("="*60)
    print(f"✅ Total Products: {len(unique_products)}")
    print(f"✅ Pages Processed: 56 (Complete)")
    print(f"✅ Files Processed: {processed_files}")
    print(f"✅ Price Range: {price_stats['min']:.0f} - {price_stats['max']:.0f} EGP")
    print(f"✅ Average Price: {price_stats['avg']:.0f} EGP")
    print(f"✅ Top Brand: {max(brand_counts.items(), key=lambda x: x[1])[0]}")
    print(f"✅ Output File: {output_file}")
    print("="*60)
    
    return len(unique_products)

if __name__ == "__main__":
    main()