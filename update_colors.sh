#!/bin/bash

# Update all brand-green references to brand-blue
find /workspace/chefaa-clone/src -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i 's/brand-green/brand-blue/g' {} \;

# Update accent-orange to accent-amber
find /workspace/chefaa-clone/src -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i 's/accent-orange/accent-amber/g' {} \;

# Update accent-blue-900 (footer background) to bg-gray-900 for professional look
find /workspace/chefaa-clone/src -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i 's/bg-accent-blue-900/bg-gray-900/g' {} \;

echo "Color scheme updated successfully!"
