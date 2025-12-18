"""Tests for LLM extraction schema validation."""
import pytest
from pydantic import ValidationError
from app.services.extraction import (
    ExtractedDecision,
    ExtractedActionItem,
    ExtractedEntity,
    MeetingIntelligence,
)


def test_extracted_decision_validation():
    """Test ExtractedDecision schema."""
    # Valid decision
    decision = ExtractedDecision(
        decision="We will launch in Q2",
        rationale="Market conditions are favorable",
        confidence="high",
        source_chunk_indices=[1, 2],
    )
    assert decision.decision == "We will launch in Q2"
    assert decision.confidence == "high"
    
    # Missing required fields should fail
    with pytest.raises(ValidationError):
        ExtractedDecision(
            rationale="Some rationale",
            confidence="high",
        )


def test_extracted_action_item_validation():
    """Test ExtractedActionItem schema."""
    # Valid action item
    action = ExtractedActionItem(
        title="Complete design mockups",
        description="Create mockups for new feature",
        owner_name="Alice",
        owner_email="alice@example.com",
        due_date="2025-12-20",
        status="open",
        priority="high",
        confidence="high",
        source_chunk_indices=[5],
    )
    assert action.title == "Complete design mockups"
    assert action.status == "open"
    
    # Can create with minimal fields
    minimal_action = ExtractedActionItem(
        title="Do something",
        confidence="low",
    )
    assert minimal_action.title == "Do something"
    assert minimal_action.status == "open"  # Default value


def test_extracted_entity_validation():
    """Test ExtractedEntity schema."""
    entity = ExtractedEntity(
        kind="company",
        name="Acme Corp",
    )
    assert entity.kind == "company"
    assert entity.name == "Acme Corp"


def test_meeting_intelligence_complete():
    """Test complete MeetingIntelligence object."""
    intelligence = MeetingIntelligence(
        summary_md="# Meeting Summary\n\nThis was a productive meeting.",
        decisions=[
            ExtractedDecision(
                decision="Launch in Q2",
                confidence="high",
                source_chunk_indices=[1],
            )
        ],
        action_items=[
            ExtractedActionItem(
                title="Follow up",
                confidence="medium",
            )
        ],
        tags=["product", "planning"],
        entities=[
            ExtractedEntity(kind="person", name="Alice"),
        ],
    )
    
    assert "Meeting Summary" in intelligence.summary_md
    assert len(intelligence.decisions) == 1
    assert len(intelligence.action_items) == 1
    assert len(intelligence.tags) == 2
    assert len(intelligence.entities) == 1


def test_meeting_intelligence_empty():
    """Test MeetingIntelligence with minimal data."""
    intelligence = MeetingIntelligence(
        summary_md="Brief summary.",
    )
    
    assert intelligence.summary_md == "Brief summary."
    assert intelligence.decisions == []
    assert intelligence.action_items == []
    assert intelligence.tags == []
    assert intelligence.entities == []





