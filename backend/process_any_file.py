#!/usr/bin/env python
"""Process any uploaded file - pass artifact_id as argument."""
import sys
from pathlib import Path
import uuid
import json

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from supabase import create_client
from app.config import settings
from app.services.document import DocumentService

def process_file(artifact_id: str):
    """Process an uploaded file and extract real data with AI."""
    
    # Create Supabase admin client
    admin_supabase = create_client(
        settings.supabase_url,
        settings.supabase_service_role_key
    )
    
    # Get artifact details from database
    print(f"Fetching artifact {artifact_id}...")
    artifact_response = admin_supabase.table('artifacts').select('*').eq('id', artifact_id).execute()
    
    if not artifact_response.data:
        print(f"❌ Artifact not found")
        return
    
    artifact = artifact_response.data[0]
    filename = artifact['filename']
    org_id = artifact['org_id']
    file_path = f"/tmp/artifacts/{artifact_id}/{filename}"
    
    print(f"✓ Found artifact: {filename}")
    
    # Extract text from DOCX
    print(f"\nReading DOCX file...")
    try:
        text_content = DocumentService.extract_text_from_docx(file_path)
        print(f"✓ Extracted {len(text_content)} characters")
    except Exception as e:
        print(f"❌ Failed to read file: {e}")
        return
    
    # Create meeting record
    print(f"\nCreating meeting record...")
    meeting_id = str(uuid.uuid4())
    
    admin_supabase.table('meetings').insert({
        'id': meeting_id,
        'org_id': org_id,
        'title': filename.replace('.docx', '').replace('_', ' ')
    }).execute()
    
    print(f"✓ Created meeting: {meeting_id}")
    
    # Link artifact to meeting
    admin_supabase.table('artifacts').update({
        'meeting_id': meeting_id,
        'transcription_status': 'processing'
    }).eq('id', artifact_id).execute()
    
    # Extract intelligence with OpenAI
    print(f"\nExtracting intelligence with AI...")
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=settings.openai_api_key)
        
        prompt = f"""Extract meeting intelligence from this document. Return ONLY valid JSON with this structure:

{{
  "decisions": [
    {{"decision_text": "text", "rationale": "why or null", "decision_maker": "who or null"}}
  ],
  "action_items": [
    {{"action_text": "text", "assignee": "who or null", "priority": "high|medium|low", "due_date": "YYYY-MM-DD or null"}}
  ],
  "attendees": [
    {{"name": "name", "email": "email or null", "role": "role or null"}}
  ],
  "key_points": ["point1", "point2"],
  "summary": "Brief summary"
}}

RULES:
- Extract ONLY explicitly stated information
- NEVER fabricate data
- Use null for missing info

Document:
{text_content}
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Extract only factual information. Never fabricate."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        intelligence = json.loads(response.choices[0].message.content)
        
        print(f"✓ Extracted:")
        print(f"   - {len(intelligence.get('decisions', []))} decisions")
        print(f"   - {len(intelligence.get('action_items', []))} action items")
        print(f"   - {len(intelligence.get('attendees', []))} attendees")
        print(f"   - {len(intelligence.get('key_points', []))} key points")
        
    except Exception as e:
        print(f"❌ AI extraction failed: {e}")
        intelligence = {'decisions': [], 'action_items': [], 'attendees': [], 'key_points': []}
    
    # Save decisions
    print(f"\nSaving decisions...")
    for decision in intelligence.get('decisions', []):
        admin_supabase.table('decisions').insert({
            'meeting_id': meeting_id,
            'org_id': org_id,
            'decision_text': decision.get('decision_text'),
            'rationale': decision.get('rationale'),
            'decision_maker': decision.get('decision_maker')
        }).execute()
        print(f"✓ {decision.get('decision_text', '')[:60]}")
    
    # Save action items
    print(f"\nSaving action items...")
    for action in intelligence.get('action_items', []):
        admin_supabase.table('action_items').insert({
            'meeting_id': meeting_id,
            'org_id': org_id,
            'action_text': action.get('action_text'),
            'assignee': action.get('assignee'),
            'priority': action.get('priority', 'medium'),
            'status': 'todo'
        }).execute()
        print(f"✓ {action.get('action_text', '')[:60]}")
    
    # Save attendees
    print(f"\nSaving attendees...")
    for attendee in intelligence.get('attendees', []):
        attendee_id = str(uuid.uuid4())
        admin_supabase.table('attendees').insert({
            'id': attendee_id,
            'org_id': org_id,
            'name': attendee.get('name'),
            'email': attendee.get('email'),
            'role': attendee.get('role')
        }).execute()
        
        admin_supabase.table('meeting_attendees').insert({
            'meeting_id': meeting_id,
            'attendee_id': attendee_id
        }).execute()
        print(f"✓ {attendee.get('name', 'Unknown')}")
    
    # Mark as completed
    admin_supabase.table('artifacts').update({
        'transcription_status': 'completed'
    }).eq('id', artifact_id).execute()
    
    print(f"\n✅ PROCESSING COMPLETE!")
    print(f"\n📊 View in dashboard: http://localhost:8000/dashboard-ui")
    print(f"📋 View meeting: http://localhost:8000/meeting/{meeting_id}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_file(sys.argv[1])
    else:
        # Default to the uploaded file
        process_file("e978c129-031d-47d4-bcc2-756e007d7ac7")

