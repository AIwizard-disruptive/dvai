"""
Post-processing service - Auto-generates all documents after meeting parsing
Runs automatically when 3-agent workflow completes
"""
import uuid
from datetime import datetime
from typing import Dict, List
from supabase import create_client
from app.config import settings


class PostProcessingService:
    """Automatically generate all documents after meeting is parsed."""
    
    def __init__(self):
        self.supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    async def process_meeting(self, meeting_id: str, org_id: str):
        """
        Auto-generate all documents for a meeting.
        
        Called automatically after 3-agent workflow completes.
        Generates documents in both Swedish and English.
        Stores links in database.
        """
        
        print(f"\n{'='*80}")
        print(f"POST-PROCESSING: Auto-generating documents for meeting {meeting_id[:8]}...")
        print(f"{'='*80}")
        
        # Fetch meeting data
        meeting_response = self.supabase.table('meetings').select('*').eq('id', meeting_id).execute()
        if not meeting_response.data:
            print("❌ Meeting not found")
            return
        
        meeting = meeting_response.data[0]
        
        # Fetch related data
        participants = self.supabase.table('meeting_participants').select('people(name, email, role)').eq('meeting_id', meeting_id).execute()
        attendees = [p['people'] for p in participants.data if p.get('people')]
        
        decisions = self.supabase.table('decisions').select('*').eq('meeting_id', meeting_id).execute().data
        actions = self.supabase.table('action_items').select('*').eq('meeting_id', meeting_id).execute().data
        
        # Document types to generate
        doc_types = [
            ('meeting_notes', 'Meeting Notes', 'markdown'),
            ('email_decision_update', 'Decision Update Email', 'email'),
            ('email_action_reminder', 'Action Reminder Email', 'email'),
            ('email_meeting_summary', 'Meeting Summary Email', 'email'),
        ]
        
        generated_docs = []
        
        # Generate each document in both languages
        for doc_type, doc_title, doc_format in doc_types:
            for lang, lang_name in [('sv', 'Swedish'), ('en', 'English')]:
                try:
                    # Generate using template (fast, no API needed)
                    content = await self._generate_document_template(
                        doc_type,
                        meeting,
                        attendees,
                        decisions,
                        actions,
                        lang
                    )
                    
                    # Save to database
                    doc_id = str(uuid.uuid4())
                    doc_record = {
                        'id': doc_id,
                        'meeting_id': meeting_id,
                        'org_id': org_id,
                        'title': f"{doc_title} ({lang_name})",
                        'doc_type': doc_type,
                        'language': lang,
                        'format': doc_format,
                        'content': content,
                        'storage_path': f"/documents/{meeting_id}/{doc_type}_{lang}.txt",
                        'created_at': datetime.utcnow().isoformat(),
                        'updated_at': datetime.utcnow().isoformat()
                    }
                    
                    # Store in generated_documents table
                    self.supabase.table('generated_documents').insert(doc_record).execute()
                    
                    generated_docs.append({
                        'id': doc_id,
                        'title': doc_record['title'],
                        'type': doc_type,
                        'language': lang
                    })
                    
                    print(f"  ✓ Generated: {doc_title} ({lang_name})")
                    
                except Exception as e:
                    print(f"  ⚠ Failed to generate {doc_title} ({lang_name}): {e}")
        
        print(f"\n✅ Post-processing complete: {len(generated_docs)} documents generated")
        print(f"  - Documents available on meeting page as download links")
        
        return generated_docs
    
    async def _generate_document_template(
        self,
        doc_type: str,
        meeting: Dict,
        attendees: List,
        decisions: List,
        actions: List,
        lang: str
    ) -> str:
        """Generate document using templates (works without OpenAI)."""
        
        metadata = meeting.get('meeting_metadata', {}) if isinstance(meeting.get('meeting_metadata'), dict) else {}
        current_date = datetime.now().strftime('%Y-%m-%d')
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M')
        meeting_date = meeting.get('meeting_date') or current_date
        
        if doc_type == 'meeting_notes':
            return self._template_meeting_notes(meeting, attendees, decisions, actions, metadata, meeting_date, current_datetime, lang)
        elif doc_type == 'email_decision_update':
            return self._template_decision_email(meeting, decisions, lang)
        elif doc_type == 'email_action_reminder':
            return self._template_action_reminder(meeting, actions, lang)
        elif doc_type == 'email_meeting_summary':
            return self._template_summary_email(meeting, metadata, lang)
        
        return "Document template not found"
    
    def _template_meeting_notes(self, meeting, attendees, decisions, actions, metadata, meeting_date, current_datetime, lang):
        """Generate meeting notes."""
        
        key_points = metadata.get('key_points', [])
        topics = metadata.get('main_topics', [])
        
        attendees_list = '\n'.join([f"- **{att['name']}**{' - ' + att['role'] if att.get('role') else ''}" for att in attendees]) if attendees else '_Inga deltagare_' if lang == 'sv' else '_No attendees_'
        
        key_points_list = '\n'.join([f"- {p}" for p in key_points]) if key_points else ('_Inga nyckel punkter_' if lang == 'sv' else '_No key points_')
        
        topics_list = ', '.join(topics) if topics else ('_Inga ämnen_' if lang == 'sv' else '_No topics_')
        
        decisions_parts = []
        for i, dec in enumerate(decisions, 1):
            decided_by = dec.get('source_quote', '')
            decisions_parts.append(f"""### {i}. {dec['decision']}

**{'Motivering' if lang == 'sv' else 'Rationale'}:** {dec.get('rationale', 'Ej angiven' if lang == 'sv' else 'Not specified')}  
{f"**{'Beslutat av' if lang == 'sv' else 'Decided by'}:** {decided_by}" if decided_by else ''}
""")
        decisions_text = '\n'.join(decisions_parts) if decisions else ('_Inga beslut_' if lang == 'sv' else '_No decisions_')
        
        actions_parts = []
        for i, action in enumerate(actions, 1):
            due = action.get('due_date', '')
            desc = action.get('description', '')
            actions_parts.append(f"""### {i}. {action['title']}

- **{'Ansvarig' if lang == 'sv' else 'Owner'}:** {action.get('owner_name', 'Ej tilldelad' if lang == 'sv' else 'Unassigned')}
- **{'Prioritet' if lang == 'sv' else 'Priority'}:** {(action.get('priority', 'medium')).upper()}
- **Status:** {action.get('status', 'open')}
{f"- **{'Deadline' if lang == 'sv' else 'Due'}:** {due}" if due else ''}
{f"- **{'Beskrivning' if lang == 'sv' else 'Description'}:** {desc}" if desc else ''}
""")
        actions_text = '\n'.join(actions_parts) if actions else ('_Inga åtgärder_' if lang == 'sv' else '_No actions_')
        
        if lang == 'sv':
            return f"""# {meeting['title']}

**Disruptive Ventures**  
**Datum:** {meeting_date}  
**Längd:** {meeting.get('duration_minutes', 'Ej angivet')} minuter  
**Typ:** {meeting.get('meeting_type', 'Teammöte')}  

---

## 👥 Deltagare ({len(attendees)})

{attendees_list}

---

## 💡 Viktiga Diskussionspunkter

{key_points_list}

---

## 🏷️ Huvudämnen

{topics_list}

---

## ✅ Beslut ({len(decisions)})

{decisions_text}

---

## 🎯 Åtgärdspunkter ({len(actions)})

{actions_text}

---

**Genererad:** {current_datetime}  
**System:** Disruptive Ventures Meeting Intelligence  
**Webb:** https://www.disruptiveventures.se
"""
        else:
            return f"""# {meeting['title']}

**Disruptive Ventures**  
**Date:** {meeting_date}  
**Duration:** {meeting.get('duration_minutes', 'Not specified')} minutes  
**Type:** {meeting.get('meeting_type', 'Team Meeting')}  

---

## 👥 Attendees ({len(attendees)})

{attendees_list}

---

## 💡 Key Discussion Points

{key_points_list}

---

## 🏷️ Main Topics

{topics_list}

---

## ✅ Decisions ({len(decisions)})

{decisions_text}

---

## 🎯 Action Items ({len(actions)})

{actions_text}

---

**Generated:** {current_datetime}  
**System:** Disruptive Ventures Meeting Intelligence  
**Web:** https://www.disruptiveventures.se
"""
    
    def _template_decision_email(self, meeting, decisions, lang):
        """Template for decision email."""
        
        decisions_parts = []
        for i, dec in enumerate(decisions, 1):
            rationale = dec.get('rationale', 'Se anteckningar' if lang == 'sv' else 'See notes')
            decisions_parts.append(f"{i}. {dec['decision']}\n   {'Motivering' if lang == 'sv' else 'Rationale'}: {rationale}")
        
        decisions_list = '\n\n'.join(decisions_parts)
        
        if lang == 'sv':
            return f"""Ämne: Beslut från möte: {meeting['title']}

Hej alla,

Efter vårt möte "{meeting['title']}" vill jag bekräfta följande beslut:

{decisions_list}

Vänligen granska och hör av er vid frågor.

Mvh,
Disruptive Ventures
https://www.disruptiveventures.se
"""
        else:
            return f"""Subject: Decision Update: {meeting['title']}

Hi everyone,

Following our meeting "{meeting['title']}", here are the confirmed decisions:

{decisions_list}

Please review and reach out with any questions.

Best regards,
Disruptive Ventures
https://www.disruptiveventures.se
"""
    
    def _template_action_reminder(self, meeting, actions, lang):
        """Template for action reminder."""
        
        actions_parts = []
        for i, action in enumerate(actions, 1):
            owner = action.get('owner_name', 'Ej tilldelad' if lang == 'sv' else 'Unassigned')
            due_date = action.get('due_date', '')
            due_text = f" - {'Deadline' if lang == 'sv' else 'Due'}: {due_date}" if due_date else ''
            actions_parts.append(f"{i}. {action['title']}\n   → {owner}{due_text}")
        
        actions_list = '\n\n'.join(actions_parts)
        
        if lang == 'sv':
            return f"""Ämne: Åtgärdspunkter: {meeting['title']}

Hej teamet,

Här är åtgärdspunkterna från "{meeting['title']}":

{actions_list}

Mvh,
Disruptive Ventures
https://www.disruptiveventures.se
"""
        else:
            return f"""Subject: Action Items: {meeting['title']}

Hi team,

Here are the action items from "{meeting['title']}":

{actions_list}

Best regards,
Disruptive Ventures
https://www.disruptiveventures.se
"""
    
    def _template_summary_email(self, meeting, metadata, lang):
        """Template for summary email."""
        
        key_points = metadata.get('key_points', [])
        topics = metadata.get('main_topics', [])
        
        points_list = '\n'.join([f"- {p}" for p in key_points]) if key_points else ('Se mötesanteckningar' if lang == 'sv' else 'See meeting notes')
        topics_list = ', '.join(topics) if topics else ('Flera ämnen' if lang == 'sv' else 'Multiple topics')
        
        if lang == 'sv':
            return f"""Ämne: Sammanfattning: {meeting['title']}

Hej alla,

Sammanfattning från "{meeting['title']}":

**Ämnen:** {topics_list}

**Viktiga punkter:**
{points_list}

Se fullständiga anteckningar för detaljer.

Mvh,
Disruptive Ventures
https://www.disruptiveventures.se
"""
        else:
            return f"""Subject: Summary: {meeting['title']}

Hi everyone,

Summary from "{meeting['title']}":

**Topics:** {topics_list}

**Key points:**
{points_list}

See full notes for details.

Best regards,
Disruptive Ventures
https://www.disruptiveventures.se
"""

