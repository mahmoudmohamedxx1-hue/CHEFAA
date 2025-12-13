#!/bin/bash
# Convert all images to WebP format
cd /workspace/chefaa-clone/public/images

echo "Converting images to WebP format..."

count=0
for img in *.jpg *.jpeg *.png 2>/dev/null; do
  if [ -f "$img" ]; then
    filename="${img%.*}"
    
    # Convert to WebP with quality 85 (good balance of quality/size)
    cwebp -q 85 "$img" -o "${filename}.webp" 2>/dev/null
    
    if [ $? -eq 0 ]; then
      count=$((count + 1))
      echo "✓ Converted: $img → ${filename}.webp"
    fi
  fi
done

echo ""
echo "Conversion complete: $count images converted to WebP"
echo ""
echo "File sizes comparison:"
du -sh . 2>/dev/null
echo ""
echo "WebP files created:"
ls -lh *.webp 2>/dev/null | wc -l
