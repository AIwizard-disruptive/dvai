#!/usr/bin/env python3
"""
Sync COEO Pipeline Stages from Pipedrive
=========================================
Fetches pipeline stages from COEO's Pipedrive and stores them in the database.
These stages will be used as Kanban columns in the Building wheel.

Usage:
    python sync_coeo_stages.py
"""

import asyncio
import sys
sys.path.insert(0, '.')

from supabase import create_client
from app.services.pipedrive_sync import PipedriveSyncService
from app.config import settings
from dotenv import load_dotenv

load_dotenv()


async def sync_coeo_stages():
    """Sync COEO's pipeline stages from Pipedrive."""
    
    print("\n" + "="*70)
    print("🔄 SYNCING COEO PIPELINE STAGES FROM PIPEDRIVE")
    print("="*70 + "\n")
    
    try:
        # Initialize Supabase client
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Find COEO's portfolio company ID
        print("🔍 Looking for COEO in portfolio companies...")
        result = supabase.table('portfolio_companies') \
            .select('id, organizations(name)') \
            .execute()
        
        coeo_pc = None
        for pc in result.data:
            if pc['organizations']['name'] == 'Coeo':
                coeo_pc = pc
                break
        
        if not coeo_pc:
            print("❌ COEO not found in portfolio_companies table")
            print("\nMake sure you've run: python add_portfolio_companies.py")
            return
        
        print(f"✅ Found COEO (ID: {coeo_pc['id']})")
        
        # Check if Pipedrive integration exists
        integration = supabase.table('portfolio_company_integrations') \
            .select('*') \
            .eq('portfolio_company_id', coeo_pc['id']) \
            .eq('integration_type', 'pipedrive') \
            .execute()
        
        if not integration.data:
            print("❌ COEO Pipedrive integration not found")
            print("\nMake sure you've run: python add_coeo_pipedrive_to_db.py")
            return
        
        print(f"✅ Found COEO Pipedrive integration")
        print(f"   Domain: {integration.data[0].get('company_domain', 'N/A')}")
        
        # Initialize sync service
        sync_service = PipedriveSyncService(supabase, settings.encryption_key)
        
        # Sync stages
        print(f"\n📥 Fetching pipeline stages from Pipedrive...")
        result = await sync_service.sync_pipeline_stages(coeo_pc['id'])
        
        if result['success']:
            print(f"\n✅ Successfully synced {result['stages_synced']} stages!\n")
            print("Stages synced:")
            for i, stage_name in enumerate(result['stage_names'], 1):
                print(f"  {i}. {stage_name}")
            
            print("\n" + "="*70)
            print("✅ SYNC COMPLETE!")
            print("="*70)
            print("\nThese stages are now available in the Building wheel.")
            print("Go to: http://localhost:8000/wheels/building")
            print("Select COEO and you'll see the Kanban board with these columns.")
        else:
            print(f"\n❌ Sync failed: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(sync_coeo_stages())
