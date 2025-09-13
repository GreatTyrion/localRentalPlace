#!/usr/bin/env python3
"""
Simplified Kijiji scraper using JSON-LD structured data
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime
import pandas as pd

class SimpleKijijiScraper:
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        
    def setup_session(self):
        """Setup session with realistic browser headers"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
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
        
    def extract_listings_from_search_page(self, url):
        """Extract listing data from search page using JSON-LD structured data"""
        print(f"Scraping search page: {url}")
        
        content = self.get_page(url)
        if not content:
            return []
            
        soup = BeautifulSoup(content, "html.parser")
        
        # Extract JSON-LD structured data
        json_scripts = soup.find_all('script', type='application/ld+json')
        listings = []
        
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and 'itemListElement' in data:
                    for item in data['itemListElement']:
                        if 'item' in item:
                            listing_data = self.extract_listing_from_json_ld(item['item'])
                            if listing_data:
                                listings.append(listing_data)
            except (json.JSONDecodeError, KeyError) as e:
                continue
                
        print(f"Found {len(listings)} listings from structured data")
        return listings
        
    def extract_listing_from_json_ld(self, item_data):
        """Extract listing information from JSON-LD data"""
        try:
            # Extract basic information
            title = item_data.get('name', 'No title')
            description = item_data.get('description', 'No description')
            url = item_data.get('url', '')
            
            # Extract price
            price = "Not available"
            if 'offers' in item_data and 'price' in item_data['offers']:
                price = f"${item_data['offers']['price']}"
                
            # Extract address
            address = item_data.get('address', 'No address')
            if isinstance(address, dict):
                address = address.get('streetAddress', 'No address')
                
            # Extract coordinates
            latitude = None
            longitude = None
            if 'geo' in item_data:
                geo = item_data['geo']
                latitude = geo.get('latitude')
                longitude = geo.get('longitude')
                
            # Extract property attributes
            attributes = {}
            if 'numberOfBedrooms' in item_data:
                attributes['Bedrooms'] = item_data['numberOfBedrooms']
            if 'numberOfBathroomsTotal' in item_data:
                attributes['Bathrooms'] = item_data['numberOfBathroomsTotal']
            if 'floorSize' in item_data and 'value' in item_data['floorSize']:
                attributes['Size (sq ft)'] = item_data['floorSize']['value']
            if 'petsAllowed' in item_data:
                attributes['Pets Allowed'] = 'Yes' if item_data['petsAllowed'] == 'true' else 'No'
            if 'leaseLength' in item_data:
                attributes['Lease Length'] = item_data['leaseLength']
                
            # Format attributes as string
            attr_string = " *** ".join([f"{k}: {v}" for k, v in attributes.items()])
            
            return {
                'title': title,
                'url': url,
                'address': address,
                'latitude': latitude,
                'longitude': longitude,
                'price': price,
                'info': attr_string,
                'description': description
            }
            
        except Exception as e:
            print(f"Error extracting listing data: {e}")
            return None
            
    def scrape_kijiji_rentals(self, max_pages=3):
        """Main scraping function"""
        print("Starting Kijiji rental scraping...")
        
        # Updated URLs that work
        base_urls = [
            "https://www.kijiji.ca/b-apartments-condos/st-johns/c37l1700113",
            "https://www.kijiji.ca/b-for-rent/st-johns/c30349001l1700113"
        ]
        
        all_listings = []
        
        for base_url in base_urls:
            print(f"\nScraping from: {base_url}")
            
            # Scrape first page
            listings = self.extract_listings_from_search_page(base_url)
            all_listings.extend(listings)
            
            # Scrape additional pages
            for page in range(2, max_pages + 1):
                page_url = f"{base_url}?ad=offering&sort=dateDesc&page={page}"
                page_listings = self.extract_listings_from_search_page(page_url)
                if not page_listings:  # No more listings
                    break
                all_listings.extend(page_listings)
                time.sleep(random.uniform(3, 6))  # Be respectful
                
        print(f"\nTotal listings found: {len(all_listings)}")
        return all_listings
        
    def save_to_csv(self, listings, output_file="kijiji_rentals.csv"):
        """Save listings to CSV file"""
        if not listings:
            print("No listings to save")
            return
            
        df = pd.DataFrame(listings)
        df = df.drop_duplicates(subset=['url'])  # Remove duplicates
        df.to_csv(output_file, index=False)
        print(f"Saved {len(df)} listings to {output_file}")

def main():
    """Main function to run the scraper"""
    scraper = SimpleKijijiScraper()
    
    # Scrape listings
    listings = scraper.scrape_kijiji_rentals(max_pages=2)
    
    if listings:
        # Save to CSV
        scraper.save_to_csv(listings)
        
        print(f"\nScraping completed! Found {len(listings)} rental listings.")
        print("Files created:")
        print("- kijiji_rentals.csv (listing data)")
        
        # Show sample of listings
        print("\nSample listings:")
        for i, listing in enumerate(listings[:5]):
            print(f"\n{i+1}. {listing['title']}")
            print(f"   Price: {listing['price']}")
            print(f"   Address: {listing['address']}")
            print(f"   Info: {listing['info']}")
    else:
        print("No listings found. Check your internet connection and try again.")

if __name__ == "__main__":
    main()
