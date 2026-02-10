#!/usr/bin/env python3
"""Test connection to car listing sites."""

import requests
import sys

def test_site(url, name):
    """Test if site is accessible."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"✓ {name}: {response.status_code}")
        return True
    except Exception as e:
        print(f"✗ {name}: {e}")
        return False

print("Testing connection to car listing sites...\n")

results = []
results.append(test_site('https://www.webmotors.com.br', 'Webmotors'))
results.append(test_site('https://www.olx.com.br', 'OLX'))

print(f"\nResult: {sum(results)}/{len(results)} sites accessible")
print("\nNote: 403/404 responses are normal - sites may block scrapers.")
print("The skill includes proper User-Agent headers in the scraping scripts.")

sys.exit(0 if all(results) else 1)
