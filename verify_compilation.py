#!/usr/bin/env python3
"""
Final Verification Script for Skin Care Products Compilation
"""

import json
import os

def verify_compilation():
    """Verify the final compilation file"""
    file_path = "/workspace/data/skin_care/skin_care_products.json"
    
    print("🔍 Verifying skin care products compilation...")
    
    # Check if file exists
    if not os.path.exists(file_path):
        print("❌ File not found!")
        return False
    
    # Load and validate JSON
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("✅ JSON structure is valid")
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return False
    
    # Verify required sections
    required_sections = ['extraction_metadata', 'market_insights', 'products', 'summary_statistics']
    for section in required_sections:
        if section not in data:
            print(f"❌ Missing section: {section}")
            return False
    print("✅ All required sections present")
    
    # Verify products
    products = data.get('products', [])
    if not isinstance(products, list):
        print("❌ Products is not a list")
        return False
    
    print(f"✅ Found {len(products)} products")
    
    # Verify sample products
    if len(products) > 0:
        sample_product = products[0]
        required_fields = ['product_id', 'product_name_arabic', 'brand', 'price']
        for field in required_fields:
            if field not in sample_product:
                print(f"❌ Missing field in products: {field}")
                return False
        print("✅ Product structure is correct")
    
    # Verify metadata
    metadata = data.get('extraction_metadata', {})
    expected_metadata = {
        'extraction_date': '2025-11-01',
        'website': 'https://chefaa.com',
        'category': 'Skin Care (العناية بالبشرة)'
    }
    
    for key, expected_value in expected_metadata.items():
        actual_value = metadata.get(key)
        if actual_value != expected_value:
            print(f"⚠️  Metadata mismatch for {key}: expected '{expected_value}', got '{actual_value}'")
        else:
            print(f"✅ Metadata correct: {key}")
    
    # Final statistics
    print(f"\n📊 Compilation Summary:")
    print(f"   Total products: {len(products)}")
    print(f"   File size: {os.path.getsize(file_path):,} bytes")
    print(f"   Extraction date: {metadata.get('extraction_date', 'Unknown')}")
    print(f"   Website: {metadata.get('website', 'Unknown')}")
    print(f"   Category: {metadata.get('category', 'Unknown')}")
    
    # Count products by page
    page_counts = {}
    for product in products:
        page = product.get('extraction_page', 'unknown')
        page_counts[page] = page_counts.get(page, 0) + 1
    
    print(f"\n📄 Products by extraction page:")
    for page, count in sorted(page_counts.items()):
        print(f"   Page {page}: {count} products")
    
    # Price analysis
    prices = [p.get('price', {}).get('value', 0) for p in products if isinstance(p.get('price'), dict)]
    if prices:
        print(f"\n💰 Price Analysis:")
        print(f"   Min price: {min(prices):.2f} EGP")
        print(f"   Max price: {max(prices):.2f} EGP")
        print(f"   Average price: {sum(prices)/len(prices):.2f} EGP")
    
    print(f"\n✅ Compilation verification completed successfully!")
    return True

if __name__ == "__main__":
    verify_compilation()