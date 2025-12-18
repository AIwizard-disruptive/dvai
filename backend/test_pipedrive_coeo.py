"""Test Pipedrive integration with Coeo account."""
import asyncio
import sys
sys.path.insert(0, '.')

from app.integrations.pipedrive_client import PipedriveClient

# Coeo Pipedrive credentials
COEO_API_TOKEN = "0082d57f308450640715cf7bf106a665287ddaaa"
COEO_DOMAIN = "coeo.pipedrive.com"


async def test_coeo_pipeline():
    """Fetch and display Coeo's Pipedrive data."""
    
    print("\n🔄 Connecting to Coeo Pipedrive...\n")
    
    client = PipedriveClient(api_token=COEO_API_TOKEN, company_domain=COEO_DOMAIN)
    
    # Get stages first
    print("📊 Fetching pipeline stages...")
    stages = await client.get_stages()
    
    print(f"\n✅ Found {len(stages)} pipeline stages:\n")
    for stage in stages:
        print(f"   {stage.get('name')} (ID: {stage.get('id')}) - Order: {stage.get('order_nr')}")
    
    # Get deals
    print(f"\n📦 Fetching deals...\n")
    deals = await client.get_deals(status="all_not_deleted", limit=200)
    
    print(f"✅ Found {len(deals)} deals\n")
    
    # Group by stage
    deals_by_stage = {}
    for deal in deals:
        stage_name = deal.get('stage_name', 'Unknown')
        if stage_name not in deals_by_stage:
            deals_by_stage[stage_name] = []
        deals_by_stage[stage_name].append(deal)
    
    # Display summary
    print("="*80)
    print("DEALS BY STAGE")
    print("="*80)
    
    for stage_name, stage_deals in sorted(deals_by_stage.items()):
        total_value = sum(d.get('value', 0) for d in stage_deals)
        print(f"\n📍 {stage_name}")
        print(f"   Deals: {len(stage_deals)}")
        print(f"   Total Value: {total_value:,.0f} SEK")
        
        # Show first 3 deals in each stage
        for deal in stage_deals[:3]:
            org_name = deal.get('org_name', 'No org')
            value = deal.get('value', 0)
            print(f"   - {deal.get('title')} ({org_name}) - {value:,.0f} SEK")
        
        if len(stage_deals) > 3:
            print(f"   ... and {len(stage_deals) - 3} more")
    
    print("\n" + "="*80)
    print(f"📊 TOTAL PIPELINE VALUE: {sum(d.get('value', 0) for d in deals):,.0f} SEK")
    print("="*80)
    
    # Get organizations
    print(f"\n👥 Fetching organizations...\n")
    orgs = await client.get_organizations(limit=50)
    print(f"✅ Found {len(orgs)} organizations")
    
    # Get persons
    print(f"\n🧑 Fetching contacts...\n")
    persons = await client.get_persons(limit=50)
    print(f"✅ Found {len(persons)} contacts")
    
    print("\n✅ Pipedrive integration test complete!\n")
    
    return deals, stages


if __name__ == "__main__":
    asyncio.run(test_coeo_pipeline())

