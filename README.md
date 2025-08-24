# Armitage Market Mirror

## Overview
Armitage Market Mirror is a Python-based web scraper that collects product listings for Armitage products from eBay and Amazon, performs fuzzy matching to identify relevant listings, stores data in a SQLite database, and exports results to a CSV file. It analyzes pricing, keywords, and listing trends to provide market insights, such as average prices, low-price listings, and popular keywords. The tool is designed for market intelligence, helping users identify pricing and listing gaps for competitive positioning.

- **Developer**: Encrypter15 (encrypter15@gmail.com)
- **License**: MIT
- **Version**: 1.0.4
- **Last Updated**: August 24, 2025

## Features
- **Web Scraping**: Scrapes product listings from eBay and Amazon using `requests` and `BeautifulSoup`.
- **Fuzzy Matching**: Uses `fuzzywuzzy` to filter relevant listings based on product title similarity (match score >70).
- **SQLite Storage**: Stores listings in a persistent SQLite database (`armitage_listings.db`).
- **CSV Export**: Exports all database records to a CSV file (`armitage_listings_export.csv`).
- **Analysis**: Generates insights on average/lowest prices, listings below a user-defined threshold, and top keywords.
- **Anti-Bot**: Rotates multiple user-agents to reduce the risk of being blocked by target websites.

## Requirements
- Python 3.8+
- Libraries listed in `requirements.txt` (see [Installation](#installation))

## Installation
1. **Clone the Repository** (if applicable):
   ```bash
   git clone <repository-url>
   cd armitage-market-mirror
Create a Virtual Environment (recommended):
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install Dependencies:
pip install -r requirements.txt
Usage
Run the Script:
python armitage_market_mirror.py
Provide Inputs:
Enter a product search term (e.g., Armitage brass tap).
Enter a price threshold for alerts (e.g., 50 for $50). If invalid, defaults to $50.
Output:
The script scrapes eBay and Amazon, stores data in armitage_listings.db, and generates insights in the console.
A CSV file (armitage_listings_export.csv) is created with all database records.
Example console output:
Enter product search term (e.g., Armitage brass tap): Armitage brass tap
Enter price threshold for alerts (e.g., 50 for $50): 50

Scraping for: Armitage brass tap (Price threshold: $50)

=== Insights ===
Average price: $65.43
Lowest price: $45.99
Found 2 listings below $50:
- eBay: Armitage Vintage Brass Faucet ($45.99)
- Amazon: Armitage Brass Tap Refurbished ($48.50)
Top keywords: brass, tap, armitage, vintage, faucet
Exported database to armitage_listings_export.csv
Database
File: armitage_listings.db
Schema:
id: Auto-incrementing primary key
site: Source site (e.g., eBay, Amazon)
title: Listing title
price: Listing price (float)
seller: Seller name
link: Listing URL
match_score: Fuzzy match score (integer)
search_term: User-provided search term
timestamp: Scrape timestamp (ISO format)
Management: The database persists data across runs. To reset, delete armitage_listings.db.
Notes
Anti-Bot: The script rotates user-agents to avoid detection, but Amazon/eBay may still block requests. For production, consider:
Proxy rotation
APIs (e.g., Amazon Affiliate API)
selenium or playwright for dynamic pages
Extensibility:
Add more sites (e.g., Etsy, Wayfair) by extending the SITES dictionary and adding scraper functions.
Integrate a UI (e.g., Streamlit) for visualization.
Enhance with selenium for JavaScript-rendered pages.
Further Enhancements:
Add filters for CSV export (e.g., by date or site).
Implement alerts via email (smtplib) or SMS (twilio).
Limitations:
Scraping may fail if sites change their HTML structure.
Rate limiting or CAPTCHAs may require additional handling.
Development
Changelog (from armitage_market_mirror.py):
1.0.4 (2025-08-24): Added multiple user-agents with random selection for anti-bot resilience. Updated developer email.
1.0.3 (2025-08-24): Added notes on anti-bot, extensibility, database management, and enhancements.
1.0.2 (2025-08-24): Added user inputs, SQLite database, and CSV export.
1.0.1 (2025-08-23): Added fuzzy matching and keyword analysis.
1.0.0 (2025-08-22): Initial version with basic scraping.
License
This project is licensed under the MIT License. See the LICENSE file for details.
Contact
For questions or contributions, contact Encrypter15 at encrypter15@gmail.com.
