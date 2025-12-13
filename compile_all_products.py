#!/usr/bin/env python3
import json
import os
import glob
from typing import List, Dict, Any

def extract_products_from_file(file_path: str) -> List[Dict[str, Any]]:
    """Extract products from a single JSON file."""
    products = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Handle different file structures
        if 'products' in data and isinstance(data['products'], list):
            products = data['products']
        elif 'consolidated_chefaa_skin_care_products' in data:
            # Handle consolidated file structure
            if 'products_by_page' in data['consolidated_chefaa_skin_care_products']:
                for page_data in data['consolidated_chefaa_skin_care_products']['products_by_page'].values():
                    if 'products' in page_data:
                        products.extend(page_data['products'])
        
        # Clean and standardize products
        cleaned_products = []
        for product in products:
            if isinstance(product, dict):
                cleaned_products.append(clean_product_data(product))
                
        return cleaned_products
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []

def clean_product_data(product: Dict[str, Any]) -> Dict[str, Any]:
    """Clean and standardize product data."""
    cleaned = {
        'product_name': '',
        'product_name_arabic': '',
        'product_name_english': '',
        'price': {},
        'brand': '',
        'product_type': '',
        'category': '',
        'size_volume': '',
        'availability': 'Available',
        'customer_ratings': None,
        'specifications': {},
        'description': '',
        'benefits': [],
        'product_url': '',
        'source_page': ''
    }
    
    # Extract product names
    if 'product_name' in product:
        cleaned['product_name'] = product['product_name']
    if 'product_name_arabic' in product:
        cleaned['product_name_arabic'] = product['product_name_arabic']
    if 'product_name_english' in product:
        cleaned['product_name_english'] = product['product_name_english']
    
    # Handle nested name structures
    if 'product_name' in product and isinstance(product['product_name'], dict):
        name_data = product['product_name']
        cleaned['product_name'] = name_data.get('english', '') or name_data.get('arabic', '')
        cleaned['product_name_arabic'] = name_data.get('arabic', '')
        cleaned['product_name_english'] = name_data.get('english', '')
    
    # Extract price
    if 'price' in product:
        if isinstance(product['price'], dict):
            cleaned['price'] = product['price']
        elif isinstance(product['price'], (int, float)):
            cleaned['price'] = {'value': product['price'], 'currency': 'EGP'}
        elif isinstance(product['price_egp'], (int, float)):
            cleaned['price'] = {'value': product['price_egp'], 'currency': 'EGP'}
    
    # Extract brand
    if 'brand' in product:
        cleaned['brand'] = product['brand']
    elif 'brand_name' in product:
        cleaned['brand'] = product['brand_name']
    
    # Extract other fields
    for field in ['product_type', 'category', 'size_volume', 'availability_status', 'availability', 'customer_ratings', 'product_url']:
        if field in product:
            cleaned[field.replace('_status', '')] = product[field]
    
    # Handle specifications
    if 'specifications' in product:
        cleaned['specifications'] = product['specifications']
    
    # Extract description and benefits
    if 'description' in product:
        cleaned['description'] = product['description']
    elif 'description_specifications' in product:
        cleaned['description'] = product['description_specifications']
    
    if 'benefits' in product:
        cleaned['benefits'] = product['benefits']
    
    # Ensure Arabic and English names exist
    if not cleaned['product_name_arabic'] and cleaned['product_name']:
        cleaned['product_name_arabic'] = cleaned['product_name']
    
    if not cleaned['product_name_english'] and cleaned['product_name']:
        cleaned['product_name_english'] = cleaned['product_name']
    
    return cleaned

def main():
    # Find all skin care product files
    file_patterns = [
        '/workspace/browser/extracted_content/*skin*products*.json',
        '/workspace/browser/extracted_content/*skin*page*products*.json',
        '/workspace/chefaa_skin_care_consolidated_products.json',
        '/workspace/chefaa_skin_care_products_comprehensive_extraction.json'
    ]
    
    all_products = []
    processed_files = set()
    
    for pattern in file_patterns:
        files = glob.glob(pattern)
        for file_path in files:
            if file_path not in processed_files:
                print(f"Processing: {file_path}")
                products = extract_products_from_file(file_path)
                if products:
                    # Add source info to products
                    for product in products:
                        product['source_file'] = os.path.basename(file_path)
                    all_products.extend(products)
                    processed_files.add(file_path)
    
    # Remove duplicates based on product name and price
    seen = set()
    unique_products = []
    for product in all_products:
        key = (product.get('product_name_arabic', ''), 
               product.get('price', {}).get('value', 0),
               product.get('brand', ''))
        if key not in seen:
            seen.add(key)
            unique_products.append(product)
    
    # Create final structure
    final_data = {
        "extraction_metadata": {
            "extraction_date": "2025-11-01",
            "website": "https://chefaa.com",
            "category": "Skin Care",
            "total_products_extracted": len(unique_products),
            "total_files_processed": len(processed_files),
            "files_processed": list(processed_files),
            "extraction_status": "complete",
            "note": "Comprehensive extraction from all available skin care pages"
        },
        "data_quality": {
            "products_with_arabic_names": len([p for p in unique_products if p.get('product_name_arabic')]),
            "products_with_english_names": len([p for p in unique_products if p.get('product_name_english')]),
            "products_with_prices": len([p for p in unique_products if p.get('price')]),
            "products_with_brands": len([p for p in unique_products if p.get('brand')]),
            "products_with_availability": len([p for p in unique_products if p.get('availability')])
        },
        "products": unique_products
    }
    
    # Save to the requested location
    output_file = '/workspace/data/skin_care/skin_care_products.json'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    print(f"Compiled {len(unique_products)} unique products from {len(processed_files)} files")
    print(f"Saved to: {output_file}")
    
    # Print summary statistics
    brands = [p.get('brand') for p in unique_products if p.get('brand')]
    brand_counts = {}
    for brand in brands:
        brand_counts[brand] = brand_counts.get(brand, 0) + 1
    
    print(f"\nTop 10 brands:")
    for brand, count in sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {brand}: {count} products")
    
    prices = [p.get('price', {}).get('value', 0) for p in unique_products if p.get('price', {}).get('value')]
    if prices:
        print(f"\nPrice statistics:")
        print(f"  Min: {min(prices):.2f} EGP")
        print(f"  Max: {max(prices):.2f} EGP")
        print(f"  Average: {sum(prices)/len(prices):.2f} EGP")

if __name__ == "__main__":
    main()
