#!/usr/bin/env python3
"""
Compare car listings to identify new ones.
Usage: python3 compare_listings.py --new webmotors_listings.json --old previous_listings.json
"""

import argparse
import json
import hashlib
import sys

def generate_listing_hash(listing):
    """Generate unique hash for a listing based on title, price, and URL."""
    key = f"{listing['title']}|{listing['price']}|{listing['url']}"
    return hashlib.md5(key.encode()).hexdigest()

def load_listings(filename):
    """Load listings from JSON file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def compare_listings(new_listings, old_listings):
    """Compare listings and return new ones."""
    old_hashes = {generate_listing_hash(l) for l in old_listings}

    new_items = []
    for listing in new_listings:
        listing_hash = generate_listing_hash(listing)
        if listing_hash not in old_hashes:
            listing['_is_new'] = True
            new_items.append(listing)
        else:
            listing['_is_new'] = False

    return new_items

def format_summary(new_listings):
    """Format a summary of new listings."""
    if not new_listings:
        return "Nenhum novo anúncio encontrado."

    summary = f"🚗 Encontrados {len(new_listings)} novos anúncios:\n\n"

    for listing in new_listings:
        summary += f"• {listing['title']}\n"
        summary += f"  💰 {listing['price_text']} - {listing.get('year', 'N/A')}\n"
        summary += f"  🔗 {listing['url']}\n"
        if listing.get('location'):
            summary += f"  📍 {listing['location']}\n"
        summary += f"  📱 {listing['source']}\n\n"

    return summary

def main():
    parser = argparse.ArgumentParser(description='Compare car listings')
    parser.add_argument('--new', required=True, help='New listings file')
    parser.add_argument('--old', help='Previous listings file (optional)')
    parser.add_argument('--output', help='Output file for merged listings')
    parser.add_argument('--summary', action='store_true', help='Print summary to stdout')

    args = parser.parse_args()

    # Load listings
    new_listings = load_listings(args.new)
    old_listings = load_listings(args.old) if args.old else []

    print(f"Loaded {len(new_listings)} new listings, {len(old_listings)} old listings")

    # Compare
    new_items = compare_listings(new_listings, old_listings)

    print(f"Found {len(new_items)} new listings")

    # Print summary
    if args.summary:
        print("\n" + format_summary(new_items))

    # Save merged listings if requested
    if args.output:
        # Merge old and new, marking which are new
        merged = old_listings + new_listings
        with open(args.output, 'w') as f:
            json.dump(merged, f, indent=2, ensure_ascii=False)
        print(f"Saved merged listings to {args.output}")

    return 0

if __name__ == '__main__':
    sys.exit(main())
