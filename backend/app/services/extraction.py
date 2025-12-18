"""LLM extraction service for meeting intelligence."""
import json
from typing import Optional
from pydantic import BaseModel, Field
from openai import AsyncOpenAI

from app.config import settings


# Pydantic models for structured output
class ExtractedDecision(BaseModel):
    """A decision made in the meeting."""
    decision: str = Field(description="The decision that was made")
    rationale: Optional[str] = Field(default=None, description="Why this decision was made")
    confidence: str = Field(description="Confidence level: high, medium, low")
    source_chunk_indices: list[int] = Field(
        default_factory=list,
        description="Indices of transcript chunks where this was mentioned"
    )


class ExtractedActionItem(BaseModel):
    """An action item from the meeting."""
    title: str = Field(description="Short title/summary of the action item")
    description: Optional[str] = Field(default=None, description="Detailed description")
    owner_name: Optional[str] = Field(default=None, description="Name of person responsible (only if explicitly mentioned)")
    owner_email: Optional[str] = Field(default=None, description="Email of person responsible (only if explicitly mentioned)")
    due_date: Optional[str] = Field(default=None, description="Due date in YYYY-MM-DD format (only if explicitly mentioned)")
    status: str = Field(default="open", description="Status: open, in_progress, blocked, done")
    priority: Optional[str] = Field(default=None, description="Priority: high, medium, low")
    confidence: str = Field(description="Confidence level: high, medium, low")
    source_chunk_indices: list[int] = Field(
        default_factory=list,
        description="Indices of transcript chunks where this was mentioned"
    )


class ExtractedEntity(BaseModel):
    """A named entity mentioned in the meeting."""
    kind: str = Field(description="Entity type: person, company, product, location")
    name: str = Field(description="Entity name")


class MeetingIntelligence(BaseModel):
    """Structured meeting intelligence extracted by LLM."""
    summary_md: str = Field(description="Markdown-formatted meeting summary")
    decisions: list[ExtractedDecision] = Field(
        default_factory=list,
        description="Decisions made in the meeting"
    )
    action_items: list[ExtractedActionItem] = Field(
        default_factory=list,
        description="Action items from the meeting"
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Relevant tags for categorization"
    )
    entities: list[ExtractedEntity] = Field(
        default_factory=list,
        description="Named entities mentioned"
    )


class ExtractionService:
    """Service for extracting meeting intelligence using LLM."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
    
    async def extract_intelligence(
        self,
        transcript_chunks: list[dict],
        meeting_metadata: Optional[dict] = None,
        participants: Optional[list[str]] = None,
    ) -> MeetingIntelligence:
        """
        Extract structured meeting intelligence from transcript.
        
        Args:
            transcript_chunks: List of transcript chunks with 'text', 'speaker', etc.
            meeting_metadata: Optional meeting metadata (title, date, etc.)
            participants: Optional list of participant names/emails
        
        Returns:
            MeetingIntelligence with structured outputs
        """
        # Build context
        transcript_text = self._build_transcript_text(transcript_chunks)
        system_prompt = self._build_system_prompt(meeting_metadata, participants)
        
        # Call OpenAI with strict JSON schema
        response = await self.client.chat.completions.create(
            model="gpt-4o-2024-08-06",  # Model with structured outputs
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Transcript:\n\n{transcript_text}"},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "meeting_intelligence",
                    "strict": True,
                    "schema": MeetingIntelligence.model_json_schema(),
                },
            },
            temperature=0.1,
        )
        
        # Parse response
        content = response.choices[0].message.content
        data = json.loads(content)
        
        return MeetingIntelligence(**data)
    
    def _build_transcript_text(self, chunks: list[dict]) -> str:
        """Build formatted transcript text with chunk indices."""
        lines = []
        for i, chunk in enumerate(chunks):
            speaker = chunk.get("speaker", "Unknown")
            text = chunk.get("text", "")
            lines.append(f"[{i}] {speaker}: {text}")
        
        return "\n".join(lines)
    
    def _build_system_prompt(
        self,
        meeting_metadata: Optional[dict],
        participants: Optional[list[str]],
    ) -> str:
        """Build system prompt with context."""
        prompt_parts = [
            "You are an expert meeting analyst. Extract structured intelligence from the meeting transcript.",
            "",
            "Guidelines:",
            "- Be precise and factual. Only extract information explicitly stated.",
            "- For action items: Only assign owner/email if explicitly mentioned. Never invent names or emails.",
            "- For due dates: Only extract if explicitly stated. Use YYYY-MM-DD format.",
            "- Confidence: Use 'high' if explicitly stated, 'medium' if implied, 'low' if uncertain.",
            "- Source indices: Reference the [N] chunk numbers where information was found.",
            "- Summary: Write a concise markdown summary (2-4 paragraphs) covering key points.",
        ]
        
        if meeting_metadata:
            prompt_parts.extend([
                "",
                "Meeting Context:",
                f"- Title: {meeting_metadata.get('title', 'N/A')}",
                f"- Date: {meeting_metadata.get('date', 'N/A')}",
                f"- Type: {meeting_metadata.get('type', 'N/A')}",
            ])
        
        if participants:
            prompt_parts.extend([
                "",
                "Known Participants:",
                *[f"- {p}" for p in participants],
            ])
        
        return "\n".join(prompt_parts)


# Singleton instance
_extraction_service: Optional[ExtractionService] = None


def get_extraction_service() -> ExtractionService:
    """Get or create extraction service instance."""
    global _extraction_service
    if _extraction_service is None:
        _extraction_service = ExtractionService()
    return _extraction_service





