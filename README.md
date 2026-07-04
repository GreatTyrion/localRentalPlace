# 🏠 St. John's Rentals — Rental Explorer

A modern web scraper **and** interactive Rental Explorer for rental properties in
St. John's, Newfoundland, using Kijiji.ca.

The scraper collects listings and renders them into a single, self-contained
`index.html` — a polished single-page app with an interactive map, filterable/sortable
listing cards, and a market-analytics header. It's hosted on **GitHub Pages**.

## ✨ Features

- **Modern Scraping**: Uses JSON-LD structured data for reliable extraction
- **Anti-Bot Protection**: Bypasses modern website protection measures
- **Rich Data**: Extracts prices, addresses, bedrooms, bathrooms, amenities
- **Rental Explorer UI** (`index.html`): split-view interactive map + listing cards
  with live search, price/bedroom/bathroom/pets filters, sorting, and card ↔ map pin
  syncing. Light **and** dark themes (with toggle), fully responsive
- **Market Analysis**: In-app price-distribution and bedroom charts plus a terminal
  summary report
- **Self-contained & deploy-ready**: one `index.html`, no build step — data embedded,
  libraries from CDNs; drops straight into GitHub Pages

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
# Scrape fresh listings and rebuild the Rental Explorer (index.html)
uv run python main.py

# Rebuild the dashboard from the existing CSV — no scraping, no network.
# Use this to iterate on the design or to redeploy without re-scraping.
uv run python main.py --from-csv
```

### Preview locally

```bash
python -m http.server        # then open http://localhost:8000/index.html
```

Serving over HTTP (rather than opening the file directly) mirrors the GitHub Pages
project subpath, so relative behaviour matches production.

## 📊 Output Files

- `index.html` - **The Rental Explorer app** (interactive map + filterable listing
  cards + analytics). This is the page served on GitHub Pages
- `kijiji_rentals.csv` - Structured data of all rental listings

## 🚀 Deployment (GitHub Pages)

The site is served from the `master` branch root, with `index.html` as the entry page.
To deploy an update:

```bash
uv run python main.py --from-csv   # regenerate index.html (or run a full scrape)
git add index.html                 # + any code/template/CSV changes
git commit -m "Update rentals"
git push origin master             # GitHub Pages redeploys automatically
```

The dashboard is fully self-contained (inline CSS/JS, embedded data, CDN libraries),
so there is **no build step** and no broken asset paths under the project subpath.

## 📁 Project Structure

```text
├── main.py                    # Main entry point (scrape, or --from-csv rebuild)
├── scraper.py                 # Core scraper + dashboard renderer
├── templates/
│   └── dashboard.html.j2      # Rental Explorer app (Jinja2 template)
├── index.html                 # Generated app (served on GitHub Pages)
├── kijiji_rentals.csv         # Generated listing data
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
