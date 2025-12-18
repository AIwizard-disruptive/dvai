"""
Add Portfolio Companies to Database
=====================================
This script adds the DV portfolio companies to the database.

Requirements:
- organizations table exists
- portfolio_companies table exists
- orgs table has DV entry
"""

import asyncio
from datetime import date, datetime
from typing import Optional
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Portfolio companies data
PORTFOLIO_COMPANIES = [
    {
        "name": "Crystal Alarm",
        "website_url": "https://crystalalarm.se",
        "domain": "crystalalarm.se",
        "founders": ["Jens Olsson", "Christoffer Wiklander"],
        "founder_emails": [],  # Not publicly shown
        "general_email": None,
        "industry": "Security Technology",
        "description": "Security and alarm systems provider",
        "country": "Sweden",
    },
    {
        "name": "LumberScan",
        "website_url": "https://lumberscan.com",
        "domain": "lumberscan.com",
        "founders": ["Daniel Johansson", "Rasmus Larsson"],
        "founder_emails": [],  # Not publicly shown
        "general_email": "info@lumberscan.com",
        "industry": "Forest Technology",
        "description": "Lumber scanning and quality assessment technology",
        "country": "Sweden",
    },
    {
        "name": "Alent Dynamic",
        "website_url": "https://alentdynamic.se",
        "domain": "alentdynamic.se",
        "founders": ["Peter Henriksson", "Peder Björkman"],
        "founder_emails": ["peter.henriksson@alentdynamic.se", "peder.bjorkman@alentdynamic.se"],
        "general_email": "info@alentdynamic.se",
        "industry": "Industrial Technology",
        "description": "Dynamic industrial solutions",
        "country": "Sweden",
    },
    {
        "name": "LunaLEC",
        "website_url": "https://lunalec.com",
        "domain": "lunalec.com",
        "founders": ["Ludvig Edman", "Nathaniel Robinson"],
        "founder_emails": [],  # Not publicly shown
        "general_email": None,
        "industry": "Lighting Technology",
        "description": "Advanced lighting and electrochemistry solutions",
        "country": "Sweden",
    },
    {
        "name": "Vaylo",
        "website_url": "https://vaylo.com",
        "domain": "vaylo.com",
        "founders": ["Einar Halldin"],
        "founder_emails": [],  # Not publicly shown
        "general_email": "info@vaylo.com",
        "industry": "Travel Technology",
        "description": "Travel planning and booking platform (formerly Resemolnet)",
        "country": "Sweden",
        "notes": "Previously known as Resemolnet",
    },
    {
        "name": "Coeo",
        "website_url": "https://coeo.events",
        "domain": "coeo.events",
        "founders": ["Anders Gunnarsson", "Tinna Sandström"],
        "founder_emails": ["anders@coeo.events", "tinna@coeo.events"],
        "general_email": None,
        "industry": "Event Technology",
        "description": "Event management and collaboration platform",
        "country": "Sweden",
    },
    {
        "name": "Basic Safety",
        "website_url": "https://basic-safety.se",
        "domain": "basic-safety.se",
        "founders": ["Fredric Lundqvist", "Johan Grimståhl"],
        "founder_emails": ["fredric@basic-safety.se", "johan@basic-safety.se"],
        "general_email": "info@basic-safety.se",
        "industry": "Safety Equipment",
        "description": "Safety equipment and solutions provider",
        "country": "Sweden",
    },
    {
        "name": "Service Node",
        "website_url": "https://servicenode.se",
        "domain": "servicenode.se",
        "founders": ["Jonas Westborg", "Fredrik Olofsson"],
        "founder_emails": [],  # Not publicly shown
        "general_email": None,
        "industry": "Service Technology",
        "description": "Service management and optimization platform",
        "country": "Sweden",
    },
]


async def add_portfolio_companies():
    """Add portfolio companies to the database."""
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        print("❌ Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set")
        return
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    
    print("🚀 Starting portfolio companies import...\n")
    
    # Get DV org_id
    print("📋 Fetching DV organization...")
    orgs_result = supabase.table('orgs').select('*').execute()
    dv_org = None
    
    if orgs_result.data:
        # Look for Disruptive Ventures org
        for org in orgs_result.data:
            if 'disruptive' in org.get('name', '').lower():
                dv_org = org
                break
        
        # If not found, use first org
        if not dv_org:
            dv_org = orgs_result.data[0]
        
        print(f"✅ Using org: {dv_org['name']} (ID: {dv_org['id']})\n")
    else:
        print("❌ Error: No organizations found in orgs table")
        return
    
    dv_org_id = dv_org['id']
    
    # Process each company
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for company in PORTFOLIO_COMPANIES:
        print(f"📦 Processing: {company['name']}")
        print(f"   Website: {company['website_url']}")
        print(f"   Founders: {', '.join(company['founders'])}")
        
        try:
            # Check if organization already exists
            existing_org = supabase.table('organizations').select('*').eq('domain', company['domain']).execute()
            
            if existing_org.data and len(existing_org.data) > 0:
                print(f"   ⚠️  Organization already exists, skipping...")
                skip_count += 1
                print()
                continue
            
            # Create organization
            org_data = {
                'org_id': dv_org_id,
                'name': company['name'],
                'website_url': company['website_url'],
                'domain': company['domain'],
                'organization_type': 'portfolio',
                'industry': company.get('industry'),
                'description': company.get('description'),
                'country': company.get('country'),
                'primary_email': company.get('general_email'),
                'relationship_status': 'active',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
            }
            
            org_result = supabase.table('organizations').insert(org_data).execute()
            
            if not org_result.data:
                print(f"   ❌ Failed to create organization")
                error_count += 1
                print()
                continue
            
            org_id = org_result.data[0]['id']
            print(f"   ✅ Created organization (ID: {org_id})")
            
            # Create portfolio_companies entry
            portfolio_data = {
                'organization_id': org_id,
                'dv_org_id': dv_org_id,
                'investment_stage': 'seed',  # Default, can be updated later
                'status': 'active',
                'ceo_dashboard_enabled': True,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
            }
            
            portfolio_result = supabase.table('portfolio_companies').insert(portfolio_data).execute()
            
            if portfolio_result.data:
                print(f"   ✅ Added to portfolio_companies")
                success_count += 1
            else:
                print(f"   ⚠️  Organization created but failed to add to portfolio_companies")
                error_count += 1
            
            # Add founders as people (if we have their emails)
            for idx, founder_name in enumerate(company['founders']):
                founder_email = None
                if idx < len(company['founder_emails']):
                    founder_email = company['founder_emails'][idx]
                
                # Only add if we have an email
                if founder_email:
                    # Check if person already exists
                    existing_person = supabase.table('people').select('*').eq('email', founder_email).execute()
                    
                    if not existing_person.data or len(existing_person.data) == 0:
                        person_data = {
                            'org_id': dv_org_id,
                            'name': founder_name,
                            'email': founder_email,
                            'person_type': 'founder',
                            'primary_organization_id': org_id,
                            'job_title': 'Co-Founder',
                            'created_at': datetime.now().isoformat(),
                            'updated_at': datetime.now().isoformat(),
                        }
                        
                        person_result = supabase.table('people').insert(person_data).execute()
                        
                        if person_result.data:
                            print(f"   ✅ Added founder: {founder_name}")
                        else:
                            print(f"   ⚠️  Failed to add founder: {founder_name}")
                    else:
                        print(f"   ℹ️  Founder already exists: {founder_name}")
            
            print()
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            error_count += 1
            print()
            continue
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    print(f"✅ Successfully added: {success_count}")
    print(f"⚠️  Skipped (already exists): {skip_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📦 Total processed: {len(PORTFOLIO_COMPANIES)}")
    print("="*60)
    
    if success_count > 0:
        print("\n✅ Portfolio companies have been added to the database!")
        print("   You can now view them in the Building Companies wheel.")
    
    if error_count > 0:
        print("\n⚠️  Some companies had errors. Please check the log above.")


if __name__ == "__main__":
    asyncio.run(add_portfolio_companies())

