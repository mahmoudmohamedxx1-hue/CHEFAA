-- Image Fix SQL Updates for Products
-- Updating products with placeholder pharmaceutical images

-- 1. Doliprane 1000mg Tablets (Pain Relief)
UPDATE products 
SET image_url = 'https://via.placeholder.com/400x400/4A90E2/FFFFFF?text=Doliprane+1000mg'
WHERE id = 'e808aae3-7cbc-4d62-8028-5b37f808ffb0';

-- 2. Panadol Migraine Tablets (Pain Relief)
UPDATE products 
SET image_url = 'https://via.placeholder.com/400x400/E94B3C/FFFFFF?text=Panadol+Migraine'
WHERE id = '8d6930f8-6da4-4cc6-8d1f-40fb4e07a64d';

-- 3. Amigrawest 2.5mg (Migraine Treatment)
UPDATE products 
SET image_url = 'https://via.placeholder.com/400x400/8E44AD/FFFFFF?text=Amigrawest+2.5mg'
WHERE id = '4d4bc3f9-bd4b-48bb-b7be-df88250c28c1';

-- 4. Panadol Advance 500mg (Pain Relief)
UPDATE products 
SET image_url = 'https://via.placeholder.com/400x400/3498DB/FFFFFF?text=Panadol+Advance+500mg'
WHERE id = '0186c3c7-41b4-4179-a9e0-7a80fa8e847e';

-- 5. Abimol (Pain Relief)
UPDATE products 
SET image_url = 'https://via.placeholder.com/400x400/1ABC9C/FFFFFF?text=Abimol'
WHERE id = 'a2af7049-1b60-45ef-ad02-0868335f2ca5';

-- 6. Abimol Extra (Pain Relief)
UPDATE products 
SET image_url = 'https://via.placeholder.com/400x400/2ECC71/FFFFFF?text=Abimol+Extra'
WHERE id = '1cda7cac-83f5-4a95-97e6-6982f457378c';

-- 7. Anselacox (Pain Relief)
UPDATE products 
SET image_url = 'https://via.placeholder.com/400x400/F39C12/FFFFFF?text=Anselacox'
WHERE id = 'e81096ce-87e7-46a6-93f8-49e55d0050e2';

-- 8. Brufen 400mg (Anti-inflammatory)
UPDATE products 
SET image_url = 'https://via.placeholder.com/400x400/E67E22/FFFFFF?text=Brufen+400mg'
WHERE id = '9c75b4e0-22c4-4a5e-a776-aa6e33f8777a';

-- 9. Brufen 600mg (Anti-inflammatory)
UPDATE products 
SET image_url = 'https://via.placeholder.com/400x400/D35400/FFFFFF?text=Brufen+600mg'
WHERE id = '9e8427d6-170c-4f77-951c-ef7a0dc56017';

-- 10. Brufen Cold 20 (Cold & Flu)
UPDATE products 
SET image_url = 'https://via.placeholder.com/400x400/9B59B6/FFFFFF?text=Brufen+Cold+20'
WHERE id = '0707b16f-7e6d-414a-95dd-783063bc3598';

-- 11. Controloc 20mg (Proton Pump Inhibitor)
UPDATE products 
SET image_url = 'https://via.placeholder.com/400x400/34495E/FFFFFF?text=Controloc+20mg'
WHERE id = '1d10f32f-9c16-4876-86e2-6c773fa19be8';

-- 12. Panadol Cold & Flu (Cold & Flu)
UPDATE products 
SET image_url = 'https://via.placeholder.com/400x400/16A085/FFFFFF?text=Panadol+Cold+%26+Flu'
WHERE id = '0b8d4ee0-a2e6-4910-995a-91f71072bfb0';

-- 13. Aerius Tablets (Antihistamine)
UPDATE products 
SET image_url = 'https://via.placeholder.com/400x400/C0392B/FFFFFF?text=Aerius+Tablets'
WHERE id = '1d895375-2def-4043-83c7-f0b3c1d9431c';

-- 14. Nasonex (Nasal Spray)
UPDATE products 
SET image_url = 'https://via.placeholder.com/400x400/8E44AD/FFFFFF?text=Nasonex'
WHERE id = '4b38bcd1-44fd-4193-ba6b-6dde649cfcdf';

-- 15. Acti-Colla C 10 Sachets (Collagen Supplement)
UPDATE products 
SET image_url = 'https://via.placeholder.com/400x400/27AE60/FFFFFF?text=Acti-Colla+C+10'
WHERE id = '09146d26-8378-4bfe-a4cc-85d9b43bad72';

-- Verification query to check updated products
SELECT id, name, image_url, 
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