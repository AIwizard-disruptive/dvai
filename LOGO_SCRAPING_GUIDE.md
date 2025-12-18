# Company Logo Scraping Guide

## Overview

Your system now has automatic company logo scraping capabilities! It will:
1. **Try Clearbit Logo API first** (free, fast, no scraping needed)
2. **Scrape company websites as fallback** if Clearbit doesn't have the logo
3. **Cache results** in the `logo_scrape_cache` table

## Features

### Smart Logo Detection
The scraper tries multiple sources in order of quality:
1. Apple touch icon (usually high quality)
2. Open Graph image (social media preview)
3. High-resolution favicon (192px+)
4. Standard favicon
5. Default /favicon.ico location

### Caching
All scraped logos are cached in the database to avoid re-scraping:
- ✅ Faster subsequent lookups
- ✅ Reduces external requests
- ✅ Works offline for cached domains

---

## Usage

### Option 1: Bulk Enrichment (CLI Script)

Enrich all your portfolio companies at once:

```bash
cd backend

# Enrich all portfolio companies
python enrich_company_logos.py --portfolio

# Enrich companies from people emails
python enrich_company_logos.py --people

# Enrich both
python enrich_company_logos.py --all

# Force refresh existing logos
python enrich_company_logos.py --all --force

# Test with limited companies
python enrich_company_logos.py --portfolio --limit 5
```

**Example output:**
```
🎨 Company Logo Enrichment

📊 Fetching portfolio companies...
Found 47 companies

Processing companies... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%

✅ Enrichment Complete!

┏━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric                   ┃ Count ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Total Companies          │    47 │
│ Enriched                 │    42 │
│ Skipped                  │     3 │
│ Failed                   │     2 │
└──────────────────────────┴───────┘
```

### Option 2: REST API

#### Scrape Single Company Logo
```bash
curl -X POST http://localhost:8000/api/logos/scrape \
  -H "Content-Type: application/json" \
  -d '{"domain": "stripe.com"}'
```

**Response:**
```json
{
  "domain": "stripe.com",
  "logo_url": "https://stripe.com/img/v3/home/social.png",
  "company_name": "Stripe",
  "cached": false,
  "scraped_at": "2025-12-17T14:30:00"
}
```

#### Bulk Scrape Multiple Companies
```bash
curl -X POST http://localhost:8000/api/logos/bulk-scrape \
  -H "Content-Type: application/json" \
  -d '{
    "domains": ["stripe.com", "shopify.com", "notion.so"],
    "force_refresh": false
  }'
```

**Response:**
```json
{
  "total": 3,
  "success_count": 3,
  "cached_count": 0,
  "failed_count": 0,
  "results": {
    "success": [
      {"domain": "stripe.com", "logo_url": "https://..."},
      {"domain": "shopify.com", "logo_url": "https://..."},
      {"domain": "notion.so", "logo_url": "https://..."}
    ],
    "failed": [],
    "cached": []
  }
}
```

#### Get Cached Logo
```bash
curl http://localhost:8000/api/logos/cache/stripe.com
```

#### Enrich All Portfolio Companies
```bash
curl -X POST http://localhost:8000/api/logos/enrich-portfolio
```

---

## Option 3: Programmatic Use

### In Python Code

```python
from app.services.company_enrichment import (
    get_best_logo_url,
    scrape_logo_from_website,
    extract_domain_from_email
)

# Get logo from email
email = "john@stripe.com"
domain = extract_domain_from_email(email)  # "stripe.com"

# Get best logo (Clearbit + scraping)
logo_url = await get_best_logo_url(domain, try_scraping=True)
# Returns: "https://logo.clearbit.com/stripe.com" or scraped URL

# Force website scraping (skip Clearbit)
logo_url = await scrape_logo_from_website(domain)
# Returns: "https://stripe.com/img/logo.png"
```

### In Your Dealflow/Portfolio Views

The logos are automatically available in your database:

```python
# Portfolio companies already have logo_url field populated
companies = supabase.table('portfolio_companies').select('*').execute()

for company in companies.data:
    print(f"{company['name']}: {company['logo_url']}")
```

---

## Database Schema

### `logo_scrape_cache` Table

Caches all scraped logos:

```sql
CREATE TABLE logo_scrape_cache (
    id UUID PRIMARY KEY,
    domain TEXT UNIQUE NOT NULL,
    logo_url TEXT,
    company_name TEXT,
    scraped_at TIMESTAMP,
    scrape_method TEXT  -- 'clearbit' or 'scraped'
);
```

---

## Configuration

### Clearbit Logo API (Default)

- ✅ **Free tier** - no API key needed
- ✅ **Fast** - CDN-backed
- ✅ **No rate limits** on logo API
- ⚠️ Limited coverage (major companies only)

URL format: `https://logo.clearbit.com/{domain}`

### Website Scraping (Fallback)

When Clearbit doesn't have a logo:
- Fetches company homepage
- Parses HTML for logo tags
- Returns best quality logo found
- ⏱️ Slower (~2-5 seconds per domain)
- ✅ Higher coverage (any company with website)

---

## Tips & Best Practices

1. **Run bulk enrichment once** to populate existing companies
2. **Let it cache** - subsequent lookups will be instant
3. **Use `--force` sparingly** - only when logos are outdated
4. **API rate limiting** - be respectful when scraping websites
5. **Clearbit first** - it's faster and more reliable for major companies

---

## Troubleshooting

### Logo not found
- Check if domain is correct (no https://, no www)
- Try visiting the website manually
- Some sites block scrapers (403/401 errors)

### Slow scraping
- Normal - website scraping takes 2-5 seconds per domain
- Use Clearbit when available (instant)
- Cache results to avoid re-scraping

### Failed requests
```python
# Check logs for details
tail -f backend/logs/app.log
```

---

## Examples from Your Data

Looking at the screenshot you shared, your companies would be enriched like:

```
Disruptive Ventures → https://logo.clearbit.com/disruptiveventures.se
Portfolio Companies → Scraped from each company's website
Contacts' Companies → Extracted from email domains
```

---

## Next Steps

1. **Run initial enrichment:**
   ```bash
   cd backend
   python enrich_company_logos.py --all
   ```

2. **Update your UI** to display the logos:
   ```tsx
   <img src={company.logo_url} alt={company.name} />
   ```

3. **Set up automatic enrichment** for new companies using the API endpoints

---

## API Documentation

Full API docs available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Look for the "Logo Scraper" tag in the docs.

