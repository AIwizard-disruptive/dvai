"""AI-powered meeting agenda generation service."""
import json
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from openai import AsyncOpenAI

from app.config import settings


class AgendaTopic(BaseModel):
    """A topic to discuss in the meeting."""
    topic: str = Field(description="The discussion topic")
    duration_minutes: int = Field(description="Estimated duration in minutes")
    owner: Optional[str] = Field(default=None, description="Person leading this topic (if known)")


class ExpectedDecision(BaseModel):
    """A decision that needs to be made in the meeting."""
    decision_point: str = Field(description="What needs to be decided")
    context: str = Field(description="Brief context for why this decision is needed")
    options: list[str] = Field(default_factory=list, description="Possible options or approaches")


class ProposedNextStep(BaseModel):
    """A proposed next step or action after the meeting."""
    action: str = Field(description="The proposed action")
    owner: Optional[str] = Field(default=None, description="Suggested person responsible")
    timeline: Optional[str] = Field(default=None, description="Suggested timeline (e.g., 'within 1 week')")


class MeetingAgenda(BaseModel):
    """AI-generated meeting agenda."""
    meeting_objective: str = Field(description="Clear objective/purpose of the meeting")
    agenda_topics: list[AgendaTopic] = Field(
        default_factory=list,
        description="Discussion topics with estimated durations"
    )
    expected_decisions: list[ExpectedDecision] = Field(
        default_factory=list,
        description="Key decisions that need to be made"
    )
    proposed_next_steps: list[ProposedNextStep] = Field(
        default_factory=list,
        description="Suggested next steps and actions"
    )
    suggested_duration_minutes: int = Field(description="Suggested total meeting duration")
    preparation_notes: list[str] = Field(
        default_factory=list,
        description="Things participants should prepare before the meeting"
    )


class AgendaGeneratorService:
    """Service for generating meeting agendas using AI."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
    
    async def generate_agenda(
        self,
        meeting_name: str,
        meeting_description: str,
        participants: Optional[list[str]] = None,
        meeting_context: Optional[dict] = None,
    ) -> MeetingAgenda:
        """
        Generate a structured meeting agenda from name and description.
        
        Args:
            meeting_name: Title of the meeting
            meeting_description: Description of what the meeting is about
            participants: Optional list of participant names/emails
            meeting_context: Optional additional context (company, previous meetings, etc.)
        
        Returns:
            MeetingAgenda with structured agenda items
        """
        system_prompt = self._build_system_prompt(participants, meeting_context)
        user_prompt = self._build_user_prompt(meeting_name, meeting_description)
        
        # Call OpenAI with strict JSON schema
        response = await self.client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "meeting_agenda",
                    "strict": True,
                    "schema": MeetingAgenda.model_json_schema(),
                },
            },
            temperature=0.3,  # Slightly creative but structured
        )
        
        # Parse response
        content = response.choices[0].message.content
        data = json.loads(content)
        
        return MeetingAgenda(**data)
    
    def format_agenda_for_calendar(self, agenda: MeetingAgenda) -> str:
        """
        Format agenda as rich text for Google Calendar description.
        
        Args:
            agenda: Generated meeting agenda
        
        Returns:
            Formatted text suitable for calendar event description
        """
        lines = [
            f"🎯 Meeting Objective",
            f"{agenda.meeting_objective}",
            "",
            f"📋 Agenda ({agenda.suggested_duration_minutes} minutes)",
        ]
        
        for i, topic in enumerate(agenda.agenda_topics, 1):
            owner_text = f" ({topic.owner})" if topic.owner else ""
            lines.append(f"{i}. {topic.topic}{owner_text} — {topic.duration_minutes} min")
        
        if agenda.expected_decisions:
            lines.extend([
                "",
                "✅ Key Decisions to Make",
            ])
            for decision in agenda.expected_decisions:
                lines.append(f"• {decision.decision_point}")
                if decision.options:
                    lines.append(f"  Options: {', '.join(decision.options)}")
        
        if agenda.proposed_next_steps:
            lines.extend([
                "",
                "🚀 Proposed Next Steps",
            ])
            for step in agenda.proposed_next_steps:
                owner_text = f" (@{step.owner})" if step.owner else ""
                timeline_text = f" — {step.timeline}" if step.timeline else ""
                lines.append(f"• {step.action}{owner_text}{timeline_text}")
        
        if agenda.preparation_notes:
            lines.extend([
                "",
                "📚 Preparation",
            ])
            for note in agenda.preparation_notes:
                lines.append(f"• {note}")
        
        return "\n".join(lines)
    
    def format_agenda_as_markdown(self, agenda: MeetingAgenda) -> str:
        """
        Format agenda as markdown for database storage.
        
        Args:
            agenda: Generated meeting agenda
        
        Returns:
            Markdown-formatted agenda
        """
        lines = [
            "# Meeting Agenda",
            "",
            "## Objective",
            f"{agenda.meeting_objective}",
            "",
            f"## Agenda ({agenda.suggested_duration_minutes} minutes)",
        ]
        
        for i, topic in enumerate(agenda.agenda_topics, 1):
            owner_text = f" *({topic.owner})*" if topic.owner else ""
            lines.append(f"{i}. **{topic.topic}**{owner_text} — *{topic.duration_minutes} min*")
        
        if agenda.expected_decisions:
            lines.extend([
                "",
                "## Key Decisions to Make",
            ])
            for decision in agenda.expected_decisions:
                lines.append(f"### {decision.decision_point}")
                lines.append(f"{decision.context}")
                if decision.options:
                    lines.append("")
                    lines.append("**Options:**")
                    for option in decision.options:
                        lines.append(f"- {option}")
                lines.append("")
        
        if agenda.proposed_next_steps:
            lines.extend([
                "## Proposed Next Steps",
            ])
            for step in agenda.proposed_next_steps:
                owner_text = f" *(@{step.owner})*" if step.owner else ""
                timeline_text = f" — *{step.timeline}*" if step.timeline else ""
                lines.append(f"- {step.action}{owner_text}{timeline_text}")
        
        if agenda.preparation_notes:
            lines.extend([
                "",
                "## Preparation",
            ])
            for note in agenda.preparation_notes:
                lines.append(f"- {note}")
        
        return "\n".join(lines)
    
    def _build_system_prompt(
        self,
        participants: Optional[list[str]],
        meeting_context: Optional[dict],
    ) -> str:
        """Build system prompt for agenda generation."""
        prompt_parts = [
            "You are an expert meeting facilitator and business strategist.",
            "Generate a comprehensive, actionable meeting agenda based on the meeting name and description.",
            "",
            "Guidelines:",
            "- Create SPECIFIC, actionable agenda items (not generic)",
            "- Estimate realistic time durations for each topic",
            "- Identify key decisions that need to be made",
            "- Propose concrete next steps (not vague follow-ups)",
            "- Only assign owners if participants are provided and roles are clear",
            "- Suggest preparation items to make the meeting more effective",
            "- Be professional and business-focused",
            "- Total meeting duration should be realistic (typically 30-90 minutes)",
            "",
            "IMPORTANT: Follow GDPR principles:",
            "- Do NOT fabricate names, emails, or personal data",
            "- Only use participant information if explicitly provided",
            "- Mark owner fields as null if not clearly derivable",
        ]
        
        if participants:
            prompt_parts.extend([
                "",
                "Meeting Participants:",
                *[f"- {p}" for p in participants],
            ])
        
        if meeting_context:
            prompt_parts.extend([
                "",
                "Additional Context:",
            ])
            for key, value in meeting_context.items():
                prompt_parts.append(f"- {key}: {value}")
        
        return "\n".join(prompt_parts)
    
    def _build_user_prompt(self, meeting_name: str, meeting_description: str) -> str:
        """Build user prompt with meeting details."""
        return f"""Generate a detailed, actionable agenda for this meeting:

Meeting Name: {meeting_name}

Description:
{meeting_description}

Please create a structured agenda with:
1. Clear meeting objective
2. Specific discussion topics with time estimates
3. Key decisions that need to be made
4. Proposed next steps after the meeting
5. Preparation notes for participants
"""


# Singleton instance
_agenda_generator_service: Optional[AgendaGeneratorService] = None


def get_agenda_generator_service() -> AgendaGeneratorService:
    """Get or create agenda generator service instance."""
    global _agenda_generator_service
    if _agenda_generator_service is None:
        _agenda_generator_service = AgendaGeneratorService()
    return _agenda_generator_service


