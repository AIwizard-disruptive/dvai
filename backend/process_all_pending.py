#!/usr/bin/env python3
"""
Process all pending artifacts and generate Drive/Linear for each.

For each uploaded file:
1. Extract text from .docx
2. Parse meeting data (3-agent workflow)
3. Create Google Drive folder
4. Upload documents
5. Create Linear project
6. Create Linear tasks with Drive links
7. Set proper assignees and deadlines
"""
import asyncio
import sys
import os
sys.path.insert(0, '/Users/marcus/Library/Mobile Documents/com~apple~CloudDocs/Documents/Cursor-projects/Disruptive Ventures/DV Legacy/dv/backend')

from supabase import create_client
from app.config import settings


async def process_all_pending():
    """Process all pending artifacts."""
    
    print("\n" + "=" * 80)
    print("BATCH PROCESSING ALL PENDING FILES")
    print("=" * 80)
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    # Get all pending artifacts
    artifacts = supabase.table('artifacts').select('*').eq('transcription_status', 'pending').order('created_at', desc=True).execute().data
    
    print(f"\n📊 Found {len(artifacts)} files to process\n")
    
    if not artifacts:
        print("✅ No pending files. All caught up!")
        return
    
    results = {
        'processed': 0,
        'failed': 0,
        'meetings_created': [],
        'errors': []
    }
    
    for idx, artifact in enumerate(artifacts, 1):
        print(f"\n{'='*80}")
        print(f"Processing {idx}/{len(artifacts)}: {artifact['filename']}")
        print(f"{'='*80}")
        
        try:
            # Process this file using the existing process script
            import subprocess
            
            result = subprocess.run(
                [
                    sys.executable,
                    'process_any_file.py',
                    artifact['filename']
                ],
                cwd='/Users/marcus/Library/Mobile Documents/com~apple~CloudDocs/Documents/Cursor-projects/Disruptive Ventures/DV Legacy/dv/backend',
                capture_output=True,
                text=True,
                timeout=180  # 3 minutes per file
            )
            
            if result.returncode == 0:
                results['processed'] += 1
                print(f"✅ Successfully processed: {artifact['filename']}")
                
                # Get the meeting that was created
                updated_artifact = supabase.table('artifacts').select('meeting_id').eq('id', artifact['id']).execute().data[0]
                
                if updated_artifact.get('meeting_id'):
                    results['meetings_created'].append(updated_artifact['meeting_id'])
                    print(f"   ✓ Meeting created: {updated_artifact['meeting_id'][:8]}...")
            else:
                results['failed'] += 1
                error_msg = result.stderr or result.stdout or "Unknown error"
                results['errors'].append(f"{artifact['filename']}: {error_msg[:200]}")
                print(f"❌ Failed to process: {artifact['filename']}")
                print(f"   Error: {error_msg[:200]}")
        
        except Exception as e:
            results['failed'] += 1
            results['errors'].append(f"{artifact['filename']}: {str(e)}")
            print(f"❌ Error processing {artifact['filename']}: {str(e)}")
    
    print("\n" + "=" * 80)
    print("✅ BATCH PROCESSING COMPLETE")
    print("=" * 80)
    print(f"\n📊 Results:")
    print(f"  ✓ Processed: {results['processed']}/{len(artifacts)}")
    print(f"  ✗ Failed: {results['failed']}")
    print(f"  ✓ Meetings created: {len(results['meetings_created'])}")
    
    if results['errors']:
        print(f"\n⚠️  Errors:")
        for error in results['errors'][:5]:
            print(f"  - {error}")
    
    # Now run enhanced distribution for all new meetings
    if results['meetings_created']:
        print(f"\n🚀 Running enhanced distribution for {len(results['meetings_created'])} meetings...")
        
        for meeting_id in results['meetings_created']:
            print(f"\n📊 Generating Drive & Linear for meeting {meeting_id[:8]}...")
            try:
                # Run sync for this meeting
                result = subprocess.run(
                    [sys.executable, 'sync_with_drive_links.py'],
                    cwd='/Users/marcus/Library/Mobile Documents/com~apple~CloudDocs/Documents/Cursor-projects/Disruptive Ventures/DV Legacy/dv/backend',
                    env={**os.environ, 'MEETING_ID': meeting_id},
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if 'ENHANCED SYNC COMPLETE' in result.stdout:
                    print(f"   ✅ Drive & Linear generated!")
                else:
                    print(f"   ⚠ Partial completion")
            
            except Exception as e:
                print(f"   ❌ Generation failed: {str(e)}")
    
    print("\n✅ All done! Refresh dashboard to see results.")
    print(f"\nDashboard: http://localhost:8000/dashboard-ui")


if __name__ == "__main__":
    asyncio.run(process_all_pending())


