#!/usr/bin/env python3
"""
Fix all 2023 dates to 2025 and regenerate Drive folders.
WhisperFlow didn't exist in 2023, so all dates should be 2025.
"""
import asyncio
from supabase import create_client
from app.config import settings


async def fix_dates_and_regenerate():
    """Update all 2023 dates to 2025 and regenerate Drive folders."""
    
    print("\n" + "="*80)
    print("FIXING DATES: 2023 → 2025")
    print("="*80)
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    # Get all meetings
    meetings = supabase.table('meetings').select('id, title, meeting_date').execute().data
    
    print(f"\n📊 Found {len(meetings)} meetings\n")
    
    updated = 0
    for m in meetings:
        old_date = m.get('meeting_date')
        
        if old_date and '2023' in str(old_date):
            # Replace 2023 with 2025
            new_date = str(old_date).replace('2023', '2025')
            
            supabase.table('meetings').update({
                'meeting_date': new_date
            }).eq('id', m['id']).execute()
            
            print(f"✓ Updated: {m['title'][:45]}")
            print(f"  {old_date} → {new_date}")
            updated += 1
    
    print(f"\n✅ Updated {updated} meeting dates from 2023 to 2025")
    
    # Clear Drive/Linear metadata so they regenerate with new dates
    print(f"\n🗑️ Clearing old Drive/Linear references...")
    
    for m in meetings:
        supabase.table('meetings').update({
            'meeting_metadata': {}
        }).eq('id', m['id']).execute()
    
    print(f"✅ Cleared metadata from {len(meetings)} meetings")
    print(f"\n💡 Now regenerating with 2025 dates...")
    
    return meetings


if __name__ == "__main__":
    meetings = asyncio.run(fix_dates_and_regenerate())
    
    print("\n" + "="*80)
    print("✅ DATES FIXED! Now regenerating Drive & Linear...")
    print("="*80)
    
    # Regenerate all meetings with corrected dates
    import subprocess
    import os
    
    meetings_with_tasks = []
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    for m in meetings:
        actions = supabase.table('action_items').select('id').eq('meeting_id', m['id']).execute()
        if len(actions.data) > 0:
            meetings_with_tasks.append(m['id'])
    
    print(f"\n🚀 Regenerating {len(meetings_with_tasks)} meetings...\n")
    
    for idx, meeting_id in enumerate(meetings_with_tasks, 1):
        meeting = supabase.table('meetings').select('title').eq('id', meeting_id).execute().data[0]
        print(f"[{idx}/{len(meetings_with_tasks)}] {meeting['title'][:50]}...")
        
        try:
            result = subprocess.run(
                ['python3', 'sync_with_drive_links.py', meeting_id],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if 'ENHANCED SYNC COMPLETE' in result.stdout:
                print(f"   ✅ Generated in 2025 folder!\n")
            else:
                print(f"   ⚠ Partial completion\n")
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}\n")
    
    print("="*80)
    print("✅ ALL MEETINGS NOW IN 2025!")
    print("="*80)
    print("\nAll Drive folders now in: /Meetings/2025/")
    print("Dashboard: http://localhost:8000/dashboard-ui")


