#!/usr/bin/env python3
"""
Modern Kijiji scraper using JSON-LD structured data and improved anti-bot handling
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime
from geopy.geocoders import ArcGIS
import folium
from folium.plugins import MarkerCluster
import pandas as pd
from queue import Queue
import threading
from urllib.parse import urljoin
import re

class ModernKijijiScraper:
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        self.data_queue = Queue(maxsize=0)
        
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
            
    def get_detailed_listing_info(self, listing_url):
        """Get additional details from individual listing page"""
        print(f"Getting detailed info for: {listing_url}")
        
        content = self.get_page(listing_url)
        if not content:
            return {}
            
        soup = BeautifulSoup(content, "html.parser")
        
        details = {}
        
        # Try to get coordinates from meta tags
        lat_meta = soup.find('meta', {'property': 'og:latitude'})
        lng_meta = soup.find('meta', {'property': 'og:longitude'})
        
        if lat_meta and lng_meta:
            try:
                details['latitude'] = float(lat_meta.get('content'))
                details['longitude'] = float(lng_meta.get('content'))
            except (ValueError, TypeError):
                pass
                
        # Try to get more detailed description
        description_selectors = [
            '[data-testid*="description"]',
            '.description',
            '[class*="description"]',
        ]
        
        for selector in description_selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem:
                details['description'] = desc_elem.get_text().strip()
                break
                
        return details
        
    def geocode_address(self, address):
        """Geocode address using ArcGIS"""
        try:
            geolocator = ArcGIS()
            location = geolocator.geocode(address)
            if location:
                return location.latitude, location.longitude
        except Exception as e:
            print(f"Geocoding failed for {address}: {e}")
        return None, None
        
    def scrape_kijiji_rentals(self, max_pages=5):
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
        
        # Process listings
        processed_listings = []
        for i, listing in enumerate(all_listings):
            print(f"Processing listing {i+1}/{len(all_listings)}: {listing['title'][:50]}...")
            
            # Get additional details if needed
            if not listing['latitude'] or not listing['longitude']:
                details = self.get_detailed_listing_info(listing['url'])
                if details.get('latitude') and details.get('longitude'):
                    listing['latitude'] = details['latitude']
                    listing['longitude'] = details['longitude']
                if details.get('description'):
                    listing['description'] = details['description']
                    
            # Geocode if still no coordinates
            if not listing['latitude'] or not listing['longitude']:
                lat, lng = self.geocode_address(listing['address'])
                if lat and lng:
                    listing['latitude'] = lat
                    listing['longitude'] = lng
                    
            processed_listings.append(listing)
            time.sleep(random.uniform(1, 3))  # Be respectful
            
        return processed_listings
        
    def create_map(self, listings, output_file="modern_rental_map.html"):
        """Create interactive map from listings"""
        print("Creating interactive map...")
        
        # Filter out listings without coordinates
        valid_listings = [l for l in listings if l['latitude'] and l['longitude']]
        print(f"Creating map with {len(valid_listings)} listings with coordinates")
        
        if not valid_listings:
            print("No listings with coordinates found!")
            return
            
        # Create map centered on St. John's
        map_center = [47.5669, -52.7067]
        m = folium.Map(location=map_center, zoom_start=13)
        
        # Add marker cluster
        marker_cluster = MarkerCluster().add_to(m)
        
        # Color function for price-based markers
        def get_marker_color(price):
            try:
                price_num = float(re.sub(r'[^\d.]', '', price))
                if price_num < 800:
                    return 'green'
                elif price_num < 1200:
                    return 'orange'
                else:
                    return 'red'
            except:
                return 'blue'
                
        # Add markers
        for listing in valid_listings:
            # Create popup content
            popup_html = f"""
            <div style="width: 300px;">
                <h3>{listing['title']}</h3>
                <p><strong>Price:</strong> {listing['price']}</p>
                <p><strong>Address:</strong> {listing['address']}</p>
                <p><strong>Info:</strong> {listing['info']}</p>
                <p><strong>Description:</strong> {listing['description'][:200]}...</p>
                <p><a href="{listing['url']}" target="_blank">View on Kijiji</a></p>
            </div>
            """
            
            folium.Marker(
                location=[listing['latitude'], listing['longitude']],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color=get_marker_color(listing['price']))
            ).add_to(marker_cluster)
            
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Save map
        m.save(output_file)
        print(f"Map saved as {output_file}")
        
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
    scraper = ModernKijijiScraper()
    
    # Scrape listings
    listings = scraper.scrape_kijiji_rentals(max_pages=3)
    
    if listings:
        # Save to CSV
        scraper.save_to_csv(listings)
        
        # Create map
        scraper.create_map(listings)
        
        print(f"\nScraping completed! Found {len(listings)} rental listings.")
        print("Files created:")
        print("- kijiji_rentals.csv (listing data)")
        print("- modern_rental_map.html (interactive map)")
    else:
        print("No listings found. Check your internet connection and try again.")

if __name__ == "__main__":
    main()
