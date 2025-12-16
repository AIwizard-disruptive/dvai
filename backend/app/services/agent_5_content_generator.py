"""
Agent 5: Content Generator Service
Purpose: Generate professional reports with 100% citation coverage
Rule: EVERY statement must be cited - distinguish document vs research vs analysis
"""

import json
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime

from pydantic import BaseModel, Field
from openai import AsyncOpenAI
import markdown

from app.config import settings
from app.services.agent_2_analyzer import AnalysisResult
from app.services.agent_3_researcher import ResearchResult
from app.services.agent_4_question_generator import QuestionSet


class ContentType(str, Enum):
    """Types of content that can be generated."""
    DUE_DILIGENCE = "due_diligence"
    SWOT_ANALYSIS = "swot_analysis"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    INVESTMENT_MEMO = "investment_memo"
    EXECUTIVE_SUMMARY = "executive_summary"
    RISK_ASSESSMENT = "risk_assessment"
    MARKET_ANALYSIS = "market_analysis"
    FINANCIAL_SUMMARY = "financial_summary"


class ConfidenceLevel(str, Enum):
    """Confidence in generated content."""
    HIGH = "high"  # 0.8+
    MEDIUM = "medium"  # 0.6-0.79
    LOW = "low"  # < 0.6


class Citation(BaseModel):
    """A citation reference."""
    ref_id: str  # e.g., "[1]"
    source_type: str  # "document", "research", "analysis"
    source_text: str  # Full citation text
    url: Optional[str] = None


class GeneratedContent(BaseModel):
    """Generated content with citations."""
    content_type: ContentType
    content_markdown: str
    content_html: Optional[str] = None
    
    # Quality metrics
    citations: List[Citation] = Field(default_factory=list)
    citation_coverage: float = Field(ge=0.0, le=1.0)  # % of claims cited
    confidence_level: ConfidenceLevel
    
    # Metadata
    disclaimer: str
    word_count: int
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generator_version: str = "1.0.0"


class ContentGeneratorAgent:
    """
    Agent 5: Content Generator
    
    Generates professional analysis documents with complete citation coverage.
    
    Rules:
    - EVERY factual statement must have inline citation
    - Distinguish: document facts vs research vs analysis/opinion
    - Include "Unknown/Missing Data" section
    - Add disclaimer about data sources and dates
    - Use professional, objective tone
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.version = "1.0.0"
    
    async def generate(
        self,
        content_type: ContentType,
        analysis_result: AnalysisResult,
        research_results: Optional[List[ResearchResult]] = None,
        questions: Optional[QuestionSet] = None,
        company_name: Optional[str] = None,
        document_date: Optional[str] = None
    ) -> GeneratedContent:
        """
        Generate professional content with full citations.
        
        Args:
            content_type: Type of content to generate
            analysis_result: Output from Agent 2
            research_results: Output from Agent 3
            questions: Output from Agent 4
            company_name: Company name
            document_date: Date of source document
        
        Returns:
            GeneratedContent with markdown, citations, quality metrics
        """
        
        # Build context
        context = self._build_context(
            analysis_result, research_results, questions,
            company_name, document_date
        )
        
        # Generate content based on type
        if content_type == ContentType.DUE_DILIGENCE:
            content_md = await self._generate_due_diligence(context)
        elif content_type == ContentType.SWOT_ANALYSIS:
            content_md = await self._generate_swot(context)
        elif content_type == ContentType.EXECUTIVE_SUMMARY:
            content_md = await self._generate_executive_summary(context)
        elif content_type == ContentType.INVESTMENT_MEMO:
            content_md = await self._generate_investment_memo(context)
        elif content_type == ContentType.RISK_ASSESSMENT:
            content_md = await self._generate_risk_assessment(context)
        else:
            content_md = await self._generate_generic_report(context, content_type)
        
        # Parse citations
        citations = self._extract_citations(content_md)
        
        # Calculate citation coverage
        citation_coverage = self._calculate_citation_coverage(content_md)
        
        # Determine confidence level
        confidence = self._determine_confidence(
            analysis_result, citation_coverage
        )
        
        # Generate disclaimer
        disclaimer = self._generate_disclaimer(document_date)
        
        # Convert to HTML
        content_html = markdown.markdown(content_md, extensions=['tables', 'fenced_code'])
        
        return GeneratedContent(
            content_type=content_type,
            content_markdown=content_md,
            content_html=content_html,
            citations=citations,
            citation_coverage=citation_coverage,
            confidence_level=confidence,
            disclaimer=disclaimer,
            word_count=len(content_md.split())
        )
    
    def _build_context(
        self,
        analysis_result: AnalysisResult,
        research_results: Optional[List[ResearchResult]],
        questions: Optional[QuestionSet],
        company_name: Optional[str],
        document_date: Optional[str]
    ) -> Dict[str, Any]:
        """Build structured context for content generation."""
        
        return {
            "company_name": company_name or "Unknown",
            "document_date": document_date or "Unknown",
            "classification": analysis_result.classification.value,
            "key_metrics": {
                name: {
                    "value": str(metric.value),
                    "source": metric.source_citation,
                    "confidence": metric.confidence,
                    "stated": metric.stated
                }
                for name, metric in analysis_result.key_metrics.items()
            },
            "insights": [
                {
                    "claim": ins.claim,
                    "category": ins.category,
                    "evidence": ins.supporting_evidence,
                    "type": ins.stated_vs_implied
                }
                for ins in analysis_result.insights
            ],
            "risks": [
                {
                    "claim": risk.claim,
                    "category": risk.category,
                    "evidence": risk.supporting_evidence
                }
                for risk in analysis_result.risks_identified
            ],
            "gaps": [
                {
                    "metric": gap.metric,
                    "importance": gap.importance,
                    "note": gap.note
                }
                for gap in analysis_result.gaps
            ],
            "research": [
                {
                    "claim": res.claim,
                    "status": res.verification_status.value,
                    "sources": len(res.public_sources),
                    "discrepancies": [
                        {
                            "document": disc.claim_from_document,
                            "research": disc.finding_from_research,
                            "severity": disc.severity
                        }
                        for disc in res.discrepancies
                    ]
                }
                for res in (research_results or [])
            ],
            "questions": {
                "critical": [q.question for q in (questions.critical if questions else [])],
                "high": [q.question for q in (questions.high_priority if questions else [])]
            },
            "overall_confidence": analysis_result.overall_confidence,
            "data_completeness": analysis_result.data_completeness
        }
    
    async def _generate_due_diligence(self, context: Dict[str, Any]) -> str:
        """Generate due diligence report."""
        
        system_prompt = """You are a venture capital analyst writing a due diligence report.

CRITICAL RULES:
1. EVERY factual claim must have inline citation: [^1]
2. Distinguish clearly:
   - From document: "According to the pitch deck (slide 5)...[^1]"
   - From research: "Crunchbase reports...[^2]"
   - Analysis/opinion: "Based on the stated metrics, potential concerns include..."
3. Include "Unknown/Missing Data" section listing gaps
4. Use professional, objective tone
5. No speculation beyond what data supports

CITATION FORMAT:
- Use [^N] for inline citations
- Include sources section at end with full references
- Number citations sequentially

STRUCTURE:
# Due Diligence Report: [Company Name]

## Executive Summary
[2-3 paragraphs with key findings, all cited]

## Company Overview
[Classification, stage, sector - from document]

## Financials
[Revenue, funding, burn - with sources or mark as unknown]

## Team & Organization
[Key team members mentioned in document]

## Product & Market
[What's stated about product, market size, competition]

## Risks Identified
[Numbered list of risks with evidence]

## Unknown/Missing Data
[Bullet list of critical gaps]

## Key Questions for Follow-up
[From question generator, if available]

---
## Sources
[^1]: Pitch deck, slide X, dated YYYY-MM-DD
[^2]: Crunchbase profile, accessed YYYY-MM-DD
..."""

        user_prompt = f"""Generate a due diligence report based on this data:

{json.dumps(context, indent=2)}

Remember: Every claim must be cited. If data is missing, explicitly state "Not disclosed in provided materials"."""

        response = await self.client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=4000
        )
        
        return response.choices[0].message.content
    
    async def _generate_swot(self, context: Dict[str, Any]) -> str:
        """Generate SWOT analysis."""
        
        system_prompt = """You are a venture capital analyst writing a SWOT analysis.

RULES:
- Base ONLY on data provided (document + research)
- Every point must be cited
- Distinguish "stated" vs "inferred" clearly
- No generic startup advice

FORMAT:
# SWOT Analysis: [Company Name]

## Strengths
- **[Strength]**: [Evidence with citation][^1]

## Weaknesses  
- **[Weakness]**: [Evidence with citation][^2]

## Opportunities
- **[Opportunity]**: [Evidence with citation][^3]

## Threats
- **[Threat]**: [Evidence with citation][^4]

## Summary
[Brief synthesis]

---
## Sources
[Citations]"""

        user_prompt = f"""Generate SWOT analysis:

{json.dumps(context, indent=2)}"""

        response = await self.client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=3000
        )
        
        return response.choices[0].message.content
    
    async def _generate_executive_summary(self, context: Dict[str, Any]) -> str:
        """Generate executive summary."""
        
        system_prompt = """Generate a concise executive summary (500 words max) with key findings.

Must include:
- Company overview
- Key metrics (with citations)
- Top 3 risks
- Top 3 opportunities
- Investment recommendation signal (positive/neutral/negative with rationale)

All claims cited."""

        user_prompt = f"""Context: {json.dumps(context, indent=2)}"""

        response = await self.client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    async def _generate_investment_memo(self, context: Dict[str, Any]) -> str:
        """Generate investment committee memo."""
        
        system_prompt = """Generate investment memo for IC presentation.

Structure:
1. Investment Thesis (3-4 sentences)
2. Key Metrics Table
3. Investment Highlights (3-5 bullets)
4. Key Risks (3-5 bullets)
5. Open Questions (from question generator)
6. Recommendation

Professional tone, all cited."""

        user_prompt = f"""Context: {json.dumps(context, indent=2)}"""

        response = await self.client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=3000
        )
        
        return response.choices[0].message.content
    
    async def _generate_risk_assessment(self, context: Dict[str, Any]) -> str:
        """Generate risk assessment report."""
        
        system_prompt = """Generate comprehensive risk assessment.

Categories:
- Financial Risks
- Market Risks  
- Team Risks
- Technical Risks
- Legal/Compliance Risks

Each risk: Description, Evidence, Severity (Critical/High/Medium/Low), Mitigation suggestions.

All cited."""

        user_prompt = f"""Context: {json.dumps(context, indent=2)}"""

        response = await self.client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=3500
        )
        
        return response.choices[0].message.content
    
    async def _generate_generic_report(
        self,
        context: Dict[str, Any],
        content_type: ContentType
    ) -> str:
        """Generate any other report type."""
        
        system_prompt = f"""Generate {content_type.value.replace('_', ' ')} report.

Rules: Professional tone, all claims cited, include sources section."""

        user_prompt = f"""Context: {json.dumps(context, indent=2)}"""

        response = await self.client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=3000
        )
        
        return response.choices[0].message.content
    
    def _extract_citations(self, content: str) -> List[Citation]:
        """Extract all citations from markdown content."""
        
        citations = []
        
        # Find all footnote references [^1], [^2], etc.
        import re
        citation_pattern = r'\[\^(\d+)\]:\s*(.+?)(?=\n\[\^|\n\n|\Z)'
        
        for match in re.finditer(citation_pattern, content, re.DOTALL):
            ref_id = match.group(1)
            citation_text = match.group(2).strip()
            
            # Determine source type
            source_type = "document"
            if any(word in citation_text.lower() for word in ["crunchbase", "linkedin", "techcrunch", "bloomberg"]):
                source_type = "research"
            elif "analysis" in citation_text.lower() or "based on" in citation_text.lower():
                source_type = "analysis"
            
            # Extract URL if present
            url = None
            url_match = re.search(r'https?://[^\s]+', citation_text)
            if url_match:
                url = url_match.group(0)
            
            citations.append(Citation(
                ref_id=f"[{ref_id}]",
                source_type=source_type,
                source_text=citation_text,
                url=url
            ))
        
        return citations
    
    def _calculate_citation_coverage(self, content: str) -> float:
        """Calculate % of factual claims that are cited."""
        
        # Simple heuristic: count sentences vs citation markers
        import re
        
        # Remove sources section
        content_without_sources = re.split(r'\n#+\s*Sources\s*\n', content)[0]
        
        # Count sentences with factual claims (simple heuristic)
        sentences = re.split(r'[.!?]+', content_without_sources)
        factual_sentences = [
            s for s in sentences
            if any(indicator in s.lower() for indicator in [
                'is', 'are', 'was', 'were', 'has', 'have', 'shows', 'reports',
                '$', '%', 'million', 'billion', 'founded', 'raised'
            ])
        ]
        
        if not factual_sentences:
            return 1.0  # No factual claims
        
        # Count citation markers
        citation_count = len(re.findall(r'\[\^\d+\]', content_without_sources))
        
        # Estimate coverage (rough heuristic)
        coverage = min(1.0, citation_count / len(factual_sentences))
        
        return coverage
    
    def _determine_confidence(
        self,
        analysis_result: AnalysisResult,
        citation_coverage: float
    ) -> ConfidenceLevel:
        """Determine overall confidence in generated content."""
        
        combined_confidence = (
            analysis_result.overall_confidence * 0.7 +
            citation_coverage * 0.3
        )
        
        if combined_confidence >= 0.8:
            return ConfidenceLevel.HIGH
        elif combined_confidence >= 0.6:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    def _generate_disclaimer(self, document_date: Optional[str]) -> str:
        """Generate standard disclaimer."""
        
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        return (
            f"**Disclaimer**: This analysis is based solely on provided documents "
            f"dated {document_date or 'unknown'} and public sources accessed on {today}. "
            f"Information may be incomplete, outdated, or inaccurate. This is not investment advice. "
            f"Conduct independent verification before making investment decisions."
        )


# Singleton instance
_content_generator_agent: Optional[ContentGeneratorAgent] = None


def get_content_generator_agent() -> ContentGeneratorAgent:
    """Get or create content generator agent instance."""
    global _content_generator_agent
    if _content_generator_agent is None:
        _content_generator_agent = ContentGeneratorAgent()
    return _content_generator_agent

