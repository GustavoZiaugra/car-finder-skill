#!/usr/bin/env python3
"""
OLX scraper for car listings.
Usage: python3 scrape_olx.py --query "Honda Civic 2020" --price-max 80000
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

# OLX search URL pattern
BASE_URL = "https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/{state}"

def build_url(params):
    """Build OLX search URL based on parameters."""
    state = params.get('state', 'sp')
    url = BASE_URL.format(state=state)

    query = params.get('query', '')
    if query:
        url += f"/q-{query.replace(' ', '-')}"

    query_params = []
    if params.get('price_min'):
        query_params.append(f"pe={params['price_min']}")
    if params.get('price_max'):
        query_params.append(f"ps={params['price_max']}")
    if params.get('year_min'):
        query_params.append(f"re={params['year_min']}")
    if params.get('year_max'):
        query_params.append(f"rs={params['year_max']}")

    if query_params:
        url += "?" + "&".join(query_params)

    return url

def scrape_listings(url, max_pages=5):
    """Scrape car listings from OLX."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    listings = []

    for page in range(1, max_pages + 1):
        page_url = f"{url}&page={page}" if '?' in url else f"{url}?page={page}"

        try:
            response = requests.get(page_url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find listing cards - update selector based on actual OLX HTML
            cards = soup.find_all('li', {'data-cy': 'l-card'})

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
        # Extract data from card - adjust selectors based on actual OLX HTML
        title_elem = card.find('h6')
        price_elem = card.find('span', {'data-testid': 'ad-price'})
        link_elem = card.find('a')

        if not title_elem or not price_elem or not link_elem:
            return None

        title = title_elem.get_text(strip=True)
        price_text = price_elem.get_text(strip=True)
        link = link_elem.get('href', '')

        # Parse price (e.g., "R$ 45.000" -> 45000)
        price_match = re.search(r'[\d.]+', price_text.replace('.', '').replace(',', ''))
        price = int(price_match.group()) if price_match else 0

        # Extract details from title or card
        # Example: "Honda Civic Touring 2021 Automatico"
        year_match = re.search(r'\b(20\d{2})\b', title)
        year = int(year_match.group()) if year_match else 0

        # Try to get location
        location_elem = card.find('span', {'data-testid': 'location-date'})
        location = location_elem.get_text(strip=True) if location_elem else ''

        return {
            'source': 'olx',
            'title': title,
            'price': price,
            'price_text': price_text,
            'year': year,
            'url': link if link.startswith('http') else f"https://www.olx.com.br{link}",
            'location': location,
            'scraped_at': datetime.utcnow().isoformat()
        }

    except Exception as e:
        print(f"Error parsing card: {e}")
        return None

def save_listings(listings, output_file='olx_listings.json'):
    """Save listings to JSON file."""
    with open(output_file, 'w') as f:
        json.dump(listings, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(listings)} listings to {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Scrape OLX car listings')
    parser.add_argument('--query', help='Search query (e.g., "Honda Civic 2020")')
    parser.add_argument('--year-min', type=int, help='Minimum year')
    parser.add_argument('--year-max', type=int, help='Maximum year')
    parser.add_argument('--price-min', type=int, help='Minimum price')
    parser.add_argument('--price-max', type=int, help='Maximum price')
    parser.add_argument('--state', default='sp', help='State abbreviation (default: sp)')
    parser.add_argument('--pages', type=int, default=5, help='Maximum pages to scrape (default: 5)')
    parser.add_argument('--output', default='olx_listings.json', help='Output file (default: olx_listings.json)')

    args = parser.parse_args()

    params = {
        'query': args.query,
        'year_min': args.year_min,
        'year_max': args.year_max,
        'price_min': args.price_min,
        'price_max': args.price_max,
        'state': args.state
    }

    url = build_url(params)
    print(f"Scraping: {url}")

    listings = scrape_listings(url, max_pages=args.pages)
    save_listings(listings, args.output)

if __name__ == '__main__':
    main()
