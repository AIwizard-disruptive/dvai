"""
Document Processor Orchestrator
Coordinates all 6 agents in the document intelligence pipeline
"""

import asyncio
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime
import hashlib

from pydantic import BaseModel, Field

from app.services.agent_1_extractor import get_extractor_agent, ExtractionResult
from app.services.agent_2_analyzer import get_analyzer_agent, AnalysisResult
from app.services.agent_3_researcher import get_researcher_agent, ResearchResult
from app.services.agent_4_question_generator import get_question_generator_agent, QuestionSet
from app.services.agent_5_content_generator import (
    get_content_generator_agent,
    GeneratedContent,
    ContentType
)
from app.services.agent_6_verifier import get_verifier_agent, VerificationResult


class ProcessingStage(str, Enum):
    """Stages in the processing pipeline."""
    UPLOAD = "upload"
    EXTRACTION = "extraction"
    ANALYSIS = "analysis"
    RESEARCH = "research"
    QUESTION_GENERATION = "question_generation"
    CONTENT_GENERATION = "content_generation"
    VERIFICATION = "verification"
    COMPLETE = "complete"
    FAILED = "failed"


class ProcessingStatus(str, Enum):
    """Overall processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_REVIEW = "requires_review"


class DocumentProcessingResult(BaseModel):
    """Complete result from document processing pipeline."""
    # Input
    document_id: str
    filename: str
    document_type: str
    
    # Processing stages
    current_stage: ProcessingStage
    status: ProcessingStatus
    
    # Results from each agent
    extraction: Optional[ExtractionResult] = None
    analysis: Optional[AnalysisResult] = None
    research: Optional[List[ResearchResult]] = None
    questions: Optional[QuestionSet] = None
    generated_content: Optional[Dict[ContentType, GeneratedContent]] = None
    verification: Optional[Dict[ContentType, VerificationResult]] = None
    
    # Quality metrics
    overall_confidence: float = 0.0
    requires_human_review: bool = False
    review_reason: Optional[str] = None
    
    # Timing
    processing_time_ms: Optional[int] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Errors
    error_message: Optional[str] = None
    failed_stage: Optional[ProcessingStage] = None


class DocumentProcessor:
    """
    Document Processor Orchestrator
    
    Coordinates the 6-agent pipeline:
    1. Agent 1: Extract data from document
    2. Agent 2: Analyze extracted data
    3. Agent 3: Research & verify claims (optional)
    4. Agent 4: Generate DD questions
    5. Agent 5: Generate reports (DD, SWOT, etc.)
    6. Agent 6: Verify quality before release
    """
    
    def __init__(self):
        self.version = "1.0.0"
        
        # Initialize all agents
        self.extractor = get_extractor_agent()
        self.analyzer = get_analyzer_agent()
        self.researcher = get_researcher_agent()
        self.question_generator = get_question_generator_agent()
        self.content_generator = get_content_generator_agent()
        self.verifier = get_verifier_agent()
    
    async def process_document(
        self,
        file_content: bytes,
        filename: str,
        document_type: str = "other",
        mime_type: Optional[str] = None,
        enable_research: bool = True,
        generate_content_types: Optional[List[ContentType]] = None,
        company_name: Optional[str] = None,
        document_date: Optional[str] = None
    ) -> DocumentProcessingResult:
        """
        Process a document through the complete 6-agent pipeline.
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
            document_type: Type of document (pitch_deck, financial_report, etc.)
            mime_type: MIME type (auto-detected if not provided)
            enable_research: Whether to run Agent 3 (Researcher)
            generate_content_types: Which reports to generate (defaults to all)
            company_name: Company name for context
            document_date: Date of document
        
        Returns:
            DocumentProcessingResult with all outputs
        """
        
        # Generate document ID
        document_id = hashlib.sha256(file_content).hexdigest()[:16]
        
        # Initialize result
        result = DocumentProcessingResult(
            document_id=document_id,
            filename=filename,
            document_type=document_type,
            current_stage=ProcessingStage.UPLOAD,
            status=ProcessingStatus.PROCESSING
        )
        
        start_time = datetime.utcnow()
        
        try:
            # STAGE 1: EXTRACTION
            result.current_stage = ProcessingStage.EXTRACTION
            result.extraction = await self._run_extraction(
                file_content, filename, mime_type
            )
            
            if result.extraction.confidence_score < 0.5:
                result.requires_human_review = True
                result.review_reason = "Low extraction quality"
            
            # STAGE 2: ANALYSIS
            result.current_stage = ProcessingStage.ANALYSIS
            result.analysis = await self._run_analysis(
                result.extraction,
                filename=filename,
                document_type=document_type
            )
            
            if result.analysis.requires_human_review:
                result.requires_human_review = True
                result.review_reason = result.analysis.review_reason
            
            # STAGE 3: RESEARCH (Optional)
            if enable_research:
                result.current_stage = ProcessingStage.RESEARCH
                result.research = await self._run_research(
                    result.analysis,
                    company_name=company_name
                )
            
            # STAGE 4: QUESTION GENERATION
            result.current_stage = ProcessingStage.QUESTION_GENERATION
            result.questions = await self._run_question_generation(
                result.analysis,
                result.research,
                company_name=company_name
            )
            
            # STAGE 5: CONTENT GENERATION
            result.current_stage = ProcessingStage.CONTENT_GENERATION
            
            if generate_content_types is None:
                generate_content_types = self._get_default_content_types(document_type)
            
            result.generated_content = {}
            for content_type in generate_content_types:
                content = await self._run_content_generation(
                    content_type,
                    result.analysis,
                    result.research,
                    result.questions,
                    company_name=company_name,
                    document_date=document_date
                )
                result.generated_content[content_type] = content
            
            # STAGE 6: VERIFICATION
            result.current_stage = ProcessingStage.VERIFICATION
            result.verification = {}
            
            for content_type, content in result.generated_content.items():
                verification = await self._run_verification(
                    content,
                    output_mode="internal"
                )
                result.verification[content_type] = verification
                
                if not verification.approved:
                    result.requires_human_review = True
                    if not result.review_reason:
                        result.review_reason = "Content failed QA verification"
            
            # Calculate overall confidence
            result.overall_confidence = self._calculate_overall_confidence(result)
            
            # Mark as complete
            result.current_stage = ProcessingStage.COMPLETE
            result.status = (
                ProcessingStatus.REQUIRES_REVIEW
                if result.requires_human_review
                else ProcessingStatus.COMPLETED
            )
            
        except Exception as e:
            result.status = ProcessingStatus.FAILED
            result.error_message = str(e)
            result.failed_stage = result.current_stage
            result.current_stage = ProcessingStage.FAILED
            
            print(f"Processing failed at {result.failed_stage}: {e}")
        
        finally:
            # Record timing
            end_time = datetime.utcnow()
            result.completed_at = end_time
            result.processing_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        return result
    
    async def _run_extraction(
        self,
        file_content: bytes,
        filename: str,
        mime_type: Optional[str]
    ) -> ExtractionResult:
        """Run Agent 1: Extractor."""
        
        return await self.extractor.extract(
            file_content=file_content,
            filename=filename,
            mime_type=mime_type
        )
    
    async def _run_analysis(
        self,
        extraction: ExtractionResult,
        filename: str,
        document_type: str
    ) -> AnalysisResult:
        """Run Agent 2: Analyzer."""
        
        return await self.analyzer.analyze(
            extraction_result=extraction,
            document_context={
                "filename": filename,
                "document_type": document_type,
                "uploaded_at": datetime.utcnow().isoformat()
            }
        )
    
    async def _run_research(
        self,
        analysis: AnalysisResult,
        company_name: Optional[str]
    ) -> List[ResearchResult]:
        """Run Agent 3: Researcher."""
        
        return await self.researcher.research_claims(
            analysis_result=analysis,
            company_name=company_name,
            max_claims_to_verify=10
        )
    
    async def _run_question_generation(
        self,
        analysis: AnalysisResult,
        research: Optional[List[ResearchResult]],
        company_name: Optional[str]
    ) -> QuestionSet:
        """Run Agent 4: Question Generator."""
        
        return await self.question_generator.generate_questions(
            analysis_result=analysis,
            research_results=research,
            company_name=company_name
        )
    
    async def _run_content_generation(
        self,
        content_type: ContentType,
        analysis: AnalysisResult,
        research: Optional[List[ResearchResult]],
        questions: Optional[QuestionSet],
        company_name: Optional[str],
        document_date: Optional[str]
    ) -> GeneratedContent:
        """Run Agent 5: Content Generator."""
        
        return await self.content_generator.generate(
            content_type=content_type,
            analysis_result=analysis,
            research_results=research,
            questions=questions,
            company_name=company_name,
            document_date=document_date
        )
    
    async def _run_verification(
        self,
        generated_content: GeneratedContent,
        output_mode: str
    ) -> VerificationResult:
        """Run Agent 6: Verifier."""
        
        return self.verifier.verify(
            generated_content=generated_content,
            output_mode=output_mode,
            min_citation_coverage=0.85,
            allow_pii=(output_mode == "internal")
        )
    
    def _get_default_content_types(self, document_type: str) -> List[ContentType]:
        """Get default content types to generate based on document type."""
        
        if document_type.startswith("pitch_deck"):
            return [
                ContentType.DUE_DILIGENCE,
                ContentType.SWOT_ANALYSIS,
                ContentType.EXECUTIVE_SUMMARY
            ]
        elif document_type.startswith("financial"):
            return [
                ContentType.FINANCIAL_SUMMARY,
                ContentType.RISK_ASSESSMENT
            ]
        elif document_type == "market_research":
            return [
                ContentType.MARKET_ANALYSIS,
                ContentType.COMPETITIVE_ANALYSIS
            ]
        else:
            return [
                ContentType.EXECUTIVE_SUMMARY
            ]
    
    def _calculate_overall_confidence(
        self,
        result: DocumentProcessingResult
    ) -> float:
        """Calculate overall confidence across all stages."""
        
        confidences = []
        
        if result.extraction:
            confidences.append(result.extraction.confidence_score)
        
        if result.analysis:
            confidences.append(result.analysis.overall_confidence)
        
        if result.verification:
            for verification in result.verification.values():
                confidences.append(verification.final_confidence)
        
        return sum(confidences) / len(confidences) if confidences else 0.0
    
    async def process_batch(
        self,
        documents: List[Dict[str, Any]],
        max_concurrent: int = 3
    ) -> List[DocumentProcessingResult]:
        """
        Process multiple documents concurrently.
        
        Args:
            documents: List of dicts with file_content, filename, etc.
            max_concurrent: Maximum concurrent processing jobs
        
        Returns:
            List of DocumentProcessingResults
        """
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_semaphore(doc):
            async with semaphore:
                return await self.process_document(**doc)
        
        tasks = [process_with_semaphore(doc) for doc in documents]
        return await asyncio.gather(*tasks, return_exceptions=True)


# Singleton instance
_document_processor: Optional[DocumentProcessor] = None


def get_document_processor() -> DocumentProcessor:
    """Get or create document processor instance."""
    global _document_processor
    if _document_processor is None:
        _document_processor = DocumentProcessor()
    return _document_processor


