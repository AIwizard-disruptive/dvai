#!/usr/bin/env python3
"""
Quick test script for logo scraping functionality
"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.services.company_enrichment import (
    get_best_logo_url,
    scrape_logo_from_website,
    extract_domain_from_email,
    get_company_name_from_domain
)


async def test_logo_scraping():
    """Test logo scraping with various companies."""
    print("\n🎨 Testing Logo Scraping\n")
    print("=" * 60)
    
    # Test cases
    test_companies = [
        "stripe.com",
        "shopify.com",
        "notion.so",
        "disruptiveventures.se",
        "github.com",
        "figma.com"
    ]
    
    print("\n1️⃣  Testing Clearbit + Scraping (best method)\n")
    
    for domain in test_companies:
        print(f"Testing: {domain}")
        try:
            logo_url = await get_best_logo_url(domain, try_scraping=True)
            company_name = get_company_name_from_domain(domain)
            
            method = "Clearbit" if "clearbit.com" in logo_url else "Scraped"
            print(f"  ✅ {company_name}")
            print(f"     Logo: {logo_url}")
            print(f"     Method: {method}\n")
        except Exception as e:
            print(f"  ❌ Error: {str(e)}\n")
    
    print("\n2️⃣  Testing Email Domain Extraction\n")
    
    test_emails = [
        "john@stripe.com",
        "jane@disruptiveventures.se",
        "support@gmail.com",  # Should be filtered out
        "hello@notion.so"
    ]
    
    for email in test_emails:
        domain = extract_domain_from_email(email)
        if domain:
            print(f"  ✅ {email} → {domain}")
        else:
            print(f"  ⚠️  {email} → (filtered out - personal email)")
    
    print("\n3️⃣  Testing Direct Website Scraping\n")
    
    # Test scraping a specific website
    test_domain = "stripe.com"
    print(f"Scraping {test_domain} directly...")
    
    try:
        scraped_logo = await scrape_logo_from_website(test_domain)
        if scraped_logo:
            print(f"  ✅ Found logo: {scraped_logo}")
        else:
            print(f"  ⚠️  No logo found")
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ Test complete!\n")
    print("Next steps:")
    print("  1. Run bulk enrichment: python enrich_company_logos.py --all")
    print("  2. Test API: curl http://localhost:8000/api/logos/scrape -d '{\"domain\":\"stripe.com\"}'")
    print("  3. View docs: http://localhost:8000/docs\n")


if __name__ == '__main__':
    asyncio.run(test_logo_scraping())

