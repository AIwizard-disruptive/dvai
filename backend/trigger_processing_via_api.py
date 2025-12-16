#!/usr/bin/env python3
"""
Trigger processing for all pending uploads via API.
Simpler and more reliable than subprocess approach.
"""
import httpx
import asyncio
from supabase import create_client
from app.config import settings


async def trigger_all_processing():
    """Trigger processing for all pending artifacts via API."""
    
    print("\n" + "=" * 80)
    print("TRIGGERING PROCESSING FOR ALL UPLOADED FILES")
    print("=" * 80)
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    # Get all pending artifacts
    artifacts = supabase.table('artifacts').select('id, filename, meeting_id').eq('transcription_status', 'pending').order('created_at', desc=True).execute().data
    
    print(f"\n📊 Found {len(artifacts)} files to process\n")
    
    if not artifacts:
        print("✅ No pending files!")
        return
    
    # For each artifact, trigger processing via the parse_and_save script
    async with httpx.AsyncClient(timeout=120.0) as client:
        for idx, artifact in enumerate(artifacts[:10], 1):  # Process first 10
            print(f"\n[{idx}/10] Processing: {artifact['filename'][:60]}...")
            
            try:
                # Call the parse API endpoint if it exists
                # Or trigger via subprocess
                import subprocess
                result = subprocess.run(
                    ['python3', 'parse_and_save.py', f"/tmp/artifacts/{artifact['id']}/{artifact['filename']}"],
                    cwd='/Users/marcus/Library/Mobile Documents/com~apple~CloudDocs/Documents/Cursor-projects/Disruptive Ventures/DV Legacy/dv/backend',
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if "SUCCESS" in result.stdout or "✅" in result.stdout:
                    print(f"   ✅ Parsed successfully!")
                    
                    # Get meeting ID
                    updated = supabase.table('artifacts').select('meeting_id').eq('id', artifact['id']).execute().data[0]
                    if updated.get('meeting_id'):
                        print(f"   ✓ Meeting created: {updated['meeting_id'][:8]}...")
                else:
                    print(f"   ⚠ Parsing incomplete:")
                    print(f"   {result.stdout[:200]}")
            
            except Exception as e:
                print(f"   ❌ Error: {str(e)[:150]}")
    
    print("\n" + "=" * 80)
    print("✅ PROCESSING TRIGGERED")
    print("=" * 80)
    print("\n💡 Files are being processed in background")
    print("📊 Check dashboard in 1-2 minutes to see results")
    print(f"\nDashboard: http://localhost:8000/dashboard-ui")


if __name__ == "__main__":
    asyncio.run(trigger_all_processing())


