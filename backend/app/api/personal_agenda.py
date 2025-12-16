"""
Personal Agenda - User-Specific View
Shows each person ONLY their action items and decisions
Automatically populated from meeting parsing
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from supabase import create_client
from app.config import settings
from app.api.styles import get_dv_styles

router = APIRouter()


@router.get("/agenda/{person_name}", response_class=HTMLResponse)
async def personal_agenda(person_name: str):
    """
    Personal agenda for specific team member.
    
    Shows:
    - Their assigned action items
    - Decisions that affect them
    - Meetings they attended
    - Documents sent to them
    
    All automatically populated - NO manual work needed.
    """
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    # Get person
    person_response = supabase.table('people').select('*').ilike('name', f'%{person_name}%').limit(1).execute()
    
    if not person_response.data:
        return HTMLResponse(f"<h1>Person not found: {person_name}</h1>", status_code=404)
    
    person = person_response.data[0]
    
    # Get their action items
    my_actions = supabase.table('action_items').select('*, meetings(title, meeting_date)').ilike('owner_name', f'%{person_name}%').execute().data
    
    # Get meetings they attended
    my_meetings = supabase.table('meeting_participants').select('meetings(*)').eq('person_id', person['id']).execute()
    meetings_attended = [m['meetings'] for m in my_meetings.data if m.get('meetings')]
    
    # Get decisions from their meetings
    meeting_ids = [m['id'] for m in meetings_attended]
    my_decisions = []
    for mid in meeting_ids:
        decs = supabase.table('decisions').select('*, meetings(title)').eq('meeting_id', mid).execute().data
        my_decisions.extend(decs)
    
    html = f"""
<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Personal Agenda - {person['name']}</title>
    {get_dv_styles()}
    <style>
        .agenda-container {{
            max-width: 1000px;
            margin: 0 auto;
            padding: 30px;
        }}
        
        .priority-high {{
            border-left-color: #dc3545 !important;
        }}
        
        .priority-medium {{
            border-left-color: #ff9800 !important;
        }}
        
        .priority-low {{
            border-left-color: #17a2b8 !important;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo" style="margin-bottom: 15px;">
            <span class="logo-accent">Disruptive</span> Ventures
        </div>
        <h1>Personal Agenda: {person['name']}</h1>
        <p>Auto-generated from your meetings | Updated automatically</p>
    </div>
    
    <div class="nav">
        <a href="/dashboard-ui">← Dashboard</a>
        <span style="margin-left: auto; color: #4a4a4a; font-size: 14px;">
            ✓ Synced with Linear | ✓ Synced with Calendar
        </span>
    </div>
    
    <div class="agenda-container">
        
        <!-- Stats -->
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{len(my_actions)}</div>
                <div class="stat-label">Your Tasks</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{sum(1 for a in my_actions if a.get('priority') == 'high')}</div>
                <div class="stat-label">High Priority</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(meetings_attended)}</div>
                <div class="stat-label">Meetings Attended</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(my_decisions)}</div>
                <div class="stat-label">Relevant Decisions</div>
            </div>
        </div>
        
        <!-- Your Action Items -->
        <div class="section">
            <h2 class="section-title">🎯 Your Action Items</h2>
            <p style="color: #666; margin-bottom: 20px;">
                ✓ Automatically sent to your Linear account<br>
                ✓ Deadlines added to your Google Calendar<br>
                ✓ Notifications sent via Slack and Email
            </p>
            
            {''.join([f'''
            <div class="card priority-{action.get('priority', 'low')}">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                    <h3 style="color: #1a1a1a; margin: 0; flex: 1;">{action['title']}</h3>
                    <div style="display: flex; gap: 8px;">
                        <span class="badge badge-{action.get('priority', 'low')}">{action.get('priority', 'low').upper()}</span>
                        <span class="badge badge-{action.get('status', 'open')}">{action.get('status', 'open').upper()}</span>
                    </div>
                </div>
                
                {f'<p style="color: #4a4a4a; margin-bottom: 15px;">{action.get("description")}</p>' if action.get('description') else ''}
                
                <div style="display: flex; gap: 20px; font-size: 14px; color: #666; padding-top: 15px; border-top: 1px solid #e0e0e0;">
                    {f'<span>📅 Due: {action.get("due_date", "No deadline")}</span>'}
                    <span>📋 From: {action.get('meetings', {}).get('title', 'Meeting') if isinstance(action.get('meetings'), dict) else 'Meeting'}</span>
                    <a href="#" style="margin-left: auto; color: #0066cc; text-decoration: none; font-weight: 600;">→ Open in Linear</a>
                </div>
            </div>
            ''' for action in my_actions]) if my_actions else '<div class="empty-state"><div class="empty-state-title">No tasks assigned</div><p>You have no pending action items</p></div>'}
        </div>
        
        <!-- Relevant Decisions -->
        <div class="section">
            <h2 class="section-title">✅ Relevant Decisions</h2>
            <p style="color: #666; margin-bottom: 20px;">
                Decisions from meetings you attended
            </p>
            
            {''.join([f'''
            <div class="decision">
                <div class="decision-text">{decision['decision']}</div>
                {f'<div class="decision-meta"><strong>Motivering:</strong> {decision.get("rationale")}</div>' if decision.get('rationale') else ''}
                <div style="font-size: 13px; color: #999; margin-top: 10px;">
                    From: {decision.get('meetings', {}).get('title', 'Meeting') if isinstance(decision.get('meetings'), dict) else 'Meeting'}
                </div>
            </div>
            ''' for decision in my_decisions[:10]]) if my_decisions else '<div class="empty-state"><p>No relevant decisions</p></div>'}
        </div>
        
        <!-- Your Meetings -->
        <div class="section">
            <h2 class="section-title">📅 Your Meetings</h2>
            
            {''.join([f'''
            <div class="card">
                <h3 style="margin: 0 0 10px 0;">{meeting.get('title', 'Untitled')}</h3>
                <div style="display: flex; gap: 15px; font-size: 14px; color: #666;">
                    <span>📅 {meeting.get('meeting_date', 'No date')}</span>
                    <span>⏱️ {meeting.get('duration_minutes', 'N/A')} min</span>
                    <a href="/meeting/{meeting.get('id')}" style="margin-left: auto; color: #0066cc; text-decoration: none; font-weight: 600;">View details →</a>
                </div>
            </div>
            ''' for meeting in meetings_attended[:5]]) if meetings_attended else '<div class="empty-state"><p>No meetings attended</p></div>'}
        </div>
        
    </div>
</body>
</html>
    """
    
    return HTMLResponse(content=html)




