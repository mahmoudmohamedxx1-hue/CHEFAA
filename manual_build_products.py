#!/usr/bin/env python3
"""
Manual Products Builder
Creates the final skin care products file by extracting from key source files.
"""

import json
import re
from pathlib import Path

def extract_price(price_str):
    """Extract numeric price from various formats"""
    if isinstance(price_str, (int, float)):
        return float(price_str)
    
    # Extract number from string
    if isinstance(price_str, str):
        # Remove non-numeric characters except decimal point
        numbers = re.findall(r'\d+(?:\.\d+)?', price_str)
        if numbers:
            return float(numbers[0])
    
    return 0.0

def process_products_array(products, page_num="unknown"):
    """Process a products array into normalized format"""
    normalized = []
    
    for product in products:
        # Different field name mappings
        name_ar = (product.get('product_name_arabic') or 
                  product.get('product_name') or 
                  product.get('name', ''))
        
        name_en = product.get('product_name_english', '')
        
        # Extract brand
        brand = (product.get('brand') or 
                product.get('brand_name', ''))
        
        # Extract price
        price = extract_price(product.get('price_egp') or product.get('price', 0))
        
        # Extract other fields
        size = product.get('size_volume') or product.get('size', '')
        availability = (product.get('availability_status') or 
                       product.get('availability', '') or 
                       'Available')
        
        url = product.get('product_url') or product.get('link', '') or product.get('url', '')
        
        # Create normalized product
        normalized_product = {
            "product_id": len(normalized) + 1,
            "product_name_arabic": name_ar,
            "product_name_english": name_en,
            "brand": brand,
            "price": {"value": price, "currency": "EGP"},
            "product_type": product.get('product_type_category', '') or product.get('product_type', ''),
            "category": "Skin Care",
            "size_volume": size,
            "availability": availability,
            "customer_ratings": product.get('ratings_reviews') or product.get('ratings', None),
            "product_url": url,
            "specifications": {
                "active_ingredients": [],
                "benefits": [],
                "skin_type": [],
                "usage_instructions": ""
            },
            "extraction_page": page_num
        }
        
        if name_ar:  # Only add if has Arabic name
            normalized.append(normalized_product)
    
    return normalized

def read_and_extract_json(file_path):
    """Read file and extract JSON content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find JSON content between ```json tags
        json_start = content.find('```json')
        if json_start != -1:
            json_start += 7
            json_end = content.rfind('```')
            if json_end > json_start:
                json_content = content[json_start:json_end].strip()
            else:
                return None
        else:
            json_content = content
        
        # Parse JSON
        return json.loads(json_content)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def build_compilation():
    """Build the final compilation from key files"""
    
    # Key files to process
    key_files = [
        ("/workspace/browser/extracted_content/chefaa_skin_care_page2_products.json", "2"),
        ("/workspace/browser/extracted_content/chefaa_skin_care_page3_products.json", "3"),
        ("/workspace/browser/extracted_content/chefaa_skin_care_page_6_products.json", "6"),
        ("/workspace/browser/extracted_content/chefaa_skincare_products_p45.json", "45"),
        ("/workspace/browser/extracted_content/chefaa_skincare_products_page56.json", "56"),
    ]
    
    all_products = []
    
    for file_path, page_num in key_files:
        print(f"Processing {file_path}...")
        
        data = read_and_extract_json(file_path)
        if not data:
            print(f"  ❌ Failed to extract data")
            continue
        
        products = []
        if 'products' in data and isinstance(data['products'], list):
            products = data['products']
        elif 'relevant_products' in data and isinstance(data['relevant_products'], list):
            products = data['relevant_products']
        elif 'products_available' in data and isinstance(data['products_available'], list):
            products = data['products_available']
        
        print(f"  Found {len(products)} products")
        
        # Process and normalize
        normalized = process_products_array(products, page_num)
        all_products.extend(normalized)
        
        print(f"  Added {len(normalized)} normalized products (Total: {len(all_products)})")
    
    # Add products from the main skin care products file
    main_file = "/workspace/browser/extracted_content/chefaa_skin_care_products.json"
    print(f"\nProcessing {main_file}...")
    
    data = read_and_extract_json(main_file)
    if data:
        # Extract from relevant_products
        if 'relevant_products' in data and isinstance(data['relevant_products'], list):
            products = data['relevant_products']
            normalized = process_products_array(products, "main")
            all_products.extend(normalized)
            print(f"  Added {len(normalized)} products from main file (Total: {len(all_products)})")
    
    # Remove duplicates
    print(f"\nRemoving duplicates from {len(all_products)} products...")
    unique_products = []
    seen = set()
    
    for product in all_products:
        # Create unique key
        key = f"{product['product_name_arabic']}|{product['brand']}|{product['price']['value']}"
        if key not in seen:
            seen.add(key)
            unique_products.append(product)
    
    print(f"After deduplication: {len(unique_products)} unique products")
    
    # Reassign IDs
    for i, product in enumerate(unique_products, 1):
        product['product_id'] = i
    
    # Calculate statistics
    prices = [p['price']['value'] for p in unique_products if p['price']['value'] > 0]
    brands = [p['brand'] for p in unique_products if p['brand']]
    
    from collections import Counter
    brand_counts = Counter(brands)
    
    price_stats = {
        "minimum_price": min(prices) if prices else 0,
        "maximum_price": max(prices) if prices else 0,
        "average_price": round(sum(prices) / len(prices), 2) if prices else 0
    }
    
    # Create final structure
    final_data = {
        "extraction_metadata": {
            "extraction_date": "2025-11-01",
            "website": "https://chefaa.com",
            "category": "Skin Care (العناية بالبشرة)",
            "total_pages_extracted": "5+ pages processed",
            "total_products_extracted": len(unique_products),
            "extraction_status": "manual_compilation",
            "note": "Manual compilation of extracted Chefaa.com skin care catalog products from key pages",
            "data_quality": {
                "products_with_arabic_names": f"{len([p for p in unique_products if p['product_name_arabic']])} / {len(unique_products)}",
                "products_with_english_names": f"{len([p for p in unique_products if p['product_name_english']])} / {len(unique_products)}",
                "products_with_prices": f"{len([p for p in unique_products if p['price']['value'] > 0])} / {len(unique_products)}",
                "products_with_brands": f"{len([p for p in unique_products if p['brand']])} / {len(unique_products)}",
                "products_with_availability": f"{len([p for p in unique_products if p['availability']])} / {len(unique_products)}",
            }
        },
        "market_insights": {
            "price_statistics": {
                "currency": "EGP",
                **price_stats
            },
            "top_brands": dict(brand_counts.most_common(10)),
            "price_distribution": {
                "budget_under_100_egp": f"{len([p for p in prices if p < 100]) / len(prices) * 100:.1f}%" if prices else "0%",
                "mid_range_100_400_egp": f"{len([p for p in prices if 100 <= p < 400]) / len(prices) * 100:.1f}%" if prices else "0%",
                "premium_400_800_egp": f"{len([p for p in prices if 400 <= p < 800]) / len(prices) * 100:.1f}%" if prices else "0%",
                "luxury_800_plus_egp": f"{len([p for p in prices if p >= 800]) / len(prices) * 100:.1f}%" if prices else "0%"
            }
        },
        "products": unique_products,
        "summary_statistics": {
            "total_unique_products": len(unique_products),
            "extraction_success_rate": "manual_compilation",
            "pages_with_successful_extraction": "5+ pages processed",
            "estimated_total_catalog_size": f"{len(unique_products)} products in compilation",
            "currency_consistency": "100% EGP",
            "data_completeness_score": f"{len([p for p in unique_products if p['product_name_arabic'] and p['price']['value'] > 0]) / len(unique_products) * 100:.1f}%"
        }
    }
    
    # Write final file
    output_file = "/workspace/data/skin_care/skin_care_products.json"
    import os
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Compilation completed!")
    print(f"📁 Final file: {output_file}")
    print(f"📊 Total products: {len(unique_products)}")
    
    if prices:
        print(f"💰 Price range: {min(prices)} - {max(prices)} EGP")
        print(f"💰 Average price: {price_stats['average_price']} EGP")
    
    print(f"🏷️  Top brands: {list(brand_counts.most_common(5))}")
    
    return len(unique_products)

if __name__ == "__main__":
    print("🚀 Starting manual compilation...")
    build_compilation()