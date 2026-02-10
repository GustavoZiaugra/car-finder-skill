---
name: car-finder
description: Find and monitor car listings on Webmotors and OLX with configurable filters and daily notifications. Use when searching for used cars, tracking new listings, or automating car search workflows in the Brazilian market.
---

# Car Finder

## Overview

Automate car searches on Webmotors and OLX, compare daily results to identify new listings, and receive notifications when matching cars become available.

## Quick Start

1. **Create configuration** - Define your search criteria in a JSON config file
2. **Run initial scrape** - Gather current listings from both sites
3. **Set up daily checks** - Schedule automatic scraping and comparison
4. **Get notified** - Receive alerts when new cars match your criteria

## Workflow

### Step 1: Configure Search Criteria

Create `car_finder_config.json` with your parameters:

```json
{
  "brand": "Honda",
  "model": "Civic",
  "year_min": 2018,
  "year_max": 2022,
  "price_min": 50000,
  "price_max": 90000,
  "km_max": 50000,
  "state": "sp",
  "pages": 5
}
```

**Available parameters:**
- `brand`, `model`: Car make and model (Webmotors)
- `query`: Free-text search (OLX)
- `year_min`, `year_max`: Year range
- `price_min`, `price_max`: Price range in BRL
- `km_max`: Maximum kilometers
- `state`: Brazilian state abbreviation
- `pages`: Number of pages to scrape

### Step 2: Scrape Current Listings

Run both scrapers:

```bash
python3 scripts/scrape_webmotors.py --brand Honda --model Civic --year-min 2018 --price-max 90000 --state sp --output webmotors_new.json

python3 scripts/scrape_olx.py --query "Honda Civic 2020" --price-max 90000 --state sp --output olx_new.json
```

### Step 3: Compare and Identify New Listings

Compare today's results with previous data:

```bash
python3 scripts/compare_listings.py --new webmotors_new.json --old webmotors_previous.json --summary

python3 scripts/compare_listings.py --new olx_new.json --old olx_previous.json --summary
```

The `--summary` flag prints a human-readable list of new listings.

### Step 4: Set Up Daily Automation

Use cron or OpenClaw's cron system to run daily:

```bash
# Run every day at 8 AM
0 8 * * * cd /path/to/car-finder && python3 scripts/scrape_webmotors.py --config car_finder_config.json --output webmotors_new.json && python3 scripts/scrape_olx.py --config car_finder_config.json --output olx_new.json && python3 scripts/compare_listings.py --new webmotors_new.json --old webmotors_previous.json --summary | telegram-send && mv webmotors_new.json webmotors_previous.json
```

With OpenClaw, create a daily cron job that runs the scripts and sends Telegram notifications.

## Output Format

Each listing includes:

```json
{
  "source": "webmotors",
  "title": "Honda Civic Touring 2.0 16V Flex Aut. 2021",
  "price": 85000,
  "price_text": "R$ 85.000",
  "year": 2021,
  "url": "https://www.webmotors.com.br/carro/...",
  "location": "São Paulo - SP",
  "scraped_at": "2026-02-10T14:30:00.000Z"
}
```

## Troubleshooting

### 403 Forbidden Responses

**Current Status:** Webmotors and OLX block automated scraping with 403 responses. This is expected behavior due to anti-bot protections.

**See [references/limitations.md](references/limitations.md) for:**
- Detailed explanation of why scraping is blocked
- Official API alternatives
- Paid scraping service options
- Browser automation approaches

### Empty Results
- Verify parameter spelling and format
- Try increasing `pages` parameter
- Check if site HTML structure changed

### Site Changes
If scraping stops working (after overcoming 403):
1. Inspect the site's current HTML
2. Update CSS selectors in the appropriate scraping script
3. Test with small page count first

### Rate Limiting
If blocked (after overcoming 403):
- Add delays between requests
- Reduce `pages` parameter
- Rotate User-Agent strings
- Scrape less frequently

## Resources

### scripts/scrape_webmotors.py
Scrapes car listings from Webmotors based on filters.

**Usage:**
```bash
python3 scripts/scrape_webmotors.py --brand <brand> --model <model> --year-min <year> --year-max <year> --price-min <price> --price-max <price> --km-max <km> --state <state> --pages <n> --output <file>
```

### scripts/scrape_olx.py
Scrapes car listings from OLX based on search query and filters.

**Usage:**
```bash
python3 scripts/scrape_olx.py --query "<search>" --year-min <year> --year-max <year> --price-min <price> --price-max <price> --state <state> --pages <n> --output <file>
```

### scripts/compare_listings.py
Compares new and old listings to identify new items.

**Usage:**
```bash
python3 scripts/compare_listings.py --new <new_file> --old <old_file> --output <merged_file> --summary
```

### references/usage.md
Detailed documentation with examples, parameter descriptions, and automation tips. Load this for more comprehensive guidance.

## Dependencies

Install required packages:

```bash
pip install requests beautifulsoup4
```
