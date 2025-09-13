#!/usr/bin/env python3
"""
Kijiji Rental Scraper - Main Entry Point
"""

from scraper import KijijiScraperFinal

def main():
    """Main function to run the Kijiji rental scraper"""
    print("🏠 Kijiji Rental Scraper")
    print("Scraping rental listings from St. John's, NL")
    print("-" * 50)
    
    scraper = KijijiScraperFinal()
    
    # Scrape listings
    listings = scraper.scrape_kijiji_rentals(max_pages=10)
    
    if listings:
        # Generate summary report
        scraper.generate_summary_report(listings)
        
        # Save to CSV
        scraper.save_to_csv(listings)
        
        # Create map or list view
        scraper.create_map(listings)
        
        print("\n✅ Scraping completed successfully!")
        print("📁 Files created:")
        print("   - kijiji_rentals.csv (listing data)")
        print("   - kijiji_rental_map.html (interactive map) OR kijiji_rental_list.html (list view)")
        print("\n🌐 Open the HTML file in your browser to view the results!")
    else:
        print("❌ No listings found. Check your internet connection and try again.")

if __name__ == "__main__":
    main()
