#!/usr/bin/env python3
"""
Simple test of the modern Kijiji scraper
"""

from modern_kijiji_scraper import ModernKijijiScraper

def test_scraper():
    scraper = ModernKijijiScraper()
    
    # Test with just one page
    print("Testing modern scraper with one page...")
    listings = scraper.extract_listings_from_search_page("https://www.kijiji.ca/b-apartments-condos/st-johns/c37l1700113")
    
    if listings:
        print(f"✓ Successfully extracted {len(listings)} listings")
        
        # Show first few listings
        for i, listing in enumerate(listings[:3]):
            print(f"\nListing {i+1}:")
            print(f"  Title: {listing['title']}")
            print(f"  Price: {listing['price']}")
            print(f"  Address: {listing['address']}")
            print(f"  URL: {listing['url']}")
            
        return True
    else:
        print("✗ No listings found")
        return False

if __name__ == "__main__":
    test_scraper()
