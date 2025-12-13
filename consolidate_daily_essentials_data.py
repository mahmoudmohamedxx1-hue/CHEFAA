#!/usr/bin/env python3
"""
Daily Essentials Data Consolidation Script
Consolidates all extracted product data from multiple sources and removes duplicates.
"""

import json
import re
from typing import Dict, List, Any, Set
from pathlib import Path
import hashlib

class DataConsolidator:
    def __init__(self):
        self.products = []
        self.seen_urls = set()  # Track unique product URLs to avoid duplicates
        self.product_counter = 1
        
    def load_phase1_data(self, file_path: str) -> List[Dict]:
        """Load data from the phase1 comprehensive file (pages 1-3)"""
        products = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if 'products' in data:
                for product in data['products']:
                    # Standardize the data structure
                    standardized_product = {
                        'product_id': self.product_counter,
                        'page_number': product.get('page_number', 1),
                        'product_name_arabic': self._clean_text(product.get('arabic_name', '')),
                        'product_name_english': self._clean_text(product.get('english_name', '')),
                        'description': self._clean_text(product.get('description', '')),
                        'price_egp': self._extract_price(product.get('price', '')),
                        'currency': 'EGP',
                        'brand': self._clean_text(product.get('brand', '')),
                        'stock_status': self._standardize_stock_status(product.get('stock_status', '')),
                        'specifications': self._clean_text(product.get('specifications', '')),
                        'product_url': self._clean_url(product.get('product_url', '')),
                        'category': self._clean_text(product.get('category', 'Daily Essentials')),
                        'source_file': 'phase1_comprehensive'
                    }
                    
                    # Only add if URL is unique
                    if standardized_product['product_url'] not in self.seen_urls:
                        standardized_product['product_id'] = self.product_counter
                        products.append(standardized_product)
                        self.seen_urls.add(standardized_product['product_url'])
                        self.product_counter += 1
                        
        except Exception as e:
            print(f"Error loading phase1 data: {e}")
            
        return products
    
    def load_page_products(self, file_path: str, page_number: int) -> List[Dict]:
        """Load data from individual page product files"""
        products = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract JSON from the content (files have format markers)
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                data = json.loads(json_str)
                
                if 'products' in data:
                    for product in data['products']:
                        # Standardize the data structure
                        standardized_product = {
                            'product_id': self.product_counter,
                            'page_number': page_number,
                            'product_name_arabic': self._clean_text(product.get('product_name_arabic', '')),
                            'product_name_english': self._clean_text(product.get('product_name_english', '')),
                            'description': '',
                            'price_egp': self._extract_price(product.get('price_egp', product.get('price', ''))),
                            'currency': product.get('currency', 'EGP'),
                            'brand': self._clean_text(product.get('brand', '')),
                            'stock_status': self._standardize_stock_status(product.get('stock_status', '')),
                            'specifications': self._format_specifications(product.get('specifications', {})),
                            'product_url': self._clean_url(product.get('product_url', '')),
                            'category': self._clean_text(product.get('category', 'Daily Essentials')),
                            'source_file': f'page_{page_number}'
                        }
                        
                        # Only add if URL is unique
                        if standardized_product['product_url'] not in self.seen_urls:
                            standardized_product['product_id'] = self.product_counter
                            products.append(standardized_product)
                            self.seen_urls.add(standardized_product['product_url'])
                            self.product_counter += 1
                            
        except Exception as e:
            print(f"Error loading page {page_number} data: {e}")
            
        return products
    
    def _clean_text(self, text: str) -> str:
        """Clean and standardize text content"""
        if not text:
            return ""
        # Remove ellipsis and clean up
        text = re.sub(r'\.{3,}.*$', '', text)
        return text.strip()
    
    def _clean_url(self, url: str) -> str:
        """Clean and standardize URLs"""
        if not url:
            return ""
        # Ensure HTTPS and remove any query parameters
        url = re.sub(r'\?.*$', '', url)
        if url.startswith('http:'):
            url = url.replace('http:', 'https:', 1)
        return url
    
    def _extract_price(self, price_str: str) -> float:
        """Extract numeric price from price string"""
        if not price_str:
            return 0.0
            
        # Remove currency symbols and extract numbers
        price_clean = re.sub(r'[^\d.,]', '', str(price_str))
        if price_clean:
            try:
                # Handle both comma and dot decimal separators
                price_clean = price_clean.replace(',', '.')
                return float(price_clean)
            except ValueError:
                return 0.0
        return 0.0
    
    def _standardize_stock_status(self, status: str) -> str:
        """Standardize stock status terms"""
        if not status:
            return "Unknown"
        
        status_lower = status.lower()
        if 'in stock' in status_lower or 'available' in status_lower:
            return "In Stock"
        elif 'out of stock' in status_lower or 'unavailable' in status_lower:
            return "Out of Stock"
        else:
            return "Unknown"
    
    def _format_specifications(self, specs) -> str:
        """Format specifications from dict or string"""
        if isinstance(specs, dict):
            return ', '.join([f"{k}: {v}" for k, v in specs.items()])
        elif isinstance(specs, list):
            return ', '.join(specs)
        else:
            return str(specs) if specs else ""
    
    def consolidate_all_data(self):
        """Consolidate all available data sources"""
        print("Starting data consolidation...")
        
        # Load phase1 data (pages 1-3)
        print("Loading phase1 comprehensive data...")
        phase1_products = self.load_phase1_data('/workspace/chefaa_daily_essentials_phase1_comprehensive_updated.json')
        self.products.extend(phase1_products)
        print(f"Added {len(phase1_products)} products from phase1 (pages 1-3)")
        
        # Load individual page data
        page_files = {
            1: '/workspace/browser/extracted_content/chefaa_daily_essentials_products.json',
            39: '/workspace/browser/extracted_content/chefaa_daily_essentials_page_39_products.json',
            43: '/workspace/browser/extracted_content/chefaa_daily_essentials_page43_products.json'
        }
        
        for page_num, file_path in page_files.items():
            if Path(file_path).exists():
                print(f"Loading page {page_num} data...")
                page_products = self.load_page_products(file_path, page_num)
                # Remove duplicates that might already exist
                new_products = [p for p in page_products if p['product_url'] not in self.seen_urls]
                self.products.extend(new_products)
                # Update seen URLs
                for p in new_products:
                    self.seen_urls.add(p['product_url'])
                print(f"Added {len(new_products)} unique products from page {page_num}")
            else:
                print(f"File not found: {file_path}")
        
        print(f"Total consolidated products: {len(self.products)}")
        
        # Update product IDs sequentially
        for i, product in enumerate(self.products, 1):
            product['product_id'] = i
    
    def generate_summary_stats(self) -> Dict[str, Any]:
        """Generate summary statistics of the consolidated data"""
        if not self.products:
            return {}
        
        # Count by page
        page_counts = {}
        brand_counts = {}
        category_counts = {}
        price_range = {'min': float('inf'), 'max': 0, 'sum': 0}
        
        for product in self.products:
            # Page counts
            page_num = product.get('page_number', 'Unknown')
            page_counts[page_num] = page_counts.get(page_num, 0) + 1
            
            # Brand counts
            brand = product.get('brand', 'Unknown')
            if brand:
                brand_counts[brand] = brand_counts.get(brand, 0) + 1
            
            # Category counts
            category = product.get('category', 'Unknown')
            category_counts[category] = category_counts.get(category, 0) + 1
            
            # Price statistics
            price = product.get('price_egp', 0)
            if isinstance(price, (int, float)) and price > 0:
                price_range['min'] = min(price_range['min'], price)
                price_range['max'] = max(price_range['max'], price)
                price_range['sum'] += price
        
        avg_price = price_range['sum'] / len([p for p in self.products if p.get('price_egp', 0) > 0])
        
        return {
            'total_products': len(self.products),
            'pages_covered': len(page_counts),
            'page_distribution': page_counts,
            'top_brands': dict(sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            'category_distribution': category_counts,
            'price_statistics': {
                'min_price': price_range['min'] if price_range['min'] != float('inf') else 0,
                'max_price': price_range['max'],
                'average_price': round(avg_price, 2)
            },
            'extraction_coverage': f"{len(page_counts)} pages covered from target range"
        }
    
    def save_consolidated_data(self, output_path: str):
        """Save the consolidated data to JSON file"""
        if not self.products:
            print("No products to save!")
            return
        
        # Generate metadata and summary
        metadata = {
            'source': 'Chefaa.com Daily Essentials Category',
            'extraction_date': '2025-11-01',
            'base_url': 'https://chefaa.com/eg-ar/now/category/daily-essentials',
            'total_pages_target': 62,
            'total_unique_products_extracted': len(self.products),
            'currency': 'Egyptian Pounds (EGP)',
            'language': 'Arabic/English',
            'data_sources': ['phase1_comprehensive', 'browser_extraction_pages'],
            'consolidation_date': '2025-11-01',
            'notes': 'Consolidated from multiple extraction sessions. Some pages may not have been successfully extracted.'
        }
        
        summary_stats = self.generate_summary_stats()
        
        consolidated_data = {
            'metadata': metadata,
            'summary_statistics': summary_stats,
            'products': self.products
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(consolidated_data, f, ensure_ascii=False, indent=2)
            print(f"Consolidated data saved to: {output_path}")
            print(f"Total unique products: {len(self.products)}")
        except Exception as e:
            print(f"Error saving data: {e}")

def main():
    consolidator = DataConsolidator()
    consolidator.consolidate_all_data()
    consolidator.save_consolidated_data('/workspace/data/daily_essentials_products.json')

if __name__ == "__main__":
    main()
