#!/usr/bin/env python3
"""
Modern Kijiji scraper v2.0 - Complete solution with mapping
Updated for 2024 Kijiji structure using JSON-LD data
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import re
from geopy.geocoders import ArcGIS

class KijijiScraperV2:
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        self.geocoder = ArcGIS()
        
    def setup_session(self):
        """Setup session with realistic browser headers"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
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
            
    def geocode_address(self, address):
        """Geocode address using ArcGIS"""
        try:
            location = self.geocoder.geocode(address)
            if location:
                return location.latitude, location.longitude
        except Exception as e:
            print(f"Geocoding failed for {address}: {e}")
        return None, None
        
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
        
        # Process listings - geocode addresses without coordinates
        processed_listings = []
        for i, listing in enumerate(all_listings):
            print(f"Processing listing {i+1}/{len(all_listings)}: {listing['title'][:50]}...")
            
            # Geocode if no coordinates
            if not listing['latitude'] or not listing['longitude']:
                lat, lng = self.geocode_address(listing['address'])
                if lat and lng:
                    listing['latitude'] = lat
                    listing['longitude'] = lng
                    
            processed_listings.append(listing)
            time.sleep(random.uniform(1, 2))  # Be respectful to geocoding service
            
        return processed_listings
        
    def create_map(self, listings, output_file="kijiji_rental_map.html"):
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
        
    def generate_summary_report(self, listings):
        """Generate a summary report of the scraped data"""
        if not listings:
            return
            
        print("\n" + "="*60)
        print("KIJIJI RENTAL SCRAPING SUMMARY REPORT")
        print("="*60)
        
        # Basic stats
        total_listings = len(listings)
        listings_with_coords = len([l for l in listings if l['latitude'] and l['longitude']])
        
        print(f"Total listings found: {total_listings}")
        print(f"Listings with coordinates: {listings_with_coords}")
        print(f"Geocoding success rate: {(listings_with_coords/total_listings)*100:.1f}%")
        
        # Price analysis
        prices = []
        for listing in listings:
            try:
                price_str = listing['price'].replace('$', '').replace(',', '')
                price = float(price_str)
                prices.append(price)
            except:
                continue
                
        if prices:
            print(f"\nPrice Analysis:")
            print(f"  Average price: ${sum(prices)/len(prices):.0f}")
            print(f"  Minimum price: ${min(prices):.0f}")
            print(f"  Maximum price: ${max(prices):.0f}")
            
            # Price ranges
            under_800 = len([p for p in prices if p < 800])
            between_800_1200 = len([p for p in prices if 800 <= p < 1200])
            over_1200 = len([p for p in prices if p >= 1200])
            
            print(f"\nPrice Distribution:")
            print(f"  Under $800: {under_800} listings")
            print(f"  $800-$1200: {between_800_1200} listings")
            print(f"  Over $1200: {over_1200} listings")
        
        # Bedroom analysis
        bedrooms = {}
        for listing in listings:
            if 'Bedrooms' in listing['info']:
                try:
                    bed_info = listing['info'].split('Bedrooms: ')[1].split(' *** ')[0]
                    if bed_info in bedrooms:
                        bedrooms[bed_info] += 1
                    else:
                        bedrooms[bed_info] = 1
                except:
                    continue
                    
        if bedrooms:
            print(f"\nBedroom Distribution:")
            for beds, count in sorted(bedrooms.items()):
                print(f"  {beds} bedrooms: {count} listings")
        
        print("="*60)

def main():
    """Main function to run the scraper"""
    print("Kijiji Rental Scraper v2.0")
    print("Updated for 2024 Kijiji structure")
    print("-" * 40)
    
    scraper = KijijiScraperV2()
    
    # Scrape listings
    listings = scraper.scrape_kijiji_rentals(max_pages=3)
    
    if listings:
        # Generate summary report
        scraper.generate_summary_report(listings)
        
        # Save to CSV
        scraper.save_to_csv(listings)
        
        # Create map
        scraper.create_map(listings)
        
        print(f"\n✓ Scraping completed successfully!")
        print("Files created:")
        print("- kijiji_rentals.csv (listing data)")
        print("- kijiji_rental_map.html (interactive map)")
        print("\nOpen kijiji_rental_map.html in your browser to view the interactive map!")
    else:
        print("✗ No listings found. Check your internet connection and try again.")

if __name__ == "__main__":
    main()
