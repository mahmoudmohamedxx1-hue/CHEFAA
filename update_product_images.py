import requests
import json

SUPABASE_URL = "https://sggthvsfucciptpgokgk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNnZ3RodnNmdWNjaXB0cGdva2drIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTkzMDcyMCwiZXhwIjoyMDc3NTA2NzIwfQ.wzbtz77OtHcW8Ie6m_mc2On3qumQKJz26x_ygAqluhc"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# Map of keywords to image paths
image_mappings = {
    'dove': '/workspace/imgs/dove_original_beauty_bar_soap_4_pack_deep_moisture.jpg',
    'panadol': '/workspace/imgs/Panadol_500mg_Paracetamol_Pain_Relief_Box_Front.jpg',
    'pantene': '/workspace/imgs/pantene_pro_v_sheer_volume_shampoo_bottle_white_background.jpg',
    'loreal': '/workspace/imgs/Loreal_Ever_Pure_Thickening_Shampoo_Conditioner_Product_Photo.jpg',
    'cerave': '/workspace/imgs/cerave_daily_moisturizing_lotion_white_background.jpg',
    'garnier': '/workspace/imgs/Garnier_PureActive_Anti_Blackhead_Deep_Pore_Wash_Product_Photo.jpg',
    'nivea': '/workspace/imgs/nivea_body_lotion_original_moisture_500ml_white_background.jpg',
    'neutrogena': '/workspace/imgs/neutrogena-sheer-zinc-mineral-sunscreen-spf-50-white-background.jpg',
    'pampers': '/workspace/imgs/pampers_swaddlers_diaper_pack_size_5_104_count.jpg',
    'molfix': '/workspace/imgs/pampers_swaddlers_size1_216count_diaper_pack.jpg',
}

# Generic fallback images for categories
category_fallbacks = {
    'medication': '/workspace/imgs/medication_pills_spilled_from_prescription_bottle_white_background.jpg',
    'hair': '/workspace/imgs/loreal_absolut_repair_molecular_hair_care_products_studio.jpg',
    'skin': '/workspace/imgs/cerave_facial_moisturising_lotion_white_background.jpg',
    'baby': '/workspace/imgs/pampers-swaddlers-newborn-jumbo-pack-diapers.jpg',
}

print("Updating products with real images...")

# Get all products
response = requests.get(
    f"{SUPABASE_URL}/rest/v1/products?select=id,name,name_ar,brand,category_id",
    headers=headers
)

products = response.json()
print(f"Found {len(products)} products")

updates_made = 0

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
        # Hair Care
        if category_id == '5fff1dcd-f553-48d1-bb18-308ac1b7464c':
            image_path = category_fallbacks['hair']
        # Medications
        elif category_id == '00b6ecb8-30f9-43c6-9e3c-4e9bfbabde77':
            image_path = category_fallbacks['medication']
        # Skin Care
        elif category_id == 'b41aefa7-3c94-4a69-9eb3-3daa3fd5fa50':
            image_path = category_fallbacks['skin']
        # Mom & Baby
        elif category_id == 'fcd2a965-f02b-4447-bf44-3a3cddfcef8b':
            image_path = category_fallbacks['baby']
    
    # Update product if we have an image
    if image_path:
        update_response = requests.patch(
            f"{SUPABASE_URL}/rest/v1/products?id=eq.{product['id']}",
            headers=headers,
            json={"images": [image_path]}
        )
        
        if update_response.status_code in [200, 204]:
            updates_made += 1
            if updates_made <= 10:  # Show first 10
                print(f"✓ Updated: {product.get('name', product.get('name_ar', 'Unknown'))[:50]}")

print(f"\nComplete: Updated {updates_made} products with images")
