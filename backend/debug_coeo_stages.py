"""Debug Coeo's Pipedrive stage names."""
import asyncio
import sys
sys.path.insert(0, '.')

from app.integrations.pipedrive_client import PipedriveClient
from collections import Counter

COEO_API_TOKEN = "0082d57f308450640715cf7bf106a665287ddaaa"

async def analyze_stages():
    client = PipedriveClient(api_token=COEO_API_TOKEN)
    
    # Get all deals
    deals = await client.get_deals(status="all_not_deleted", limit=200)
    
    print(f"\n✅ Fetched {len(deals)} deals\n")
    
    # Inspect first deal to see available fields
    if deals:
        print("📋 First deal structure:")
        print("="*62)
        first_deal = deals[0]
        for key, value in sorted(first_deal.items()):
            if key not in ['custom_fields', 'org_id', 'person_id']:
                val_str = str(value)[:50] if value else 'None'
                print(f"  {key:<30} {val_str}")
        print("="*62)
    
    # Count deals by stage
    stage_counts = Counter(deal.get('stage_name', 'Unknown') for deal in deals)
    stage_id_counts = Counter(deal.get('stage_id', 'No ID') for deal in deals)
    
    print("\n📊 Stages by stage_name:")
    for stage_name, count in stage_counts.most_common(10):
        print(f"  {stage_name}: {count}")
    
    print("\n📊 Stages by stage_id:")
    for stage_id, count in stage_id_counts.most_common(10):
        print(f"  Stage ID {stage_id}: {count} deals")

if __name__ == "__main__":
    asyncio.run(analyze_stages())

