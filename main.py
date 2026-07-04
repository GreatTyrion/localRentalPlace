#!/usr/bin/env python3
"""
Kijiji Rental Scraper - Main Entry Point
"""

import sys

from scraper import KijijiScraperFinal


def build_from_csv():
    """Regenerate the Rental Explorer dashboard from the existing CSV.

    No network access or geocoding is performed -- this simply re-renders
    index.html from kijiji_rentals.csv. Handy for iterating on the design
    and for redeploying to GitHub Pages without re-scraping.
    """
    print("🏠 Rebuilding Rental Explorer from kijiji_rentals.csv")
    print("-" * 50)
    scraper = KijijiScraperFinal()
    scraper.build_dashboard_from_csv()
    print("\n✅ Dashboard rebuilt: index.html")
    print("🌐 Open index.html in your browser, or commit & push to deploy.")


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

        # Build the Rental Explorer dashboard (index.html)
        scraper.create_map(listings)

        print("\n✅ Scraping completed successfully!")
        print("📁 Files created:")
        print("   - kijiji_rentals.csv (listing data)")
        print("   - index.html (Rental Explorer dashboard)")
        print("\n🌐 Open index.html in your browser to view the results!")
    else:
        print("❌ No listings found. Check your internet connection and try again.")


if __name__ == "__main__":
    if "--from-csv" in sys.argv[1:]:
        build_from_csv()
    else:
        main()
