"""Tests for AI agenda generation service."""
import pytest
from datetime import datetime
from app.services.agenda_generator import (
    AgendaGeneratorService,
    MeetingAgenda,
    AgendaTopic,
    ExpectedDecision,
    ProposedNextStep,
)


@pytest.fixture
def agenda_service():
    """Get agenda generator service instance."""
    # Mock the API key for testing
    import os
    os.environ["OPENAI_API_KEY"] = "sk-test-fake-key-for-testing"
    return AgendaGeneratorService(api_key="sk-test-fake-key")


def test_format_agenda_for_calendar():
    """Test calendar formatting of agenda."""
    service = AgendaGeneratorService(api_key="test-key")
    
    agenda = MeetingAgenda(
        meeting_objective="Test the agenda formatting system",
        agenda_topics=[
            AgendaTopic(topic="Introduction", duration_minutes=10, owner="Alice"),
            AgendaTopic(topic="Main discussion", duration_minutes=30, owner=None),
        ],
        expected_decisions=[
            ExpectedDecision(
                decision_point="Choose technology stack",
                context="Need to decide before development starts",
                options=["React", "Vue", "Angular"]
            )
        ],
        proposed_next_steps=[
            ProposedNextStep(
                action="Create prototype",
                owner="Bob",
                timeline="within 1 week"
            )
        ],
        suggested_duration_minutes=45,
        preparation_notes=["Review documentation", "Prepare questions"]
    )
    
    # Format for calendar
    formatted = service.format_agenda_for_calendar(agenda)
    
    # Assertions
    assert "🎯 Meeting Objective" in formatted
    assert "Test the agenda formatting system" in formatted
    assert "📋 Agenda (45 minutes)" in formatted
    assert "1. Introduction (Alice) — 10 min" in formatted
    assert "2. Main discussion — 30 min" in formatted
    assert "✅ Key Decisions to Make" in formatted
    assert "Choose technology stack" in formatted
    assert "Options: React, Vue, Angular" in formatted
    assert "🚀 Proposed Next Steps" in formatted
    assert "Create prototype (@Bob) — within 1 week" in formatted
    assert "📚 Preparation" in formatted
    assert "Review documentation" in formatted


def test_format_agenda_as_markdown():
    """Test markdown formatting of agenda."""
    service = AgendaGeneratorService(api_key="test-key")
    
    agenda = MeetingAgenda(
        meeting_objective="Plan Q1 initiatives",
        agenda_topics=[
            AgendaTopic(topic="Review Q4 results", duration_minutes=15, owner="CEO"),
        ],
        expected_decisions=[
            ExpectedDecision(
                decision_point="Budget allocation",
                context="Q1 budget needs approval",
                options=[]
            )
        ],
        proposed_next_steps=[
            ProposedNextStep(
                action="Finalize Q1 OKRs",
                owner="PM",
                timeline="by Friday"
            )
        ],
        suggested_duration_minutes=60,
        preparation_notes=["Review financial report"]
    )
    
    # Format as markdown
    markdown = service.format_agenda_as_markdown(agenda)
    
    # Assertions
    assert "# Meeting Agenda" in markdown
    assert "## Objective" in markdown
    assert "Plan Q1 initiatives" in markdown
    assert "## Agenda (60 minutes)" in markdown
    assert "**Review Q4 results**" in markdown
    assert "*(CEO)*" in markdown
    assert "## Key Decisions to Make" in markdown
    assert "### Budget allocation" in markdown
    assert "## Proposed Next Steps" in markdown
    assert "Finalize Q1 OKRs" in markdown
    assert "*(PM)*" in markdown
    assert "by Friday" in markdown


def test_agenda_without_optional_fields():
    """Test agenda generation with minimal data."""
    service = AgendaGeneratorService(api_key="test-key")
    
    agenda = MeetingAgenda(
        meeting_objective="Simple meeting",
        agenda_topics=[
            AgendaTopic(topic="Discussion", duration_minutes=30, owner=None),
        ],
        expected_decisions=[],
        proposed_next_steps=[],
        suggested_duration_minutes=30,
        preparation_notes=[]
    )
    
    # Should not error with missing optional fields
    formatted = service.format_agenda_for_calendar(agenda)
    markdown = service.format_agenda_as_markdown(agenda)
    
    assert "Simple meeting" in formatted
    assert "Simple meeting" in markdown


def test_system_prompt_building():
    """Test system prompt construction."""
    service = AgendaGeneratorService(api_key="test-key")
    
    # With participants
    prompt1 = service._build_system_prompt(
        participants=["alice@test.com", "bob@test.com"],
        meeting_context=None
    )
    assert "alice@test.com" in prompt1
    assert "bob@test.com" in prompt1
    assert "GDPR" in prompt1  # Should include GDPR warning
    
    # With context
    prompt2 = service._build_system_prompt(
        participants=None,
        meeting_context={"company": "Acme Corp", "industry": "SaaS"}
    )
    assert "Acme Corp" in prompt2
    assert "SaaS" in prompt2


def test_user_prompt_building():
    """Test user prompt construction."""
    service = AgendaGeneratorService(api_key="test-key")
    
    prompt = service._build_user_prompt(
        meeting_name="Q1 Planning",
        meeting_description="Discuss Q1 goals and objectives"
    )
    
    assert "Q1 Planning" in prompt
    assert "Discuss Q1 goals and objectives" in prompt
    assert "actionable agenda" in prompt


def test_gdpr_compliance_in_prompts():
    """Test that system prompts include GDPR compliance instructions."""
    service = AgendaGeneratorService(api_key="test-key")
    
    prompt = service._build_system_prompt(participants=None, meeting_context=None)
    
    # Check for GDPR-related instructions
    assert "Do NOT fabricate" in prompt or "NOT fabricate" in prompt
    assert "only use participant information if explicitly provided" in prompt.lower()


@pytest.mark.asyncio
async def test_agenda_structure_validation():
    """Test that generated agenda follows expected structure."""
    # This test would require mocking OpenAI API or using a test fixture
    # For now, we validate the structure of a manually created agenda
    
    agenda = MeetingAgenda(
        meeting_objective="Test objective",
        agenda_topics=[
            AgendaTopic(topic="Topic 1", duration_minutes=20, owner="Alice")
        ],
        expected_decisions=[
            ExpectedDecision(
                decision_point="Decision 1",
                context="Context here",
                options=["Option A", "Option B"]
            )
        ],
        proposed_next_steps=[
            ProposedNextStep(action="Action 1", owner="Bob", timeline="1 week")
        ],
        suggested_duration_minutes=60,
        preparation_notes=["Prep 1"]
    )
    
    # Validate all fields are present
    assert agenda.meeting_objective == "Test objective"
    assert len(agenda.agenda_topics) == 1
    assert agenda.agenda_topics[0].topic == "Topic 1"
    assert len(agenda.expected_decisions) == 1
    assert len(agenda.proposed_next_steps) == 1
    assert agenda.suggested_duration_minutes == 60


def test_no_pii_in_generated_content():
    """
    Test that the agenda generator doesn't fabricate personal data.
    This is enforced through system prompts and should be validated in integration tests.
    """
    service = AgendaGeneratorService(api_key="test-key")
    
    # Create agenda without participants
    agenda = MeetingAgenda(
        meeting_objective="Team sync",
        agenda_topics=[
            AgendaTopic(topic="Updates", duration_minutes=15, owner=None)
        ],
        expected_decisions=[],
        proposed_next_steps=[
            ProposedNextStep(action="Follow up", owner=None, timeline="next week")
        ],
        suggested_duration_minutes=30,
        preparation_notes=[]
    )
    
    # Format and verify no owner is assigned when not provided
    formatted = service.format_agenda_for_calendar(agenda)
    
    # Should not contain fabricated names
    assert "@" not in formatted or "alice" not in formatted.lower()
    assert "owner=None" not in formatted  # Should handle None gracefully


# Integration test markers (require OpenAI API key)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_agenda_generation():
    """
    Integration test with real OpenAI API.
    Requires OPENAI_API_KEY environment variable.
    Run with: pytest -m integration
    """
    import os
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set")
    
    service = AgendaGeneratorService()
    
    agenda = await service.generate_agenda(
        meeting_name="Product Launch Planning",
        meeting_description="Plan the launch of our new mobile app. Need to discuss marketing strategy, app store optimization, press outreach, and launch event. Budget is $50K.",
        participants=["marketing@test.com", "product@test.com"],
        meeting_context={"company": "Tech Startup", "product": "Mobile App"}
    )
    
    # Validate structure
    assert agenda.meeting_objective
    assert len(agenda.agenda_topics) > 0
    assert len(agenda.expected_decisions) > 0
    assert len(agenda.proposed_next_steps) > 0
    assert agenda.suggested_duration_minutes > 0
    
    # Validate content quality
    assert "launch" in agenda.meeting_objective.lower() or "app" in agenda.meeting_objective.lower()
    
    # Validate no fabricated data
    for topic in agenda.agenda_topics:
        if topic.owner:
            assert topic.owner in ["marketing@test.com", "product@test.com"]
    
    print("\n=== Generated Agenda ===")
    print(service.format_agenda_as_markdown(agenda))


