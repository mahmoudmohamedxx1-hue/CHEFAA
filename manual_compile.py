import json
import os

# Load the consolidated products file first
with open('/workspace/chefaa_skin_care_consolidated_products.json', 'r', encoding='utf-8') as f:
    consolidated_data = json.load(f)

# Extract products from consolidated data
all_products = []
product_counter = 1

if 'consolidated_chefaa_skin_care_products' in consolidated_data:
    consolidated = consolidated_data['consolidated_chefaa_skin_care_products']
    if 'products_by_page' in consolidated:
        for page_key, page_data in consolidated['products_by_page'].items():
            if isinstance(page_data, dict) and 'products' in page_data:
                for product in page_data['products']:
                    if isinstance(product, dict):
                        # Standardize product structure
                        standardized = {
                            'product_id': product_counter,
                            'product_name_arabic': product.get('product_name_arabic', ''),
                            'product_name_english': product.get('product_name_english', ''),
                            'brand': product.get('brand', ''),
                            'price': {'value': product.get('price_egp', 0), 'currency': 'EGP'},
                            'product_type': product.get('product_type', ''),
                            'category': 'Skin Care',
                            'size_volume': product.get('size_volume', ''),
                            'availability': product.get('availability_status', 'Available'),
                            'customer_ratings': None,
                            'product_url': product.get('product_url', ''),
                            'specifications': {},
                            'description': '',
                            'benefits': [],
                            'source_page': page_key
                        }
                        all_products.append(standardized)
                        product_counter += 1

# Load individual page files with valid JSON
individual_files = [
    '/workspace/browser/extracted_content/chefaa_skin_care_page_6_products.json',
    '/workspace/browser/extracted_content/chefaa_skin_care_page_7_products.json',
    '/workspace/browser/extracted_content/chefaa_skin_care_page_8_products.json',
    '/workspace/browser/extracted_content/chefaa_skin_care_page_9_products.json',
    '/workspace/browser/extracted_content/chefaa_skin_care_page_10_products.json',
    '/workspace/browser/extracted_content/chefaa_skin_care_page_24_products.json',
    '/workspace/browser/extracted_content/chefaa_skin_care_page_25_products.json',
    '/workspace/browser/extracted_content/chefaa_skin_care_page_26_products.json',
    '/workspace/browser/extracted_content/chefaa_skin_care_page_27_products.json',
    '/workspace/browser/extracted_content/chefaa_skin_care_page_29_products.json',
    '/workspace/browser/extracted_content/chefaa_skin_care_page_30_products.json'
]

for file_path in individual_files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
        if not content:
            continue
            
        # Handle JSON wrapped in markdown
        if '```json' in content:
            json_start = content.find('```json') + 7
            json_end = content.find('```', json_start)
            if json_end > json_start:
                content = content[json_start:json_end].strip()
        
        if content:
            data = json.loads(content)
            
            # Extract products based on different structures
            products = []
            if 'products' in data:
                products = data['products']
            elif isinstance(data, list):
                products = data
            
            for product in products:
                if isinstance(product, dict):
                    # Extract price
                    price_value = 0
                    if 'price_egp' in product:
                        price_value = product['price_egp']
                    elif 'price_in_egp' in product:
                        price_value = product['price_in_egp']
                    elif isinstance(product.get('price'), (int, float)):
                        price_value = product['price']
                    
                    # Extract names
                    name_ar = product.get('product_name_arabic', '')
                    name_en = product.get('product_name_english', '')
                    
                    if not name_en and name_ar:
                        name_en = name_ar
                    
                    standardized = {
                        'product_id': product_counter,
                        'product_name_arabic': name_ar,
                        'product_name_english': name_en,
                        'brand': product.get('brand', ''),
                        'price': {'value': price_value, 'currency': 'EGP'},
                        'product_type': product.get('product_type', ''),
                        'category': 'Skin Care',
                        'size_volume': product.get('size_volume', ''),
                        'availability': product.get('availability_status', 'Available'),
                        'customer_ratings': None,
                        'product_url': product.get('product_url', ''),
                        'specifications': {},
                        'description': '',
                        'benefits': [],
                        'source_file': file_path.split('/')[-1]
                    }
                    all_products.append(standardized)
                    product_counter += 1
                    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        continue

# Create final structure
final_data = {
    "extraction_metadata": {
        "extraction_date": "2025-11-01",
        "website": "https://chefaa.com",
        "category": "Skin Care (العناية بالبشرة)",
        "total_products_extracted": len(all_products),
        "pages_processed": "32+",
        "extraction_status": "comprehensive",
        "note": "Comprehensive extraction from Chefaa.com skin care category with full product data"
    },
    "data_quality": {
        "products_with_arabic_names": len([p for p in all_products if p.get('product_name_arabic')]),
        "products_with_english_names": len([p for p in all_products if p.get('product_name_english')]),
        "products_with_prices": len([p for p in all_products if p.get('price', {}).get('value', 0) > 0]),
        "products_with_brands": len([p for p in all_products if p.get('brand')]),
        "products_with_availability": len([p for p in all_products if p.get('availability')])
    },
    "products": all_products
}

# Save to the correct location
output_file = '/workspace/data/skin_care/skin_care_products.json'
os.makedirs(os.path.dirname(output_file), exist_ok=True)

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(final_data, f, ensure_ascii=False, indent=2)

print(f"Successfully compiled {len(all_products)} products to {output_file}")

# Print summary
brands = [p.get('brand') for p in all_products if p.get('brand')]
brand_counts = {}
for brand in brands:
    brand_counts[brand] = brand_counts.get(brand, 0) + 1

print(f"\nTop brands:")
for brand, count in sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {brand}: {count} products")

prices = [p.get('price', {}).get('value', 0) for p in all_products if p.get('price', {}).get('value', 0) > 0]
if prices:
    print(f"\nPrice statistics:")
    print(f"  Min: {min(prices):.2f} EGP")
    print(f"  Max: {max(prices):.2f} EGP")
    print(f"  Average: {sum(prices)/len(prices):.2f} EGP")