# Car Finder

**🚗 Find and monitor car listings on Webmotors and OLX with daily notifications**

This OpenClaw skill helps you track car listings on Brazilian marketplaces with configurable filters.

## Features

- 🔍 **Multi-site search** - Webmotors and OLX
- 🎛️ **Configurable filters** - Brand, model, year, price, kilometers
- 📬 **Daily notifications** - Get alerted to new listings
- 🔄 **Comparison tracking** - Identify new cars compared to previous search
- 🇧🇷 **Brazilian market focus** - Optimized for Brazilian buyers

## ⚠️ Important Limitation

**Webmotors and OLX currently block automated scraping** with HTTP 403 responses.

This is expected behavior due to anti-bot protections (Cloudflare, WAF, etc.).

### Workarounds

1. **Official site alerts** - Use built-in email alerts on Webmotors/OLX
2. **Paid scraping services** - Apify, ScrapeOps, ZenRows (~$50-200/mo)
3. **API access** - Contact platforms for commercial API access
4. **Browser automation** - Playwright/Selenium (more complex, still may be blocked)

### Current Skill Status

The scraping scripts are functional but **blocked by the sites**. The code structure is solid and can be used if:
- Sites relax their protections
- You use through a proxy/VPN service
- Sites provide compatible APIs

## Quick Start

```bash
# Webmotors search
python3 scripts/scrape_webmotors.py --brand Honda --model Civic --year-min 2018 --year-max 2022 --price-max 90000 --state sp --output civic_webmotors.json

# OLX search
python3 scripts/scrape_olx.py --query "Honda Civic 2020" --price-max 90000 --state sp --output civic_olx.json

# Compare listings
python3 scripts/compare_listings.py --new civic_new.json --old civic_previous.json --summary
```

## Installation

1. **Clone this repository:**
```bash
git clone https://github.com/GustavoZiaugra/car-finder-skill.git
cd car-finder-skill
```

2. **Install dependencies:**
```bash
pip install requests beautifulsoup4
```

3. **Load skill into OpenClaw:**
   - Open OpenClaw Control UI
   - Go to Skills → Import Skill
   - Select this directory

## Usage Examples

### Webmotors

```bash
# Honda Civic, 2018-2022, under R$90k, São Paulo
python3 scripts/scrape_webmotors.py --brand Honda --model Civic --year-min 2018 --year-max 2022 --price-max 90000 --state sp --pages 5 --output results.json

# Volkswagen Golf, any year, under R$60k, Minas Gerais
python3 scripts/scrape_webmotors.py --brand Volkswagen --model Golf --price-max 60000 --state mg --output golf.json
```

### OLX

```bash
# Free text search
python3 scripts/scrape_olx.py --query "Honda Civic 2020" --price-max 90000 --state sp --output results.json

# With year filter
python3 scripts/scrape_olx.py --query "Toyota Corolla" --year-min 2019 --year-max 2021 --state rj --output corolla.json
```

### Comparison

```bash
# Find new listings
python3 scripts/compare_listings.py --new today.json --old yesterday.json --summary --output merged.json

# Get summary of new items
python3 scripts/compare_listings.py --new today.json --old yesterday.json --summary
```

## Parameters

### Webmotors

| Parameter | Description | Example |
|-----------|-------------|----------|
| `--brand` | Car brand | `--brand Honda` |
| `--model` | Car model | `--model Civic` |
| `--year-min` | Minimum year | `--year-min 2018` |
| `--year-max` | Maximum year | `--year-max 2022` |
| `--price-min` | Minimum price (BRL) | `--price-min 50000` |
| `--price-max` | Maximum price (BRL) | `--price-max 90000` |
| `--km-max` | Maximum kilometers | `--km-max 50000` |
| `--state` | State abbreviation | `--state sp` |
| `--pages` | Max pages to scrape | `--pages 5` |
| `--output` | Output file | `--output results.json` |

### OLX

| Parameter | Description | Example |
|-----------|-------------|----------|
| `--query` | Search query | `--query "Honda Civic"` |
| `--year-min` | Minimum year | `--year-min 2019` |
| `--year-max` | Maximum year | `--year-max 2021` |
| `--price-min` | Minimum price (BRL) | `--price-min 40000` |
| `--price-max` | Maximum price (BRL) | `--price-max 80000` |
| `--state` | State abbreviation | `--state rj` |
| `--pages` | Max pages to scrape | `--pages 3` |
| `--output` | Output file | `--output results.json` |

### Comparison

| Parameter | Description | Example |
|-----------|-------------|----------|
| `--new` | New listings file | `--new today.json` |
| `--old` | Previous listings file | `--old yesterday.json` |
| `--output` | Merged output file | `--output merged.json` |
| `--summary` | Print human-readable summary | `--summary` |

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

## Daily Automation Workflow

Set up a daily check to find new listings:

```bash
# Cron job example
#!/bin/bash

# Directory
cd /path/to/car-finder

# Scrape today
python3 scripts/scrape_webmotors.py --brand Honda --model Civic --year-min 2018 --price-max 90000 --state sp --output webmotors_new.json
python3 scripts/scrape_olx.py --query "Honda Civic" --price-max 90000 --state sp --output olx_new.json

# Compare with yesterday
python3 scripts/compare_listings.py --new webmotors_new.json --old webmotors_previous.json --summary | telegram-send
python3 scripts/compare_listings.py --new olx_new.json --old olx_previous.json --summary | telegram-send

# Archive for tomorrow
mv webmotors_new.json webmotors_previous.json
mv olx_new.json olx_previous.json
```

## Troubleshooting

### 403 Forbidden Errors

**Current status:** Webmotors and OLX block scraping attempts.

**Why:** Anti-bot protections, Cloudflare/WAF, IP reputation checks.

**Solutions:**
1. Use official site alert systems (recommended)
2. Use paid scraping services (Apify, ScrapeOps)
3. Contact platforms for API access
4. Accept that automated scraping is blocked

### Empty Results

If you manage to get past 403:
- Verify parameter spelling and format
- Try increasing `--pages` parameter
- Check if site HTML structure changed

## Why This Skill Still Exists

Even though scraping is blocked, this skill demonstrates:

- ✅ Multi-source scraping architecture
- ✅ Listing comparison and deduplication
- ✅ Notification generation workflow
- ✅ Configurable filter system
- ✅ Clean, maintainable code structure

The code patterns can be adapted to:
- Sites with less aggressive protections
- Official APIs when available
- Alternative data sources

## Contributing

To add features or improve the skill:

1. Fork this repository
2. Make your changes
3. Submit a pull request

To add more Brazilian states to the knowledge base, see `SKILL.md`.

## License

MIT License - Use freely for personal and commercial purposes.

## Credits

Created by **Gustavo (GustavoZiaugra)** with OpenClaw
- Webmotors scraping functionality
- OLX scraping functionality
- Listing comparison and tracking
- Daily notification support

---

**Find this and more OpenClaw skills at ClawHub.com**

⭐ **Star this repository if you find it useful!**

⚠️ **Note:** This skill is provided as-is. Scraping may be blocked by site protections. Consider using official site alerts or APIs for production use.
