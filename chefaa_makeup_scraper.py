#!/usr/bin/env python3
"""
Comprehensive makeup products scraper for Chefaa.com
Systematically collects all makeup products from main category and subcategories
"""

import json
import time
import requests
from urllib.parse import urljoin, urlparse, parse_qs
import re
from datetime import datetime

class ChefaaMakeupScraper:
    def __init__(self):
        self.base_url = "https://chefaa.com"
        self.arabic_base = "/eg-ar/now"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ar,en-US;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.all_products = []
        self.category_summary = {
            'main_category': 'المكياج و الاكسسوارات (Makeup & Accessories)',
            'total_products': 0,
            'pages_scraped': 0,
            'subcategories_found': [],
            'brands_found': set(),
            'price_range': {'min': None, 'max': None}
        }
    
    def extract_price(self, price_text):
        """Extract numeric price from Arabic text"""
        if not price_text:
            return None
        
        # Extract numbers from price text
        numbers = re.findall(r'[\d,]+', str(price_text))
        if numbers:
            # Remove commas and convert to int
            price = int(numbers[0].replace(',', ''))
            return price
        return None
    
    def clean_arabic_text(self, text):
        """Clean and normalize Arabic text"""
        if not text:
            return ""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', str(text).strip())
        return text
    
    def parse_product_data(self, product_element):
        """Extract product information from a product element"""
        try:
            # Extract product name
            name_elem = product_element.find('a', href=True)
            if not name_elem:
                return None
            
            product_name = self.clean_arabic_text(name_elem.get_text())
            product_url = urljoin(self.base_url, name_elem.get('href'))
            
            # Extract price
            price_elem = product_element.find('a', href=product_url)
            price_text = ""
            if price_elem:
                price_text = price_elem.get_text().strip()
            
            price = self.extract_price(price_text)
            
            # Determine brand from name or URL
            brand = "Unknown"
            if "إيفا" in product_name or "Eva" in product_name:
                brand = "Eva"
            elif "لونا" in product_name or "Luna" in product_name:
                brand = "Luna"
            elif "يولو" in product_name or "Yolo" in product_name:
                brand = "Yolo"
            elif "نيل" in product_name or "Nail" in product_name:
                brand = "Nail 15"
            elif "شان" in product_name or "Shaan" in product_name:
                brand = "Shaan"
            elif "كابيكسي" in product_name or "Capixy" in product_name:
                brand = "Capixy"
            elif "كافلون" in product_name or "Caflon" in product_name:
                brand = "Caflon"
            elif "في" in product_name or "Fe" in product_name:
                brand = "Fe"
            
            # Extract specifications
            specifications = {}
            
            # Volume/size
            volume_match = re.search(r'(\d+)[ملجم]*', product_name)
            if volume_match:
                specifications['volume'] = volume_match.group(0)
            
            # Additional features
            if "خالي من عطر" in product_name:
                specifications['feature'] = "Fragrance-free"
            if "للبشرة المعرضة لحب الشباب" in product_name:
                specifications['skin_type'] = "Acne-prone skin"
            if "للعناية" in product_name:
                specifications['category'] = "Care product"
            
            # Extract description (simplified)
            description = product_name
            
            product_data = {
                'product_name': product_name,
                'description': description,
                'price': price,
                'price_text': price_text,
                'brand': brand,
                'product_url': product_url,
                'rating': None,  # Not visible in main listing
                'stock_status': 'In Stock',  # Assuming all listed products are in stock
                'specifications': specifications,
                'extracted_at': datetime.now().isoformat()
            }
            
            return product_data
            
        except Exception as e:
            print(f"Error parsing product: {e}")
            return None
    
    def scrape_page(self, url, page_name=""):
        """Scrape a single page for products"""
        print(f"Scraping {page_name}: {url}")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find product elements - adjust selector based on actual HTML structure
            products = []
            product_links = soup.find_all('a', href=re.compile(r'/nowProduct/'))
            
            for link in product_links:
                # Find parent container that likely contains product info
                product_container = link.find_parent()
                while product_container and not self.is_product_container(product_container):
                    product_container = product_container.find_parent()
                
                if product_container:
                    product_data = self.parse_product_data(product_container)
                    if product_data:
                        products.append(product_data)
            
            print(f"Found {len(products)} products on this page")
            return products
            
        except Exception as e:
            print(f"Error scraping page {url}: {e}")
            return []
    
    def is_product_container(self, element):
        """Check if element is likely a product container"""
        # Look for common product indicators
        text = element.get_text().lower()
        if any(indicator in text for indicator in ['جنيه', 'price', 'add to cart', 'اضف']):
            return True
        return False
    
    def scrape_main_category(self):
        """Scrape all pages of the main makeup category"""
        print("=== Scraping Main Makeup Category ===")
        
        base_url = f"{self.base_url}{self.arabic_base}/category/makeup-accessories"
        
        # Scrape page 1 (already extracted, but including for completeness)
        for page in range(1, 9):  # 8 pages total
            if page == 1:
                url = base_url
            else:
                url = f"{base_url}?page={page}"
            
            products = self.scrape_page(url, f"Main Category Page {page}")
            self.all_products.extend(products)
            self.category_summary['pages_scraped'] += 1
            
            # Small delay to be respectful
            time.sleep(1)
    
    def scrape_subcategory(self, subcategory_name, subcategory_url):
        """Scrape a specific subcategory"""
        print(f"\n=== Scraping Subcategory: {subcategory_name} ===")
        
        full_url = f"{self.base_url}{self.arabic_base}{subcategory_url}"
        products = self.scrape_page(full_url, subcategory_name)
        
        # Mark products with subcategory
        for product in products:
            product['subcategory'] = subcategory_name
        
        return products
    
    def run_complete_scrape(self):
        """Run the complete scraping process"""
        print("Starting comprehensive makeup products scraping...")
        
        # Scrape main category
        self.scrape_main_category()
        
        # Define subcategories
        subcategories = [
            ("الوجه (Face)", "/category/makeup-accessories/makeup-face"),
            ("العيون (Eyes)", "/category/makeup-accessories/makeup-eyes"),
            ("الرموش (Eyelashes)", "/category/makeup-accessories/makeup-eyelashes"),
            ("الشفاه (Lips)", "/category/makeup-accessories/makeup-lips"),
            ("الاظافر (Nails)", "/category/makeup-accessories/makeup-nails")
        ]
        
        # Scrape each subcategory
        for subcat_name, subcat_url in subcategories:
            subcat_products = self.scrape_subcategory(subcat_name, subcat_url)
            self.all_products.extend(subcat_products)
            self.category_summary['subcategories_found'].append(subcat_name)
        
        # Update summary statistics
        self.category_summary['total_products'] = len(self.all_products)
        
        # Extract brands
        for product in self.all_products:
            if product['brand'] != "Unknown":
                self.category_summary['brands_found'].add(product['brand'])
        
        # Calculate price range
        prices = [p['price'] for p in self.all_products if p['price']]
        if prices:
            self.category_summary['price_range']['min'] = min(prices)
            self.category_summary['price_range']['max'] = max(prices)
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive report"""
        report = {
            'summary': {
                **self.category_summary,
                'brands_found': list(self.category_summary['brands_found']),
                'extraction_timestamp': datetime.now().isoformat(),
                'scraping_method': 'Automated extraction from Chefaa.com'
            },
            'products': self.all_products,
            'subcategory_breakdown': {},
            'brand_breakdown': {},
            'price_analysis': {}
        }
        
        # Subcategory breakdown
        subcats = {}
        for product in self.all_products:
            subcat = product.get('subcategory', 'Main Category')
            if subcat not in subcats:
                subcats[subcat] = []
            subcats[subcat].append(product)
        
        for subcat, products in subcats.items():
            report['subcategory_breakdown'][subcat] = {
                'count': len(products),
                'products': products
            }
        
        # Brand breakdown
        brands = {}
        for product in self.all_products:
            brand = product['brand']
            if brand not in brands:
                brands[brand] = []
            brands[brand].append(product)
        
        for brand, products in brands.items():
            report['brand_breakdown'][brand] = {
                'count': len(products),
                'products': products
            }
        
        return report
    
    def save_report(self, filename="chefaa_makeup_complete_report.json"):
        """Save the complete report to file"""
        report = self.run_complete_scrape()
        
        filepath = f"/workspace/data/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n=== COMPLETE SCRAPING REPORT ===")
        print(f"Total Products Found: {report['summary']['total_products']}")
        print(f"Pages Scraped: {report['summary']['pages_scraped']}")
        print(f"Subcategories: {len(report['summary']['subcategories_found'])}")
        print(f"Unique Brands: {len(report['summary']['brands_found'])}")
        print(f"Price Range: {report['summary']['price_range']['min']} - {report['summary']['price_range']['max']} EGP")
        print(f"Report saved to: {filepath}")
        
        return filepath

if __name__ == "__main__":
    scraper = ChefaaMakeupScraper()
    scraper.save_report()