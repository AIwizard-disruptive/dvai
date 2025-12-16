"""
Task Assistance API
Generates AI-powered guidance for action items and sends to assignees
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from supabase import create_client
from app.config import settings
from app.services.task_assistant import TaskAssistant

router = APIRouter()


class TaskAssistanceRequest(BaseModel):
    """Request for task assistance."""
    action_item_id: str
    send_via: str = "email"  # email, slack, both
    language: str = "sv"


class TaskAssistanceResponse(BaseModel):
    """Response with generated assistance."""
    success: bool
    email_sent: bool = False
    slack_sent: bool = False
    email_subject: Optional[str] = None
    email_preview: Optional[str] = None
    ai_prompt: Optional[str] = None
    time_estimate: Optional[str] = None


@router.post("/assist", response_model=TaskAssistanceResponse)
async def generate_task_assistance(request: TaskAssistanceRequest):
    """
    Generate intelligent assistance for an action item.
    
    Uses AI to:
    1. Understand the task deeply
    2. Generate perfect AI prompt for assignee
    3. Provide step-by-step approach
    4. Estimate time and tools needed
    5. Send via email/Slack
    """
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    # Get action item
    action_response = supabase.table('action_items').select('*').eq('id', request.action_item_id).execute()
    if not action_response.data:
        raise HTTPException(status_code=404, detail="Action item not found")
    
    action = action_response.data[0]
    
    # Get meeting context
    meeting_response = supabase.table('meetings').select('*').eq('id', action['meeting_id']).execute()
    meeting_context = meeting_response.data[0] if meeting_response.data else {}
    
    # Get assignee info
    assignee_info = {
        'name': action.get('owner_name', 'Team member'),
        'email': action.get('owner_email')
    }
    
    # Generate assistance
    assistant = TaskAssistant()
    
    try:
        analysis = await assistant.analyze_and_assist(action, meeting_context, assignee_info)
        email = await assistant.generate_assistance_email(action, analysis, assignee_info, language=request.language)
        
        # TODO: Actually send email via Gmail API or Slack API
        # For now, return the generated content
        
        return TaskAssistanceResponse(
            success=True,
            email_sent=False,  # Set to True when email API integrated
            slack_sent=False,
            email_subject=email['subject'],
            email_preview=email['body'][:500],
            ai_prompt=analysis.get('best_prompt', ''),
            time_estimate=analysis.get('time_estimate', '')
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate assistance: {str(e)}")


@router.get("/preview/{action_item_id}")
async def preview_task_assistance(action_item_id: str, language: str = "sv"):
    """
    Preview the assistance that would be sent for an action item.
    Returns the full email/Slack content without sending.
    """
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    # Get action item
    action_response = supabase.table('action_items').select('*').eq('id', action_item_id).execute()
    if not action_response.data:
        raise HTTPException(status_code=404, detail="Action item not found")
    
    action = action_response.data[0]
    
    # Get meeting context
    meeting_response = supabase.table('meetings').select('*').eq('id', action['meeting_id']).execute()
    meeting_context = meeting_response.data[0] if meeting_response.data else {}
    
    # Get assignee info
    assignee_info = {
        'name': action.get('owner_name', 'Team member'),
        'email': action.get('owner_email')
    }
    
    # Generate assistance
    assistant = TaskAssistant()
    
    try:
        analysis = await assistant.analyze_and_assist(action, meeting_context, assignee_info)
        email = await assistant.generate_assistance_email(action, analysis, assignee_info, language=language)
        slack_msg = await assistant.generate_slack_message(action, analysis, assignee_info)
        
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(content=email['body'])
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate preview: {str(e)}")


@router.post("/complete/{action_item_id}")
async def complete_task_with_ai(action_item_id: str, language: str = "sv"):
    """
    COMPLETE the task using 4-agent workflow with research.
    
    Agents:
    1. RESEARCHER: Find and verify sources
    2. GENERATOR: Create actual solution
    3. MATCHER: Verify completeness
    4. QA: Check links, sources, quality
    
    Returns ready-to-use solution + email to assignee.
    """
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    # Get action item
    action_response = supabase.table('action_items').select('*').eq('id', action_item_id).execute()
    if not action_response.data:
        raise HTTPException(status_code=404, detail="Action item not found")
    
    action = action_response.data[0]
    
    # Get meeting context
    meeting_response = supabase.table('meetings').select('*').eq('id', action['meeting_id']).execute()
    meeting_context = meeting_response.data[0] if meeting_response.data else {}
    
    try:
        # Run 4-agent workflow
        from app.services.four_agent_task_completion import FourAgentTaskCompletion
        
        system = FourAgentTaskCompletion()
        result = await system.complete_task(action, meeting_context, language)
        
        if not result['success']:
            raise HTTPException(
                status_code=400,
                detail=f"Task completion failed QA: {result.get('issues', [])}"
            )
        
        # Return the complete package
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(
            content=result['email']['body'],
            headers={"Content-Type": "text/plain; charset=utf-8"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete task: {str(e)}")

