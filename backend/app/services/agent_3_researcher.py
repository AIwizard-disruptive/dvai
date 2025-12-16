"""
Agent 3: Researcher Service
Purpose: Find corroborating public data to verify or enrich extracted information
Rule: ONLY use approved sources - flag discrepancies
"""

import json
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime
import re

from pydantic import BaseModel, Field
import httpx
from openai import AsyncOpenAI

from app.config import settings
from app.services.agent_2_analyzer import AnalysisResult, MetricValue


class VerificationStatus(str, Enum):
    """Status of claim verification."""
    CONFIRMED = "confirmed"
    CONTRADICTED = "contradicted"
    NOT_FOUND = "not_found"
    UNCERTAIN = "uncertain"


class SourceReliability(str, Enum):
    """Reliability rating of sources."""
    HIGH = "high"  # Crunchbase, official company sites, major news outlets
    MEDIUM = "medium"  # Industry blogs, verified LinkedIn
    LOW = "low"  # Unverified or questionable sources


class PublicSource(BaseModel):
    """A public source used for verification."""
    url: str
    title: str
    accessed_date: datetime = Field(default_factory=datetime.utcnow)
    excerpt: Optional[str] = None
    reliability: SourceReliability
    relevance_score: float = Field(ge=0.0, le=1.0)


class Discrepancy(BaseModel):
    """A discrepancy found between document and public data."""
    claim_from_document: str
    finding_from_research: str
    severity: str  # "critical", "moderate", "minor"
    sources: List[PublicSource]


class ResearchResult(BaseModel):
    """Result from researching a specific claim."""
    claim: str
    claim_source: str  # Where in document
    verification_status: VerificationStatus
    public_sources: List[PublicSource] = Field(default_factory=list)
    source_count: int = 0
    discrepancies: List[Discrepancy] = Field(default_factory=list)
    additional_context: Dict[str, Any] = Field(default_factory=dict)
    confidence_adjustment: float = Field(ge=-1.0, le=1.0, default=0.0)
    researched_at: datetime = Field(default_factory=datetime.utcnow)


class ResearcherAgent:
    """
    Agent 3: Researcher
    
    Finds public data to verify or contextualize document claims.
    
    Approved Sources:
    - Crunchbase, PitchBook (funding data)
    - LinkedIn (team, headcount)
    - Official company websites + press releases
    - TechCrunch, Bloomberg, WSJ (news)
    - SEC EDGAR (public financials)
    
    Forbidden Sources:
    - Wikipedia, Quora, random blogs
    - Unverified user-generated content
    - Paywalled content without access
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.version = "1.0.0"
        
        # Approved source domains
        self.approved_sources = {
            "crunchbase.com": SourceReliability.HIGH,
            "pitchbook.com": SourceReliability.HIGH,
            "linkedin.com": SourceReliability.HIGH,
            "techcrunch.com": SourceReliability.HIGH,
            "bloomberg.com": SourceReliability.HIGH,
            "wsj.com": SourceReliability.HIGH,
            "reuters.com": SourceReliability.HIGH,
            "ft.com": SourceReliability.HIGH,
            "sec.gov": SourceReliability.HIGH,
            "theinformation.com": SourceReliability.HIGH,
        }
    
    async def research_claims(
        self,
        analysis_result: AnalysisResult,
        company_name: Optional[str] = None,
        max_claims_to_verify: int = 10
    ) -> List[ResearchResult]:
        """
        Research key claims from analysis to verify with public data.
        
        Args:
            analysis_result: Output from Agent 2 (Analyzer)
            company_name: Company name to research (if known)
            max_claims_to_verify: Limit research to top N claims
        
        Returns:
            List of research results for each claim verified
        """
        
        research_results = []
        
        # Identify key claims to verify
        claims_to_verify = self._prioritize_claims(analysis_result, max_claims_to_verify)
        
        for claim_info in claims_to_verify:
            try:
                result = await self._research_single_claim(
                    claim=claim_info["claim"],
                    claim_source=claim_info["source"],
                    company_name=company_name
                )
                research_results.append(result)
            except Exception as e:
                # Log error but continue with other claims
                print(f"Research error for claim '{claim_info['claim']}': {str(e)}")
                research_results.append(ResearchResult(
                    claim=claim_info["claim"],
                    claim_source=claim_info["source"],
                    verification_status=VerificationStatus.UNCERTAIN,
                    additional_context={"error": str(e)}
                ))
        
        return research_results
    
    def _prioritize_claims(
        self,
        analysis_result: AnalysisResult,
        max_claims: int
    ) -> List[Dict[str, str]]:
        """Prioritize which claims to research based on importance."""
        
        claims = []
        
        # Priority 1: Key metrics (funding, revenue, team size)
        priority_metrics = ["funding", "revenue", "arr", "mrr", "team_size", "headcount"]
        for metric_name, metric_value in analysis_result.key_metrics.items():
            if any(pm in metric_name.lower() for pm in priority_metrics):
                if metric_value.value is not None and metric_value.stated:
                    claims.append({
                        "claim": f"{metric_name}: {metric_value.value}",
                        "source": metric_value.source_citation,
                        "priority": 1
                    })
        
        # Priority 2: High-confidence insights
        for insight in analysis_result.insights:
            if insight.confidence >= 0.8 and insight.stated_vs_implied == "stated":
                claims.append({
                    "claim": insight.claim,
                    "source": ", ".join(insight.supporting_evidence),
                    "priority": 2
                })
        
        # Priority 3: Risks (to validate they're real)
        for risk in analysis_result.risks_identified:
            if risk.confidence >= 0.7:
                claims.append({
                    "claim": risk.claim,
                    "source": ", ".join(risk.supporting_evidence),
                    "priority": 3
                })
        
        # Sort by priority and limit
        claims.sort(key=lambda x: x["priority"])
        return claims[:max_claims]
    
    async def _research_single_claim(
        self,
        claim: str,
        claim_source: str,
        company_name: Optional[str]
    ) -> ResearchResult:
        """Research a single claim using approved sources."""
        
        # Use LLM to generate search queries
        search_queries = await self._generate_search_queries(claim, company_name)
        
        # Search for information
        all_sources = []
        for query in search_queries[:3]:  # Limit to 3 queries
            sources = await self._search_web(query)
            all_sources.extend(sources)
        
        # Filter to approved sources only
        approved_sources = [
            src for src in all_sources
            if self._is_approved_source(src.url)
        ]
        
        # Analyze findings
        if not approved_sources:
            return ResearchResult(
                claim=claim,
                claim_source=claim_source,
                verification_status=VerificationStatus.NOT_FOUND,
                public_sources=[],
                source_count=0,
                confidence_adjustment=0.0
            )
        
        # Use LLM to compare claim with findings
        verification = await self._verify_claim_with_sources(
            claim, approved_sources[:5]  # Limit to top 5 sources
        )
        
        return ResearchResult(
            claim=claim,
            claim_source=claim_source,
            verification_status=verification["status"],
            public_sources=approved_sources[:5],
            source_count=len(approved_sources),
            discrepancies=verification.get("discrepancies", []),
            additional_context=verification.get("context", {}),
            confidence_adjustment=verification.get("confidence_adjustment", 0.0)
        )
    
    async def _generate_search_queries(
        self,
        claim: str,
        company_name: Optional[str]
    ) -> List[str]:
        """Use LLM to generate effective search queries."""
        
        prompt = f"""Generate 2-3 specific search queries to verify this claim:

Claim: {claim}
Company: {company_name or "Unknown"}

Generate queries that would find information from:
- Crunchbase, PitchBook (for funding/valuation)
- TechCrunch, Bloomberg (for news)
- LinkedIn (for team/company info)
- Official company website

Return ONLY the search queries, one per line."""
        
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",  # Faster model for query generation
            messages=[
                {"role": "system", "content": "You generate precise search queries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        queries = response.choices[0].message.content.strip().split("\n")
        return [q.strip("- ").strip() for q in queries if q.strip()]
    
    async def _search_web(self, query: str) -> List[PublicSource]:
        """
        Search web for information.
        
        Note: This is a placeholder. In production, integrate with:
        - Google Custom Search API
        - Bing Search API
        - Or dedicated APIs (Crunchbase, etc.)
        """
        
        # TODO: Integrate with actual search API
        # For now, return empty to avoid fake data
        
        # Example structure (when real API is integrated):
        # response = await self.http_client.get(
        #     "https://api.search.com/search",
        #     params={"q": query, "api_key": settings.search_api_key}
        # )
        # results = response.json()
        # return [self._parse_search_result(r) for r in results["items"]]
        
        return []
    
    def _is_approved_source(self, url: str) -> bool:
        """Check if URL is from an approved source."""
        
        for domain, reliability in self.approved_sources.items():
            if domain in url.lower():
                return True
        
        # Also allow official company domains (.com, .io, .co)
        # but mark as medium reliability
        if re.match(r'https?://(?:www\.)?[\w-]+\.(com|io|co)/?', url):
            # Check if it looks like a company domain (not a platform)
            if not any(platform in url.lower() for platform in 
                      ['facebook', 'twitter', 'instagram', 'reddit', 'medium', 'wordpress']):
                return True
        
        return False
    
    def _get_source_reliability(self, url: str) -> SourceReliability:
        """Determine reliability of a source."""
        
        for domain, reliability in self.approved_sources.items():
            if domain in url.lower():
                return reliability
        
        # Default to medium for company domains
        return SourceReliability.MEDIUM
    
    async def _verify_claim_with_sources(
        self,
        claim: str,
        sources: List[PublicSource]
    ) -> Dict[str, Any]:
        """Use LLM to compare claim with research findings."""
        
        sources_text = "\n\n".join([
            f"Source {i+1} ({src.reliability.value}):\n"
            f"URL: {src.url}\n"
            f"Title: {src.title}\n"
            f"Excerpt: {src.excerpt or 'N/A'}"
            for i, src in enumerate(sources)
        ])
        
        prompt = f"""Compare the document claim with research findings and determine verification status.

DOCUMENT CLAIM:
{claim}

PUBLIC SOURCES FOUND:
{sources_text}

TASK:
1. Determine if sources CONFIRM, CONTRADICT, or are UNCERTAIN about the claim
2. Identify any discrepancies (with severity: critical/moderate/minor)
3. Provide confidence adjustment (-1.0 to +1.0)

RULES:
- CONFIRMED: 3+ high-reliability sources agree
- CONTRADICTED: Sources provide conflicting information
- UNCERTAIN: Ambiguous or insufficient information

Return JSON:
{{
  "status": "confirmed" | "contradicted" | "not_found" | "uncertain",
  "discrepancies": [
    {{
      "claim_from_document": "...",
      "finding_from_research": "...",
      "severity": "critical" | "moderate" | "minor"
    }}
  ],
  "context": {{}},
  "confidence_adjustment": 0.2
}}
"""
        
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You verify claims against sources."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Parse discrepancies
        if "discrepancies" in result:
            result["discrepancies"] = [
                Discrepancy(
                    claim_from_document=d.get("claim_from_document", ""),
                    finding_from_research=d.get("finding_from_research", ""),
                    severity=d.get("severity", "minor"),
                    sources=sources
                )
                for d in result["discrepancies"]
            ]
        
        return result
    
    async def close(self):
        """Close HTTP client."""
        await self.http_client.aclose()


# Singleton instance
_researcher_agent: Optional[ResearcherAgent] = None


def get_researcher_agent() -> ResearcherAgent:
    """Get or create researcher agent instance."""
    global _researcher_agent
    if _researcher_agent is None:
        _researcher_agent = ResearcherAgent()
    return _researcher_agent

