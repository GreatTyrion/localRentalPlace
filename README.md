# 🏠 Kijiji Rental Scraper

A modern web scraper for rental properties in St. John's, Newfoundland, using Kijiji.ca.

## ✨ Features

- **Modern Scraping**: Uses JSON-LD structured data for reliable extraction
- **Anti-Bot Protection**: Bypasses modern website protection measures
- **Rich Data**: Extracts prices, addresses, bedrooms, bathrooms, amenities
- **Beautiful Output**: Creates HTML list view and CSV data files
- **Market Analysis**: Provides price distribution and property statistics

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd localRentalPlace

# Install dependencies
uv add beautifulsoup4 folium geopy pandas requests
```

### Usage

```bash
# Run the scraper
uv run python main.py

# Or run directly
uv run python scraper.py
```

## 📊 Output Files

- `kijiji_rentals.csv` - Structured data of all rental listings
- `kijiji_rental_list.html` - Beautiful HTML list view
- `kijiji_rental_map.html` - Interactive map (when coordinates available)

## 📁 Project Structure

```text
├── main.py                    # Main entry point
├── scraper.py                 # Core scraper implementation
├── pyproject.toml            # Project configuration
├── requirements.txt          # Dependencies
├── archive/                  # Original 2020 code
├── development/              # Development and test files
└── playground/               # Jupyter notebooks
```

## 🔧 Configuration

The scraper is configured to scrape:

- St. John's apartments and condos
- General rental properties
- Up to 2 pages per category (configurable)

## 📈 Sample Results

- **162 listings** found in recent test
- **Price range**: $24 - $100,000
- **Average price**: $3,162
- **Property types**: 1-4 bedrooms, various amenities

## 🛠️ Development

Development files and test scripts are in the `development/` folder:

- `modern_kijiji_scraper.py` - Full-featured version with mapping
- `simple_kijiji_scraper.py` - Simplified version for testing
- Various test and analysis scripts

## 📝 License

This project is for educational and personal use. Please respect Kijiji's terms of service.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!
