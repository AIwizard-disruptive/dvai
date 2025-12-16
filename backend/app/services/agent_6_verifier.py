"""
Agent 6: Verifier Service (QA Approver)
Purpose: Final quality check before content is released
Rule: Catch hallucinations, missing citations, and quality issues
"""

import re
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime

from pydantic import BaseModel, Field

from app.services.agent_5_content_generator import GeneratedContent, Citation


class VerificationStatus(str, Enum):
    """Status of verification."""
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_REVIEW = "requires_review"


class IssueSeverity(str, Enum):
    """Severity of identified issues."""
    CRITICAL = "critical"  # Must fix before release
    HIGH = "high"  # Should fix
    MEDIUM = "medium"  # Nice to fix
    LOW = "low"  # Minor issue


class VerificationIssue(BaseModel):
    """An issue found during verification."""
    issue_type: str  # "missing_citation", "hallucination", "pii_detected", etc.
    severity: IssueSeverity
    description: str
    location: Optional[str] = None  # Line/section where issue was found
    suggestion: Optional[str] = None  # How to fix


class VerificationResult(BaseModel):
    """Complete verification result."""
    status: VerificationStatus
    approved: bool
    
    # Issues found
    issues: List[VerificationIssue] = Field(default_factory=list)
    critical_issues: int = 0
    high_issues: int = 0
    medium_issues: int = 0
    low_issues: int = 0
    
    # Quality metrics
    citation_coverage_actual: float = Field(ge=0.0, le=1.0)
    pii_detected: bool = False
    hallucination_detected: bool = False
    format_valid: bool = True
    
    # Overall confidence
    final_confidence: float = Field(ge=0.0, le=1.0)
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list)
    
    # Metadata
    verified_at: datetime = Field(default_factory=datetime.utcnow)
    verifier_version: str = "1.0.0"


class VerifierAgent:
    """
    Agent 6: Verifier (QA Approver)
    
    Final quality check before content release.
    
    Verification Checklist:
    - Every factual claim has citation
    - All citations are valid
    - No hallucinations or assumptions
    - No unsupported inferences
    - PII redacted (if external output)
    - Disclaimers present
    - "Unknown" sections included
    - Ambiguities flagged
    - Confidence scores justified
    """
    
    def __init__(self):
        self.version = "1.0.0"
        
        # Forbidden phrases that indicate hallucinations
        self.forbidden_phrases = [
            "typically",
            "usually",
            "often",
            "generally",
            "commonly",
            "industry standard",
            "best practice",
            "it is likely",
            "probably",
            "presumably",
            "one can assume",
            "it can be inferred",
        ]
        
        # PII patterns to detect
        self.pii_patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        }
    
    def verify(
        self,
        generated_content: GeneratedContent,
        output_mode: str = "internal",  # "internal", "external_redacted", "external_full"
        min_citation_coverage: float = 0.9,
        allow_pii: bool = False
    ) -> VerificationResult:
        """
        Verify generated content for quality and compliance.
        
        Args:
            generated_content: Output from Agent 5
            output_mode: Where content will be used
            min_citation_coverage: Minimum required citation coverage (0-1)
            allow_pii: Whether PII is allowed in output
        
        Returns:
            VerificationResult with approval status and issues
        """
        
        issues: List[VerificationIssue] = []
        
        # Check 1: Citation coverage
        citation_issues = self._verify_citations(
            generated_content.content_markdown,
            generated_content.citations,
            min_citation_coverage
        )
        issues.extend(citation_issues)
        
        # Check 2: Hallucination detection
        hallucination_issues = self._detect_hallucinations(
            generated_content.content_markdown
        )
        issues.extend(hallucination_issues)
        
        # Check 3: PII detection (if external output)
        pii_issues = []
        if not allow_pii:
            pii_issues = self._detect_pii(
                generated_content.content_markdown,
                output_mode
            )
            issues.extend(pii_issues)
        
        # Check 4: Format validation
        format_issues = self._verify_format(generated_content.content_markdown)
        issues.extend(format_issues)
        
        # Check 5: Required sections
        section_issues = self._verify_required_sections(
            generated_content.content_markdown,
            generated_content.content_type.value
        )
        issues.extend(section_issues)
        
        # Check 6: Confidence scores
        confidence_issues = self._verify_confidence_scores(generated_content)
        issues.extend(confidence_issues)
        
        # Categorize issues by severity
        critical_count = len([i for i in issues if i.severity == IssueSeverity.CRITICAL])
        high_count = len([i for i in issues if i.severity == IssueSeverity.HIGH])
        medium_count = len([i for i in issues if i.severity == IssueSeverity.MEDIUM])
        low_count = len([i for i in issues if i.severity == IssueSeverity.LOW])
        
        # Determine status
        if critical_count > 0:
            status = VerificationStatus.REJECTED
            approved = False
        elif high_count > 2:
            status = VerificationStatus.REQUIRES_REVIEW
            approved = False
        elif high_count > 0 or medium_count > 5:
            status = VerificationStatus.REQUIRES_REVIEW
            approved = False
        else:
            status = VerificationStatus.APPROVED
            approved = True
        
        # Calculate actual citation coverage
        actual_coverage = self._calculate_actual_citation_coverage(
            generated_content.content_markdown
        )
        
        # Determine final confidence
        final_confidence = self._calculate_final_confidence(
            generated_content,
            actual_coverage,
            len(issues)
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(issues, generated_content)
        
        return VerificationResult(
            status=status,
            approved=approved,
            issues=issues,
            critical_issues=critical_count,
            high_issues=high_count,
            medium_issues=medium_count,
            low_issues=low_count,
            citation_coverage_actual=actual_coverage,
            pii_detected=len(pii_issues) > 0,
            hallucination_detected=len(hallucination_issues) > 0,
            format_valid=len(format_issues) == 0,
            final_confidence=final_confidence,
            recommendations=recommendations
        )
    
    def _verify_citations(
        self,
        content: str,
        citations: List[Citation],
        min_coverage: float
    ) -> List[VerificationIssue]:
        """Verify citation coverage and validity."""
        
        issues = []
        
        # Remove sources section for analysis
        content_without_sources = re.split(r'\n#+\s*Sources\s*\n', content)[0]
        
        # Find all factual sentences
        sentences = re.split(r'[.!?]+', content_without_sources)
        factual_sentences = [
            s for s in sentences
            if any(indicator in s.lower() for indicator in [
                'is', 'are', 'was', 'were', 'has', 'have', 'had',
                'shows', 'reports', 'states', 'indicates',
                '$', '%', 'million', 'billion', 'founded', 'raised',
                'revenue', 'growth', 'team', 'market', 'customer'
            ]) and len(s.strip()) > 20  # Ignore very short sentences
        ]
        
        # Find all citation markers
        citation_markers = re.findall(r'\[\^\d+\]', content_without_sources)
        
        # Check if each factual sentence has a citation
        uncited_sentences = []
        for sentence in factual_sentences:
            sentence = sentence.strip()
            if sentence and not re.search(r'\[\^\d+\]', sentence):
                uncited_sentences.append(sentence[:100])
        
        # Issue if too many uncited factual claims
        if uncited_sentences:
            actual_coverage = 1 - (len(uncited_sentences) / max(len(factual_sentences), 1))
            if actual_coverage < min_coverage:
                issues.append(VerificationIssue(
                    issue_type="missing_citations",
                    severity=IssueSeverity.CRITICAL,
                    description=f"Only {actual_coverage:.0%} of factual claims are cited (minimum: {min_coverage:.0%})",
                    location="Throughout document",
                    suggestion=f"Add citations to {len(uncited_sentences)} uncited factual claims"
                ))
        
        # Verify citation references are valid
        citation_refs = {c.ref_id for c in citations}
        for marker in set(citation_markers):
            if marker not in citation_refs:
                issues.append(VerificationIssue(
                    issue_type="invalid_citation",
                    severity=IssueSeverity.HIGH,
                    description=f"Citation marker {marker} has no corresponding source",
                    suggestion="Add source to references or remove marker"
                ))
        
        # Check for broken URLs in citations
        for citation in citations:
            if citation.url:
                if not citation.url.startswith('http'):
                    issues.append(VerificationIssue(
                        issue_type="invalid_url",
                        severity=IssueSeverity.MEDIUM,
                        description=f"Invalid URL format in {citation.ref_id}",
                        location=citation.source_text[:100]
                    ))
        
        return issues
    
    def _detect_hallucinations(self, content: str) -> List[VerificationIssue]:
        """Detect potential hallucinations or unsupported claims."""
        
        issues = []
        
        content_lower = content.lower()
        
        # Check for forbidden phrases
        for phrase in self.forbidden_phrases:
            if phrase in content_lower:
                # Find context
                pattern = re.compile(rf'.{{0,50}}{re.escape(phrase)}.{{0,50}}', re.IGNORECASE)
                matches = pattern.findall(content)
                
                for match in matches[:3]:  # Limit to first 3 occurrences
                    # Check if it's in a quoted section (which is OK)
                    if '"' not in match and "'" not in match:
                        issues.append(VerificationIssue(
                            issue_type="hallucination_risk",
                            severity=IssueSeverity.CRITICAL,
                            description=f"Forbidden phrase '{phrase}' suggests hallucination",
                            location=match.strip(),
                            suggestion="Remove unsupported generalization or provide citation"
                        ))
        
        # Check for "estimated" without citation
        if 'estimated' in content_lower or 'approximately' in content_lower:
            pattern = re.compile(r'(estimated|approximately)[^\[]{0,50}', re.IGNORECASE)
            matches = pattern.findall(content)
            
            for match in matches:
                if not re.search(r'\[\^\d+\]', match):
                    issues.append(VerificationIssue(
                        issue_type="unsupported_estimate",
                        severity=IssueSeverity.HIGH,
                        description="Estimate provided without source citation",
                        location=match[:80],
                        suggestion="Cite source or state explicitly that this is an assumption"
                    ))
        
        # Check for placeholder data
        placeholders = ['lorem ipsum', 'xxx', 'tbd', 'todo', 'placeholder', 'example.com']
        for placeholder in placeholders:
            if placeholder in content_lower:
                issues.append(VerificationIssue(
                    issue_type="placeholder_data",
                    severity=IssueSeverity.CRITICAL,
                    description=f"Placeholder text detected: '{placeholder}'",
                    suggestion="Replace with real data or remove"
                ))
        
        return issues
    
    def _detect_pii(self, content: str, output_mode: str) -> List[VerificationIssue]:
        """Detect personally identifiable information."""
        
        issues = []
        
        # Only check if output is external
        if output_mode.startswith('external'):
            
            for pii_type, pattern in self.pii_patterns.items():
                matches = re.findall(pattern, content)
                
                if matches:
                    issues.append(VerificationIssue(
                        issue_type="pii_detected",
                        severity=IssueSeverity.CRITICAL,
                        description=f"{pii_type.upper()} detected in external-facing content",
                        location=f"Found {len(matches)} instances",
                        suggestion="Redact or mask PII before external release"
                    ))
        
        return issues
    
    def _verify_format(self, content: str) -> List[VerificationIssue]:
        """Verify markdown format is valid."""
        
        issues = []
        
        # Check for sources section
        if '## Sources' not in content and '## References' not in content:
            issues.append(VerificationIssue(
                issue_type="missing_sources",
                severity=IssueSeverity.HIGH,
                description="No sources/references section found",
                suggestion="Add '## Sources' section with all citations"
            ))
        
        # Check for basic structure
        if not re.search(r'^#\s+.+', content, re.MULTILINE):
            issues.append(VerificationIssue(
                issue_type="missing_title",
                severity=IssueSeverity.MEDIUM,
                description="No title heading found",
                suggestion="Add title with # heading"
            ))
        
        return issues
    
    def _verify_required_sections(
        self,
        content: str,
        content_type: str
    ) -> List[VerificationIssue]:
        """Verify required sections exist for content type."""
        
        issues = []
        
        # Define required sections per content type
        required_sections = {
            "due_diligence": ["Executive Summary", "Unknown", "Missing Data", "Sources"],
            "swot_analysis": ["Strengths", "Weaknesses", "Opportunities", "Threats", "Sources"],
            "investment_memo": ["Investment Thesis", "Key Metrics", "Risks", "Sources"],
            "risk_assessment": ["Risks", "Sources"],
        }
        
        required = required_sections.get(content_type, ["Sources"])
        
        for section in required:
            if section.lower() not in content.lower():
                issues.append(VerificationIssue(
                    issue_type="missing_section",
                    severity=IssueSeverity.HIGH if section in ["Sources", "Unknown"] else IssueSeverity.MEDIUM,
                    description=f"Required section missing: {section}",
                    suggestion=f"Add '{section}' section"
                ))
        
        return issues
    
    def _verify_confidence_scores(
        self,
        generated_content: GeneratedContent
    ) -> List[VerificationIssue]:
        """Verify confidence scores are justified."""
        
        issues = []
        
        # Check if confidence matches citation coverage
        if generated_content.citation_coverage < 0.8 and generated_content.confidence_level.value == "high":
            issues.append(VerificationIssue(
                issue_type="confidence_mismatch",
                severity=IssueSeverity.MEDIUM,
                description="High confidence claimed but citation coverage is low",
                suggestion="Lower confidence level or add more citations"
            ))
        
        return issues
    
    def _calculate_actual_citation_coverage(self, content: str) -> float:
        """Calculate actual citation coverage."""
        
        content_without_sources = re.split(r'\n#+\s*Sources\s*\n', content)[0]
        
        # Count factual sentences
        sentences = re.split(r'[.!?]+', content_without_sources)
        factual_sentences = [
            s for s in sentences
            if any(indicator in s.lower() for indicator in [
                'is', 'are', 'was', 'were', 'has', 'have',
                '$', '%', 'million', 'billion', 'founded', 'raised'
            ]) and len(s.strip()) > 20
        ]
        
        if not factual_sentences:
            return 1.0
        
        # Count cited sentences
        cited_sentences = [s for s in factual_sentences if re.search(r'\[\^\d+\]', s)]
        
        return len(cited_sentences) / len(factual_sentences)
    
    def _calculate_final_confidence(
        self,
        generated_content: GeneratedContent,
        actual_coverage: float,
        issue_count: int
    ) -> float:
        """Calculate final confidence score."""
        
        # Start with content's confidence
        base_confidence = {
            "high": 0.9,
            "medium": 0.7,
            "low": 0.5
        }.get(generated_content.confidence_level.value, 0.5)
        
        # Adjust for citation coverage
        coverage_factor = actual_coverage
        
        # Adjust for issues
        issue_penalty = min(0.4, issue_count * 0.05)
        
        final = base_confidence * coverage_factor * (1 - issue_penalty)
        
        return max(0.0, min(1.0, final))
    
    def _generate_recommendations(
        self,
        issues: List[VerificationIssue],
        generated_content: GeneratedContent
    ) -> List[str]:
        """Generate actionable recommendations."""
        
        recommendations = []
        
        # Group issues by type
        issue_types = {}
        for issue in issues:
            if issue.issue_type not in issue_types:
                issue_types[issue.issue_type] = []
            issue_types[issue.issue_type].append(issue)
        
        # Generate recommendations
        if "missing_citations" in issue_types:
            recommendations.append("Add citations to all factual claims")
        
        if "hallucination_risk" in issue_types:
            recommendations.append("Remove unsupported generalizations or add sources")
        
        if "pii_detected" in issue_types:
            recommendations.append("Redact PII before external release")
        
        if "missing_section" in issue_types:
            sections = [i.description.split(": ")[1] for i in issue_types["missing_section"]]
            recommendations.append(f"Add required sections: {', '.join(sections)}")
        
        if generated_content.citation_coverage < 0.8:
            recommendations.append("Increase citation coverage to at least 80%")
        
        if not recommendations:
            recommendations.append("Content meets quality standards - approved for release")
        
        return recommendations


# Singleton instance
_verifier_agent: Optional[VerifierAgent] = None


def get_verifier_agent() -> VerifierAgent:
    """Get or create verifier agent instance."""
    global _verifier_agent
    if _verifier_agent is None:
        _verifier_agent = VerifierAgent()
    return _verifier_agent

