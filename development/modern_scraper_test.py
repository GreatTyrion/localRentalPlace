#!/usr/bin/env python3
"""
Modern web scraper test for Kijiji with improved anti-bot detection handling
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urljoin, urlparse
import json

class ModernKijijiScraper:
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        
    def setup_session(self):
        """Setup session with realistic browser headers"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        })
        
    def get_page(self, url, retries=3):
        """Get page content with retry logic"""
        for attempt in range(retries):
            try:
                # Random delay between requests
                time.sleep(random.uniform(2, 5))
                
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 200:
                    return response.content
                elif response.status_code == 403:
                    print(f"Access forbidden (403) for {url}")
                    return None
                elif response.status_code == 429:
                    print(f"Rate limited (429) for {url}, waiting longer...")
                    time.sleep(random.uniform(10, 20))
                    continue
                else:
                    print(f"HTTP {response.status_code} for {url}")
                    
            except requests.exceptions.RequestException as e:
                print(f"Request error (attempt {attempt + 1}): {e}")
                if attempt < retries - 1:
                    time.sleep(random.uniform(5, 10))
                    
        return None
        
    def test_kijiji_urls(self):
        """Test various Kijiji URL patterns"""
        test_urls = [
            # Current possible URLs
            "https://www.kijiji.ca/b-apartments-condos/st-johns/c37l1700113",
            "https://www.kijiji.ca/b-apartments-condos/st-johns/c37l1700113?ad=offering",
            "https://www.kijiji.ca/b-apartments-condos/st-johns/c37l1700113?ad=offering&sort=dateDesc",
            "https://www.kijiji.ca/b-for-rent/st-johns/c30349001l1700113",
            "https://www.kijiji.ca/b-for-rent/st-johns/c30349001l1700113?ad=offering",
            
            # Try with different location codes
            "https://www.kijiji.ca/b-apartments-condos/newfoundland/c37l9003",
            "https://www.kijiji.ca/b-apartments-condos/newfoundland/c37l9003?ad=offering",
        ]
        
        print("Testing Kijiji URLs with modern scraper...")
        print("=" * 60)
        
        working_urls = []
        
        for i, url in enumerate(test_urls, 1):
            print(f"\n{i}. Testing: {url}")
            
            content = self.get_page(url)
            if content:
                soup = BeautifulSoup(content, "html.parser")
                
                # Check if we got a valid page
                title = soup.find('title')
                if title:
                    print(f"   Page title: {title.get_text().strip()}")
                
                # Look for various listing indicators
                indicators = {
                    'search-item': soup.find_all('div', class_=lambda x: x and 'search-item' in x),
                    'listing': soup.find_all('div', class_=lambda x: x and 'listing' in x),
                    'ad': soup.find_all('div', class_=lambda x: x and 'ad' in x),
                    'item': soup.find_all('div', class_=lambda x: x and 'item' in x),
                    'article': soup.find_all('article'),
                    'data-testid': soup.find_all(attrs={'data-testid': True}),
                }
                
                found_any = False
                for name, elements in indicators.items():
                    if elements:
                        print(f"   ✓ Found {len(elements)} {name} elements")
                        found_any = True
                
                if found_any:
                    working_urls.append(url)
                    # Save sample HTML
                    with open(f"kijiji_working_{i}.html", "w", encoding="utf-8") as f:
                        f.write(soup.prettify())
                    print(f"   ✓ Saved sample to kijiji_working_{i}.html")
                else:
                    print(f"   ✗ No listing elements found")
                    
                # Check for common elements
                price_elements = soup.find_all(string=lambda text: text and '$' in text and any(char.isdigit() for char in text))
                print(f"   - Price elements found: {len(price_elements)}")
                
            else:
                print(f"   ✗ Failed to get content")
        
        return working_urls
        
    def analyze_listing_structure(self, listing_url):
        """Analyze the structure of a specific listing"""
        print(f"\nAnalyzing listing structure: {listing_url}")
        
        content = self.get_page(listing_url)
        if not content:
            return None
            
        soup = BeautifulSoup(content, "html.parser")
        
        # Look for common listing elements
        structure = {
            'title': self.find_title(soup),
            'price': self.find_price(soup),
            'address': self.find_address(soup),
            'description': self.find_description(soup),
            'coordinates': self.find_coordinates(soup),
            'attributes': self.find_attributes(soup),
        }
        
        print("Listing structure analysis:")
        for key, value in structure.items():
            if value:
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: Not found")
                
        return structure
        
    def find_title(self, soup):
        """Find listing title"""
        selectors = [
            'h1[class*="title"]',
            'h1[class*="heading"]',
            'h1',
            '[data-testid*="title"]',
            '.title',
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
        return None
        
    def find_price(self, soup):
        """Find listing price"""
        # Look for price in various formats
        price_patterns = [
            r'\$[\d,]+',
            r'CAD\s*\$[\d,]+',
            r'\$\s*[\d,]+',
        ]
        
        import re
        text = soup.get_text()
        for pattern in price_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        return None
        
    def find_address(self, soup):
        """Find listing address"""
        selectors = [
            '[class*="address"]',
            '[data-testid*="address"]',
            'span[class*="location"]',
            '.address',
            '.location',
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
        return None
        
    def find_description(self, soup):
        """Find listing description"""
        selectors = [
            '[class*="description"]',
            '[data-testid*="description"]',
            '.description',
            'div[class*="content"]',
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()[:200] + "..." if len(element.get_text()) > 200 else element.get_text().strip()
        return None
        
    def find_coordinates(self, soup):
        """Find latitude and longitude"""
        # Look for meta tags
        lat_meta = soup.find('meta', {'property': 'og:latitude'})
        lng_meta = soup.find('meta', {'property': 'og:longitude'})
        
        if lat_meta and lng_meta:
            try:
                lat = float(lat_meta.get('content'))
                lng = float(lng_meta.get('content'))
                return (lat, lng)
            except (ValueError, TypeError):
                pass
                
        # Look for JSON-LD structured data
        json_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                if 'geo' in data:
                    geo = data['geo']
                    if 'latitude' in geo and 'longitude' in geo:
                        return (float(geo['latitude']), float(geo['longitude']))
            except (json.JSONDecodeError, KeyError, ValueError):
                continue
                
        return None
        
    def find_attributes(self, soup):
        """Find property attributes"""
        attributes = {}
        
        # Look for definition lists
        dts = soup.find_all('dt')
        dds = soup.find_all('dd')
        
        for dt, dd in zip(dts, dds):
            key = dt.get_text().strip()
            value = dd.get_text().strip()
            if key and value:
                attributes[key] = value
                
        return attributes

def main():
    scraper = ModernKijijiScraper()
    
    # Test URLs
    working_urls = scraper.test_kijiji_urls()
    
    if working_urls:
        print(f"\n✓ Found {len(working_urls)} working URLs:")
        for url in working_urls:
            print(f"  - {url}")
            
        # Try to analyze a listing if we found working URLs
        # This would require finding a specific listing URL from the search results
        print("\nNote: To analyze specific listings, we would need to extract listing URLs from the search results first.")
    else:
        print("\n✗ No working URLs found. Kijiji may have strong anti-bot protection.")
        print("Consider using:")
        print("1. Selenium with a real browser")
        print("2. Proxy rotation")
        print("3. Kijiji's official API if available")
        print("4. Alternative data sources")

if __name__ == "__main__":
    main()
