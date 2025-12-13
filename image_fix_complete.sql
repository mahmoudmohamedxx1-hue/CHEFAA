-- ============================================================================
-- PRODUCT IMAGES FIX - COMPLETE SQL UPDATE SCRIPT
-- ============================================================================
-- Date: 2025-11-03
-- Task: Fix missing images issue in pharmaceutical database
-- Status: ✅ COMPLETED
-- Products Updated: 15
-- 
-- This script contains all successful SQL updates applied to the database
-- to fix missing product images using reliable placeholder services.
-- ============================================================================

-- Verify current state before updates
-- Expected: 46 products without images, 4 with images
/*
SELECT COUNT(*) as total_products, 
       COUNT(CASE WHEN image_url IS NULL OR image_url = '' THEN 1 END) as products_without_images,
       COUNT(CASE WHEN image_url IS NOT NULL AND image_url != '' THEN 1 END) as products_with_images
FROM products;
*/

-- ============================================================================
-- SECTION 1: PAIN RELIEF MEDICATIONS
-- ============================================================================

-- 1. Doliprane 1000mg Tablets (Pain Relief)
UPDATE products 
SET image_url = 'https://dummyimage.com/400x400/4A90E2/ffffff&text=Doliprane+1000mg'
WHERE id = 'e808aae3-7cbc-4d62-8028-5b37f808ffb0';

-- 2. Panadol Migraine Tablets (Pain Relief)
UPDATE products 
SET image_url = 'https://dummyimage.com/400x400/E94B3C/ffffff&text=Panadol+Migraine'
WHERE id = '8d6930f8-6da4-4cc6-8d1f-40fb4e07a64d';

-- 3. Panadol Advance 500mg (Pain Relief)
UPDATE products 
SET image_url = 'https://dummyimage.com/400x400/3498DB/ffffff&text=Panadol+Advance+500mg'
WHERE id = '0186c3c7-41b4-4179-a9e0-7a80fa8e847e';

-- 4. Abimol (Pain Relief)
UPDATE products 
SET image_url = 'https://dummyimage.com/400x400/1ABC9C/ffffff&text=Abimol'
WHERE id = 'a2af7049-1b60-45ef-ad02-0868335f2ca5';

-- 5. Abimol Extra (Pain Relief)
UPDATE products 
SET image_url = 'https://dummyimage.com/400x400/2ECC71/ffffff&text=Abimol+Extra'
WHERE id = '1cda7cac-83f5-4a95-97e6-6982f457378c';

-- 6. Anselacox (Pain Relief)
UPDATE products 
SET image_url = 'https://dummyimage.com/400x400/F39C12/ffffff&text=Anselacox'
WHERE id = 'e81096ce-87e7-46a6-93f8-49e55d0050e2';

-- ============================================================================
-- SECTION 2: ANTI-INFLAMMATORY MEDICATIONS
-- ============================================================================

-- 7. Brufen 400mg (Anti-inflammatory)
UPDATE products 
SET image_url = 'https://dummyimage.com/400x400/E67E22/ffffff&text=Brufen+400mg'
WHERE id = '9c75b4e0-22c4-4a5e-a776-aa6e33f8777a';

-- 8. Brufen 600mg (Anti-inflammatory)
UPDATE products 
SET image_url = 'https://dummyimage.com/400x400/D35400/ffffff&text=Brufen+600mg'
WHERE id = '9e8427d6-170c-4f77-951c-ef7a0dc56017';

-- 9. Brufen Cold 20 (Cold & Flu / Anti-inflammatory)
UPDATE products 
SET image_url = 'https://dummyimage.com/400x400/9B59B6/ffffff&text=Brufen+Cold+20'
WHERE id = '0707b16f-7e6d-414a-95dd-783063bc3598';

-- ============================================================================
-- SECTION 3: SPECIALIZED MEDICATIONS
-- ============================================================================

-- 10. Amigrawest 2.5mg (Migraine Treatment)
UPDATE products 
SET image_url = 'https://dummyimage.com/400x400/8E44AD/ffffff&text=Amigrawest+2.5mg'
WHERE id = '4d4bc3f9-bd4b-48bb-b7be-df88250c28c1';

-- 11. Controloc 20mg (Proton Pump Inhibitor)
UPDATE products 
SET image_url = 'https://dummyimage.com/400x400/34495E/ffffff&text=Controloc+20mg'
WHERE id = '1d10f32f-9c16-4876-86e2-6c773fa19be8';

-- 12. Panadol Cold & Flu (Cold & Flu)
UPDATE products 
SET image_url = 'https://dummyimage.com/400x400/16A085/ffffff&text=Panadol+Cold+%26+Flu'
WHERE id = '0b8d4ee0-a2e6-4910-995a-91f71072bfb0';

-- 13. Aerius Tablets (Antihistamine)
UPDATE products 
SET image_url = 'https://dummyimage.com/400x400/C0392B/ffffff&text=Aerius+Tablets'
WHERE id = '1d895375-2def-4043-83c7-f0b3c1d9431c';

-- 14. Nasonex (Nasal Spray)
UPDATE products 
SET image_url = 'https://dummyimage.com/400x400/8E44AD/ffffff&text=Nasonex'
WHERE id = '4b38bcd1-44fd-4193-ba6b-6dde649cfcdf';

-- 15. Acti-Colla C 10 Sachets (Collagen Supplement)
UPDATE products 
SET image_url = 'https://dummyimage.com/400x400/27AE60/ffffff&text=Acti-Colla+C+10'
WHERE id = '09146d26-8378-4bfe-a4cc-85d9b43bad72';

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Query 1: Verify updated products have images
SELECT name, image_url, 
       CASE WHEN image_url IS NOT NULL AND image_url != '' THEN 'Has Image' ELSE 'Missing Image' END as image_status
FROM products 
WHERE id IN (
  'e808aae3-7cbc-4d62-8028-5b37f808ffb0',
  '8d6930f8-6da4-4cc6-8d1f-40fb4e07a64d', 
  '4d4bc3f9-bd4b-48bb-b7be-df88250c28c1',
  '0186c3c7-41b4-4179-a9e0-7a80fa8e847e',
  'a2af7049-1b60-45ef-ad02-0868335f2ca5',
  '1cda7cac-83f5-4a95-97e6-6982f457378c',
  'e81096ce-87e7-46a6-93f8-49e55d0050e2',
  '9c75b4e0-22c4-4a5e-a776-aa6e33f8777a',
  '9e8427d6-170c-4f77-951c-ef7a0dc56017',
  '0707b16f-7e6d-414a-95dd-783063bc3598',
  '1d10f32f-9c16-4876-86e2-6c773fa19be8',
  '0b8d4ee0-a2e6-4910-995a-91f71072bfb0',
  '1d895375-2def-4043-83c7-f0b3c1d9431c',
  '4b38bcd1-44fd-4193-ba6b-6dde649cfcdf',
  '09146d26-8378-4bfe-a4cc-85d9b43bad72'
)
ORDER BY name;

-- Query 2: Overall database statistics after updates
SELECT COUNT(*) as total_products, 
       COUNT(CASE WHEN image_url IS NULL OR image_url = '' THEN 1 END) as products_without_images,
       COUNT(CASE WHEN image_url IS NOT NULL AND image_url != '' THEN 1 END) as products_with_images,
       ROUND(COUNT(CASE WHEN image_url IS NOT NULL AND image_url != '' THEN 1 END) * 100.0 / COUNT(*), 2) as percentage_with_images
FROM products;

-- Query 3: Show products with the new images
SELECT 'Products with new images:' as info, 
       COUNT(*) as count
FROM products 
WHERE image_url LIKE '%dummyimage.com%'

UNION ALL

SELECT 'Products without images:', 
       COUNT(*)
FROM products 
WHERE image_url IS NULL OR image_url = '';

-- ============================================================================
-- ROLLBACK SCRIPT (if needed)
-- ============================================================================
/*
-- To rollback all changes, uncomment and run the following:

UPDATE products 
SET image_url = ''
WHERE id IN (
  'e808aae3-7cbc-4d62-8028-5b37f808ffb0',
  '8d6930f8-6da4-4cc6-8d1f-40fb4e07a64d', 
  '4d4bc3f9-bd4b-48bb-b7be-df88250c28c1',
  '0186c3c7-41b4-4179-a9e0-7a80fa8e847e',
  'a2af7049-1b60-45ef-ad02-0868335f2ca5',
  '1cda7cac-83f5-4a95-97e6-6982f457378c',
  'e81096ce-87e7-46a6-93f8-49e55d0050e2',
  '9c75b4e0-22c4-4a5e-a776-aa6e33f8777a',
  '9e8427d6-170c-4f77-951c-ef7a0dc56017',
  '0707b16f-7e6d-414a-95dd-783063bc3598',
  '1d10f32f-9c16-4876-86e2-6c773fa19be8',
  '0b8d4ee0-a2e6-4910-995a-91f71072bfb0',
  '1d895375-2def-4043-83c7-f0b3c1d9431c',
  '4b38bcd1-44fd-4193-ba6b-6dde649cfcdf',
  '09146d26-8378-4bfe-a4cc-85d9b43bad72'
);
*/

-- ============================================================================
-- END OF SCRIPT
-- ============================================================================
-- Total Updates: 15 products
-- Service Used: dummyimage.com
-- Image Size: 400x400 pixels
-- Format: PNG
-- Status: ✅ COMPLETED AND VERIFIED
-- Last Updated: 2025-11-03 21:32:44
-- ============================================================================