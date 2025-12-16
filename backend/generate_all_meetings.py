#!/usr/bin/env python3
"""
Generate Drive folders and Linear projects for ALL meetings with tasks.
Runs the enhanced distribution for each meeting.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from supabase import create_client
from app.config import settings

# Import the sync function
import importlib.util
spec = importlib.util.spec_from_file_location("sync_module", "sync_with_drive_links.py")
sync_module = importlib.util.module_from_spec(spec)


async def generate_for_all_meetings():
    """Generate Drive & Linear for all meetings with tasks."""
    
    print("\n" + "="*80)
    print("GENERATE DRIVE & LINEAR FOR ALL MEETINGS")
    print("="*80)
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    # Get all meetings
    meetings = supabase.table('meetings').select('id, title').order('created_at', desc=True).execute().data
    
    # Filter to meetings with tasks
    meetings_with_tasks = []
    for m in meetings:
        actions = supabase.table('action_items').select('id').eq('meeting_id', m['id']).execute()
        if len(actions.data) > 0:
            meetings_with_tasks.append((m, len(actions.data)))
    
    print(f"\n📊 Found {len(meetings_with_tasks)} meetings with tasks\n")
    
    for idx, (meeting, task_count) in enumerate(meetings_with_tasks, 1):
        print(f"\n[{idx}/{len(meetings_with_tasks)}] {meeting['title'][:60]}")
        print(f"Tasks: {task_count}")
        print("-"*80)
        
        try:
            # Run sync_with_drive_links for this meeting
            import subprocess
            import os
            
            result = subprocess.run(
                ['python3', 'sync_with_drive_links.py'],
                cwd='/Users/marcus/Library/Mobile Documents/com~apple~CloudDocs/Documents/Cursor-projects/Disruptive Ventures/DV Legacy/dv/backend',
                env={**os.environ, 'MEETING_ID': meeting['id']},
                capture_output=True,
                text=True,
                timeout=180
            )
            
            if 'ENHANCED SYNC COMPLETE' in result.stdout:
                # Extract URLs from output
                import re
                drive_match = re.search(r'Drive: (https://drive\.google\.com/[^\s]+)', result.stdout)
                linear_match = re.search(r'Linear: (https://linear\.app/[^\s]+)', result.stdout)
                
                print(f"✅ Generated successfully!")
                if drive_match:
                    print(f"   📁 Drive: {drive_match.group(1)[:60]}...")
                if linear_match:
                    print(f"   📊 Linear: {linear_match.group(1)[:60]}...")
            else:
                print(f"⚠ Partial completion")
                # Print first few lines of output for debugging
                lines = result.stdout.split('\n')[:10]
                for line in lines:
                    if line.strip():
                        print(f"   {line[:70]}")
        
        except Exception as e:
            print(f"❌ Error: {str(e)[:150]}")
    
    print("\n" + "="*80)
    print("✅ GENERATION COMPLETE")
    print("="*80)
    print(f"\n📊 Generated for {len(meetings_with_tasks)} meetings")
    print("\nRefresh dashboard to see Drive & Linear buttons!")
    print("Dashboard: http://localhost:8000/dashboard-ui")


if __name__ == "__main__":
    asyncio.run(generate_for_all_meetings())


