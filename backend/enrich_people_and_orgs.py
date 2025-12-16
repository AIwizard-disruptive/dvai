#!/usr/bin/env python3
"""
Enrich people and organizations.
- Extract companies from email domains
- Scrape logos from websites
- Link people to organizations
"""
import asyncio
from supabase import create_client
from app.config import settings
from app.services.logo_scraper import LogoScraper


async def enrich_all():
    """Enrich all people with organization data."""
    
    print("\n" + "="*80)
    print("ENRICHING PEOPLE & ORGANIZATIONS")
    print("="*80)
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    # Get org_id
    meeting = supabase.table('meetings').select('org_id').limit(1).execute().data[0]
    org_id = meeting['org_id']
    
    # Get all people with emails
    people = supabase.table('people').select('*').not_.is_('email', 'null').execute().data
    
    print(f"\n📊 Found {len(people)} people with emails\n")
    
    # Group by domain
    domains = {}
    for person in people:
        if person.get('email') and '@' in person['email']:
            domain = person['email'].split('@')[1]
            if domain not in domains:
                domains[domain] = []
            domains[domain].append(person)
    
    print(f"📊 Found {len(domains)} unique organizations\n")
    
    # Create or enrich each organization
    for domain, people_list in domains.items():
        print(f"🏢 {domain} ({len(people_list)} people)")
        
        # Check if organization exists
        org_check = supabase.table('organizations').select('id, logo_url').eq('org_id', org_id).eq('domain', domain).execute()
        
        if org_check.data:
            # Organization exists
            organization_id = org_check.data[0]['id']
            print(f"   ✓ Organization exists: {organization_id[:8]}...")
        else:
            # Create organization and scrape logo
            print(f"   🔍 Scraping logo and info...")
            
            try:
                enriched_data = await LogoScraper.get_logo_from_domain(domain)
                
                company_name = enriched_data.get('company_name') or domain.split('.')[0].title()
                
                org_data = {
                    'org_id': org_id,
                    'name': company_name,
                    'domain': domain,
                    'website_url': f'https://{domain}',
                    'logo_url': enriched_data.get('logo_url'),
                    'favicon_url': enriched_data.get('favicon_url'),
                    'description': enriched_data.get('description'),
                    'organization_type': 'client' if 'disruptiveventures' not in domain else 'internal',
                }
                
                org_result = supabase.table('organizations').insert(org_data).execute()
                organization_id = org_result.data[0]['id']
                
                print(f"   ✅ Created organization: {company_name}")
                if enriched_data.get('logo_url'):
                    print(f"   ✅ Logo scraped: {enriched_data['logo_url'][:50]}...")
            
            except Exception as e:
                print(f"   ⚠ Failed to scrape: {str(e)[:100]}")
                # Create basic organization without logo
                org_result = supabase.table('organizations').insert({
                    'org_id': org_id,
                    'name': domain.split('.')[0].title(),
                    'domain': domain,
                    'website_url': f'https://{domain}',
                    'organization_type': 'client' if 'disruptiveventures' not in domain else 'internal',
                }).execute()
                organization_id = org_result.data[0]['id']
        
        # Link people to organization
        for person in people_list:
            # Update person with organization link
            supabase.table('people').update({
                'primary_organization_id': organization_id,
                'person_type': 'internal' if 'disruptiveventures' in domain else 'client',
            }).eq('id', person['id']).execute()
            
            print(f"      → Linked: {person['name']}")
    
    print("\n" + "="*80)
    print("✅ ENRICHMENT COMPLETE")
    print("="*80)
    
    # Show summary
    orgs = supabase.table('organizations').select('*').eq('org_id', org_id).execute().data
    
    print(f"\n📊 Summary:")
    print(f"  Organizations created: {len(orgs)}")
    print(f"  People enriched: {len(people)}")
    
    print(f"\n🏢 Organizations:")
    for org in orgs:
        logo_status = "✅ Logo" if org.get('logo_url') else "⚠️ No logo"
        print(f"  - {org['name']} ({logo_status})")
    
    print(f"\n🎯 Knowledge Bank: http://localhost:8000/knowledge/")


if __name__ == "__main__":
    asyncio.run(enrich_all())


