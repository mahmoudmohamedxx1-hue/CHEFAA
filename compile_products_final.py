#!/usr/bin/env python3
import json
import os
import glob
from typing import List, Dict, Any, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_json_safely(file_path: str) -> Tuple[Dict, bool]:
    """Load JSON file safely, return (data, success)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
        # Handle empty files
        if not content:
            return {}, False
            
        # Try to parse JSON
        data = json.loads(content)
        return data, True
        
    except json.JSONDecodeError as e:
        logging.warning(f"JSON decode error in {file_path}: {e}")
        return {}, False
    except Exception as e:
        logging.warning(f"Error reading {file_path}: {e}")
        return {}, False

def extract_products_from_data(data: Dict[str, Any], source_file: str) -> List[Dict[str, Any]]:
    """Extract products from data structure"""
    products = []
    
    try:
        # Handle different data structures
        if 'products' in data and isinstance(data['products'], list):
            products.extend(data['products'])
            
        elif 'consolidated_chefaa_skin_care_products' in data:
            # Handle consolidated file structure
            consolidated = data['consolidated_chefaa_skin_care_products']
            if 'products_by_page' in consolidated:
                for page_key, page_data in consolidated['products_by_page'].items():
                    if isinstance(page_data, dict) and 'products' in page_data:
                        products.extend(page_data['products'])
                        
        elif isinstance(data.get('products'), list):
            products = data['products']
            
        # Handle other structures
        for key in data:
            if isinstance(data[key], dict) and 'products' in data[key]:
                products.extend(data[key]['products'])
            elif isinstance(data[key], list):
                for item in data[key]:
                    if isinstance(item, dict) and 'products' in item:
                        products.extend(item['products'])
                        
    except Exception as e:
        logging.warning(f"Error extracting products from {source_file}: {e}")
        
    return products

def standardize_product(product: Dict[str, Any], product_id: int, source_info: str) -> Dict[str, Any]:
    """Standardize product data structure"""
    
    def safe_get(data: Dict, keys: List[str], default: Any = "") -> Any:
        for key in keys:
            if isinstance(data, dict) and key in data:
                return data[key]
        return default
    
    def clean_price(price_data) -> Dict[str, Any]:
        if isinstance(price_data, dict):
            return price_data
        elif isinstance(price_data, (int, float)):
            return {"value": price_data, "currency": "EGP"}
        elif isinstance(price_data, str):
            # Try to extract numeric value
            import re
            numbers = re.findall(r'\d+(?:\.\d+)?', price_data)
            if numbers:
                return {"value": float(numbers[0]), "currency": "EGP"}
        return {"value": 0, "currency": "EGP"}
    
    # Extract price
    price_egp = safe_get(product, ['price_egp', 'price_in_egp'])
    price = clean_price(price_egp) if price_egp else clean_price(safe_get(product, ['price']))
    
    # Extract names
    name_ar = safe_get(product, ['product_name_arabic', 'product_name'])
    name_en = safe_get(product, ['product_name_english'])
    
    # If no separate English name, use the main name
    if not name_en and name_ar:
        name_en = name_ar
        
    # Handle nested name structures
    if isinstance(product.get('product_name'), dict):
        name_ar = safe_get(product['product_name'], ['arabic', 'arabic_name'], name_ar)
        name_en = safe_get(product['product_name'], ['english', 'english_name'], name_en)
    
    # Clean and standardize
    standardized = {
        "product_id": product_id,
        "product_name_arabic": str(name_ar) if name_ar else "",
        "product_name_english": str(name_en) if name_en else "",
        "brand": str(safe_get(product, ['brand'])) or "Unknown",
        "price": price,
        "product_type": str(safe_get(product, ['product_type'])) or "",
        "category": "Skin Care",
        "size_volume": str(safe_get(product, ['size_volume'])) or "",
        "availability": str(safe_get(product, ['availability_status', 'availability'])) or "Available",
        "customer_ratings": None,
        "product_url": str(safe_get(product, ['product_url'])) or "",
        "specifications": {},
        "description": str(safe_get(product, ['description'])) or "",
        "benefits": [],
        "source_info": source_info
    }
    
    # Add specifications if available
    if 'specifications' in product:
        standardized['specifications'] = product['specifications']
    elif 'benefits' in product:
        standardized['benefits'] = product['benefits']
    elif 'benefits_list' in product:
        standardized['benefits'] = product['benefits_list']
        
    return standardized

def main():
    """Main function to compile all products"""
    logging.info("Starting product compilation...")
    
    # Find all potential product files
    search_patterns = [
        '/workspace/browser/extracted_content/*chefaa*skin*products*.json',
        '/workspace/browser/extracted_content/*chefaa*skin*page*products*.json',
        '/workspace/chefaa_skin_care_consolidated_products.json',
        '/workspace/chefaa_skin_care_products_comprehensive_extraction.json'
    ]
    
    all_products = []
    processed_files = set()
    file_stats = {'valid': 0, 'invalid': 0, 'empty': 0}
    
    # Search for files
    files_found = []
    for pattern in search_patterns:
        files_found.extend(glob.glob(pattern))
    
    logging.info(f"Found {len(files_found)} files to process")
    
    # Process each file
    for file_path in files_found:
        if file_path in processed_files:
            continue
            
        logging.info(f"Processing: {os.path.basename(file_path)}")
        
        data, success = load_json_safely(file_path)
        
        if not success:
            file_stats['invalid'] += 1
            logging.warning(f"Could not load JSON from {file_path}")
            continue
            
        if not data:
            file_stats['empty'] += 1
            logging.warning(f"Empty data in {file_path}")
            continue
            
        file_stats['valid'] += 1
        processed_files.add(file_path)
        
        # Extract products
        products = extract_products_from_data(data, os.path.basename(file_path))
        
        if products:
            # Add unique IDs and standardize
            for i, product in enumerate(products):
                if isinstance(product, dict):
                    standardized = standardize_product(product, len(all_products) + 1, os.path.basename(file_path))
                    all_products.append(standardized)
            logging.info(f"Extracted {len(products)} products from {os.path.basename(file_path)}")
        else:
            logging.warning(f"No products found in {os.path.basename(file_path)}")
    
    # Remove duplicates based on name, brand, and URL
    seen = set()
    unique_products = []
    
    for product in all_products:
        # Create a key for deduplication
        key = (
            product.get('product_name_arabic', ''),
            product.get('brand', ''),
            product.get('price', {}).get('value', 0),
            product.get('product_url', '')
        )
        
        if key not in seen and key[0]:  # Ensure we have a name
            seen.add(key)
            unique_products.append(product)
    
    logging.info(f"Compiled {len(unique_products)} unique products from {len(processed_files)} valid files")
    
    # Create final structure
    final_data = {
        "extraction_metadata": {
            "extraction_date": "2025-11-01",
            "website": "https://chefaa.com",
            "category": "Skin Care",
            "total_products_extracted": len(unique_products),
            "total_files_processed": len(processed_files),
            "file_statistics": file_stats,
            "extraction_status": "comprehensive",
            "note": f"Comprehensive extraction from {len(processed_files)} files with {file_stats['valid']} valid, {file_stats['invalid']} invalid, {file_stats['empty']} empty files"
        },
        "data_quality": {
            "products_with_arabic_names": len([p for p in unique_products if p.get('product_name_arabic')]),
            "products_with_english_names": len([p for p in unique_products if p.get('product_name_english')]),
            "products_with_prices": len([p for p in unique_products if p.get('price', {}).get('value', 0) > 0]),
            "products_with_brands": len([p for p in unique_products if p.get('brand')]),
            "products_with_availability": len([p for p in unique_products if p.get('availability')])
        },
        "products": unique_products
    }
    
    # Save to requested location
    output_file = '/workspace/data/skin_care/skin_care_products.json'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    logging.info(f"Saved {len(unique_products)} products to {output_file}")
    
    # Print summary statistics
    brands = [p.get('brand') for p in unique_products if p.get('brand') and p.get('brand') != 'Unknown']
    brand_counts = {}
    for brand in brands:
        brand_counts[brand] = brand_counts.get(brand, 0) + 1
    
    print(f"\n=== COMPILATION SUMMARY ===")
    print(f"Files processed: {len(processed_files)}")
    print(f"Valid files: {file_stats['valid']}")
    print(f"Total unique products: {len(unique_products)}")
    
    if brand_counts:
        print(f"\nTop brands:")
        for brand, count in sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {brand}: {count} products")
    
    prices = [p.get('price', {}).get('value', 0) for p in unique_products if p.get('price', {}).get('value', 0) > 0]
    if prices:
        print(f"\nPrice statistics:")
        print(f"  Range: {min(prices):.2f} - {max(prices):.2f} EGP")
        print(f"  Average: {sum(prices)/len(prices):.2f} EGP")
    
    return len(unique_products)

if __name__ == "__main__":
    main()