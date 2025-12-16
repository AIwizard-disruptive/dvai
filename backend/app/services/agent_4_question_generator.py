"""
Agent 4: Question Generator Service
Purpose: Generate intelligent DD questions based on gaps and risks
Rule: Questions must be specific, data-driven, and answerable
"""

import json
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime

from pydantic import BaseModel, Field
from openai import AsyncOpenAI

from app.config import settings
from app.services.agent_2_analyzer import AnalysisResult
from app.services.agent_3_researcher import ResearchResult, VerificationStatus


class QuestionPriority(str, Enum):
    """Priority level of questions."""
    CRITICAL = "critical"  # Deal-breakers if unanswered
    HIGH = "high"  # Significant risks
    MEDIUM = "medium"  # Nice-to-know
    LOW = "low"  # Optional context


class QuestionCategory(str, Enum):
    """Category of question."""
    FINANCIAL = "financial"
    TECHNICAL = "technical"
    TEAM = "team"
    MARKET = "market"
    LEGAL = "legal"
    PRODUCT = "product"
    COMPETITIVE = "competitive"
    OPERATIONAL = "operational"


class Question(BaseModel):
    """A due diligence question."""
    question: str
    category: QuestionCategory
    priority: QuestionPriority
    triggered_by: str  # What data point or gap triggered this
    risk_category: Optional[str] = None
    suggested_sources: List[str] = Field(default_factory=list)
    context: Optional[str] = None


class QuestionSet(BaseModel):
    """Complete set of generated questions."""
    critical: List[Question] = Field(default_factory=list)
    high_priority: List[Question] = Field(default_factory=list)
    medium_priority: List[Question] = Field(default_factory=list)
    low_priority: List[Question] = Field(default_factory=list)
    
    total_count: int = 0
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class QuestionGeneratorAgent:
    """
    Agent 4: Question Generator
    
    Generates specific, actionable due diligence questions based on:
    - Information gaps from analysis
    - Risks identified
    - Discrepancies from research
    - Unusual or suspicious claims
    
    Question Quality Rules:
    - Must be specific and data-driven
    - Must reference source that triggered it
    - Must be answerable (not philosophical)
    - Must explain the risk/opportunity
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.version = "1.0.0"
    
    async def generate_questions(
        self,
        analysis_result: AnalysisResult,
        research_results: Optional[List[ResearchResult]] = None,
        company_name: Optional[str] = None
    ) -> QuestionSet:
        """
        Generate due diligence questions from analysis and research.
        
        Args:
            analysis_result: Output from Agent 2
            research_results: Output from Agent 3 (optional)
            company_name: Company name for context
        
        Returns:
            QuestionSet with prioritized questions
        """
        
        # Build context for LLM
        context = self._build_context(analysis_result, research_results, company_name)
        
        # Generate questions using LLM
        questions = await self._generate_with_llm(context)
        
        # Categorize by priority
        question_set = self._categorize_questions(questions)
        
        return question_set
    
    def _build_context(
        self,
        analysis_result: AnalysisResult,
        research_results: Optional[List[ResearchResult]],
        company_name: Optional[str]
    ) -> str:
        """Build context for question generation."""
        
        context_parts = [
            f"COMPANY: {company_name or 'Unknown'}",
            "",
            "=== DOCUMENT ANALYSIS ===",
            f"Classification: {analysis_result.classification.value}",
            f"Overall Confidence: {analysis_result.overall_confidence:.2f}",
            f"Data Completeness: {analysis_result.data_completeness:.2f}",
            "",
            "KEY METRICS:",
        ]
        
        # Add key metrics
        for metric_name, metric in analysis_result.key_metrics.items():
            context_parts.append(
                f"- {metric_name}: {metric.value} "
                f"(stated: {metric.stated}, confidence: {metric.confidence:.2f})"
            )
        
        # Add gaps
        if analysis_result.gaps:
            context_parts.extend(["", "INFORMATION GAPS:"])
            for gap in analysis_result.gaps:
                context_parts.append(
                    f"- {gap.metric} ({gap.importance}): {gap.note}"
                )
        
        # Add risks
        if analysis_result.risks_identified:
            context_parts.extend(["", "RISKS IDENTIFIED:"])
            for risk in analysis_result.risks_identified[:5]:
                context_parts.append(
                    f"- {risk.claim} (confidence: {risk.confidence:.2f})"
                )
        
        # Add inconsistencies
        if analysis_result.inconsistencies:
            context_parts.extend(["", "INCONSISTENCIES:"])
            for inconsistency in analysis_result.inconsistencies:
                context_parts.append(f"- {inconsistency}")
        
        # Add research findings
        if research_results:
            context_parts.extend(["", "=== RESEARCH FINDINGS ==="])
            for result in research_results[:10]:
                context_parts.append(
                    f"Claim: {result.claim}\n"
                    f"Status: {result.verification_status.value}\n"
                    f"Sources: {result.source_count}"
                )
                
                if result.discrepancies:
                    for disc in result.discrepancies:
                        context_parts.append(
                            f"  ⚠️ Discrepancy ({disc.severity}): "
                            f"{disc.finding_from_research}"
                        )
        
        return "\n".join(context_parts)
    
    async def _generate_with_llm(self, context: str) -> List[Dict[str, Any]]:
        """Use LLM to generate questions."""
        
        system_prompt = """You are a venture capital due diligence expert. Generate specific, actionable questions based on gaps, risks, and discrepancies.

QUESTION QUALITY RULES:
1. Questions must be SPECIFIC and DATA-DRIVEN
2. Bad: "Is the team good?"
3. Good: "CEO has 2 years industry experience (LinkedIn); what expertise does the advisory board provide?"
4. Must reference the source data that triggered the question
5. Must explain the risk or opportunity
6. Must be answerable (not philosophical)

PRIORITY LEVELS:
- CRITICAL: Deal-breakers if unanswered (e.g., suspicious financials, major team gaps)
- HIGH: Significant risks (e.g., unclear market position, unverified claims)
- MEDIUM: Important but not blocking (e.g., missing context, competitor info)
- LOW: Nice-to-have context (e.g., company culture, future plans)

CATEGORIES:
- financial: Revenue, costs, funding, burn rate, unit economics
- technical: Product, tech stack, IP, scalability
- team: Founders, key hires, advisors, culture
- market: TAM, competition, positioning, go-to-market
- legal: IP ownership, contracts, compliance, litigation
- product: Features, roadmap, customer feedback, PMF
- competitive: Competitors, differentiation, moat
- operational: Processes, metrics, infrastructure

Return JSON array of questions."""
        
        user_prompt = f"""{context}

Generate 10-20 targeted due diligence questions based on the above analysis.
Focus on:
1. Critical information gaps
2. Risks that need validation
3. Discrepancies between document and research
4. Unusual or suspicious data points

Return JSON:
[
  {{
    "question": "Specific question here?",
    "category": "financial",
    "priority": "critical",
    "triggered_by": "What data point triggered this",
    "risk_category": "overstated_revenue",
    "suggested_sources": ["Stripe dashboard", "Bank statements"],
    "context": "Why this matters"
  }}
]
"""
        
        response = await self.client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("questions", [])
    
    def _categorize_questions(
        self,
        questions: List[Dict[str, Any]]
    ) -> QuestionSet:
        """Categorize questions by priority."""
        
        critical = []
        high = []
        medium = []
        low = []
        
        for q_data in questions:
            try:
                question = Question(
                    question=q_data["question"],
                    category=QuestionCategory(q_data["category"]),
                    priority=QuestionPriority(q_data["priority"]),
                    triggered_by=q_data["triggered_by"],
                    risk_category=q_data.get("risk_category"),
                    suggested_sources=q_data.get("suggested_sources", []),
                    context=q_data.get("context")
                )
                
                if question.priority == QuestionPriority.CRITICAL:
                    critical.append(question)
                elif question.priority == QuestionPriority.HIGH:
                    high.append(question)
                elif question.priority == QuestionPriority.MEDIUM:
                    medium.append(question)
                else:
                    low.append(question)
            
            except Exception as e:
                print(f"Error parsing question: {e}")
                continue
        
        return QuestionSet(
            critical=critical,
            high_priority=high,
            medium_priority=medium,
            low_priority=low,
            total_count=len(critical) + len(high) + len(medium) + len(low)
        )


# Singleton instance
_question_generator_agent: Optional[QuestionGeneratorAgent] = None


def get_question_generator_agent() -> QuestionGeneratorAgent:
    """Get or create question generator agent instance."""
    global _question_generator_agent
    if _question_generator_agent is None:
        _question_generator_agent = QuestionGeneratorAgent()
    return _question_generator_agent

