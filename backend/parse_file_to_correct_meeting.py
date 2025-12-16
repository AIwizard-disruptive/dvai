#!/usr/bin/env python3
"""
Parse meeting file and save data to the CORRECT meeting.
Takes meeting_id as parameter instead of hardcoding it.
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from supabase import create_client
from app.config import settings
from app.services.document import DocumentService
import openai


def simple_parse_meeting(text: str) -> dict:
    """
    Simple AI-powered parsing using OpenAI directly.
    Extracts attendees, action items, and decisions.
    """
    
    openai.api_key = settings.openai_api_key
    
    prompt = f"""Parse this Swedish meeting transcript and extract structured data.

Meeting transcript:
{text[:4000]}

Extract and return JSON with:
{{
  "attendees": [list of names],
  "action_items": [
    {{"title": "task", "owner_name": "person", "priority": "high/medium/low", "description": "details"}}
  ],
  "decisions": [
    {{"decision": "what was decided", "rationale": "why"}}
  ]
}}

Return only valid JSON, no other text."""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        import json
        result_text = response.choices[0].message.content
        
        # Extract JSON from response
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0]
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0]
        
        return json.loads(result_text.strip())
    
    except Exception as e:
        print(f"   ⚠ AI parsing failed: {str(e)[:100]}")
        return {"attendees": [], "action_items": [], "decisions": []}


def parse_and_save_to_meeting(file_path: str, meeting_id: str):
    """Parse file and save to specific meeting."""
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    # Get meeting info
    meeting = supabase.table('meetings').select('*').eq('id', meeting_id).execute().data[0]
    org_id = meeting['org_id']
    
    print(f"\n📄 Parsing: {os.path.basename(file_path)}")
    print(f"   Meeting: {meeting['title'][:50]}")
    print(f"   Meeting ID: {meeting_id[:8]}...")
    
    # Extract text
    print("   1. Extracting text...")
    text = DocumentService.extract_text_from_docx(file_path)
    print(f"      ✓ Extracted {len(text)} characters")
    
    # Parse with AI
    print("   2. Parsing with AI...")
    parsed_data = simple_parse_meeting(text)
    
    print(f"      ✓ Found: {len(parsed_data.get('attendees', []))} attendees")
    print(f"      ✓ Found: {len(parsed_data.get('action_items', []))} action items")
    print(f"      ✓ Found: {len(parsed_data.get('decisions', []))} decisions")
    
    # Save to THIS meeting
    print(f"   3. Saving to database...")
    
    # Save attendees
    for attendee_name in parsed_data.get('attendees', []):
        if isinstance(attendee_name, dict):
            attendee_name = attendee_name.get('name', '')
        
        if not attendee_name:
            continue
        
        # Find or create person
        person_check = supabase.table('people').select('id').eq('org_id', org_id).eq('name', attendee_name).execute()
        
        if person_check.data:
            person_id = person_check.data[0]['id']
        else:
            person = supabase.table('people').insert({
                'org_id': org_id,
                'name': attendee_name,
            }).execute().data[0]
            person_id = person['id']
        
        # Link to meeting (avoid duplicates)
        existing = supabase.table('meeting_participants').select('id').eq('meeting_id', meeting_id).eq('person_id', person_id).execute()
        if not existing.data:
            try:
                supabase.table('meeting_participants').insert({
                    'meeting_id': meeting_id,
                    'person_id': person_id,
                    'org_id': org_id,  # Required by constraint
                }).execute()
            except:
                # If fails, skip participant linking (not critical)
                pass
    
    # Save action items
    for action in parsed_data.get('action_items', []):
        supabase.table('action_items').insert({
            'org_id': org_id,
            'meeting_id': meeting_id,
            'title': action.get('title', 'Untitled'),
            'description': action.get('description'),
            'owner_name': action.get('owner_name'),
            'priority': action.get('priority', 'medium'),
            'status': 'open',
        }).execute()
    
    # Save decisions
    for decision in parsed_data.get('decisions', []):
        supabase.table('decisions').insert({
            'org_id': org_id,
            'meeting_id': meeting_id,
            'decision': decision.get('decision', ''),
            'rationale': decision.get('rationale'),
        }).execute()
    
    print(f"   ✅ Saved {len(parsed_data.get('attendees', []))} attendees")
    print(f"   ✅ Saved {len(parsed_data.get('action_items', []))} action items")
    print(f"   ✅ Saved {len(parsed_data.get('decisions', []))} decisions")
    
    return True


if __name__ == "__main__":
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    print("\n" + "="*80)
    print("PARSE ALL 5 PENDING MEETINGS TO CORRECT MEETINGS")
    print("="*80)
    
    # Get the 5 new meetings (not the Swedish one)
    all_meetings = supabase.table('meetings').select('id, title, created_at').order('created_at', desc=True).execute().data
    
    # Exclude Swedish meeting
    swedish_id = "1f75abf8-a5c3-4a40-af45-540925629dc8"
    new_meetings = [m for m in all_meetings if m['id'] != swedish_id][:5]
    
    print(f"\n📊 Processing {len(new_meetings)} meetings\n")
    
    for idx, meeting in enumerate(new_meetings, 1):
        # Get artifact for this meeting
        artifact = supabase.table('artifacts').select('id, filename').eq('meeting_id', meeting['id']).execute().data
        
        if not artifact:
            print(f"[{idx}] ⚠ No artifact for: {meeting['title'][:50]}")
            continue
        
        artifact = artifact[0]
        file_path = f"/tmp/artifacts/{artifact['id']}/{artifact['filename']}"
        
        if not os.path.exists(file_path):
            print(f"[{idx}] ❌ File not found: {artifact['filename'][:50]}")
            continue
        
        print(f"[{idx}/{len(new_meetings)}]")
        try:
            parse_and_save_to_meeting(file_path, meeting['id'])
            print(f"   ✅ Complete!\n")
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:150]}\n")
    
    print("="*80)
    print("✅ DONE! Refresh dashboard to see results")
    print("="*80)
    print("\nDashboard: http://localhost:8000/dashboard-ui")

