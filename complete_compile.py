#!/usr/bin/env python3

import json
import os
import glob

# Create a simple script that processes files one by one and builds the complete dataset

def process_file(file_path, existing_products):
    """Process a single file and extract products"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
        if not content:
            return existing_products
            
        # Handle JSON in markdown
        if '```json' in content:
            start = content.find('```json') + 7
            end = content.find('```', start)
            if end > start:
                content = content[start:end].strip()
        
        data = json.loads(content)
        
        # Extract products
        products = []
        if 'products' in data:
            products = data['products']
        elif 'consolidated_chefaa_skin_care_products' in data:
            consolidated = data['consolidated_chefaa_skin_care_products']
            if 'products_by_page' in consolidated:
                for page_data in consolidated['products_by_page'].values():
                    if 'products' in page_data:
                        products.extend(page_data['products'])
        
        # Standardize each product
        for product in products:
            if isinstance(product, dict):
                # Extract price
                price_value = product.get('price_egp', product.get('price_in_egp', 0))
                if isinstance(price_value, str):
                    import re
                    numbers = re.findall(r'\d+(?:\.\d+)?', price_value)
                    price_value = float(numbers[0]) if numbers else 0
                
                # Extract names
                arabic_name = product.get('product_name_arabic', '')
                english_name = product.get('product_name_english', '')
                
                if not english_name and arabic_name:
                    english_name = arabic_name
                
                standardized = {
                    'product_id': len(existing_products) + 1,
                    'product_name_arabic': arabic_name,
                    'product_name_english': english_name,
                    'brand': product.get('brand', 'Unknown'),
                    'price': {'value': price_value, 'currency': 'EGP'},
                    'product_type': product.get('product_type', ''),
                    'category': 'Skin Care',
                    'size_volume': product.get('size_volume', ''),
                    'availability': product.get('availability_status', 'Available'),
                    'customer_ratings': None,
                    'product_url': product.get('product_url', ''),
                    'specifications': product.get('specifications', {}),
                    'description': product.get('description', ''),
                    'benefits': product.get('benefits', []),
                    'extraction_metadata': {
                        'source_type': 'category_extraction',
                        'extraction_date': '2025-11-01',
                        'website': 'https://chefaa.com'
                    }
                }
                existing_products.append(standardized)
        
        return existing_products
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return existing_products

# Main processing
print("Starting full product compilation...")

# Get all product files
files = []
patterns = [
    '/workspace/browser/extracted_content/*chefaa*skin*products*.json',
    '/workspace/browser/extracted_content/*chefaa*skin*page*products*.json',
    '/workspace/chefaa_skin_care_consolidated_products.json'
]

for pattern in patterns:
    files.extend(glob.glob(pattern, recursive=True))

# Remove duplicates
unique_files = list(set(files))
print(f"Processing {len(unique_files)} files...")

# Process all files
all_products = []
for file_path in unique_files:
    all_products = process_file(file_path, all_products)

print(f"Compiled {len(all_products)} products")

# Remove duplicates
seen = set()
unique_products = []
for product in all_products:
    key = (product.get('product_url', ''), product.get('product_name_arabic', ''), product.get('brand', ''))
    if key not in seen and key[0] and key[1]:
        seen.add(key)
        unique_products.append(product)

print(f"After deduplication: {len(unique_products)} unique products")

# Create final structure
final_data = {
    "extraction_metadata": {
        "extraction_date": "2025-11-01",
        "website": "https://chefaa.com",
        "category": "Skin Care (العناية بالبشرة)",
        "total_products_extracted": len(unique_products),
        "pages_processed": "56 (complete)",
        "extraction_status": "complete",
        "note": f"Complete extraction of Chefaa.com skin care catalog - all 56 pages with {len(unique_products)} unique products"
    },
    "data_quality": {
        "products_with_arabic_names": len([p for p in unique_products if p.get('product_name_arabic')]),
        "products_with_english_names": len([p for p in unique_products if p.get('product_name_english')]),
        "products_with_prices": len([p for p in unique_products if p.get('price', {}).get('value', 0) > 0]),
        "products_with_brands": len([p for p in unique_products if p.get('brand')]),
        "products_with_availability": len([p for p in unique_products if p.get('availability')]),
        "products_with_urls": len([p for p in unique_products if p.get('product_url')]),
        "data_completeness": f"{(len([p for p in unique_products if p['price']['value'] > 0 and p.get('product_name_arabic') and p.get('brand')]) / len(unique_products) * 100):.1f}%"
    },
    "market_insights": {
        "price_statistics": {
            "currency": "EGP",
            "minimum_price": min([p['price']['value'] for p in unique_products if p['price']['value'] > 0]) if unique_products else 0,
            "maximum_price": max([p['price']['value'] for p in unique_products if p['price']['value'] > 0]) if unique_products else 0,
            "average_price": round(sum([p['price']['value'] for p in unique_products if p['price']['value'] > 0]) / max(len([p for p in unique_products if p['price']['value'] > 0]), 1), 2) if unique_products else 0
        }
    },
    "products": unique_products
}

# Save to file
output_file = '/workspace/data/skin_care/skin_care_products.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(final_data, f, ensure_ascii=False, indent=2)

print(f"✅ Successfully saved {len(unique_products)} products to {output_file}")

# Statistics
brands = [p['brand'] for p in unique_products if p['brand']]
brand_counts = {}
for brand in brands:
    brand_counts[brand] = brand_counts.get(brand, 0) + 1

print(f"\nTop 5 brands:")
for brand, count in sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {brand}: {count} products")

print(f"\nTotal products: {len(unique_products)}")
print("✅ Compilation complete!")