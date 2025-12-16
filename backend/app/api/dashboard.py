"""Dashboard API endpoint - view all parsed data."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from datetime import datetime

from app.config import settings
from app.api.styles import get_dv_styles

router = APIRouter()


@router.get("/dashboard-ui", response_class=HTMLResponse)
async def dashboard_ui():
    """
    Dashboard UI - Shows all parsed data from the database.
    Uses Supabase client to bypass database connection issues.
    """
    
    try:
        # Use Supabase client instead of database
        from supabase import create_client
        
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Get all meetings with processing status and metadata
        meetings_response = supabase.table('meetings').select('id, title, meeting_date, duration_minutes, created_at, company, processing_status, meeting_metadata').order('created_at', desc=True).limit(50).execute()
        meetings_data = meetings_response.data
        
        # Enrich meetings with generation status
        for m in meetings_data:
            metadata = m.get('meeting_metadata') or {}
            if isinstance(metadata, dict):
                m['has_linear_project'] = bool(metadata.get('linear_project_id'))
                m['linear_project_url'] = metadata.get('linear_project_url')
                m['drive_folder_url'] = metadata.get('drive_folder_url')
            else:
                m['has_linear_project'] = False
                m['linear_project_url'] = None
                m['drive_folder_url'] = None
            
            # Get counts for this meeting
            action_count = supabase.table('action_items').select('id', count='exact').eq('meeting_id', m['id']).execute()
            decision_count = supabase.table('decisions').select('id', count='exact').eq('meeting_id', m['id']).execute()
            
            m['action_items_count'] = action_count.count if hasattr(action_count, 'count') else 0
            m['decisions_count'] = decision_count.count if hasattr(decision_count, 'count') else 0
        
        # Format meetings as tuples for template
        meetings = [(m['id'], m['title'], m.get('meeting_date'), m.get('duration_minutes'), m.get('created_at'), m.get('company')) for m in meetings_data]
        
        # Get all decisions
        decisions_response = supabase.table('decisions').select('*').order('created_at', desc=True).limit(50).execute()
        decisions_data = decisions_response.data
        decisions = [(d['id'], d['decision'], d.get('rationale'), d.get('source_quote'), d.get('created_at'), None) for d in decisions_data]
        
        # Get all action items
        actions_response = supabase.table('action_items').select('*').order('created_at', desc=True).limit(50).execute()
        actions_data = actions_response.data
        action_items = [(a['id'], a['title'], a.get('owner_name'), a.get('due_date'), a.get('priority'), a.get('status'), a.get('created_at'), None) for a in actions_data]
        
        # Get all people - count UNIQUE attendees only
        people_response = supabase.table('people').select('*').execute()
        people_data = people_response.data
        
        # Count unique people by name (case-insensitive)
        unique_names = set()
        for p in people_data:
            name = p.get('name', '').strip()
            if name:
                unique_names.add(name.lower())
        
        unique_attendees_count = len(unique_names)
        attendees = [(p['id'], p['name'], p.get('email'), p.get('role'), 0) for p in people_data]
        
        # Get stats with unique attendees
        stats = (len(meetings_data), len(decisions_data), len(actions_data), unique_attendees_count)
        
    except Exception as e:
        # If query fails, show empty state
        meetings = []
        decisions = []
        action_items = []
        attendees = []
        stats = (0, 0, 0, 0)
        print(f"Dashboard query error: {e}")
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Disruptive Ventures Meeting Intelligence</title>
    <meta http-equiv="refresh" content="30">
    {get_dv_styles()}
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            color: #333;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%%, #764ba2 100%%);
            color: white;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}
        
        .header p {{
            opacity: 0.9;
            font-size: 16px;
        }}
        
        .nav {{
            background: white;
            padding: 15px 30px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            display: flex;
            gap: 20px;
            overflow-x: auto;
        }}
        
        .nav-btn {{
            padding: 10px 20px;
            border: none;
            background: #f0f0f0;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
            white-space: nowrap;
        }}
        
        .nav-btn.active {{
            background: #667eea;
            color: white;
        }}
        
        .nav-btn:hover {{
            background: #667eea;
            color: white;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 48px;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px;
        }}
        
        .section {{
            display: none;
        }}
        
        .section.active {{
            display: block;
        }}
        
        .section-title {{
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 20px;
            color: #333;
        }}
        
        .card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin-bottom: 20px;
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
            text-decoration: none;
            display: block;
            color: inherit;
        }}
        
        .card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        .card-title {{
            font-size: 18px;
            font-weight: 600;
            color: #333;
            flex: 1;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .badge-priority-high {{
            background: #fee;
            color: #c00;
        }}
        
        .badge-priority-medium {{
            background: #ffeaa7;
            color: #d63031;
        }}
        
        .badge-priority-low {{
            background: #e3f2fd;
            color: #1976d2;
        }}
        
        .badge-status-todo {{
            background: #f0f0f0;
            color: #666;
        }}
        
        .badge-status-in_progress {{
            background: #e3f2fd;
            color: #1976d2;
        }}
        
        .badge-status-done {{
            background: #e8f5e9;
            color: #2e7d32;
        }}
        
        .card-content {{
            color: #666;
            line-height: 1.6;
            margin-bottom: 10px;
        }}
        
        .card-meta {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            font-size: 13px;
            color: #999;
            margin-top: 15px;
        }}
        
        .card-meta-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            color: #999;
        }}
        
        .empty-state-icon {{
            font-size: 64px;
            margin-bottom: 20px;
        }}
        
        .empty-state-title {{
            font-size: 24px;
            color: #666;
            margin-bottom: 10px;
        }}
        
        .empty-state-text {{
            font-size: 16px;
            margin-bottom: 30px;
        }}
        
        .btn {{
            display: inline-block;
            padding: 12px 24px;
            background: #667eea;
            color: white;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: background 0.3s;
        }}
        
        .btn:hover {{
            background: #5568d3;
        }}
        
        .table {{
            width: 100%%;
            border-collapse: collapse;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        
        .table th {{
            background: #f8f9fa;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #666;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .table td {{
            padding: 15px;
            border-top: 1px solid #f0f0f0;
            color: #333;
        }}
        
        .table tr:hover {{
            background: #f8f9fa;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo" style="margin-bottom: 15px;">
            <span class="logo-accent">Disruptive</span> Ventures
        </div>
        <h1>Meeting Intelligence Dashboard</h1>
        <p>View all parsed meetings, decisions, action items, and attendees</p>
    </div>
    
    <div class="nav">
        <button class="nav-btn active" onclick="showSection('overview')">Overview</button>
        <button class="nav-btn" onclick="showSection('meetings')">Meetings</button>
        <button class="nav-btn" onclick="showSection('decisions')">Decisions</button>
        <button class="nav-btn" onclick="showSection('action-items')">Action Items</button>
        <button class="nav-btn" onclick="showSection('attendees')">Attendees</button>
        <a href="/upload-ui" class="nav-btn" style="margin-left: auto; text-decoration: none; color: inherit;">
            📤 Upload Files
        </a>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{stats[0] if stats else 0}</div>
            <div class="stat-label">Meetings</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats[1] if stats else 0}</div>
            <div class="stat-label">Decisions</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats[2] if stats else 0}</div>
            <div class="stat-label">Action Items</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats[3] if stats else 0}</div>
            <div class="stat-label">Attendees</div>
        </div>
    </div>
    
    <div class="container">
        <!-- Overview Section -->
        <div id="overview" class="section active">
            <h2 class="section-title">Recent Activity</h2>
            
            {''.join([f'''
            <div class="card" style="margin-bottom: 20px;">
                <div class="card-header">
                    <div class="card-title">📅 {m['title'] or "Untitled Meeting"}</div>
                    <div style="display: flex; gap: 8px;">
                        {f'<a href="{m["drive_folder_url"]}" target="_blank" style="background: #4285f4; color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 13px;">📁 Drive</a>' if m.get('drive_folder_url') else '<span style="background: #f0f0f0; color: #999; padding: 6px 12px; border-radius: 6px; font-size: 13px;">📁 No Drive</span>'}
                        {f'<a href="{m["linear_project_url"]}" target="_blank" style="background: #5e6ad2; color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 13px;">📊 Linear</a>' if m.get('linear_project_url') else '<span style="background: #f0f0f0; color: #999; padding: 6px 12px; border-radius: 6px; font-size: 13px;">📊 No Linear</span>'}
                    </div>
                </div>
                <div class="card-meta">
                    <span class="card-meta-item">📅 {str(m['meeting_date'])[:10] if m.get('meeting_date') else "No date"}</span>
                    <span class="card-meta-item">✅ {m.get('action_items_count', 0)} tasks</span>
                    <span class="card-meta-item">💡 {m.get('decisions_count', 0)} decisions</span>
                    <span class="card-meta-item">
                        <span style="background: {'#4caf50' if m.get('processing_status') == 'completed' else '#ff9800' if m.get('processing_status') == 'processing' else '#f44336'}; color: white; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: 600;">
                            {m.get('processing_status') or 'pending'}
                        </span>
                    </span>
                </div>
                
                <!-- Progress Bar -->
                <div style="margin-top: 12px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 12px; color: #666;">
                        <span>Generation Progress</span>
                        <span>{('100%' if m['has_linear_project'] and m.get('drive_folder_url') else '50%' if m['has_linear_project'] or m.get('drive_folder_url') else '0%')}</span>
                    </div>
                    <div style="background: #e0e0e0; height: 8px; border-radius: 4px; overflow: hidden;">
                        <div style="background: linear-gradient(90deg, #0066cc, #00c853); height: 100%; width: {('100%' if m['has_linear_project'] and m.get('drive_folder_url') else '50%' if m['has_linear_project'] or m.get('drive_folder_url') else '0%')}; transition: width 0.3s;"></div>
                    </div>
                    <div style="margin-top: 8px; font-size: 12px; color: #666;">
                        {'✅ Drive folder created' if m.get('drive_folder_url') else '⏳ Drive pending'} | 
                        {'✅ Linear project created' if m['has_linear_project'] else '⏳ Linear pending'}
                    </div>
                </div>
                
                <div style="margin-top: 12px;">
                    <a href="/meeting/{m['id']}" style="color: #0066cc; text-decoration: none; font-weight: 600;">View Details →</a>
                </div>
            </div>
            ''' for m in meetings_data[:10]]) if meetings_data else '<div class="empty-state"><div class="empty-state-icon">📭</div><div class="empty-state-title">No meetings yet</div><div class="empty-state-text">Upload your first meeting file to get started</div><a href="/upload-ui" class="btn">Upload Files</a></div>'}
        </div>
        
        <!-- Meetings Section -->
        <div id="meetings" class="section">
            <h2 class="section-title">All Meetings</h2>
            
            {''.join([f'''
            <a href="/meeting/{meeting[0]}" class="card">
                <div class="card-header">
                    <div class="card-title">📅 {meeting[1] or "Untitled Meeting"}</div>
                </div>
                <div class="card-meta">
                    <span class="card-meta-item">🏢 {meeting[5] or "Unknown Org"}</span>
                    <span class="card-meta-item">📅 {str(meeting[2])[:10] if meeting[2] else "No date"}</span>
                    <span class="card-meta-item">⏱️ {meeting[3] or "N/A"} minutes</span>
                    <span class="card-meta-item">🆔 {str(meeting[0])[:8]}...</span>
                    <span class="card-meta-item" style="color: #667eea; font-weight: 600;">→ View Details</span>
                </div>
            </a>
            ''' for meeting in meetings]) if meetings else '<div class="empty-state"><div class="empty-state-icon">📭</div><div class="empty-state-title">No meetings yet</div></div>'}
        </div>
        
        <!-- Decisions Section -->
        <div id="decisions" class="section">
            <h2 class="section-title">All Decisions</h2>
            
            {''.join([f'''
            <div class="card">
                <div class="card-header">
                    <div class="card-title">✅ {decision[1][:100]}{"..." if len(decision[1]) > 100 else ""}</div>
                </div>
                {f'<div class="card-content"><strong>Rationale:</strong> {decision[2]}</div>' if decision[2] else ''}
                <div class="card-meta">
                    {f'<span class="card-meta-item">👤 {decision[3]}</span>' if decision[3] else ''}
                    {f'<span class="card-meta-item">📝 {decision[5]}</span>' if decision[5] else ''}
                </div>
            </div>
            ''' for decision in decisions]) if decisions else '<div class="empty-state"><div class="empty-state-icon">📭</div><div class="empty-state-title">No decisions yet</div></div>'}
        </div>
        
        <!-- Action Items Section -->
        <div id="action-items" class="section">
            <h2 class="section-title">All Action Items</h2>
            
            {''.join([f'''
            <div class="card">
                <div class="card-header">
                    <div class="card-title">🎯 {action_item[1][:100]}{"..." if len(action_item[1]) > 100 else ""}</div>
                    <div>
                        {f'<span class="badge badge-priority-{action_item[4] or "low"}">{action_item[4] or "low"}</span>' if action_item[4] else ''}
                        {f'<span class="badge badge-status-{action_item[5] or "todo"}">{action_item[5] or "open"}</span>' if action_item[5] else ''}
                    </div>
                </div>
                <div class="card-meta">
                    {f'<span class="card-meta-item">👤 {action_item[2]}</span>' if action_item[2] else ''}
                    {f'<span class="card-meta-item">📅 Due: {action_item[3]}</span>' if action_item[3] else ''}
                    {f'<span class="card-meta-item">📝 {action_item[7]}</span>' if action_item[7] else ''}
                </div>
            </div>
            ''' for action_item in action_items]) if action_items else '<div class="empty-state"><div class="empty-state-icon">📭</div><div class="empty-state-title">No action items yet</div></div>'}
        </div>
        
        <!-- Attendees Section -->
        <div id="attendees" class="section">
            <h2 class="section-title">All Attendees</h2>
            
            {'<table class="table"><thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Meetings</th></tr></thead><tbody>' + ''.join([f'''
            <tr>
                <td><strong>{attendee[1] or "Unknown"}</strong></td>
                <td>{attendee[2] or "N/A"}</td>
                <td>{attendee[3] or "N/A"}</td>
                <td><span class="badge" style="background: #e3f2fd; color: #1976d2;">{attendee[4]} meetings</span></td>
            </tr>
            ''' for attendee in attendees]) + '</tbody></table>' if attendees else '<div class="empty-state"><div class="empty-state-icon">📭</div><div class="empty-state-title">No attendees yet</div></div>'}
        </div>
    </div>
    
    <script>
        function showSection(sectionId) {{
            // Hide all sections
            document.querySelectorAll('.section').forEach(section => {{
                section.classList.remove('active');
            }});
            
            // Show selected section
            document.getElementById(sectionId).classList.add('active');
            
            // Update active nav button
            document.querySelectorAll('.nav-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            event.target.classList.add('active');
        }}
        
        // Auto-refresh every 30 seconds
        // setTimeout(() => {{
        //     window.location.reload();
        // }}, 30000);
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html)

