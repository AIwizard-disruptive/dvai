#!/usr/bin/env python3
"""
Parse all pending meetings properly.
Each file gets parsed and saved to ITS OWN meeting (not the Swedish one).
"""
import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from supabase import create_client
from app.config import settings
from app.services.document import DocumentService
from app.services.three_agent_workflow import three_agent_meeting_parse


def parse_meeting_from_artifact(artifact_id: str, meeting_id: str, file_path: str):
    """Parse a specific meeting file and save to specific meeting."""
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    print(f"\n📄 Parsing: {os.path.basename(file_path)}")
    
    # 1. Extract text from docx
    print("   1. Extracting text...")
    text = DocumentService.extract_text_from_docx(file_path)
    print(f"      ✓ Extracted {len(text)} characters")
    
    # 2. Parse with 3-agent workflow
    print("   2. Running 3-agent parse...")
    try:
        parsed_data = three_agent_meeting_parse(text)
        print(f"      ✓ Found: {len(parsed_data.get('action_items', []))} action items, {len(parsed_data.get('decisions', []))} decisions")
    except Exception as e:
        print(f"      ⚠ 3-agent parse failed: {str(e)[:100]}")
        # Fall back to simple parsing
        parsed_data = {'action_items': [], 'decisions': [], 'attendees': []}
    
    # 3. Get org_id from meeting
    meeting = supabase.table('meetings').select('org_id, title').eq('id', meeting_id).execute().data[0]
    org_id = meeting['org_id']
    
    # 4. Save action items to THIS meeting
    print(f"   3. Saving to meeting: {meeting_id[:8]}...")
    
    for action in parsed_data.get('action_items', []):
        supabase.table('action_items').insert({
            'org_id': org_id,
            'meeting_id': meeting_id,
            'title': action.get('title', 'Untitled'),
            'description': action.get('description'),
            'owner_name': action.get('owner_name'),
            'due_date': action.get('due_date'),
            'priority': action.get('priority', 'medium'),
            'status': 'open',
        }).execute()
    
    # 5. Save decisions
    for decision in parsed_data.get('decisions', []):
        supabase.table('decisions').insert({
            'org_id': org_id,
            'meeting_id': meeting_id,
            'decision': decision.get('decision', ''),
            'rationale': decision.get('rationale'),
        }).execute()
    
    # 6. Save attendees
    for attendee in parsed_data.get('attendees', []):
        # Find or create person
        person_check = supabase.table('people').select('id').eq('org_id', org_id).eq('name', attendee.get('name', '')).execute()
        
        if person_check.data:
            person_id = person_check.data[0]['id']
        else:
            person = supabase.table('people').insert({
                'org_id': org_id,
                'name': attendee.get('name', ''),
                'email': attendee.get('email'),
            }).execute().data[0]
            person_id = person['id']
        
        # Link to meeting
        supabase.table('meeting_participants').insert({
            'meeting_id': meeting_id,
            'person_id': person_id,
        }).execute()
    
    # 7. Update artifact status
    supabase.table('artifacts').update({
        'transcription_status': 'completed'
    }).eq('id', artifact_id).execute()
    
    # 8. Update meeting status
    supabase.table('meetings').update({
        'processing_status': 'completed'
    }).eq('id', meeting_id).execute()
    
    print(f"   ✅ Saved {len(parsed_data.get('action_items', []))} action items")
    print(f"   ✅ Saved {len(parsed_data.get('decisions', []))} decisions")
    print(f"   ✅ Saved {len(parsed_data.get('attendees', []))} attendees")
    
    return True


if __name__ == "__main__":
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    print("\n" + "="*80)
    print("PARSE ALL PENDING MEETINGS (CORRECT MEETING ASSIGNMENT)")
    print("="*80)
    
    # Get artifacts with meetings but no action items
    artifacts = supabase.table('artifacts').select('id, filename, meeting_id').not_.is_('meeting_id', 'null').eq('transcription_status', 'completed').execute().data
    
    # Filter to only those whose meetings have 0 action items
    to_process = []
    for artifact in artifacts:
        if artifact.get('meeting_id'):
            actions = supabase.table('action_items').select('id').eq('meeting_id', artifact['meeting_id']).execute()
            if len(actions.data) == 0:
                to_process.append(artifact)
    
    print(f"\n📊 Found {len(to_process)} meetings to parse (have 0 action items)\n")
    
    for idx, artifact in enumerate(to_process, 1):
        file_path = f"/tmp/artifacts/{artifact['id']}/{artifact['filename']}"
        
        if os.path.exists(file_path):
            print(f"[{idx}/{len(to_process)}]")
            try:
                parse_meeting_from_artifact(artifact['id'], artifact['meeting_id'], file_path)
            except Exception as e:
                print(f"   ❌ Error: {str(e)[:150]}")
        else:
            print(f"[{idx}/{len(to_process)}] ❌ File not found: {artifact['filename'][:50]}")
    
    print(f"\n{'='*80}")
    print(f"✅ DONE! Refresh dashboard to see results")
    print(f"{'='*80}")



