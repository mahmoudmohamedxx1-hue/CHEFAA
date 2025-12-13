import requests
import json

SUPABASE_URL = "https://sggthvsfucciptpgokgk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNnZ3RodnNmdWNjaXB0cGdva2drIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTkzMDcyMCwiZXhwIjoyMDc3NTA2NzIwfQ.wzbtz77OtHcW8Ie6m_mc2On3qumQKJz26x_ygAqluhc"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

# Map of keywords to image paths (using relative paths from public folder)
image_mappings = {
    'dove': '/images/dove_original_beauty_bar_soap_4_pack_deep_moisture.jpg',
    'panadol': '/images/Panadol_500mg_Paracetamol_Pain_Relief_Box_Front.jpg',
    'pantene': '/images/pantene_pro_v_sheer_volume_shampoo_bottle_white_background.jpg',
    'loreal': '/images/Loreal_Ever_Pure_Thickening_Shampoo_Conditioner_Product_Photo.jpg',
    'l\'oreal': '/images/loreal_absolut_repair_molecular_hair_care_products_studio.jpg',
    'cerave': '/images/cerave_daily_moisturizing_lotion_white_background.jpg',
    'garnier': '/images/Garnier_PureActive_Anti_Blackhead_Deep_Pore_Wash_Product_Photo.jpg',
    'nivea': '/images/nivea_body_lotion_original_moisture_500ml_white_background.jpg',
    'neutrogena': '/images/neutrogena-sheer-zinc-mineral-sunscreen-spf-50-white-background.jpg',
    'pampers': '/images/pampers_swaddlers_diaper_pack_size_5_104_count.jpg',
    'molfix': '/images/pampers_swaddlers_size1_216count_diaper_pack.jpg',
}

# Generic fallback images for categories
category_fallbacks = {
    '00b6ecb8-30f9-43c6-9e3c-4e9bfbabde77': '/images/medication_pills_spilled_from_prescription_bottle_white_background.jpg',  # Medications
    '5fff1dcd-f553-48d1-bb18-308ac1b7464c': '/images/loreal_absolut_repair_molecular_hair_care_products_studio.jpg',  # Hair Care
    'b41aefa7-3c94-4a69-9eb3-3daa3fd5fa50': '/images/cerave_facial_moisturising_lotion_white_background.jpg',  # Skin Care
    'fcd2a965-f02b-4447-bf44-3a3cddfcef8b': '/images/pampers-swaddlers-newborn-jumbo-pack-diapers.jpg',  # Mom & Baby
    '3c0552fd-50c2-4880-9332-fd203c27ac64': '/images/dove_original_beauty_bar_soap_4_pack_deep_moisture.jpg',  # Daily Essentials
}

print("Updating products with real images...")
print("=" * 60)

# Get all products
response = requests.get(
    f"{SUPABASE_URL}/rest/v1/products?select=id,name,name_ar,brand,category_id",
    headers=headers
)

if response.status_code != 200:
    print(f"Error fetching products: {response.status_code}")
    print(response.text)
    exit(1)

products = response.json()
print(f"Found {len(products)} products\n")

updates_made = 0
batch_updates = []

for product in products:
    image_path = None
    product_name = (product.get('name') or '').lower()
    product_brand = (product.get('brand') or '').lower()
    
    # Try to match by brand first
    for brand_keyword, img_path in image_mappings.items():
        if brand_keyword in product_brand or brand_keyword in product_name:
            image_path = img_path
            break
    
    # If no match, use category-based fallback
    if not image_path:
        category_id = product.get('category_id', '')
        image_path = category_fallbacks.get(category_id)
    
    # Update product if we have an image
    if image_path:
        update_response = requests.patch(
            f"{SUPABASE_URL}/rest/v1/products?id=eq.{product['id']}",
            headers=headers,
            json={"images": [image_path]}
        )
        
        if update_response.status_code in [200, 204]:
            updates_made += 1
            if updates_made <= 15:  # Show first 15
                print(f"✓ {updates_made}. {(product.get('name') or product.get('name_ar') or 'Unknown')[:45]}")

print(f"\n{'=' * 60}")
print(f"Complete: Updated {updates_made}/{len(products)} products with images")
print("=" * 60)
