# armitage_market_mirror.py
# Developer: Encrypter15 (encrypter15@gmail.com)
# License: MIT
# Description: Scrapes eBay and Amazon for Armitage product listings, performs fuzzy matching, stores data in SQLite, and exports to CSV. Analyzes pricing, keywords, and listing trends.
# Version: 1.0.4
# Recent Changes:
# - 1.0.4 (2025-08-24): Added multiple user-agents with random selection for anti-bot resilience.
# - 1.0.3 (2025-08-24): Updated development notes to include anti-bot measures, extensibility options (additional sites, Selenium, Streamlit UI), database management instructions, and potential enhancements (export filters, email/SMS alerts).
# - 1.0.2 (2025-08-24): Added user inputs for search term and price threshold, integrated SQLite database for persistent storage, and implemented CSV export function. Enhanced error handling for invalid inputs.
# - 1.0.1 (2025-08-23): Added fuzzy matching for product titles using fuzzywuzzy, improved price parsing, and included basic keyword analysis in insights.
# - 1.0.0 (2025-08-22): Initial version with eBay and Amazon scraping using requests and BeautifulSoup, with pandas for data handling and basic price comparison.
# Notes:
# - Anti-Bot: Amazon and eBay may block requests. Consider proxies or APIs for production use.
# - Extensibility: Add more sites, enhance with Selenium for dynamic pages, or integrate a UI (e.g., Streamlit).
# - Database Management: The SQLite database persists data across runs. To reset, delete armitage_listings.db.
# - Further Enhancements: Add filters for exporting specific data (e.g., by date or site) or implement alerts via email/SMS.

import requests
from bs4 import BeautifulSoup
import pandas as pd
from fuzzywuzzy import fuzz
import re
from urllib.parse import quote
import sqlite3
from datetime import datetime
import random

# Configuration
SITES = {
    "eBay": "https://www.ebay.com/sch/i.html?_nkw={}",
    "Amazon": "https://www.amazon.com/s?k={}"
}

# List of user-agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Mobile/15E148 Safari/604.1"
]

# Initialize SQLite database
def init_db(db_name="armitage_listings.db"):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site TEXT,
            title TEXT,
            price REAL,
            seller TEXT,
            link TEXT,
            match_score INTEGER,
            search_term TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    return conn

# Function to clean text
def clean_text(text):
    return re.sub(r'\s+', ' ', text.strip()) if text else ''

# Scrape eBay listings
def scrape_ebay(search_term):
    url = SITES["eBay"].format(quote(search_term))
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        listings = []

        for item in soup.select('.s-item'):
            title = clean_text(item.select_one('.s-item__title')?.text)
            price = clean_text(item.select_one('.s-item__price')?.text)
            link = item.select_one('.s-item__link')?.get('href')
            seller = clean_text(item.select_one('.s-item__seller-info-text')?.text)
            
            if title and price:
                price_val = float(re.search(r'[\d.]+', price.replace('$', ''))?.group() or 0)
                listings.append({
                    'site': 'eBay',
                    'title': title,
                    'price': price_val,
                    'seller': seller,
                    'link': link,
                    'match_score': fuzz.ratio(title.lower(), search_term.lower()),
                    'search_term': search_term,
                    'timestamp': datetime.now().isoformat()
                })
        return listings
    except Exception as e:
        print(f"eBay scrape error: {e}")
        return []

# Scrape Amazon listings
def scrape_amazon(search_term):
    url = SITES["Amazon"].format(quote(search_term))
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        listings = []

        for item in soup.select('.s-result-item'):
            title = clean_text(item.select_one('h2 a span')?.text)
            price = clean_text(item.select_one('.a-price .a-offscreen')?.text)
            link = item.select_one('h2 a')?.get('href')
            seller = clean_text(item.select_one('.a-size-base')?.text or 'Amazon')

            if title and price:
                price_val = float(re.search(r'[\d.]+', price.replace('$', ''))?.group() or 0)
                listings.append({
                    'site': 'Amazon',
                    'title': title,
                    'price': price_val,
                    'seller': seller,
                    'link': f"https://www.amazon.com{link}" if link else '',
                    'match_score': fuzz.ratio(title.lower(), search_term.lower()),
                    'search_term': search_term,
                    'timestamp': datetime.now().isoformat()
                })
        return listings
    except Exception as e:
        print(f"Amazon scrape error: {e}")
        return []

# Store listings in SQLite
def store_listings(conn, listings):
    c = conn.cursor()
    for listing in listings:
        c.execute('''
            INSERT INTO listings (site, title, price, seller, link, match_score, search_term, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            listing['site'],
            listing['title'],
            listing['price'],
            listing['seller'],
            listing['link'],
            listing['match_score'],
            listing['search_term'],
            listing['timestamp']
        ))
    conn.commit()

# Export database to CSV
def export_to_csv(conn, filename="armitage_listings_export.csv"):
    query = "SELECT * FROM listings"
    df = pd.read_sql_query(query, conn)
    df.to_csv(filename, index=False)
    print(f"Exported database to {filename}")

# Compare and analyze listings
def analyze_listings(listings, search_term, price_threshold):
    df = pd.DataFrame(listings)
    if df.empty:
        return None, []

    # Filter by match score (>70 for relevance)
    df = df[df['match_score'] > 70].sort_values(by='price')
    
    # Generate insights
    insights = []
    if not df.empty:
        avg_price = df['price'].mean()
        min_price = df['price'].min()
        low_price_listings = df[df['price'] < price_threshold]
        
        insights.append(f"Average price: ${avg_price:.2f}")
        insights.append(f"Lowest price: ${min_price:.2f}")
        if not low_price_listings.empty:
            insights.append(f"Found {len(low_price_listings)} listings below ${price_threshold}:")
            for _, row in low_price_listings.iterrows():
                insights.append(f"- {row['site']}: {row['title']} (${row['price']:.2f})")
        
        # Keyword analysis
        common_keywords = pd.Series(' '.join(df['title']).lower().split()).value_counts().head(5)
        insights.append(f"Top keywords: {', '.join(common_keywords.index)}")
    
    return df, insights

# Main function
def main():
    # Get user inputs
    search_term = input("Enter product search term (e.g., Armitage brass tap): ").strip()
    try:
        price_threshold = float(input("Enter price threshold for alerts (e.g., 50 for $50): "))
    except ValueError:
        print("Invalid price threshold. Using default: $50")
        price_threshold = 50

    print(f"\nScraping for: {search_term} (Price threshold: ${price_threshold})")
    
    # Initialize database
    conn = init_db()
    
    # Scrape from each site
    all_listings = []
    all_listings.extend(scrape_ebay(search_term))
    all_listings.extend(scrape_amazon(search_term))
    
    # Store in database
    if all_listings:
        store_listings(conn, all_listings)
    
    # Analyze and generate insights
    df, insights = analyze_listings(all_listings, search_term, price_threshold)
    
    if df is not None:
        print("\n=== Insights ===")
        for insight in insights:
            print(insight)
    else:
        print("No relevant listings found.")
    
    # Export to CSV
    export_to_csv(conn)
    
    # Close database connection
    conn.close()

if __name__ == "__main__":
    main()
