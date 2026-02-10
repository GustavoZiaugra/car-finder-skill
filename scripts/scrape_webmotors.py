#!/usr/bin/env python3
"""
Webmotors scraper for car listings.
Usage: python3 scrape_webmotors.py --model "Civic" --year-min 2015 --year-max 2020 --price-max 80000
"""

import argparse
import json
import re
import sys
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: Install required packages: pip install requests beautifulsoup4")
    sys.exit(1)

# Webmotors search URL pattern
BASE_URL = "https://www.webmotors.com.br/comprar/carros/estoque/{state}"

def build_url(params):
    """Build Webmotors search URL based on parameters."""
    state = params.get('state', 'sp')
    url = BASE_URL.format(state=state)

    # Add filters
    if params.get('brand'):
        url += f"/{params['brand']}"
    if params.get('model'):
        url += f"/{params['model']}"

    query_params = []
    if params.get('year_min'):
        query_params.append(f"anomin={params['year_min']}")
    if params.get('year_max'):
        query_params.append(f"anomax={params['year_max']}")
    if params.get('price_min'):
        query_params.append(f"precomin={params['price_min']}")
    if params.get('price_max'):
        query_params.append(f"precomax={params['price_max']}")
    if params.get('km_max'):
        query_params.append(f"quilotetagem={params['km_max']}")

    if query_params:
        url += "?" + "&".join(query_params)

    return url

def scrape_listings(url, max_pages=5):
    """Scrape car listings from Webmotors."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }

    session = requests.Session()
    session.headers.update(headers)

    listings = []

    for page in range(1, max_pages + 1):
        page_url = f"{url}&pagina={page}" if page > 1 else url

        try:
            response = session.get(page_url, timeout=15)
            print(f"Page {page}: Status {response.status_code}")
            
            if response.status_code == 403:
                print("Site is blocking scraping attempts. This is expected behavior.")
                print("For production use, consider:")
                print("  - Using official APIs if available")
                print("  - Rotating IP addresses")
                print("  - Using paid scraping services")
                return listings
            
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find listing cards - update selector based on actual Webmotors HTML
            cards = soup.find_all('div', class_='sc-2b2ad8e4-0')

            if not cards:
                break  # No more listings

            for card in cards:
                try:
                    listing = parse_listing(card)
                    if listing:
                        listings.append(listing)
                except Exception as e:
                    print(f"Error parsing listing: {e}")
                    continue

            print(f"Page {page}: Found {len(cards)} listings")

        except requests.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            continue

    return listings

def parse_listing(card):
    """Parse a single listing card."""
    try:
        # Extract data from card - adjust selectors based on actual Webmotors HTML
        title_elem = card.find(['h2', 'h3'], class_=re.compile('.*title.*'))
        price_elem = card.find(class_=re.compile('.*price.*'))
        link_elem = card.find('a')

        if not title_elem or not price_elem or not link_elem:
            return None

        title = title_elem.get_text(strip=True)
        price_text = price_elem.get_text(strip=True)
        link = link_elem.get('href', '')

        # Parse price (e.g., "R$ 45.000" -> 45000)
        price_match = re.search(r'[\d.]+', price_text.replace('.', '').replace(',', ''))
        price = int(price_match.group()) if price_match else 0

        # Extract details from title
        # Example: "Honda Civic Touring 2021 Automatico"
        year_match = re.search(r'\b(20\d{2})\b', title)
        year = int(year_match.group()) if year_match else 0

        return {
            'source': 'webmotors',
            'title': title,
            'price': price,
            'price_text': price_text,
            'year': year,
            'url': link if link.startswith('http') else f"https://www.webmotors.com.br{link}",
            'scraped_at': datetime.utcnow().isoformat()
        }

    except Exception as e:
        print(f"Error parsing card: {e}")
        return None

def save_listings(listings, output_file='webmotors_listings.json'):
    """Save listings to JSON file."""
    with open(output_file, 'w') as f:
        json.dump(listings, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(listings)} listings to {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Scrape Webmotors car listings')
    parser.add_argument('--brand', help='Car brand (e.g., Honda, Volkswagen)')
    parser.add_argument('--model', help='Car model (e.g., Civic, Golf)')
    parser.add_argument('--year-min', type=int, help='Minimum year')
    parser.add_argument('--year-max', type=int, help='Maximum year')
    parser.add_argument('--price-min', type=int, help='Minimum price')
    parser.add_argument('--price-max', type=int, help='Maximum price')
    parser.add_argument('--km-max', type=int, help='Maximum kilometers')
    parser.add_argument('--state', default='sp', help='State abbreviation (default: sp)')
    parser.add_argument('--pages', type=int, default=5, help='Maximum pages to scrape (default: 5)')
    parser.add_argument('--output', default='webmotors_listings.json', help='Output file (default: webmotors_listings.json)')

    args = parser.parse_args()

    params = {
        'brand': args.brand,
        'model': args.model,
        'year_min': args.year_min,
        'year_max': args.year_max,
        'price_min': args.price_min,
        'price_max': args.price_max,
        'km_max': args.km_max,
        'state': args.state
    }

    url = build_url(params)
    print(f"Scraping: {url}")

    listings = scrape_listings(url, max_pages=args.pages)
    save_listings(listings, args.output)

if __name__ == '__main__':
    main()
