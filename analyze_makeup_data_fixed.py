#!/usr/bin/env python3
"""
Comprehensive Makeup Products Data Analysis for Chefaa.com
Analyzes and consolidates all collected product data - Fixed version
"""

import json
import os
import re
from datetime import datetime
from collections import defaultdict

def extract_json_from_markdown(content):
    """Extract JSON content from markdown formatted files"""
    # Look for JSON content between ```json and ```
    json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
    if json_match:
        return json_match.group(1)
    return content

def load_extracted_data():
    """Load all extracted JSON files and compile product data"""
    
    data_files = [
        "browser/extracted_content/makeup_accessories_chefaa.json",  # Page 1
        "browser/extracted_content/makeup_accessories_page2.json",   # Page 2  
        "browser/extracted_content/makeup_accessories_page3.json",   # Page 3
        "browser/extracted_content/makeup_face_products.json",       # Face subcategory
    ]
    
    all_products = []
    data_summary = {
        'source_pages': [],
        'total_products': 0,
        'brands_found': set(),
        'categories_found': defaultdict(list),
        'price_analysis': {
            'min_price': None,
            'max_price': None,
            'avg_price': None,
            'price_distribution': defaultdict(int)
        }
    }
    
    for file_path in data_files:
        if os.path.exists(file_path):
            print(f"Loading data from: {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Extract JSON from markdown
                json_content = extract_json_from_markdown(content)
                data = json.loads(json_content)
                
                # Determine products based on data structure
                products = []
                page_name = data.get('title', 'Unknown')
                
                if 'products' in data and isinstance(data['products'], list):
                    products = data['products']
                elif 'key_points' in data and isinstance(data['key_points'], list):
                    # Check if key_points contains product objects
                    if data['key_points'] and isinstance(data['key_points'][0], dict):
                        products = data['key_points']
                
                if not products:
                    print(f"   No products found in {file_path}")
                    continue
                
                # Add page info and products
                page_info = {
                    'page_name': page_name,
                    'url': data.get('url', ''),
                    'product_count': len(products),
                    'products': []
                }
                
                for product in products:
                    # Standardize product format
                    if isinstance(product, dict):
                        standardized_product = {
                            'product_name': product.get('product_name', ''),
                            'description': product.get('description', ''),
                            'price': extract_price_number(product.get('price', '')),
                            'price_text': product.get('price', ''),
                            'brand': product.get('brand', 'Unknown'),
                            'rating': product.get('rating'),
                            'stock_status': product.get('stock_status', 'In Stock'),
                            'specifications': product.get('specifications', {}),
                            'source_page': page_name,
                            'source_url': data.get('url', ''),
                            'extracted_at': datetime.now().isoformat()
                        }
                        
                        # Add to collections
                        all_products.append(standardized_product)
                        page_info['products'].append(standardized_product)
                        
                        # Update statistics
                        data_summary['brands_found'].add(standardized_product['brand'])
                        
                        # Categorize products
                        categorize_product(standardized_product, data_summary)
                        
                        # Price analysis
                        if standardized_product['price']:
                            price = standardized_product['price']
                            update_price_analysis(price, data_summary['price_analysis'])
                
                data_summary['source_pages'].append(page_info)
                data_summary['total_products'] += len(products)
                print(f"   Loaded {len(products)} products")
                
            except Exception as e:
                print(f"   Error loading {file_path}: {e}")
                continue
    
    # Convert set to list for JSON serialization
    data_summary['brands_found'] = list(data_summary['brands_found'])
    
    return all_products, data_summary

def extract_price_number(price_text):
    """Extract numeric price from price text"""
    if not price_text:
        return None
    
    # Handle different price formats
    numbers = re.findall(r'[\d,]+', str(price_text))
    if numbers:
        try:
            return int(numbers[0].replace(',', ''))
        except ValueError:
            return None
    return None

def categorize_product(product, summary):
    """Categorize product based on name and specifications"""
    name = product['product_name'].lower()
    
    if any(word in name for word in ['طلاء أظافر', 'nail polish', 'أظافر']):
        summary['categories_found']['Nail Polish'].append(product)
    elif any(word in name for word in ['مرطب شفاه', 'lip', 'شفاه']):
        summary['categories_found']['Lip Care'].append(product)
    elif any(word in name for word in ['كونسيلر', 'concealer', 'كريم اساس', 'foundation']):
        summary['categories_found']['Face Makeup'].append(product)
    elif any(word in name for word in ['رموش', 'eyelash', 'ماسكارا', 'mascara']):
        summary['categories_found']['Eye Makeup'].append(product)
    elif any(word in name for word in ['سيرم', 'serum']):
        summary['categories_found']['Serums'].append(product)
    elif any(word in name for word in ['قطن', 'cotton', 'وسادة']):
        summary['categories_found']['Accessories'].append(product)
    else:
        summary['categories_found']['Other'].append(product)

def update_price_analysis(price, price_analysis):
    """Update price analysis statistics"""
    if price_analysis['min_price'] is None or price < price_analysis['min_price']:
        price_analysis['min_price'] = price
    if price_analysis['max_price'] is None or price > price_analysis['max_price']:
        price_analysis['max_price'] = price
    
    # Create price ranges
    if price < 50:
        price_analysis['price_distribution']['Under 50 EGP'] += 1
    elif price < 100:
        price_analysis['price_distribution']['50-99 EGP'] += 1
    elif price < 200:
        price_analysis['price_distribution']['100-199 EGP'] += 1
    elif price < 300:
        price_analysis['price_distribution']['200-299 EGP'] += 1
    elif price < 500:
        price_analysis['price_distribution']['300-499 EGP'] += 1
    else:
        price_analysis['price_distribution']['500+ EGP'] += 1

def calculate_average_price(prices):
    """Calculate average price from list of prices"""
    if not prices:
        return None
    return sum(prices) / len(prices)

def generate_comprehensive_report():
    """Generate comprehensive analysis report"""
    products, summary = load_extracted_data()
    
    # Calculate average price
    all_prices = [p['price'] for p in products if p['price']]
    summary['price_analysis']['avg_price'] = calculate_average_price(all_prices)
    
    # Convert defaultdict to regular dict for JSON
    summary['categories_found'] = dict(summary['categories_found'])
    
    # Create final report
    report = {
        'extraction_summary': {
            'total_products_extracted': len(products),
            'source_pages_count': len(summary['source_pages']),
            'extraction_date': datetime.now().isoformat(),
            'website': 'chefaa.com',
            'category': 'Makeup & Accessories',
            'data_quality': 'Systematic extraction with detailed product information',
            'navigation_issues': 'Some subcategories (Eyes, Lips, Nails, Eyelashes) redirected to other pages'
        },
        'detailed_statistics': summary,
        'product_catalog': products,
        'extracted_pages_detail': summary['source_pages'],
        'key_findings': {
            'most_common_brand': get_most_common_brand(products),
            'most_expensive_product': max(products, key=lambda x: x['price'] or 0) if products else None,
            'cheapest_product': min(products, key=lambda x: x['price'] or float('inf')) if products else None,
            'product_categories': list(summary['categories_found'].keys())
        },
        'technical_notes': {
            'successful_pages': ['Main Category Page 1', 'Main Category Page 2', 'Main Category Page 3', 'Face Subcategory'],
            'redirected_pages': ['Eyes Subcategory', 'Lips Subcategory', 'Nails Subcategory', 'Eyelashes Subcategory'],
            'extraction_method': 'Browser-based extraction with systematic navigation',
            'data_format': 'JSON with detailed product specifications'
        }
    }
    
    return report

def get_most_common_brand(products):
    """Get the most common brand from products"""
    if not products:
        return 'Unknown'
    
    brand_counts = defaultdict(int)
    for product in products:
        if product['brand']:
            brand_counts[product['brand']] += 1
    
    if brand_counts:
        return max(brand_counts.items(), key=lambda x: x[1])[0]
    return 'Unknown'

def save_final_report(report, filename="chefaa_makeup_comprehensive_report.json"):
    """Save the comprehensive report"""
    os.makedirs('/workspace/data', exist_ok=True)
    filepath = f'/workspace/data/{filename}'
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return filepath

def print_summary_report(report):
    """Print a formatted summary of the findings"""
    print("\n" + "="*80)
    print("🎯 CHEFAA MAKEUP PRODUCTS EXTRACTION REPORT")
    print("="*80)
    
    summary = report['extraction_summary']
    stats = report['detailed_statistics']
    
    print(f"\n📊 EXTRACTION SUMMARY:")
    print(f"   • Total Products: {summary['total_products_extracted']}")
    print(f"   • Pages Analyzed: {summary['source_pages_count']}")
    print(f"   • Website: {summary['website']}")
    print(f"   • Category: {summary['category']}")
    
    print(f"\n🏷️ BRANDS FOUND ({len(stats['brands_found'])}):")
    for brand in sorted(stats['brands_found']):
        print(f"   • {brand}")
    
    print(f"\n💰 PRICE ANALYSIS:")
    price_info = stats['price_analysis']
    print(f"   • Price Range: {price_info['min_price']} - {price_info['max_price']} EGP")
    print(f"   • Average Price: {price_info['avg_price']:.2f} EGP" if price_info['avg_price'] else "   • Average Price: Not calculated")
    
    print(f"\n📂 PRODUCT CATEGORIES:")
    for category, products in stats['categories_found'].items():
        print(f"   • {category}: {len(products)} products")
    
    print(f"\n🗂️ DATA PAGES:")
    for page in stats['source_pages']:
        print(f"   • {page['page_name']}: {page['product_count']} products")
    
    print(f"\n🔍 KEY FINDINGS:")
    findings = report['key_findings']
    print(f"   • Most Common Brand: {findings['most_common_brand']}")
    if findings['most_expensive_product']:
        print(f"   • Most Expensive: {findings['most_expensive_product']['product_name']} - {findings['most_expensive_product']['price']} EGP")
    if findings['cheapest_product']:
        print(f"   • Cheapest: {findings['cheapest_product']['product_name']} - {findings['cheapest_product']['price']} EGP")
    
    print(f"\n⚠️  NAVIGATION ISSUES:")
    print(f"   • Successfully Extracted: {len(report['technical_notes']['successful_pages'])} pages")
    print(f"   • Redirected/Issues: {len(report['technical_notes']['redirected_pages'])} subcategories")
    print("   • This may indicate limited product availability in those subcategories")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    print("Analyzing Chefaa makeup products data...")
    
    # Generate comprehensive report
    report = generate_comprehensive_report()
    
    # Save report
    filepath = save_final_report(report)
    
    # Print summary
    print_summary_report(report)
    
    print(f"\n✅ Comprehensive report saved to: {filepath}")
    print("📁 Individual JSON files are available in: browser/extracted_content/")
    
    # Create a detailed product list
    print(f"\n📋 SAMPLE PRODUCTS EXTRACTED:")
    for i, product in enumerate(report['product_catalog'][:10], 1):
        print(f"   {i}. {product['product_name']} - {product['brand']} - {product['price']} EGP")
    
    if len(report['product_catalog']) > 10:
        print(f"   ... and {len(report['product_catalog']) - 10} more products")