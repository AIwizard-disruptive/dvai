"""Scrape logos for portfolio companies from their websites."""
import asyncio
from supabase import create_client
import os
from dotenv import load_dotenv
import sys

sys.path.insert(0, '.')

from app.services.company_enrichment import get_best_logo_url

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


async def scrape_logos():
    """Scrape logos for all portfolio companies."""
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    
    # Get portfolio companies with their organization info
    result = supabase.table('portfolio_companies') \
        .select('id, organization_id, organizations(id, name, website_url, domain, logo_url, favicon_url)') \
        .execute()
    
    print("\n🎨 Scraping Portfolio Company Logos...\n")
    
    success_count = 0
    skip_count = 0
    fail_count = 0
    
    for pc in result.data:
        org = pc.get('organizations', {})
        org_id = org.get('id')
        company_name = org.get('name', 'Unknown')
        website_url = org.get('website_url', '')
        existing_logo = org.get('logo_url')
        
        print(f"📦 {company_name}")
        print(f"   Website: {website_url}")
        
        # Skip if already has logo
        if existing_logo:
            print(f"   ✓ Already has logo: {existing_logo}")
            skip_count += 1
            print()
            continue
        
        if not website_url:
            print(f"   ⚠️  No website URL")
            fail_count += 1
            print()
            continue
        
        # Extract domain
        domain = website_url.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
        
        try:
            # Get best logo
            logo_url = await get_best_logo_url(domain, try_scraping=True)
            
            if logo_url:
                # Update organization with logo
                supabase.table('organizations').update({
                    'logo_url': logo_url,
                    'favicon_url': f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
                }).eq('id', org_id).execute()
                
                print(f"   ✅ Logo scraped: {logo_url}")
                success_count += 1
            else:
                print(f"   ⚠️  No logo found")
                # At least set favicon
                supabase.table('organizations').update({
                    'favicon_url': f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
                }).eq('id', org_id).execute()
                fail_count += 1
        
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            fail_count += 1
        
        print()
    
    print("="*60)
    print(f"\n✅ Scraping Complete!\n")
    print(f"  Success: {success_count}")
    print(f"  Skipped: {skip_count}")
    print(f"  Failed:  {fail_count}")
    print(f"  Total:   {len(result.data)}")
    print()


if __name__ == "__main__":
    asyncio.run(scrape_logos())

