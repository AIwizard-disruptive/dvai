"""
Layer 3: Intelligence Extraction Service
Extracts structured insights with evidence tracking

ZERO FABRICATION - All content grounded in source data
THREE-AGENT WORKFLOW - Generator → Matcher → QA
"""
import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.three_agent_workflow import (
    ThreeAgentWorkflow,
    EvidencePointer,
    ExtractionResult
)

class DecisionExtraction(BaseModel):
    """Extracted decision with evidence"""
    decision: str
    rationale: Optional[str] = None
    impact: Optional[str] = None
    confidence: float
    evidence: List[EvidencePointer]

class ActionItemExtraction(BaseModel):
    """Extracted action item with evidence"""
    title: str
    description: Optional[str] = None
    owner_name: Optional[str] = None  # NULL if not stated
    owner_email: Optional[str] = None  # NULL if not stated
    due_date: Optional[str] = None  # NULL if not stated
    priority: Optional[str] = None  # NULL if not stated
    confidence: float
    evidence: List[EvidencePointer]

class Layer3IntelligenceService:
    """
    Layer 3: Intelligence extraction with evidence
    
    RULES:
    - All extractions use 3-agent workflow
    - Every extracted item has evidence pointers
    - Never fabricate missing fields (use NULL)
    - Log missing data as issues
    - QA goal must be specified
    - Reject items that fail QA
    """
    
    def __init__(self, db: AsyncSession, qa_goal: str = "zero_hallucinations"):
        self.db = db
        self.workflow = ThreeAgentWorkflow(db)
        self.default_qa_goal = qa_goal
    
    async def extract_decisions(
        self,
        meeting_id: uuid.UUID,
        org_id: uuid.UUID,
        qa_goal: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> List[DecisionExtraction]:
        """
        Extract decisions from meeting
        
        Uses 3-agent workflow:
        1. Generator identifies decisions in transcript
        2. Matcher adds evidence pointers
        3. QA verifies no hallucinations
        
        Only approved decisions are returned
        """
        qa_goal = qa_goal or self.default_qa_goal
        correlation_id = correlation_id or str(uuid.uuid4())
        
        # Load normalized transcript
        source_data = await self._load_normalized_transcript(meeting_id)
        
        if not source_data:
            await self._log_issue(
                org_id, "missing_data",
                "critical", "No normalized transcript found for meeting"
            )
            return []
        
        # Run 3-agent workflow
        result = await self.workflow.extract_with_workflow(
            meeting_id=meeting_id,
            org_id=org_id,
            content_type="decisions",
            qa_goal=qa_goal,
            source_data=source_data,
            correlation_id=correlation_id
        )
        
        decisions = []
        
        if result.success and result.content:
            # Store decision with evidence
            decision_id = await self._store_decision(
                meeting_id=meeting_id,
                org_id=org_id,
                data=result.content.content.data,
                evidence=result.content.evidence,
                extraction_run_id=result.extraction_run_id,
                qa_result=result.qa_result
            )
            
            # Store evidence pointers
            await self._store_evidence_pointers(
                artifact_type="decision",
                artifact_id=decision_id,
                evidence=result.content.evidence
            )
            
            decisions.append(DecisionExtraction(
                decision=result.content.content.data.get("decision", ""),
                rationale=result.content.content.data.get("rationale"),
                impact=result.content.content.data.get("impact"),
                confidence=result.content.content.confidence,
                evidence=result.content.evidence
            ))
        else:
            # Log rejection
            await self._log_issue(
                org_id, "qa_failed",
                "warning",
                f"Decision extraction failed QA: {', '.join(result.qa_result.issues)}"
            )
        
        return decisions
    
    async def extract_action_items(
        self,
        meeting_id: uuid.UUID,
        org_id: uuid.UUID,
        qa_goal: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> List[ActionItemExtraction]:
        """
        Extract action items from meeting
        
        CRITICAL:
        - owner_name: NULL if not explicitly stated
        - owner_email: NULL if not explicitly stated  
        - due_date: NULL if not explicitly stated
        - Never guess or infer these fields
        """
        qa_goal = qa_goal or self.default_qa_goal
        correlation_id = correlation_id or str(uuid.uuid4())
        
        source_data = await self._load_normalized_transcript(meeting_id)
        
        if not source_data:
            return []
        
        # Run 3-agent workflow
        result = await self.workflow.extract_with_workflow(
            meeting_id=meeting_id,
            org_id=org_id,
            content_type="action_items",
            qa_goal=qa_goal,
            source_data=source_data,
            correlation_id=correlation_id
        )
        
        action_items = []
        
        if result.success and result.content:
            # Validate no fabrication
            data = result.content.content.data
            
            # Check for fabricated fields
            fabrication_check = self._check_fabrication(data, result.content.evidence)
            if fabrication_check:
                await self._log_issue(
                    org_id, "fabrication_detected",
                    "critical",
                    f"Possible fabrication: {', '.join(fabrication_check)}"
                )
                return []  # Reject if fabrication detected
            
            # Store action item
            action_item_id = await self._store_action_item(
                meeting_id=meeting_id,
                org_id=org_id,
                data=data,
                evidence=result.content.evidence,
                extraction_run_id=result.extraction_run_id,
                qa_result=result.qa_result
            )
            
            # Store evidence
            await self._store_evidence_pointers(
                artifact_type="action_item",
                artifact_id=action_item_id,
                evidence=result.content.evidence
            )
            
            action_items.append(ActionItemExtraction(
                title=data.get("title", ""),
                description=data.get("description"),
                owner_name=data.get("owner_name"),  # May be NULL
                owner_email=data.get("owner_email"),  # May be NULL
                due_date=data.get("due_date"),  # May be NULL
                priority=data.get("priority"),
                confidence=result.content.content.confidence,
                evidence=result.content.evidence
            ))
        
        return action_items
    
    def _check_fabrication(
        self,
        data: Dict,
        evidence: List[EvidencePointer]
    ) -> List[str]:
        """
        Check for fabricated data
        
        Returns list of issues if fabrication detected
        """
        issues = []
        
        # Fields that commonly get fabricated
        sensitive_fields = ["owner_name", "owner_email", "due_date", "company"]
        
        for field in sensitive_fields:
            value = data.get(field)
            if value is not None:
                # Must have evidence for this field
                has_evidence = any(
                    field.lower() in str(e.quote).lower()
                    or str(value).lower() in str(e.quote).lower()
                    for e in evidence
                )
                
                if not has_evidence:
                    issues.append(
                        f"Field '{field}' = '{value}' has no evidence - likely fabricated"
                    )
        
        return issues
    
    async def _load_normalized_transcript(
        self,
        meeting_id: uuid.UUID
    ) -> Optional[Dict]:
        """Load Layer 2 normalized transcript"""
        query = """
        SELECT id, segments, has_pii
        FROM transcripts_normalized
        WHERE meeting_id = :meeting_id
        ORDER BY created_at DESC
        LIMIT 1
        """
        result = await self.db.execute(query, {"meeting_id": meeting_id})
        row = result.fetchone()
        
        if row:
            return {
                "id": row[0],
                "segments": row[1],
                "has_pii": row[2]
            }
        return None
    
    async def _store_decision(
        self,
        meeting_id: uuid.UUID,
        org_id: uuid.UUID,
        data: Dict,
        evidence: List[EvidencePointer],
        extraction_run_id: uuid.UUID,
        qa_result: Any
    ) -> uuid.UUID:
        """Store decision in database"""
        decision_id = uuid.uuid4()
        
        query = """
        INSERT INTO decisions (
            id, meeting_id, org_id,
            decision, rationale, confidence,
            extraction_run_id, qa_passed, qa_issues,
            generator_version
        ) VALUES (
            :id, :meeting_id, :org_id,
            :decision, :rationale, :confidence,
            :extraction_run_id, :qa_passed, :qa_issues,
            :generator_version
        )
        """
        
        await self.db.execute(query, {
            "id": decision_id,
            "meeting_id": meeting_id,
            "org_id": org_id,
            "decision": data.get("decision"),
            "rationale": data.get("rationale"),
            "confidence": data.get("confidence"),
            "extraction_run_id": extraction_run_id,
            "qa_passed": qa_result.approved,
            "qa_issues": qa_result.issues,
            "generator_version": "1.0.0"
        })
        
        await self.db.commit()
        return decision_id
    
    async def _store_action_item(
        self,
        meeting_id: uuid.UUID,
        org_id: uuid.UUID,
        data: Dict,
        evidence: List[EvidencePointer],
        extraction_run_id: uuid.UUID,
        qa_result: Any
    ) -> uuid.UUID:
        """Store action item in database"""
        action_item_id = uuid.uuid4()
        
        query = """
        INSERT INTO action_items (
            id, meeting_id, org_id,
            title, description,
            owner_name, owner_email, due_date, priority,
            status, confidence,
            extraction_run_id, qa_passed, qa_issues,
            generator_version
        ) VALUES (
            :id, :meeting_id, :org_id,
            :title, :description,
            :owner_name, :owner_email, :due_date, :priority,
            :status, :confidence,
            :extraction_run_id, :qa_passed, :qa_issues,
            :generator_version
        )
        """
        
        await self.db.execute(query, {
            "id": action_item_id,
            "meeting_id": meeting_id,
            "org_id": org_id,
            "title": data.get("title"),
            "description": data.get("description"),
            "owner_name": data.get("owner_name"),  # NULL if not stated
            "owner_email": data.get("owner_email"),  # NULL if not stated
            "due_date": data.get("due_date"),  # NULL if not stated
            "priority": data.get("priority"),
            "status": "open",
            "confidence": data.get("confidence"),
            "extraction_run_id": extraction_run_id,
            "qa_passed": qa_result.approved,
            "qa_issues": qa_result.issues,
            "generator_version": "1.0.0"
        })
        
        await self.db.commit()
        return action_item_id
    
    async def _store_evidence_pointers(
        self,
        artifact_type: str,
        artifact_id: uuid.UUID,
        evidence: List[EvidencePointer]
    ):
        """Store evidence pointers for traceability"""
        for ev in evidence:
            query = """
            INSERT INTO evidence_pointers (
                id, artifact_type, artifact_id,
                source_table, source_id, source_field,
                quote, relevance_score
            ) VALUES (
                :id, :artifact_type, :artifact_id,
                :source_table, :source_id, :source_field,
                :quote, :relevance_score
            )
            """
            
            await self.db.execute(query, {
                "id": uuid.uuid4(),
                "artifact_type": artifact_type,
                "artifact_id": artifact_id,
                "source_table": ev.source_table,
                "source_id": ev.source_id,
                "source_field": ev.source_field,
                "quote": ev.quote,
                "relevance_score": ev.relevance_score
            })
        
        await self.db.commit()
    
    async def _log_issue(
        self,
        org_id: uuid.UUID,
        issue_type: str,
        severity: str,
        description: str
    ):
        """Log issue"""
        query = """
        INSERT INTO issues (
            id, org_id, issue_type, severity, description
        ) VALUES (
            :id, :org_id, :issue_type, :severity, :description
        )
        """
        await self.db.execute(query, {
            "id": uuid.uuid4(),
            "org_id": org_id,
            "issue_type": issue_type,
            "severity": severity,
            "description": description
        })
        await self.db.commit()





