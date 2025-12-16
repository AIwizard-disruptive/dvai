"""
Document generation endpoint - Works without OpenAI by using templates
When OpenAI quota available, switches to AI-enhanced generation
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse
from datetime import datetime
from supabase import create_client
from app.config import settings

router = APIRouter()


@router.get("/generate/{doc_type}")
async def generate_document(
    doc_type: str,
    meeting_id: str = Query(...),
    language: str = Query("sv")
):
    """
    Generate document from meeting data.
    Uses templates (fast, no API needed) with fallback to AI when available.
    """
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    # Fetch meeting data
    meeting_response = supabase.table('meetings').select('*, orgs(name)').eq('id', meeting_id).execute()
    if not meeting_response.data:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    meeting = meeting_response.data[0]
    org_name = meeting.get('orgs', {}).get('name', 'Disruptive Ventures') if isinstance(meeting.get('orgs'), dict) else 'Disruptive Ventures'
    
    # Get related data
    participants_response = supabase.table('meeting_participants').select('people(name, email, role)').eq('meeting_id', meeting_id).execute()
    attendees = [p['people'] for p in participants_response.data if p.get('people')]
    
    decisions_response = supabase.table('decisions').select('*').eq('meeting_id', meeting_id).execute()
    decisions = decisions_response.data
    
    actions_response = supabase.table('action_items').select('*').eq('meeting_id', meeting_id).execute()
    action_items = actions_response.data
    
    # Get metadata
    metadata = meeting.get('meeting_metadata', {}) if isinstance(meeting.get('meeting_metadata'), dict) else {}
    
    # Generate document using templates
    if doc_type == "meeting_notes":
        content = generate_meeting_notes_template(meeting, attendees, decisions, action_items, org_name, metadata, language)
    elif doc_type == "email_decision_update":
        content = generate_decision_email_template(meeting, decisions, attendees, language)
    elif doc_type == "email_action_reminder":
        content = generate_action_reminder_template(meeting, action_items, language)
    elif doc_type == "email_meeting_summary":
        content = generate_summary_email_template(meeting, metadata, language)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown document type: {doc_type}")
    
    return PlainTextResponse(
        content=content,
        headers={"Content-Disposition": f"attachment; filename=\"{doc_type}_{language}.txt\""}
    )


def generate_meeting_notes_template(meeting, attendees, decisions, actions, org_name, metadata, lang):
    """Generate professional meeting notes using template."""
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M')
    meeting_date = meeting.get('meeting_date') or current_date
    
    if lang == "sv":
        return f"""# {meeting['title']}

**{org_name}**  
**Datum:** {meeting_date}  
**Längd:** {meeting.get('duration_minutes') or 'Ej angivet'} minuter  
**Typ:** {meeting.get('meeting_type') or 'Teammöte'}  

---

## 👥 Deltagare ({len(attendees)})

{chr(10).join([f"- **{att['name']}**{' - ' + att['role'] if att.get('role') else ''}" for att in attendees]) if attendees else '_Inga deltagare registrerade_'}

---

## 💡 Viktiga Diskussionspunkter

{chr(10).join([f"- {point}" for point in metadata.get('key_points', [])]) if metadata.get('key_points') else '_Inga nyckel punkter registrerade_'}

---

## 🏷️ Huvudämnen

{', '.join(metadata.get('main_topics', [])) if metadata.get('main_topics') else '_Inga ämnen registrerade_'}

---

## ✅ Beslut Fattade ({len(decisions)})

{chr(10).join([f'''
### {i}. {dec['decision']}

**Motivering:** {dec.get('rationale') or 'Ej angiven'}  
{f"**Beslutat av:** {dec.get('source_quote')}" if dec.get('source_quote') else ''}

''' for i, dec in enumerate(decisions, 1)]) if decisions else '_Inga beslut registrerade_'}

---

## 🎯 Åtgärdspunkter ({len(actions)})

{chr(10).join([f'''
### {i}. {action['title']}

- **Ansvarig:** {action.get('owner_name') or 'Ej tilldelad'}
- **Prioritet:** {(action.get('priority') or 'medium').upper()}
- **Status:** {action.get('status') or 'open'}
{f"- **Deadline:** {action.get('due_date')}" if action.get('due_date') else ''}
{f"- **Beskrivning:** {action.get('description')}" if action.get('description') else ''}

''' for i, action in enumerate(actions, 1)]) if actions else '_Inga åtgärdspunkter registrerade_'}

---

**Genererad:** {current_datetime}  
**System:** Disruptive Ventures Meeting Intelligence  
**Webb:** https://www.disruptiveventures.se
"""
    
    else:  # English
        return f"""# {meeting['title']}

**{org_name}**  
**Date:** {meeting_date}  
**Duration:** {meeting.get('duration_minutes') or 'Not specified'} minutes  
**Type:** {meeting.get('meeting_type') or 'Team Meeting'}  

---

## 👥 Attendees ({len(attendees)})

{chr(10).join([f"- **{att['name']}**{' - ' + att['role'] if att.get('role') else ''}" for att in attendees]) if attendees else '_No attendees recorded_'}

---

## 💡 Key Discussion Points

{chr(10).join([f"- {point}" for point in metadata.get('key_points', [])]) if metadata.get('key_points') else '_No key points recorded_'}

---

## 🏷️ Main Topics

{', '.join(metadata.get('main_topics', [])) if metadata.get('main_topics') else '_No topics recorded_'}

---

## ✅ Decisions Made ({len(decisions)})

{chr(10).join([f'''
### {i}. {dec['decision']}

**Rationale:** {dec.get('rationale') or 'Not specified'}  
{f"**Decided by:** {dec.get('source_quote')}" if dec.get('source_quote') else ''}

''' for i, dec in enumerate(decisions, 1)]) if decisions else '_No decisions recorded_'}

---

## 🎯 Action Items ({len(actions)})

{chr(10).join([f'''
### {i}. {action['title']}

- **Owner:** {action.get('owner_name') or 'Unassigned'}
- **Priority:** {(action.get('priority') or 'medium').upper()}
- **Status:** {action.get('status') or 'open'}
{f"- **Due:** {action.get('due_date')}" if action.get('due_date') else ''}
{f"- **Description:** {action.get('description')}" if action.get('description') else ''}

''' for i, action in enumerate(actions, 1)]) if actions else '_No action items recorded_'}

---

**Generated:** {current_datetime}  
**System:** Disruptive Ventures Meeting Intelligence  
**Web:** https://www.disruptiveventures.se
"""


def generate_decision_email_template(meeting, decisions, attendees, lang):
    """Generate decision update email."""
    
    if lang == "sv":
        return f"""Ämne: Beslut från möte: {meeting['title']}

Hej alla,

Efter vårt möte "{meeting['title']}" vill jag bekräfta följande beslut:

{chr(10).join([f'''
{i}. {dec['decision']}
   Motivering: {dec.get('rationale') or 'Se mötesanteckningar'}
   {f"Beslutat av: {dec.get('source_quote')}" if dec.get('source_quote') else ''}
''' for i, dec in enumerate(decisions, 1)])}

Vänligen granska och hör av er om ni har frågor.

Med vänliga hälsningar,
Disruptive Ventures

---
Se fullständiga mötesanteckningar: http://localhost:8000/meeting/{meeting['id']}
https://www.disruptiveventures.se
"""
    else:
        return f"""Subject: Decision Update: {meeting['title']}

Hi everyone,

Following our meeting "{meeting['title']}", I want to confirm the following decisions:

{chr(10).join([f'''
{i}. {dec['decision']}
   Rationale: {dec.get('rationale') or 'See meeting notes'}
   {f"Decided by: {dec.get('source_quote')}" if dec.get('source_quote') else ''}
''' for i, dec in enumerate(decisions, 1)])}

Please review and let me know if you have any questions.

Best regards,
Disruptive Ventures

---
View full meeting notes: http://localhost:8000/meeting/{meeting['id']}
https://www.disruptiveventures.se
"""


def generate_action_reminder_template(meeting, actions, lang):
    """Generate action item reminder."""
    
    if lang == "sv":
        return f"""Ämne: Påminnelse: Åtgärdspunkter från {meeting['title']}

Hej teamet,

Här är åtgärdspunkterna från vårt möte "{meeting['title']}":

{chr(10).join([f'''
{i}. {action['title']}
   → Ansvarig: {action.get('owner_name') or 'Ej tilldelad'}
   → Prioritet: {(action.get('priority') or 'medium').upper()}
   {f"→ Deadline: {action.get('due_date')}" if action.get('due_date') else ''}
''' for i, action in enumerate(actions, 1)])}

Uppdatera gärna statusen när ni gör framsteg!

Med vänliga hälsningar,
Disruptive Ventures

---
https://www.disruptiveventures.se
"""
    else:
        return f"""Subject: Reminder: Action Items from {meeting['title']}

Hi team,

Here are the action items from our meeting "{meeting['title']}":

{chr(10).join([f'''
{i}. {action['title']}
   → Owner: {action.get('owner_name') or 'Unassigned'}
   → Priority: {(action.get('priority') or 'medium').upper()}
   {f"→ Due: {action.get('due_date')}" if action.get('due_date') else ''}
''' for i, action in enumerate(actions, 1)])}

Please update status as you make progress!

Best regards,
Disruptive Ventures

---
https://www.disruptiveventures.se
"""


def generate_summary_email_template(meeting, metadata, lang):
    """Generate meeting summary email."""
    
    key_points = metadata.get('key_points', []) if metadata else []
    topics = metadata.get('main_topics', []) if metadata else []
    
    if lang == "sv":
        return f"""Ämne: Sammanfattning: {meeting['title']}

Hej alla,

Här är en sammanfattning från vårt möte "{meeting['title']}":

**Huvudämnen:**
{chr(10).join([f"- {topic}" for topic in topics]) if topics else 'Inga ämnen registrerade'}

**Viktiga Punkter:**
{chr(10).join([f"- {point}" for point in key_points]) if key_points else 'Inga punkter registrerade'}

För fullständiga detaljer, beslut och åtgärdspunkter, se mötesanteckningarna.

Med vänliga hälsningar,
Disruptive Ventures

---
Se fullständiga anteckningar: http://localhost:8000/meeting/{meeting['id']}
https://www.disruptiveventures.se
"""
    else:
        return f"""Subject: Summary: {meeting['title']}

Hi everyone,

Here's a summary from our meeting "{meeting['title']}":

**Main Topics:**
{chr(10).join([f"- {topic}" for topic in topics]) if topics else 'No topics recorded'}

**Key Points:**
{chr(10).join([f"- {point}" for point in key_points]) if key_points else 'No points recorded'}

For full details, decisions and action items, see the meeting notes.

Best regards,
Disruptive Ventures

---
View full notes: http://localhost:8000/meeting/{meeting['id']}
https://www.disruptiveventures.se
"""

