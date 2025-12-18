"""Document Intelligence API - Process documents through 6-agent pipeline"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional, List
from datetime import datetime
import magic

from supabase import create_client

from app.config import settings
from app.services.document_processor import get_document_processor, ContentType
from app.services.agent_5_content_generator import ContentType as CT

router = APIRouter(prefix="/api/document-intelligence", tags=["Document Intelligence"])


@router.post("/upload")
async def upload_and_process_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    document_type: str = Form("other"),
    company_name: Optional[str] = Form(None),
    enable_research: bool = Form(True),
    generate_dd_report: bool = Form(True),
    generate_swot: bool = Form(True),
    org_id: str = Form(...)
):
    """
    Upload and process a document through the 6-agent pipeline.
    
    Returns:
        - document_id: ID for tracking processing status
        - status: Processing status
        - message: Status message
    """
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Detect MIME type
        mime_type = magic.from_buffer(file_content, mime=True)
        
        # Validate file type
        allowed_types = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword",
            "text/plain",
            "text/html"
        ]
        
        if mime_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {mime_type}. Supported: PDF, DOCX, DOC, TXT, HTML"
            )
        
        # Create database record
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        import hashlib
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        doc_record = {
            "org_id": org_id,
            "filename": file.filename,
            "file_hash": file_hash,
            "file_size": len(file_content),
            "mime_type": mime_type,
            "document_type": document_type,
            "processing_status": "processing",
            "visibility": "internal",
            "source": "upload"
        }
        
        result = supabase.table("uploaded_documents").insert(doc_record).execute()
        document_id = result.data[0]["id"]
        
        # Determine which content types to generate
        content_types = []
        if generate_dd_report:
            content_types.append(CT.DUE_DILIGENCE)
        if generate_swot:
            content_types.append(CT.SWOT_ANALYSIS)
        
        # Process in background
        background_tasks.add_task(
            process_document_pipeline,
            document_id=document_id,
            file_content=file_content,
            filename=file.filename,
            document_type=document_type,
            mime_type=mime_type,
            company_name=company_name,
            enable_research=enable_research,
            content_types=content_types if content_types else None
        )
        
        return JSONResponse({
            "document_id": document_id,
            "status": "processing",
            "message": "Document uploaded successfully. Processing started.",
            "filename": file.filename,
            "file_size": len(file_content),
            "estimated_time_minutes": 2
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{document_id}")
async def get_processing_status(document_id: str):
    """Get processing status for a document."""
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Get document
        doc = supabase.table("uploaded_documents").select("*").eq("id", document_id).single().execute()
        
        if not doc.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get analysis
        analysis = supabase.table("document_analyses").select("*").eq("document_id", document_id).order("created_at", desc=True).limit(1).execute()
        
        # Get generated content
        generated = supabase.table("generated_content").select("*").eq("analysis_id", analysis.data[0]["id"] if analysis.data else None).execute()
        
        return JSONResponse({
            "document_id": document_id,
            "filename": doc.data["filename"],
            "status": doc.data["processing_status"],
            "error": doc.data.get("processing_error"),
            "analysis_complete": len(analysis.data) > 0 if analysis.data else False,
            "reports_generated": len(generated.data) if generated.data else 0,
            "requires_review": analysis.data[0]["requires_human_review"] if analysis.data else False
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis/{document_id}")
async def get_document_analysis(document_id: str):
    """Get analysis results for a document."""
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Get latest analysis
        analysis = supabase.table("document_analyses").select("*").eq("document_id", document_id).order("analysis_version", desc=True).limit(1).single().execute()
        
        if not analysis.data:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return JSONResponse(analysis.data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/questions/{document_id}")
async def get_dd_questions(document_id: str):
    """Get due diligence questions for a document."""
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Get analysis first
        analysis = supabase.table("document_analyses").select("id").eq("document_id", document_id).order("analysis_version", desc=True).limit(1).single().execute()
        
        if not analysis.data:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Get questions
        questions = supabase.table("generated_questions").select("*").eq("analysis_id", analysis.data["id"]).execute()
        
        return JSONResponse({
            "document_id": document_id,
            "questions": questions.data,
            "total_count": len(questions.data)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/{document_id}")
async def get_generated_reports(document_id: str):
    """Get all generated reports for a document."""
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Get analysis
        analysis = supabase.table("document_analyses").select("id").eq("document_id", document_id).order("analysis_version", desc=True).limit(1).single().execute()
        
        if not analysis.data:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Get generated content
        content = supabase.table("generated_content").select("*").eq("analysis_id", analysis.data["id"]).execute()
        
        return JSONResponse({
            "document_id": document_id,
            "reports": content.data,
            "total_count": len(content.data)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/{document_id}/{content_type}")
async def get_specific_report(document_id: str, content_type: str):
    """Get a specific report type for a document."""
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Get analysis
        analysis = supabase.table("document_analyses").select("id").eq("document_id", document_id).order("analysis_version", desc=True).limit(1).single().execute()
        
        if not analysis.data:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Get specific content
        content = supabase.table("generated_content").select("*").eq("analysis_id", analysis.data["id"]).eq("content_type", content_type).order("version", desc=True).limit(1).single().execute()
        
        if not content.data:
            raise HTTPException(status_code=404, detail=f"{content_type} report not found")
        
        return JSONResponse(content.data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_processed_documents(
    org_id: str,
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None
):
    """List processed documents for an organization."""
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        query = supabase.table("v_document_pipeline_status").select("*").eq("org_id", org_id)
        
        if status:
            query = query.eq("processing_status", status)
        
        result = query.order("uploaded_at", desc=True).range(offset, offset + limit - 1).execute()
        
        return JSONResponse({
            "documents": result.data,
            "total": len(result.data),
            "limit": limit,
            "offset": offset
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Background processing function
async def process_document_pipeline(
    document_id: str,
    file_content: bytes,
    filename: str,
    document_type: str,
    mime_type: str,
    company_name: Optional[str],
    enable_research: bool,
    content_types: Optional[List[ContentType]]
):
    """Process document through pipeline and save results to database."""
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Get processor
        processor = get_document_processor()
        
        # Process document
        result = await processor.process_document(
            file_content=file_content,
            filename=filename,
            document_type=document_type,
            mime_type=mime_type,
            enable_research=enable_research,
            generate_content_types=content_types,
            company_name=company_name,
            document_date=None
        )
        
        # Save extraction
        if result.extraction:
            extraction_data = {
                "document_id": document_id,
                "extraction_version": 1,
                "extracted_text": result.extraction.extracted_text[:50000],  # Limit size
                "entities": [e.dict() for e in result.extraction.entities],
                "confidence_score": result.extraction.confidence_score,
                "ambiguities": [a.dict() for a in result.extraction.ambiguities],
                "ocr_used": result.extraction.ocr_used,
                "extractor_model": "gpt-4o-2024-08-06",
                "extractor_version": "1.0.0"
            }
            extraction_result = supabase.table("extracted_data").insert(extraction_data).execute()
            extraction_id = extraction_result.data[0]["id"]
        else:
            extraction_id = None
        
        # Save analysis
        if result.analysis and extraction_id:
            analysis_data = {
                "document_id": document_id,
                "extraction_id": extraction_id,
                "analysis_version": 1,
                "classification": result.analysis.classification.value,
                "key_metrics": {k: v.dict() for k, v in result.analysis.key_metrics.items()},
                "insights": [i.dict() for i in result.analysis.insights],
                "confidence_breakdown": result.analysis.confidence_breakdown,
                "overall_confidence": result.analysis.overall_confidence,
                "data_completeness": result.analysis.data_completeness,
                "internal_consistency": result.analysis.internal_consistency,
                "gaps": [g.dict() for g in result.analysis.gaps],
                "requires_human_review": result.analysis.requires_human_review,
                "review_reason": result.analysis.review_reason,
                "analyzer_model": "gpt-4o-2024-08-06",
                "analyzer_version": "1.0.0"
            }
            analysis_result = supabase.table("document_analyses").insert(analysis_data).execute()
            analysis_id = analysis_result.data[0]["id"]
        else:
            analysis_id = None
        
        # Save questions
        if result.questions and analysis_id:
            for question in (result.questions.critical + result.questions.high_priority + 
                           result.questions.medium_priority + result.questions.low_priority):
                question_data = {
                    "analysis_id": analysis_id,
                    "question": question.question,
                    "category": question.category.value,
                    "priority": question.priority.value,
                    "triggered_by": question.triggered_by,
                    "status": "open"
                }
                supabase.table("generated_questions").insert(question_data).execute()
        
        # Save generated content
        if result.generated_content and analysis_id:
            for content_type, content in result.generated_content.items():
                content_data = {
                    "analysis_id": analysis_id,
                    "content_type": content_type.value,
                    "content": content.content_markdown,
                    "content_html": content.content_html,
                    "sources_cited": [c.dict() for c in content.citations],
                    "confidence_level": content.confidence_level.value,
                    "citation_coverage": content.citation_coverage,
                    "disclaimer": content.disclaimer,
                    "generator_model": "gpt-4o-2024-08-06",
                    "generator_version": "1.0.0",
                    "version": 1
                }
                supabase.table("generated_content").insert(content_data).execute()
        
        # Update document status
        supabase.table("uploaded_documents").update({
            "processing_status": result.status.value,
            "processing_error": result.error_message
        }).eq("id", document_id).execute()
        
        print(f"✅ Document {document_id} processed successfully")
        
    except Exception as e:
        # Update status to failed
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        supabase.table("uploaded_documents").update({
            "processing_status": "failed",
            "processing_error": str(e)
        }).eq("id", document_id).execute()
        
        print(f"❌ Document {document_id} processing failed: {e}")


