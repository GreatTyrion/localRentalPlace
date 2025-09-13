#!/usr/bin/env python3
"""
Test script to inspect current Kijiji website structure
"""

import requests
from bs4 import BeautifulSoup
import time
from get_kijiji_content import simple_get

def test_kijiji_urls():
    """Test different possible Kijiji URLs for St. John's rentals"""
    
    # Original URL from the code
    original_url = "https://www.kijiji.ca/b-for-rent/st-johns/c30349001l1700113?ad=offering"
    
    # Possible new URLs based on current Kijiji structure
    test_urls = [
        original_url,
        "https://www.kijiji.ca/b-apartments-condos/st-johns/c37l1700113",
        "https://www.kijiji.ca/b-apartments-condos/st-johns/c37l1700113?ad=offering",
        "https://www.kijiji.ca/b-for-rent/st-johns/c30349001l1700113",
        "https://www.kijiji.ca/b-apartments-condos/st-johns/c37l1700113?ad=offering&sort=dateDesc",
    ]
    
    print("Testing Kijiji URLs...")
    print("=" * 50)
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{i}. Testing URL: {url}")
        try:
            content = simple_get(url)
            if content:
                soup = BeautifulSoup(content, "html.parser")
                
                # Look for common listing containers
                possible_containers = [
                    "div[class*='search-item']",
                    "div[class*='listing']", 
                    "div[class*='ad']",
                    "div[class*='item']",
                    "article",
                    "[data-testid*='listing']",
                    "[data-testid*='ad']"
                ]
                
                found_containers = []
                for selector in possible_containers:
                    elements = soup.select(selector)
                    if elements:
                        found_containers.append(f"{selector}: {len(elements)} found")
                
                if found_containers:
                    print(f"   ✓ SUCCESS: Found {len(soup.find_all('div'))} divs total")
                    for container in found_containers:
                        print(f"   - {container}")
                else:
                    print(f"   ✗ No listing containers found")
                    
                # Check for common elements
                title_elements = soup.find_all(['h1', 'h2', 'h3', 'h4'], string=lambda text: text and any(word in text.lower() for word in ['rent', 'apartment', 'condo', 'house']))
                price_elements = soup.find_all(string=lambda text: text and '$' in text)
                
                print(f"   - Potential titles: {len(title_elements)}")
                print(f"   - Price elements: {len(price_elements)}")
                
                # Save a sample of the HTML for inspection
                with open(f"kijiji_sample_{i}.html", "w", encoding="utf-8") as f:
                    f.write(soup.prettify())
                print(f"   - Saved sample HTML to kijiji_sample_{i}.html")
                
            else:
                print(f"   ✗ FAILED: No content received")
                
        except Exception as e:
            print(f"   ✗ ERROR: {str(e)}")
        
        time.sleep(2)  # Be respectful with requests

def inspect_specific_listing():
    """Try to find a specific listing to inspect its structure"""
    print("\n" + "=" * 50)
    print("Inspecting specific listing structure...")
    
    # Try to get a listing page directly
    test_listing_urls = [
        "https://www.kijiji.ca/v-apartments-condos/st-johns/sample-listing/1234567890",
    ]
    
    # For now, let's just check what we can find on the main page
    main_url = "https://www.kijiji.ca/b-apartments-condos/st-johns/c37l1700113"
    content = simple_get(main_url)
    
    if content:
        soup = BeautifulSoup(content, "html.parser")
        
        # Look for links to individual listings
        links = soup.find_all('a', href=True)
        listing_links = [link for link in links if '/v-' in link.get('href', '')]
        
        print(f"Found {len(listing_links)} potential listing links")
        
        if listing_links:
            # Test the first listing link
            first_link = listing_links[0]
            listing_url = "https://www.kijiji.ca" + first_link['href']
            print(f"Testing listing: {listing_url}")
            
            listing_content = simple_get(listing_url)
            if listing_content:
                listing_soup = BeautifulSoup(listing_content, "html.parser")
                
                # Look for common elements in listing pages
                title = listing_soup.find(['h1', 'h2'], class_=lambda x: x and any(word in x.lower() for word in ['title', 'heading']))
                price = listing_soup.find(string=lambda text: text and '$' in text)
                address = listing_soup.find(['span', 'div'], class_=lambda x: x and 'address' in x.lower())
                
                print(f"Title element: {title}")
                print(f"Price element: {price}")
                print(f"Address element: {address}")
                
                # Save the listing HTML
                with open("listing_sample.html", "w", encoding="utf-8") as f:
                    f.write(listing_soup.prettify())
                print("Saved listing sample to listing_sample.html")

if __name__ == "__main__":
    test_kijiji_urls()
    inspect_specific_listing()
