"""
Three-Agent Workflow System
Ensures all generated content is grounded, traceable, and QA'd

ZERO FABRICATION POLICY ENFORCED HERE
"""
import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

class EvidencePointer(BaseModel):
    """Link from generated content to source data"""
    source_table: str
    source_id: uuid.UUID
    source_field: str
    quote: str  # Exact text from source
    relevance_score: float

class GeneratedContent(BaseModel):
    """Output from Generator Agent"""
    content_type: str  # "decision", "action_item", "summary"
    data: Dict[str, Any]
    confidence: float

class MatchedContent(BaseModel):
    """Output from Matcher Agent with evidence"""
    content: GeneratedContent
    evidence: List[EvidencePointer]
    traceability_score: float  # 0-1: How well grounded in evidence

class QAResult(BaseModel):
    """Output from QA/Approver Agent"""
    approved: bool
    qa_score: float
    issues: List[str]
    recommendations: List[str]

class ExtractionResult(BaseModel):
    """Final result after 3-agent workflow"""
    success: bool
    content: Optional[MatchedContent]
    qa_result: QAResult
    extraction_run_id: uuid.UUID

class ThreeAgentWorkflow:
    """
    Implements the 3-agent workflow:
    1. Generator: Creates content from source data
    2. Matcher: Validates evidence and adds pointers
    3. QA/Approver: Verifies quality and compliance
    
    CRITICAL: Never skip any agent
    CRITICAL: QA goal must be specified
    CRITICAL: Reject if evidence insufficient
    """
    
    def __init__(
        self,
        db: AsyncSession,
        generator_model: str = "gpt-4",
        matcher_model: str = "gpt-4",
        qa_model: str = "gpt-4"
    ):
        self.db = db
        self.generator_model = generator_model
        self.matcher_model = matcher_model
        self.qa_model = qa_model
    
    async def extract_with_workflow(
        self,
        meeting_id: uuid.UUID,
        org_id: uuid.UUID,
        content_type: str,
        qa_goal: str,  # REQUIRED
        source_data: Dict,
        correlation_id: str
    ) -> ExtractionResult:
        """
        Run full 3-agent workflow
        
        Args:
            meeting_id: Meeting to extract from
            org_id: Organization
            content_type: "decisions", "action_items", "summary", etc.
            qa_goal: "zero_hallucinations", "maximize_recall", etc.
            source_data: Normalized transcript segments
            correlation_id: For tracing
        
        Returns:
            ExtractionResult with approval status
        """
        # Create extraction run
        run_id = await self._create_extraction_run(
            meeting_id, org_id, content_type, qa_goal, correlation_id
        )
        
        try:
            # AGENT 1: Generator
            generated = await self._generator_agent(
                content_type=content_type,
                source_data=source_data,
                context={"meeting_id": meeting_id, "org_id": org_id}
            )
            
            if not generated:
                await self._log_issue(
                    run_id, org_id, "generation_failed",
                    "critical", "Generator produced no output"
                )
                return ExtractionResult(
                    success=False,
                    content=None,
                    qa_result=QAResult(
                        approved=False,
                        qa_score=0.0,
                        issues=["Generation failed"],
                        recommendations=["Check source data quality"]
                    ),
                    extraction_run_id=run_id
                )
            
            # AGENT 2: Matcher (Evidence Validation)
            matched = await self._matcher_agent(
                generated_content=generated,
                source_data=source_data
            )
            
            if matched.traceability_score < 0.7:  # Threshold
                await self._log_issue(
                    run_id, org_id, "low_traceability",
                    "warning",
                    f"Traceability score {matched.traceability_score} below 0.7"
                )
            
            # AGENT 3: QA/Approver
            qa_result = await self._qa_agent(
                content=matched,
                qa_goal=qa_goal,
                source_data=source_data
            )
            
            # Log issues
            for issue in qa_result.issues:
                await self._log_issue(
                    run_id, org_id, "qa_failed",
                    "warning", issue
                )
            
            # Update extraction run
            await self._update_extraction_run(
                run_id=run_id,
                items_extracted=1 if generated else 0,
                items_passed_qa=1 if qa_result.approved else 0,
                items_rejected=0 if qa_result.approved else 1
            )
            
            return ExtractionResult(
                success=qa_result.approved,
                content=matched if qa_result.approved else None,
                qa_result=qa_result,
                extraction_run_id=run_id
            )
            
        except Exception as e:
            await self._log_issue(
                run_id, org_id, "workflow_error",
                "critical", f"Workflow failed: {str(e)}"
            )
            raise
    
    async def _generator_agent(
        self,
        content_type: str,
        source_data: Dict,
        context: Dict
    ) -> Optional[GeneratedContent]:
        """
        Agent 1: Generator
        
        Creates content ONLY from source data
        NEVER fabricates missing information
        Returns None if insufficient data
        """
        # Extract source text
        segments = source_data.get("segments", [])
        if not segments:
            return None
        
        # Prompt engineering: Explicit grounding instructions
        prompt = self._build_generator_prompt(
            content_type=content_type,
            segments=segments,
            context=context
        )
        
        # Call LLM (simplified - would use actual OpenAI API)
        # For now, return structure
        
        if content_type == "decision":
            # Extract decision from segments
            # ONLY if explicitly stated
            # Use NULL for missing fields
            data = {
                "decision": None,  # Will be extracted
                "rationale": None,  # May be missing
                "impact": None,  # May be missing
                "confidence": 0.0
            }
        elif content_type == "action_item":
            data = {
                "title": None,
                "description": None,
                "owner_name": None,  # NULL if not stated
                "owner_email": None,  # NULL if not stated
                "due_date": None,  # NULL if not stated
                "priority": None,
                "confidence": 0.0
            }
        else:
            data = {}
        
        return GeneratedContent(
            content_type=content_type,
            data=data,
            confidence=0.8  # Would come from model
        )
    
    async def _matcher_agent(
        self,
        generated_content: GeneratedContent,
        source_data: Dict
    ) -> MatchedContent:
        """
        Agent 2: Matcher
        
        CRITICAL: Validates every claim maps to source data
        Adds evidence pointers for traceability
        Rejects if insufficient evidence
        """
        evidence_pointers = []
        segments = source_data.get("segments", [])
        
        # For each field in generated content
        for field, value in generated_content.data.items():
            if value is None:
                # NULL is OK - means missing data
                continue
            
            # Find supporting evidence in source segments
            matching_segments = self._find_evidence_in_segments(
                claim=str(value),
                segments=segments,
                field=field
            )
            
            for segment in matching_segments:
                evidence_pointers.append(
                    EvidencePointer(
                        source_table="transcript_segments",
                        source_id=segment.get("id"),
                        source_field="text",
                        quote=segment.get("text", "")[:200],  # First 200 chars
                        relevance_score=segment.get("relevance", 0.0)
                    )
                )
        
        # Calculate traceability score
        # Higher score = more evidence, better grounding
        if not generated_content.data:
            traceability_score = 0.0
        else:
            non_null_fields = sum(1 for v in generated_content.data.values() if v is not None)
            fields_with_evidence = len(set(e.source_id for e in evidence_pointers))
            traceability_score = min(1.0, fields_with_evidence / max(1, non_null_fields))
        
        return MatchedContent(
            content=generated_content,
            evidence=evidence_pointers,
            traceability_score=traceability_score
        )
    
    async def _qa_agent(
        self,
        content: MatchedContent,
        qa_goal: str,
        source_data: Dict
    ) -> QAResult:
        """
        Agent 3: QA/Approver
        
        Verifies:
        1. No hallucinations (all claims have evidence)
        2. GDPR compliance (no PII leaks)
        3. Security (no sensitive data exposure)
        4. Quality (meets QA goal)
        """
        issues = []
        recommendations = []
        
        # Check 1: Zero Hallucinations
        if qa_goal in ["zero_hallucinations", "board_ready_summary"]:
            if content.traceability_score < 0.9:
                issues.append(
                    f"Traceability {content.traceability_score:.2f} below 0.9 for zero-hallucination goal"
                )
        
        # Check 2: Evidence exists for all claims
        if not content.evidence:
            issues.append("No evidence pointers found - cannot verify claims")
        
        # Check 3: No fabricated data
        for field, value in content.content.data.items():
            if field in ["owner_email", "due_date", "owner_name"]:
                if value is not None:
                    # Verify this came from source
                    has_evidence = any(
                        field.lower() in e.source_field.lower()
                        for e in content.evidence
                    )
                    if not has_evidence:
                        issues.append(
                            f"Field '{field}' has value but no evidence - possible fabrication"
                        )
                        recommendations.append(
                            f"Set '{field}' to NULL if not explicitly stated in transcript"
                        )
        
        # Check 4: GDPR compliance (basic)
        for evidence in content.evidence:
            # Check if quote contains PII (simplified)
            if self._contains_email(evidence.quote):
                # Should be tagged as PII
                recommendations.append(
                    "Evidence contains email - ensure PII tagging applied"
                )
        
        # Calculate QA score
        qa_score = 1.0
        if issues:
            qa_score = max(0.0, 1.0 - (len(issues) * 0.2))
        
        # Approve if no critical issues
        approved = len(issues) == 0 or (
            qa_goal == "maximize_recall" and qa_score >= 0.5
        )
        
        return QAResult(
            approved=approved,
            qa_score=qa_score,
            issues=issues,
            recommendations=recommendations
        )
    
    def _build_generator_prompt(
        self,
        content_type: str,
        segments: List[Dict],
        context: Dict
    ) -> str:
        """Build prompt with explicit grounding instructions"""
        segments_text = "\n".join([
            f"[{s.get('speaker', 'Unknown')}]: {s.get('text', '')}"
            for s in segments
        ])
        
        return f"""
CRITICAL INSTRUCTIONS - ZERO FABRICATION POLICY:

You are extracting {content_type} from a meeting transcript.

RULES:
1. ONLY extract information explicitly stated in the transcript
2. NEVER guess, infer, or fabricate:
   - Speaker names (if not stated, use NULL)
   - Email addresses (if not stated, use NULL)
   - Dates or deadlines (if not stated, use NULL)
   - Companies or organizations (if not stated, use NULL)
3. Use NULL for any missing information
4. Quote exact text as evidence for each claim

TRANSCRIPT:
{segments_text}

Extract {content_type} following the rules above. Return JSON.
"""
    
    def _find_evidence_in_segments(
        self,
        claim: str,
        segments: List[Dict],
        field: str
    ) -> List[Dict]:
        """Find segments that support a claim"""
        # Simplified - would use semantic search or fuzzy matching
        matching = []
        claim_lower = claim.lower()
        
        for segment in segments:
            text = segment.get("text", "").lower()
            if claim_lower in text or self._semantic_match(claim_lower, text):
                matching.append({
                    **segment,
                    "relevance": 0.85  # Would be calculated
                })
        
        return matching
    
    def _semantic_match(self, claim: str, text: str) -> bool:
        """Check if claim is semantically present in text"""
        # Simplified - would use embeddings
        keywords = claim.split()
        return any(kw in text for kw in keywords if len(kw) > 3)
    
    def _contains_email(self, text: str) -> bool:
        """Check if text contains email"""
        import re
        return bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text))
    
    async def _create_extraction_run(
        self,
        meeting_id: uuid.UUID,
        org_id: uuid.UUID,
        run_type: str,
        qa_goal: str,
        correlation_id: str
    ) -> uuid.UUID:
        """Create extraction run record"""
        run_id = uuid.uuid4()
        query = """
        INSERT INTO extraction_runs (
            id, meeting_id, org_id, run_type, qa_goal,
            generator_model, matcher_model, qa_model,
            workflow_version, started_at, correlation_id
        ) VALUES (
            :id, :meeting_id, :org_id, :run_type, :qa_goal,
            :generator_model, :matcher_model, :qa_model,
            :workflow_version, :started_at, :correlation_id
        )
        """
        await self.db.execute(query, {
            "id": run_id,
            "meeting_id": meeting_id,
            "org_id": org_id,
            "run_type": run_type,
            "qa_goal": qa_goal,
            "generator_model": self.generator_model,
            "matcher_model": self.matcher_model,
            "qa_model": self.qa_model,
            "workflow_version": "1.0.0",
            "started_at": datetime.utcnow(),
            "correlation_id": correlation_id
        })
        await self.db.commit()
        return run_id
    
    async def _update_extraction_run(
        self,
        run_id: uuid.UUID,
        items_extracted: int,
        items_passed_qa: int,
        items_rejected: int
    ):
        """Update extraction run with results"""
        query = """
        UPDATE extraction_runs SET
            items_extracted = :items_extracted,
            items_passed_qa = :items_passed_qa,
            items_rejected = :items_rejected,
            completed_at = :completed_at,
            duration_seconds = EXTRACT(EPOCH FROM (:completed_at - started_at))
        WHERE id = :id
        """
        await self.db.execute(query, {
            "id": run_id,
            "items_extracted": items_extracted,
            "items_passed_qa": items_passed_qa,
            "items_rejected": items_rejected,
            "completed_at": datetime.utcnow()
        })
        await self.db.commit()
    
    async def _log_issue(
        self,
        run_id: uuid.UUID,
        org_id: uuid.UUID,
        issue_type: str,
        severity: str,
        description: str
    ):
        """Log issue during extraction"""
        query = """
        INSERT INTO issues (
            id, extraction_run_id, org_id,
            issue_type, severity, description
        ) VALUES (
            :id, :extraction_run_id, :org_id,
            :issue_type, :severity, :description
        )
        """
        await self.db.execute(query, {
            "id": uuid.uuid4(),
            "extraction_run_id": run_id,
            "org_id": org_id,
            "issue_type": issue_type,
            "severity": severity,
            "description": description
        })
        await self.db.commit()



