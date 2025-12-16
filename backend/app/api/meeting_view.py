"""Meeting View - Monochrome design with left sidebar."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from supabase import create_client
from app.config import settings
from app.api.styles import get_dv_styles
from app.api.sidebar_component import get_admin_sidebar

router = APIRouter()


@router.get("/meeting/{meeting_id}", response_class=HTMLResponse)
async def meeting_view(meeting_id: str):
    """Meeting detail view with monochrome design."""
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Get meeting
        meeting = supabase.table('meetings').select('*').eq('id', meeting_id).single().execute().data
        
        # Get decisions
        decisions = supabase.table('decisions').select('*').eq('meeting_id', meeting_id).execute().data
        
        # Get action items
        actions = supabase.table('action_items').select('*').eq('meeting_id', meeting_id).execute().data
        
        # Get attendees
        attendees = supabase.table('meeting_attendees').select('people(*)').eq('meeting_id', meeting_id).execute().data
        
    except Exception as e:
        return HTMLResponse(f"<html><body><h1>Error loading meeting</h1><p>{str(e)}</p></body></html>")
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{meeting.get('title', 'Meeting')} - Admin</title>
    {get_dv_styles()}
    <style>
        .meeting-section {{
            margin-bottom: 32px;
        }}
        
        .section-title {{
            font-size: 14px;
            font-weight: 600;
            color: var(--gray-900);
            margin-bottom: 16px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
    </style>
</head>
<body>
    {get_admin_sidebar('dashboard', 'Markus Löwegren', 'markus.lowegren@disruptiveventures.se', '')}
    
    <div class="main-content">
        <div class="page-header">
            <h1 class="page-title">{meeting.get('title', 'Untitled Meeting')}</h1>
            <p class="page-description">
                {meeting.get('meeting_date', 'No date')} • {meeting.get('duration_minutes', 'N/A')} minutes • {meeting.get('company', 'Unknown')}
            </p>
        </div>
        
        <div class="container">
            <!-- Summary -->
            {f'''
            <div class="meeting-section">
                <h2 class="section-title">Summary</h2>
                <div style="padding: 16px; border: 1px solid var(--gray-200); border-radius: 8px; background: white;">
                    <p style="font-size: 14px; color: var(--gray-700); line-height: 1.6;">{meeting.get('summary', 'No summary available')}</p>
                </div>
            </div>
            ''' if meeting.get('summary') else ''}
            
            <!-- Decisions -->
            <div class="meeting-section">
                <h2 class="section-title">Decisions ({len(decisions)})</h2>
                {generate_decisions_html(decisions)}
            </div>
            
            <!-- Action Items -->
            <div class="meeting-section">
                <h2 class="section-title">Action Items ({len(actions)})</h2>
                {generate_actions_html(actions)}
            </div>
            
            <!-- Attendees -->
            <div class="meeting-section">
                <h2 class="section-title">Attendees ({len(attendees)})</h2>
                {generate_attendees_html(attendees)}
            </div>
        </div>
    </div>
</body>
</html>
    """
    
    return HTMLResponse(content=html)


def generate_decisions_html(decisions):
    if not decisions:
        return '<div class="empty-state"><div class="empty-state-title">No decisions recorded</div></div>'
    
    html = []
    for d in decisions:
        html.append(f'''
        <div class="item-card" style="margin-bottom: 12px;">
            <div class="item-title">{d.get('decision', 'No text')}</div>
            {f'<p style="font-size: 13px; color: var(--gray-600); margin-top: 8px;">{d.get("rationale", "")}</p>' if d.get('rationale') else ''}
        </div>
        ''')
    return '\n'.join(html)


def generate_actions_html(actions):
    if not actions:
        return '<div class="empty-state"><div class="empty-state-title">No action items</div></div>'
    
    html = []
    for a in actions:
        # Get Linear URL
        linear_url = a.get('linear_issue_url', '')
        linear_id = a.get('linear_issue_id', '')
        
        # Format due date
        due_date = a.get('due_date', '')
        due_display = str(due_date)[:10] if due_date else 'No deadline'
        
        # Description
        description = a.get('description', '')
        description_html = f'<p style="font-size: 13px; color: var(--gray-600); margin: 8px 0; line-height: 1.5;">{description[:150]}{"..." if len(description) > 150 else ""}</p>' if description else ''
        
        html.append(f'''
        <div class="item-card" style="margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div class="item-title">{a.get('title', 'Untitled')}</div>
                <div style="display: flex; gap: 4px;">
                    <span class="badge">{a.get('priority', 'low')}</span>
                    <span class="badge">{a.get('status', 'todo')}</span>
                </div>
            </div>
            
            {description_html}
            
            <div class="item-meta" style="margin-top: 8px;">
                <span>{a.get('owner_name', 'Unassigned')}</span>
                <span>•</span>
                <span>📅 {due_display}</span>
                {f'<span>•</span><a href="{linear_url}" target="_blank" style="color: var(--gray-900); text-decoration: none; font-weight: 500;">Linear {linear_id}</a>' if linear_url else ''}
            </div>
        </div>
        ''')
    return '\n'.join(html)


def generate_attendees_html(attendees):
    if not attendees:
        return '<div class="empty-state"><div class="empty-state-title">No attendees recorded</div></div>'
    
    html = []
    for a in attendees:
        person = a.get('people', {})
        html.append(f'''
        <div class="item-card" style="margin-bottom: 8px; display: flex; align-items: center; gap: 12px;">
            <div style="width: 40px; height: 40px; border-radius: 50%; background: var(--gray-200); display: flex; align-items: center; justify-content: center; font-weight: 600; color: var(--gray-600);">
                {person.get('name', '?')[0].upper() if person.get('name') else '?'}
            </div>
            <div>
                <div style="font-size: 14px; font-weight: 500; color: var(--gray-900);">{person.get('name', 'Unknown')}</div>
                <div style="font-size: 12px; color: var(--gray-600);">{person.get('email', '')}</div>
            </div>
        </div>
        ''')
    return '\n'.join(html)
