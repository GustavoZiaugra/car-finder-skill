# Car Finder Usage Guide

This skill helps you find cars on Webmotors and OLX based on your criteria, with daily notifications for new listings.

## Configuration

Create a configuration file `car_finder_config.json` with your search criteria:

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

## Parameters

### Webmotors-specific:
- `brand`: Car brand (e.g., Honda, Volkswagen, Toyota)
- `model`: Car model (e.g., Civic, Golf, Corolla)
- `year_min`: Minimum manufacturing year
- `year_max`: Maximum manufacturing year
- `price_min`: Minimum price in BRL
- `price_max`: Maximum price in BRL
- `km_max`: Maximum kilometers
- `state`: State abbreviation (sp, rj, mg, etc.)
- `pages`: Maximum pages to scrape (default: 5)

### OLX-specific:
- `query`: Free-text search query (e.g., "Honda Civic 2020")
- `year_min`: Minimum year
- `year_max`: Maximum year
- `price_min`: Minimum price
- `price_max`: Maximum price
- `state`: State abbreviation
- `pages`: Maximum pages to scrape

## Workflow

### Daily Check (Recommended)

1. **Scrape current listings:**
   ```bash
   python3 scripts/scrape_webmotors.py --config car_finder_config.json --output webmotors_new.json
   python3 scripts/scrape_olx.py --config car_finder_config.json --output olx_new.json
   ```

2. **Compare with previous results:**
   ```bash
   python3 scripts/compare_listings.py --new webmotors_new.json --old webmotors_previous.json --output webmotors_merged.json --summary
   python3 scripts/compare_listings.py --new olx_new.json --old olx_previous.json --output olx_merged.json --summary
   ```

3. **Notify if new listings found**

4. **Archive current results for next day:**
   ```bash
   mv webmotors_new.json webmotors_previous.json
   mv olx_new.json olx_previous.json
   ```

### Manual Search

To do a one-time search:

```bash
# Webmotors
python3 scripts/scrape_webmotors.py --brand Honda --model Civic --year-min 2018 --price-max 90000 --state sp --output civic_results.json

# OLX
python3 scripts/scrape_olx.py --query "Honda Civic 2020" --price-max 90000 --state sp --output civic_results.json
```

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

## Common Issues

### Empty Results

- Check if parameters are correct (brand/model spelling)
- Try increasing `pages` parameter
- Verify the site hasn't changed its HTML structure

### Changes in Site Structure

If scraping stops working, the site may have changed its HTML. You'll need to:
1. Inspect the site's HTML
2. Update the CSS selectors in the scraping script
3. Test with a small page count first

### Rate Limiting

If you get blocked:
- Increase delays between requests
- Reduce the `pages` parameter
- Use different User-Agent strings
- Consider scraping less frequently (e.g., every 2 days instead of daily)

## Automation with Cron

To run daily checks automatically, set up a cron job:

```bash
# Run at 8 AM daily
0 8 * * * cd /path/to/car-finder && /usr/bin/python3 scripts/scrape_webmotors.py --config config.json && /usr/bin/python3 scripts/scrape_olx.py --config config.json && /usr/bin/python3 scripts/compare_listings.py --new webmotors_new.json --old webmotors_previous.json --summary | /usr/bin/telegram-send
```

Replace `/usr/bin/telegram-send` with your preferred notification method.
