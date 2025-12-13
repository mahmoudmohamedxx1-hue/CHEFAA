#!/usr/bin/env python3
"""
Improved Daily Essentials Data Consolidation Script
Handles embedded JSON, URL normalization, and better duplicate detection.
"""

import json
import re
from typing import Dict, List, Any, Set
from pathlib import Path
import hashlib

class ImprovedDataConsolidator:
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
                        'product_url': self._normalize_url(product.get('product_url', '')),
                        'category': self._clean_text(product.get('category', 'Daily Essentials')),
                        'subcategory': '',
                        'source_file': 'phase1_comprehensive'
                    }
                    
                    # Only add if URL is unique
                    if standardized_product['product_url'] not in self.seen_urls and standardized_product['product_url']:
                        standardized_product['product_id'] = self.product_counter
                        products.append(standardized_product)
                        self.seen_urls.add(standardized_product['product_url'])
                        self.product_counter += 1
                        
        except Exception as e:
            print(f"Error loading phase1 data: {e}")
            
        return products
    
    def load_embedded_json_page(self, file_path: str, page_number: int) -> List[Dict]:
        """Load data from files with embedded JSON (markdown-style)"""
        products = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract JSON from the content (files have format markers like ```json)
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
                            'price_egp': float(product.get('price_egp', 0)),
                            'currency': product.get('currency', 'EGP'),
                            'brand': self._clean_text(product.get('brand', '')),
                            'stock_status': self._standardize_stock_status(product.get('stock_status', '')),
                            'specifications': self._format_specifications(product.get('specifications', {})),
                            'product_url': self._normalize_url(product.get('product_url', '')),
                            'category': self._clean_text(product.get('category', 'Daily Essentials')),
                            'subcategory': self._extract_subcategory(product.get('category', '')),
                            'source_file': f'page_{page_number}'
                        }
                        
                        # Only add if URL is unique and valid
                        if (standardized_product['product_url'] not in self.seen_urls and 
                            standardized_product['product_url'] and
                            len(standardized_product['product_name_arabic']) > 5):  # Basic validation
                            
                            standardized_product['product_id'] = self.product_counter
                            products.append(standardized_product)
                            self.seen_urls.add(standardized_product['product_url'])
                            self.product_counter += 1
                            
        except Exception as e:
            print(f"Error loading embedded JSON from page {page_number}: {e}")
            
        return products
    
    def load_browser_extracted_data(self, file_path: str, page_number: int = 1) -> List[Dict]:
        """Load data from browser-extracted content files"""
        products = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract JSON from the content
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
                            'product_name_arabic': self._clean_text(product.get('arabic_name', product.get('product_name_arabic', ''))),
                            'product_name_english': self._clean_text(product.get('english_name', product.get('product_name_english', ''))),
                            'description': self._clean_text(product.get('description', '')),
                            'price_egp': self._extract_price_from_text(product.get('price', product.get('price_egp', ''))),
                            'currency': 'EGP',
                            'brand': self._clean_text(product.get('brand', '')),
                            'stock_status': self._standardize_stock_status(product.get('stock_status', '')),
                            'specifications': self._clean_text(product.get('specifications', '')),
                            'product_url': self._normalize_url(product.get('product_url', '')),
                            'category': 'Daily Essentials',
                            'subcategory': '',
                            'source_file': f'browser_page_{page_number}'
                        }
                        
                        # Only add if URL is unique and we have meaningful data
                        if (standardized_product['product_url'] not in self.seen_urls and 
                            standardized_product['product_url'] and
                            len(standardized_product['product_name_arabic']) > 5):
                            
                            standardized_product['product_id'] = self.product_counter
                            products.append(standardized_product)
                            self.seen_urls.add(standardized_product['product_url'])
                            self.product_counter += 1
                            
        except Exception as e:
            print(f"Error loading browser extracted data from page {page_number}: {e}")
            
        return products
    
    def _clean_text(self, text: str) -> str:
        """Clean and standardize text content"""
        if not text:
            return ""
        # Remove ellipsis and clean up
        text = re.sub(r'\.{3,}.*$', '', text)
        return text.strip()
    
    def _normalize_url(self, url: str) -> str:
        """Clean and standardize URLs"""
        if not url:
            return ""
        
        # Clean up the URL
        url = url.strip()
        
        # Remove :443 port from hostname
        url = re.sub(r':443', '', url)
        
        # Ensure HTTPS
        if url.startswith('http:'):
            url = url.replace('http:', 'https:', 1)
        elif not url.startswith('https:'):
            url = 'https://' + url.lstrip('/')
        
        # Remove query parameters for duplicate detection
        url = re.sub(r'\?.*$', '', url)
        
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
    
    def _extract_price_from_text(self, price_text: str) -> float:
        """Extract price from text that may contain currency symbols"""
        if not price_text:
            return 0.0
            
        # Look for number patterns
        price_match = re.search(r'(\d+(?:\.\d+)?)', str(price_text))
        if price_match:
            try:
                return float(price_match.group(1))
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
            return json.dumps(specs, ensure_ascii=False)
        elif isinstance(specs, list):
            return ', '.join(specs)
        else:
            return str(specs) if specs else ""
    
    def _extract_subcategory(self, category_text: str) -> str:
        """Extract subcategory from category text"""
        if not category_text:
            return ""
        
        # Look for common subcategory patterns
        if 'الحماية' in category_text:
            return 'Protection'
        elif 'الفم' in category_text or 'الأسنان' in category_text:
            return 'Oral Care'
        elif 'الجسم' in category_text or 'الاستحمام' in category_text:
            return 'Bath & Body Care'
        elif 'الرجالية' in category_text:
            return 'Men Care'
        elif 'النسائية' in category_text:
            return 'Feminine Care'
        elif 'الأعشاب' in category_text or 'الفيتامينات' in category_text:
            return 'Natural Herbs & Supplements'
        
        return ""
    
    def consolidate_all_data(self):
        """Consolidate all available data sources"""
        print("Starting improved data consolidation...")
        
        # Load phase1 data (pages 1-3)
        print("Loading phase1 comprehensive data...")
        phase1_products = self.load_phase1_data('/workspace/chefaa_daily_essentials_phase1_comprehensive_updated.json')
        self.products.extend(phase1_products)
        print(f"Added {len(phase1_products)} products from phase1 (pages 1-3)")
        
        # Load embedded JSON page data
        page_files = {
            39: '/workspace/browser/extracted_content/chefaa_daily_essentials_page_39_products.json',
            43: '/workspace/browser/extracted_content/chefaa_daily_essentials_page43_products.json'
        }
        
        for page_num, file_path in page_files.items():
            if Path(file_path).exists():
                print(f"Loading embedded JSON from page {page_num}...")
                page_products = self.load_embedded_json_page(file_path, page_num)
                self.products.extend(page_products)
                print(f"Added {len(page_products)} products from page {page_num}")
            else:
                print(f"File not found: {file_path}")
        
        # Load browser extracted data
        browser_files = {
            1: '/workspace/browser/extracted_content/chefaa_daily_essentials_products.json'
        }
        
        for page_num, file_path in browser_files.items():
            if Path(file_path).exists():
                print(f"Loading browser extracted data from page {page_num}...")
                browser_products = self.load_browser_extracted_data(file_path, page_num)
                self.products.extend(browser_products)
                print(f"Added {len(browser_products)} products from browser page {page_num}")
            else:
                print(f"File not found: {file_path}")
        
        print(f"Total consolidated products: {len(self.products)}")
        
        # Update product IDs sequentially
        for i, product in enumerate(self.products, 1):
            product['product_id'] = i
    
    def generate_detailed_stats(self) -> Dict[str, Any]:
        """Generate detailed statistics of the consolidated data"""
        if not self.products:
            return {}
        
        # Count by page
        page_counts = {}
        brand_counts = {}
        category_counts = {}
        subcategory_counts = {}
        price_range = {'min': float('inf'), 'max': 0, 'sum': 0, 'valid_prices': 0}
        stock_status_counts = {}
        source_file_counts = {}
        
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
            
            # Subcategory counts
            subcategory = product.get('subcategory', 'Unknown')
            if subcategory:
                subcategory_counts[subcategory] = subcategory_counts.get(subcategory, 0) + 1
            
            # Stock status counts
            stock_status = product.get('stock_status', 'Unknown')
            stock_status_counts[stock_status] = stock_status_counts.get(stock_status, 0) + 1
            
            # Source file counts
            source_file = product.get('source_file', 'Unknown')
            source_file_counts[source_file] = source_file_counts.get(source_file, 0) + 1
            
            # Price statistics
            price = product.get('price_egp', 0)
            if isinstance(price, (int, float)) and price > 0:
                price_range['min'] = min(price_range['min'], price)
                price_range['max'] = max(price_range['max'], price)
                price_range['sum'] += price
                price_range['valid_prices'] += 1
        
        avg_price = price_range['sum'] / price_range['valid_prices'] if price_range['valid_prices'] > 0 else 0
        
        return {
            'total_products': len(self.products),
            'pages_covered': len(page_counts),
            'page_distribution': dict(sorted(page_counts.items())),
            'top_brands': dict(sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)[:15]),
            'category_distribution': dict(sorted(category_counts.items())),
            'subcategory_distribution': dict(sorted(subcategory_counts.items())),
            'stock_status_distribution': dict(sorted(stock_status_counts.items())),
            'source_file_distribution': dict(sorted(source_file_counts.items())),
            'price_statistics': {
                'min_price': price_range['min'] if price_range['min'] != float('inf') else 0,
                'max_price': price_range['max'],
                'average_price': round(avg_price, 2),
                'valid_prices_count': price_range['valid_prices']
            },
            'extraction_coverage': f"{len(page_counts)} pages covered from target range",
            'data_quality': {
                'products_with_urls': len([p for p in self.products if p.get('product_url')]),
                'products_with_brands': len([p for p in self.products if p.get('brand')]),
                'products_with_prices': len([p for p in self.products if p.get('price_egp', 0) > 0]),
                'products_with_english_names': len([p for p in self.products if p.get('product_name_english')])
            }
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
            'data_sources': ['phase1_comprehensive_updated', 'browser_extraction_pages'],
            'consolidation_date': '2025-11-01',
            'notes': 'Consolidated from multiple extraction sessions. Some pages may not have been successfully extracted due to website navigation issues.',
            'known_limitations': [
                'Page 51 could not be accessed due to navigation redirects',
                'Not all 62 pages were successfully extracted',
                'Some pages returned raw JSON and required manual browser extraction'
            ]
        }
        
        detailed_stats = self.generate_detailed_stats()
        
        consolidated_data = {
            'metadata': metadata,
            'summary_statistics': detailed_stats,
            'products': self.products
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(consolidated_data, f, ensure_ascii=False, indent=2)
            print(f"Consolidated data saved to: {output_path}")
            print(f"Total unique products: {len(self.products)}")
            print(f"Pages covered: {len(detailed_stats['page_distribution'])}")
            print(f"Top 5 brands: {list(detailed_stats['top_brands'].keys())[:5]}")
        except Exception as e:
            print(f"Error saving data: {e}")

def main():
    consolidator = ImprovedDataConsolidator()
    consolidator.consolidate_all_data()
    consolidator.save_consolidated_data('/workspace/data/daily_essentials_products.json')

if __name__ == "__main__":
    main()
