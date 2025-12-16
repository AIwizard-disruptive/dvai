"""
Agent 2: Analyzer Service
Purpose: Interpret extracted data and generate structured insights
Rule: ONLY analyze what was extracted - distinguish stated vs implied vs unknown
"""

import json
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime

from pydantic import BaseModel, Field
from openai import AsyncOpenAI

from app.config import settings
from app.services.agent_1_extractor import ExtractionResult


class DocumentClassification(str, Enum):
    """Document types with detailed classifications."""
    PITCH_DECK_PRE_SEED = "pitch_deck_pre_seed"
    PITCH_DECK_SEED = "pitch_deck_seed"
    PITCH_DECK_SERIES_A = "pitch_deck_series_a"
    PITCH_DECK_SERIES_B_PLUS = "pitch_deck_series_b_plus"
    FINANCIAL_REPORT_QUARTERLY = "financial_report_quarterly"
    FINANCIAL_REPORT_ANNUAL = "financial_report_annual"
    LEGAL_TERM_SHEET = "legal_term_sheet"
    LEGAL_CONTRACT = "legal_contract"
    MEETING_NOTES = "meeting_notes"
    MARKET_RESEARCH = "market_research"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    OTHER = "other"


class MetricValue(BaseModel):
    """A single metric extracted from the document."""
    value: Any  # The actual value
    unit: Optional[str] = None  # e.g., "USD", "%", "users"
    source_citation: str  # "page 3, paragraph 2" or "slide 8"
    confidence: float = Field(ge=0.0, le=1.0)
    note: Optional[str] = None  # e.g., "Not explicitly stated - inferred from chart"
    stated: bool = True  # True if explicitly stated, False if inferred


class Insight(BaseModel):
    """An insight derived from the document."""
    claim: str  # The insight statement
    category: str  # "financial", "market", "team", "product", "risk"
    supporting_evidence: List[str]  # Citations to source data
    confidence: float = Field(ge=0.0, le=1.0)
    stated_vs_implied: str  # "stated", "implied", "inferred"


class Gap(BaseModel):
    """Missing or unclear information."""
    metric: str
    importance: str  # "critical", "high", "medium", "low"
    note: str


class AnalysisResult(BaseModel):
    """Complete analysis result from Agent 2."""
    # Classification
    classification: DocumentClassification
    classification_confidence: float = Field(ge=0.0, le=1.0)
    
    # Key metrics (with sources)
    key_metrics: Dict[str, MetricValue] = Field(default_factory=dict)
    
    # Insights
    insights: List[Insight] = Field(default_factory=list)
    risks_identified: List[Insight] = Field(default_factory=list)
    opportunities_identified: List[Insight] = Field(default_factory=list)
    
    # Quality indicators
    confidence_breakdown: Dict[str, float] = Field(default_factory=dict)
    overall_confidence: float = Field(ge=0.0, le=1.0)
    data_completeness: float = Field(ge=0.0, le=1.0)  # % of expected fields found
    internal_consistency: bool = True  # Any contradictions?
    inconsistencies: List[str] = Field(default_factory=list)
    
    # Gaps
    gaps: List[Gap] = Field(default_factory=list)
    
    # Review flags
    requires_human_review: bool = False
    review_reason: Optional[str] = None
    
    # Metadata
    analyzer_version: str = "1.0.0"
    analyzer_model: str = "gpt-4o-2024-08-06"
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    extraction_confidence: float  # Input quality from Agent 1


class AnalyzerAgent:
    """
    Agent 2: Analyzer
    
    Interprets extracted data and generates insights that are 100% grounded in source material.
    
    Rules:
    - ONLY analyze what was extracted (no external knowledge)
    - Distinguish clearly: stated facts vs implied vs unknown
    - Cite source for EVERY metric
    - Flag inconsistencies within document
    - Never use "typically", "usually", "likely" without source
    - No industry benchmarks unless stated in document
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.version = "1.0.0"
        self.model = "gpt-4o-2024-08-06"
    
    async def analyze(
        self,
        extraction_result: ExtractionResult,
        document_context: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """
        Analyze extracted data and generate structured insights.
        
        Args:
            extraction_result: Output from Agent 1 (Extractor)
            document_context: Optional context (filename, upload date, etc.)
        
        Returns:
            AnalysisResult with classification, metrics, insights, gaps
        """
        
        # Build analysis prompt
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(extraction_result, document_context)
        
        # Call OpenAI with structured output
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "analysis_result",
                    "strict": True,
                    "schema": self._get_analysis_schema(),
                },
            },
            temperature=0.1,  # Low temperature for factual analysis
        )
        
        # Parse response
        content = response.choices[0].message.content
        data = json.loads(content)
        
        # Post-process and validate
        analysis = self._validate_and_enhance(data, extraction_result)
        
        return analysis
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with strict anti-hallucination rules."""
        
        return """You are an expert document analyst. Your job is to analyze extracted document data with PERFECT accuracy and ZERO hallucinations.

ABSOLUTE RULES:
1. ONLY analyze what is in the extracted text. Do NOT use external knowledge.
2. Distinguish clearly between:
   - STATED facts: Explicitly written in the document
   - IMPLIED facts: Can be reasonably inferred from stated facts
   - UNKNOWN: Not mentioned or unclear
3. EVERY metric must have a source citation (page number, section, etc.)
4. If information is missing, mark as "unknown" - DO NOT fill gaps
5. Flag inconsistencies within the document

FORBIDDEN PHRASES (unless directly quoted from document):
- "typically"
- "usually"
- "industry standard"
- "estimated" (without source)
- "approximately" (without source)
- "likely"
- "probably"

CONFIDENCE SCORING:
- 1.0 (100%): Explicitly stated with clear source
- 0.8-0.9: Clearly implied from multiple data points
- 0.6-0.7: Inferred from limited information
- 0.4-0.5: Unclear or ambiguous
- 0.0-0.3: Not found or highly uncertain

OUTPUT STRUCTURE:
- Classification: Document type based on content and structure
- Key Metrics: Extract all quantitative data with sources
- Insights: Factual observations grounded in data
- Risks: Issues or concerns identified in the document
- Opportunities: Positive indicators mentioned
- Gaps: What information is missing
- Inconsistencies: Any contradictions found

EXAMPLES:

✅ GOOD:
{
  "metric": "revenue",
  "value": "$2M ARR",
  "source_citation": "page 8, revenue chart",
  "confidence": 1.0,
  "stated": true
}

❌ BAD (hallucination):
{
  "metric": "burn_rate",
  "value": "$100K/month",
  "note": "Typical for a company of this size",
  "confidence": 0.8,
  "stated": false
}

✅ GOOD (handling missing data):
{
  "metric": "burn_rate",
  "value": null,
  "note": "Not disclosed in document",
  "confidence": 0.0,
  "stated": false
}

Now analyze the provided document extraction."""
    
    def _build_user_prompt(
        self,
        extraction_result: ExtractionResult,
        document_context: Optional[Dict[str, Any]]
    ) -> str:
        """Build user prompt with extraction data."""
        
        prompt_parts = [
            "DOCUMENT EXTRACTION:",
            "",
            "=== EXTRACTED TEXT ===",
            extraction_result.extracted_text[:15000],  # Truncate if too long
            "",
            "=== EXTRACTED ENTITIES ===",
        ]
        
        # Add entities
        for entity in extraction_result.entities[:100]:  # Limit to 100
            prompt_parts.append(
                f"- {entity.type.value}: '{entity.value}' "
                f"(source: {entity.source_location}, confidence: {entity.confidence:.2f})"
            )
        
        # Add tables
        if extraction_result.tables:
            prompt_parts.extend([
                "",
                "=== EXTRACTED TABLES ===",
            ])
            for table in extraction_result.tables[:10]:  # Limit to 10 tables
                prompt_parts.append(f"\nTable at {table.location}:")
                prompt_parts.append(f"Headers: {table.headers}")
                prompt_parts.append(f"Rows: {len(table.rows)}")
                if table.malformed:
                    prompt_parts.append("⚠️ Table structure is malformed")
        
        # Add ambiguities
        if extraction_result.ambiguities:
            prompt_parts.extend([
                "",
                "=== AMBIGUITIES FLAGGED BY EXTRACTOR ===",
            ])
            for amb in extraction_result.ambiguities:
                prompt_parts.append(f"- {amb.location}: {amb.issue}")
        
        # Add context
        if document_context:
            prompt_parts.extend([
                "",
                "=== DOCUMENT CONTEXT ===",
                f"Filename: {document_context.get('filename', 'N/A')}",
                f"Upload date: {document_context.get('uploaded_at', 'N/A')}",
            ])
        
        prompt_parts.extend([
            "",
            "=== EXTRACTION QUALITY ===",
            f"Overall confidence: {extraction_result.confidence_score:.2f}",
            f"OCR used: {extraction_result.ocr_used}",
            "",
            "Now provide your analysis following the strict rules above.",
        ])
        
        return "\n".join(prompt_parts)
    
    def _get_analysis_schema(self) -> Dict[str, Any]:
        """Get JSON schema for structured analysis output."""
        
        return {
            "type": "object",
            "properties": {
                "classification": {
                    "type": "string",
                    "enum": [c.value for c in DocumentClassification]
                },
                "classification_confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "key_metrics": {
                    "type": "object",
                    "additionalProperties": {
                        "type": "object",
                        "properties": {
                            "value": {"type": ["string", "number", "null"]},
                            "unit": {"type": ["string", "null"]},
                            "source_citation": {"type": "string"},
                            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                            "note": {"type": ["string", "null"]},
                            "stated": {"type": "boolean"}
                        },
                        "required": ["value", "source_citation", "confidence", "stated"],
                        "additionalProperties": False
                    }
                },
                "insights": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "claim": {"type": "string"},
                            "category": {"type": "string"},
                            "supporting_evidence": {"type": "array", "items": {"type": "string"}},
                            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                            "stated_vs_implied": {"type": "string", "enum": ["stated", "implied", "inferred"]}
                        },
                        "required": ["claim", "category", "supporting_evidence", "confidence", "stated_vs_implied"],
                        "additionalProperties": False
                    }
                },
                "risks_identified": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "claim": {"type": "string"},
                            "category": {"type": "string"},
                            "supporting_evidence": {"type": "array", "items": {"type": "string"}},
                            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                            "stated_vs_implied": {"type": "string"}
                        },
                        "required": ["claim", "category", "supporting_evidence", "confidence", "stated_vs_implied"],
                        "additionalProperties": False
                    }
                },
                "gaps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "metric": {"type": "string"},
                            "importance": {"type": "string", "enum": ["critical", "high", "medium", "low"]},
                            "note": {"type": "string"}
                        },
                        "required": ["metric", "importance", "note"],
                        "additionalProperties": False
                    }
                },
                "inconsistencies": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "data_completeness": {"type": "number", "minimum": 0, "maximum": 1}
            },
            "required": [
                "classification", "classification_confidence", "key_metrics",
                "insights", "risks_identified", "gaps", "inconsistencies", "data_completeness"
            ],
            "additionalProperties": False
        }
    
    def _validate_and_enhance(
        self,
        llm_output: Dict[str, Any],
        extraction_result: ExtractionResult
    ) -> AnalysisResult:
        """Validate LLM output and calculate additional metrics."""
        
        # Parse key metrics
        key_metrics = {}
        for metric_name, metric_data in llm_output.get("key_metrics", {}).items():
            key_metrics[metric_name] = MetricValue(**metric_data)
        
        # Parse insights
        insights = [Insight(**ins) for ins in llm_output.get("insights", [])]
        risks = [Insight(**risk) for risk in llm_output.get("risks_identified", [])]
        opportunities = [Insight(**opp) for opp in llm_output.get("opportunities_identified", [])]
        
        # Parse gaps
        gaps = [Gap(**gap) for gap in llm_output.get("gaps", [])]
        
        # Calculate confidence breakdown
        confidence_breakdown = {
            "extraction": extraction_result.confidence_score,
            "classification": llm_output.get("classification_confidence", 0.5),
            "metrics": (
                sum(m.confidence for m in key_metrics.values()) / len(key_metrics)
                if key_metrics else 0.0
            ),
            "insights": (
                sum(i.confidence for i in insights) / len(insights)
                if insights else 0.0
            ),
        }
        
        # Calculate overall confidence
        overall_confidence = sum(confidence_breakdown.values()) / len(confidence_breakdown)
        
        # Determine if human review is required
        requires_human_review = False
        review_reason = None
        
        if overall_confidence < 0.7:
            requires_human_review = True
            review_reason = f"Low overall confidence ({overall_confidence:.2f})"
        elif extraction_result.confidence_score < 0.6:
            requires_human_review = True
            review_reason = f"Low extraction quality ({extraction_result.confidence_score:.2f})"
        elif len(llm_output.get("inconsistencies", [])) > 0:
            requires_human_review = True
            review_reason = "Internal inconsistencies found"
        elif any(gap.importance == "critical" for gap in gaps):
            requires_human_review = True
            review_reason = "Critical information gaps"
        
        # Check internal consistency
        internal_consistency = len(llm_output.get("inconsistencies", [])) == 0
        
        return AnalysisResult(
            classification=DocumentClassification(llm_output["classification"]),
            classification_confidence=llm_output["classification_confidence"],
            key_metrics=key_metrics,
            insights=insights,
            risks_identified=risks,
            opportunities_identified=opportunities,
            confidence_breakdown=confidence_breakdown,
            overall_confidence=overall_confidence,
            data_completeness=llm_output.get("data_completeness", 0.5),
            internal_consistency=internal_consistency,
            inconsistencies=llm_output.get("inconsistencies", []),
            gaps=gaps,
            requires_human_review=requires_human_review,
            review_reason=review_reason,
            extraction_confidence=extraction_result.confidence_score
        )


# Singleton instance
_analyzer_agent: Optional[AnalyzerAgent] = None


def get_analyzer_agent() -> AnalyzerAgent:
    """Get or create analyzer agent instance."""
    global _analyzer_agent
    if _analyzer_agent is None:
        _analyzer_agent = AnalyzerAgent()
    return _analyzer_agent

