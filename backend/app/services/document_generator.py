"""
Dynamic Document Generator
Generates ANY type of document based on meeting content:
- Meeting notes
- Emails (decision updates, action reminders)
- Contracts
- Market analyses  
- Reports
- Proposals
"""
from typing import Dict, List, Optional
from datetime import datetime
from openai import AsyncOpenAI
from app.config import settings


class DocumentGenerator:
    """Generate documents dynamically based on meeting content."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
    
    async def generate_document(
        self,
        document_type: str,
        meeting_data: Dict,
        language: str = "sv",
        additional_context: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate any type of document from meeting data.
        
        Args:
            document_type: Type of document (email, contract, analysis, report, etc.)
            meeting_data: Meeting data with attendees, decisions, actions
            language: Language code (sv, en)
            additional_context: Extra context for generation
        
        Returns:
            Dict with 'content', 'title', 'format'
        """
        
        if not self.client:
            raise ValueError("OpenAI API key required for document generation")
        
        # Route to appropriate generator
        generators = {
            'meeting_notes': self._generate_meeting_notes,
            'email_decision_update': self._generate_decision_email,
            'email_action_reminder': self._generate_action_reminder,
            'email_meeting_summary': self._generate_summary_email,
            'contract_draft': self._generate_contract,
            'market_analysis': self._generate_market_analysis,
            'status_report': self._generate_status_report,
            'proposal': self._generate_proposal
        }
        
        generator_func = generators.get(document_type)
        if not generator_func:
            # Use AI to generate any custom document type
            return await self._generate_custom_document(document_type, meeting_data, language, additional_context)
        
        return await generator_func(meeting_data, language, additional_context)
    
    async def _generate_meeting_notes(self, meeting_data: Dict, language: str, context: Optional[str]) -> Dict:
        """Generate formal 1-page meeting notes."""
        
        meeting = meeting_data.get('meeting_info', {})
        attendees = meeting_data.get('attendees', [])
        decisions = meeting_data.get('decisions', [])
        actions = meeting_data.get('action_items', [])
        
        template = "Swedish" if language == "sv" else "English"
        
        prompt = f"""Generate professional 1-page meeting notes in {template}.

Meeting: {meeting.get('title', 'Meeting')}
Date: {meeting.get('date', datetime.now().strftime('%Y-%m-%d'))}
Attendees: {len(attendees)} people
Decisions: {len(decisions)}
Action Items: {len(actions)}

Format as professional business document with:
- Header with meeting info
- Attendee list
- Key discussion points
- Decisions made (with rationale)
- Action items (owner, deadline, priority)
- Footer

Use clear, professional language. Be concise but complete."""
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional meeting secretary creating formal meeting minutes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        return {
            'content': response.choices[0].message.content,
            'title': f"Meeting Notes - {meeting.get('title', 'Meeting')}",
            'format': 'markdown'
        }
    
    async def _generate_decision_email(self, meeting_data: Dict, language: str, context: Optional[str]) -> Dict:
        """Generate email template for decision updates."""
        
        decisions = meeting_data.get('decisions', [])
        meeting = meeting_data.get('meeting_info', {})
        
        lang_text = "Swedish" if language == "sv" else "English"
        
        prompt = f"""Generate a professional email in {lang_text} to communicate decisions from a meeting.

Meeting: {meeting.get('title')}
Decisions to communicate: {len(decisions)}

For each decision, include:
- What was decided
- Why (rationale)
- Impact/next steps
- Who decided

Tone: Professional but friendly
Format: Email with subject line"""
        
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional business communicator writing decision update emails."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        
        return {
            'content': response.choices[0].message.content,
            'title': f"Decision Update - {meeting.get('title', 'Meeting')}",
            'format': 'email'
        }
    
    async def _generate_action_reminder(self, meeting_data: Dict, language: str, context: Optional[str]) -> Dict:
        """Generate action item reminder email."""
        
        actions = meeting_data.get('action_items', [])
        
        lang_text = "Swedish" if language == "sv" else "English"
        
        prompt = f"""Generate action item reminder email in {lang_text}.

{len(actions)} action items to remind about.

Format:
- Friendly but clear subject line
- Brief intro
- List each action with owner and deadline
- Clear call-to-action
- Professional closing"""
        
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a project coordinator sending friendly action reminders."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        
        return {
            'content': response.choices[0].message.content,
            'title': "Action Items Reminder",
            'format': 'email'
        }
    
    async def _generate_summary_email(self, meeting_data: Dict, language: str, context: Optional[str]) -> Dict:
        """Generate meeting summary email for distribution."""
        
        meeting = meeting_data.get('meeting_info', {})
        key_points = meeting.get('key_points', [])
        
        lang_text = "Swedish" if language == "sv" else "English"
        
        prompt = f"""Generate a concise meeting summary email in {lang_text}.

Meeting: {meeting.get('title')}
Key points discussed: {len(key_points)}

Format:
- Clear subject line
- Brief 2-3 paragraph summary
- Key takeaways (bullet points)
- Next steps
- Link to full notes

Tone: Professional, concise"""
        
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an executive assistant writing meeting summaries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        return {
            'content': response.choices[0].message.content,
            'title': f"Meeting Summary - {meeting.get('title', 'Meeting')}",
            'format': 'email'
        }
    
    async def _generate_contract(self, meeting_data: Dict, language: str, context: Optional[str]) -> Dict:
        """Generate contract draft based on decisions."""
        
        decisions = meeting_data.get('decisions', [])
        
        prompt = f"""Based on meeting decisions, generate a professional contract draft.

Context: {context or 'Business agreement based on meeting decisions'}
Decisions made: {len(decisions)}

Create formal contract with:
- Parties section
- Recitals (background)
- Terms and conditions based on decisions
- Standard legal language
- Signature blocks

Language: Professional legal language"""
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a legal professional drafting contracts. Create professional but clear legal documents."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        return {
            'content': response.choices[0].message.content,
            'title': "Contract Draft",
            'format': 'legal_document'
        }
    
    async def _generate_market_analysis(self, meeting_data: Dict, language: str, context: Optional[str]) -> Dict:
        """Generate market analysis based on meeting discussions."""
        
        meeting = meeting_data.get('meeting_info', {})
        topics = meeting.get('main_topics', [])
        
        prompt = f"""Based on meeting discussions, generate a market analysis.

Topics discussed: {', '.join(topics)}
Context: {context or 'Market analysis from strategic meeting'}

Include:
- Executive Summary
- Market Overview
- Key Insights from Meeting
- Recommendations
- Next Steps

Format: Professional business analysis"""
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a market analyst creating professional market analyses."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        
        return {
            'content': response.choices[0].message.content,
            'title': "Market Analysis",
            'format': 'report'
        }
    
    async def _generate_status_report(self, meeting_data: Dict, language: str, context: Optional[str]) -> Dict:
        """Generate status report from meeting."""
        
        actions = meeting_data.get('action_items', [])
        decisions = meeting_data.get('decisions', [])
        
        prompt = f"""Generate executive status report based on meeting.

Actions tracked: {len(actions)}
Decisions made: {len(decisions)}

Format:
- Executive Summary
- Progress Update
- Key Decisions
- Action Items Status
- Risks/Blockers
- Next Steps"""
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an executive creating status reports for leadership."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        return {
            'content': response.choices[0].message.content,
            'title': "Status Report",
            'format': 'report'
        }
    
    async def _generate_proposal(self, meeting_data: Dict, language: str, context: Optional[str]) -> Dict:
        """Generate business proposal from meeting decisions."""
        
        decisions = meeting_data.get('decisions', [])
        
        prompt = f"""Based on meeting decisions, create a business proposal.

Context: {context or 'Business proposal from meeting outcomes'}
Decisions to implement: {len(decisions)}

Include:
- Executive Summary
- Background/Context
- Proposed Solution (based on decisions)
- Implementation Plan (based on action items)
- Budget/Resources
- Timeline
- Expected Outcomes"""
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a business development professional creating winning proposals."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        
        return {
            'content': response.choices[0].message.content,
            'title': "Business Proposal",
            'format': 'proposal'
        }
    
    async def _generate_custom_document(
        self,
        document_type: str,
        meeting_data: Dict,
        language: str,
        context: Optional[str]
    ) -> Dict:
        """Generate any custom document type using AI."""
        
        prompt = f"""Generate a '{document_type}' based on this meeting data.

Context: {context or 'Generate document from meeting outcomes'}
Language: {language}

Meeting had:
- {len(meeting_data.get('attendees', []))} attendees
- {len(meeting_data.get('decisions', []))} decisions
- {len(meeting_data.get('action_items', []))} action items

Create a professional, well-structured {document_type} that would be useful for this business context."""
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are a professional creating a {document_type}. Generate high-quality business documents."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        
        return {
            'content': response.choices[0].message.content,
            'title': document_type.replace('_', ' ').title(),
            'format': 'custom'
        }



