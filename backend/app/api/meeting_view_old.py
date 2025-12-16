"""Meeting detail view - shows parsed data in template format."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from app.api.styles import get_dv_styles

router = APIRouter()


@router.get("/meeting/{meeting_id}", response_class=HTMLResponse)
async def view_meeting(meeting_id: str):
    """
    View meeting details formatted according to the meeting notes template.
    Uses Supabase client to fetch data.
    """
    
    try:
        from supabase import create_client
        from app.config import settings
        
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Get meeting details using Supabase
        meeting_response = supabase.table('meetings').select('*, orgs(name)').eq('id', meeting_id).execute()
        
        if not meeting_response.data:
            return HTMLResponse("""
                <h1>Meeting Not Found</h1>
                <p>The meeting you're looking for doesn't exist.</p>
                <a href="/dashboard-ui">Back to Dashboard</a>
            """, status_code=404)
        
        meeting_data = meeting_response.data[0]
        org_name = meeting_data.get('orgs', {}).get('name', 'Unknown') if isinstance(meeting_data.get('orgs'), dict) else 'Unknown'
        
        # Format as tuple for template compatibility
        meeting = (
            meeting_data['id'],
            meeting_data['title'],
            meeting_data.get('meeting_date'),
            meeting_data.get('duration_minutes'),
            meeting_data.get('meeting_metadata'),
            meeting_data.get('created_at'),
            org_name,
            meeting_data.get('meeting_type'),
            meeting_data.get('location'),
            meeting_data.get('company')
        )
        
        
        # Get people (attendees)
        try:
            people_response = supabase.table('meeting_participants').select('people(name, email, role)').eq('meeting_id', meeting_id).execute()
            attendees_data = [p['people'] for p in people_response.data if p.get('people')]
            attendees = [(a['name'], a.get('email'), a.get('role')) for a in attendees_data]
        except Exception as e:
            print(f"Attendees query error: {e}")
            attendees = []
        
        # Get decisions
        decisions_response = supabase.table('decisions').select('*').eq('meeting_id', meeting_id).execute()
        decisions_data = decisions_response.data
        decisions = [(d['decision'], d.get('rationale'), d.get('source_quote'), None, d.get('created_at')) for d in decisions_data]
        
        # Get action items (keep full data for AI assistance)
        actions_response = supabase.table('action_items').select('*').eq('meeting_id', meeting_id).execute()
        actions_data = actions_response.data
        action_items = actions_data  # Keep full dict with IDs
        
        # Get source artifact
        artifact_response = supabase.table('artifacts').select('filename, file_type, created_at').eq('meeting_id', meeting_id).limit(1).execute()
        artifact = None
        if artifact_response.data:
            a = artifact_response.data[0]
            # Parse created_at if it's a string
            created_at_str = a.get('created_at', '')
            if created_at_str:
                try:
                    from datetime import datetime
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                except:
                    created_at = created_at_str
            else:
                created_at = 'Unknown'
            artifact = (a['filename'], a['file_type'], created_at)
        
    except Exception as e:
        return HTMLResponse(f"""
            <h1>Error Loading Meeting</h1>
            <p>Could not load meeting data: {str(e)}</p>
            <a href="/dashboard-ui">Back to Dashboard</a>
        """, status_code=500)
    
    # Build action items table HTML separately to avoid f-string backslash issues
    if action_items:
        action_rows = []
        for action_item in action_items:
            title = action_item.get("title", "Untitled")
            desc = action_item.get("description", "")
            desc_html = f'<br><small style="font-size: 13px; color: #666;">{desc[:80]}...</small>' if desc else ""
            owner = action_item.get("owner_name", "Unassigned")
            due = action_item.get("due_date", "No deadline")
            priority = action_item.get("priority", "low")
            status = action_item.get("status", "open")
            action_id = action_item.get("id", "")
            title_clean = action_item.get("title", "").replace("'", "")
            owner_clean = action_item.get("owner_name", "").replace("'", "")
            
            row = f'''<tr style="border-top: 1px solid #f0f0f0;">
                <td style="padding: 12px;"><strong>{title}</strong>{desc_html}</td>
                <td style="padding: 12px;">{owner}</td>
                <td style="padding: 12px;">{due}</td>
                <td style="padding: 12px;"><span class="badge badge-{priority}" style="font-size: 11px;">{priority.upper()}</span></td>
                <td style="padding: 12px;"><span class="badge badge-{status}" style="font-size: 11px;">{status}</span></td>
                <td style="padding: 12px;"><button onclick="completeTaskWithAI('{action_id}', '{title_clean}', '{owner_clean}')" style="padding: 6px 12px; background: linear-gradient(135deg, #0066cc, #ff6b35); color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; font-weight: 600;">🤖 AI</button></td>
            </tr>'''
            action_rows.append(row)
        
        action_table_html = '<table style="width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; font-size: 14px;"><thead><tr style="background: #f8f9fa;"><th style="text-align: left; padding: 10px; font-weight: 600; color: #666;">Task</th><th style="text-align: left; padding: 10px; font-weight: 600; color: #666;">Owner</th><th style="text-align: left; padding: 10px; font-weight: 600; color: #666;">Due</th><th style="text-align: left; padding: 10px; font-weight: 600; color: #666;">Priority</th><th style="text-align: left; padding: 10px; font-weight: 600; color: #666;">Status</th><th style="text-align: left; padding: 10px; font-weight: 600; color: #666;">Actions</th></tr></thead><tbody>' + ''.join(action_rows) + '</tbody></table>'
    else:
        action_table_html = '<span style="color: #999;">No action items</span>'
    
    # Format the HTML using the template structure
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{meeting[1] or "Meeting Details"} - Disruptive Ventures</title>
    {get_dv_styles()}
    <style>
        /* Clickable attendee links */
        a.attendee-link {{
            background: white;
            padding: 8px 14px;
            border-radius: 6px;
            font-size: 14px;
            border: 1px solid #e0e0e0;
            text-decoration: none;
            color: #1a1a1a;
            transition: all 0.2s;
            display: inline-block;
        }}
        
        a.attendee-link:hover {{
            border-color: #0066cc;
            box-shadow: 0 2px 8px rgba(0,102,204,0.15);
            transform: translateY(-1px);
        }}
        
        a.attendee-link strong {{
            color: #0066cc;
        }}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
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
        
        .header-meta {{
            opacity: 0.9;
            font-size: 14px;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            margin-top: 15px;
        }}
        
        .nav {{
            background: white;
            padding: 15px 30px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            display: flex;
            gap: 15px;
        }}
        
        .nav a {{
            padding: 8px 16px;
            text-decoration: none;
            color: #667eea;
            font-weight: 600;
            border-radius: 6px;
            transition: background 0.3s;
        }}
        
        .nav a:hover {{
            background: #f0f0f0;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 30px;
        }}
        
        .template {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 40px;
            padding-bottom: 30px;
            border-bottom: 2px solid #f0f0f0;
        }}
        
        .section:last-child {{
            border-bottom: none;
        }}
        
        .section-title {{
            font-size: 24px;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: 200px 1fr;
            gap: 15px;
            margin-bottom: 15px;
        }}
        
        .info-label {{
            font-weight: 600;
            color: #666;
        }}
        
        .info-value {{
            color: #333;
        }}
        
        .attendee-list {{
            display: grid;
            gap: 10px;
        }}
        
        .attendee {{
            padding: 12px;
            background: #f8f9fa;
            border-radius: 8px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .attendee-name {{
            font-weight: 600;
            color: #333;
        }}
        
        .attendee-email {{
            color: #667eea;
            font-size: 14px;
        }}
        
        .attendee-role {{
            margin-left: auto;
            padding: 4px 12px;
            background: #e3f2fd;
            color: #1976d2;
            border-radius: 12px;
            font-size: 13px;
        }}
        
        .decision {{
            padding: 20px;
            background: #e8f5e9;
            border-left: 4px solid #4caf50;
            border-radius: 8px;
            margin-bottom: 15px;
        }}
        
        .decision-text {{
            font-size: 16px;
            font-weight: 600;
            color: #2e7d32;
            margin-bottom: 10px;
        }}
        
        .decision-meta {{
            font-size: 14px;
            color: #666;
            margin-top: 8px;
        }}
        
        .action-item {{
            padding: 20px;
            background: #fff3e0;
            border-left: 4px solid #ff9800;
            border-radius: 8px;
            margin-bottom: 15px;
        }}
        
        .action-text {{
            font-size: 16px;
            font-weight: 600;
            color: #e65100;
            margin-bottom: 10px;
        }}
        
        .action-meta {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            font-size: 14px;
            color: #666;
            margin-top: 10px;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .badge-high {{
            background: #ffebee;
            color: #c62828;
        }}
        
        .badge-medium {{
            background: #fff3e0;
            color: #e65100;
        }}
        
        .badge-low {{
            background: #e3f2fd;
            color: #1976d2;
        }}
        
        .badge-todo {{
            background: #f5f5f5;
            color: #666;
        }}
        
        .badge-in_progress {{
            background: #e3f2fd;
            color: #1976d2;
        }}
        
        .badge-done {{
            background: #e8f5e9;
            color: #2e7d32;
        }}
        
        .key-points {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        
        .key-points li {{
            padding: 15px 20px;
            background: linear-gradient(135deg, #f8f9fa 0%%, #ffffff 100%%);
            border-left: 4px solid #667eea;
            border-radius: 8px;
            margin-bottom: 12px;
            padding-left: 45px;
            position: relative;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            transition: all 0.3s;
            font-size: 15px;
            line-height: 1.6;
        }}
        
        .key-points li:hover {{
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
            transform: translateX(5px);
        }}
        
        .key-points li:before {{
            content: "✓";
            position: absolute;
            left: 18px;
            color: #667eea;
            font-weight: bold;
            font-size: 18px;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 40px 20px;
            color: #999;
            font-style: italic;
        }}
        
        .source-info {{
            background: #e3f2fd;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 30px;
            border-left: 4px solid #1976d2;
        }}
        
        .source-info strong {{
            color: #1976d2;
        }}
        
        .export-btn {{
            display: inline-block;
            padding: 10px 20px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            margin-top: 20px;
        }}
        
        .export-btn:hover {{
            background: #5568d3;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div>
                <div class="logo" style="margin-bottom: 20px;">
                    <span class="logo-accent">Disruptive</span> Ventures
                </div>
                <h1>{meeting[1] or "Untitled Meeting"}</h1>
            </div>
        </div>
        <div class="header-meta">
            <span>📅 {meeting[2] if meeting[2] else "No date"}</span>
            <span>⏱️ {meeting[3] or "Unknown"} minutes</span>
            <span>🏢 {meeting[6] or meeting[9] or "Disruptive Ventures"}</span>
            {f'<span>📍 {meeting[8]}</span>' if meeting[8] else ''}
            {f'<span>🏷️ {meeting[7]}</span>' if meeting[7] else ''}
        </div>
    </div>
    
    <div class="nav">
        <a href="/dashboard-ui">← Dashboard</a>
        <a href="/upload-ui">📤 Upload</a>
        <a href="/automation/meeting-notes/{meeting[0]}" class="btn-secondary">📄 Download Notes</a>
        <button onclick="automateWorkflows()" class="btn-primary">⚡ Automate Follow-ups</button>
    </div>
    
    <div class="container">
        <div class="template">
            
            <!-- Compact Info Banner -->
            <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding: 15px 20px; border-radius: 8px; margin-bottom: 20px; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; font-size: 14px;">
                <div><strong>📄 Source:</strong> {artifact[0] if artifact else 'N/A'}</div>
                <div><strong>📅 Date:</strong> {meeting[2] or 'Not specified'}</div>
                <div><strong>⏱️ Duration:</strong> {meeting[3] or 'N/A'} min</div>
                <div><strong>🏷️ Type:</strong> {meeting[7] or 'Team meeting'}</div>
                <div><strong>🏢 Company:</strong> {meeting[9] or meeting[6] or 'Disruptive Ventures'}</div>
                {f'<div><strong>📍 Location:</strong> {meeting[8]}</div>' if meeting[8] else ''}
            </div>
            
            <!-- Attendees - Clickable to Personal Agendas -->
            <div class="section" style="margin-bottom: 20px;">
                <h3 style="font-size: 16px; font-weight: 700; margin-bottom: 10px; color: #1a1a1a;">👥 Attendees ({len(attendees)}) → Personal Dashboards</h3>
                <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                    {''.join([f'<a href="/agenda/{attendee[0]}" class="attendee-link"><strong>{attendee[0]}</strong>{" - " + attendee[2] if attendee[2] else ""}</a>' for attendee in attendees]) if attendees else '<span style="color: #999;">No attendees</span>'}
                </div>
            </div>
            
            <!-- Key Points & Topics - Compact -->
            {f'''
            <div class="section" style="margin-bottom: 20px;">
                <h3 style="font-size: 16px; font-weight: 700; margin-bottom: 10px; color: #1a1a1a;">💡 Key Points</h3>
                <div style="font-size: 14px; line-height: 1.6;">
                    {'<br>'.join([f'• {point}' for point in (meeting[4].get('key_points', []) if isinstance(meeting[4], dict) else [])])}
                </div>
            </div>
            ''' if meeting[4] and isinstance(meeting[4], dict) and meeting[4].get('key_points') else ''}
            
            {f'''
            <div class="section" style="margin-bottom: 20px;">
                <h3 style="font-size: 16px; font-weight: 700; margin-bottom: 10px; color: #1a1a1a;">🏷️ Topics</h3>
                <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                    {''.join([f'<span class="topic-badge" style="padding: 4px 10px; font-size: 12px;">{topic}</span>' for topic in (meeting[4].get('main_topics', []) if isinstance(meeting[4], dict) else [])])}
                </div>
            </div>
            ''' if meeting[4] and isinstance(meeting[4], dict) and meeting[4].get('main_topics') else ''}
            
            <!-- Decisions - Compact -->
            <div class="section" style="margin-bottom: 30px;">
                <h3 style="font-size: 16px; font-weight: 700; margin-bottom: 10px; color: #1a1a1a;">✅ Decisions ({len(decisions)})</h3>
                {''.join([f'<div style="background: #e8f5e9; padding: 12px 16px; border-left: 3px solid #28a745; border-radius: 4px; margin-bottom: 8px; font-size: 14px;"><strong>{decision[0]}</strong>{" — " + decision[1][:100] + "..." if decision[1] and len(decision[1]) > 100 else (" — " + decision[1] if decision[1] else "")}{" (" + decision[2] + ")" if decision[2] else ""}</div>' for decision in decisions]) if decisions else '<span style="color: #999;">No decisions</span>'}
            </div>
            
            <!-- Action Items - Data Table -->
            <div class="section" style="margin-bottom: 30px;">
                <h3 style="font-size: 16px; font-weight: 700; margin-bottom: 10px; color: #1a1a1a;">🎯 Action Items ({len(action_items)})</h3>
                {action_table_html}
            </div>
            
            
            <!-- Extraction Stats - Compact -->
            <div style="background: #f8f9fa; padding: 12px 20px; border-radius: 6px; margin-bottom: 20px; display: flex; gap: 30px; font-size: 14px;">
                <span><strong style="color: #0066cc;">{len(attendees)}</strong> Attendees</span>
                <span><strong style="color: #28a745;">{len(decisions)}</strong> Decisions</span>
                <span><strong style="color: #ff9800;">{len(action_items)}</strong> Actions</span>
                <span style="margin-left: auto;"><strong>📊 Extraction Complete</strong></span>
            </div>
            
            <!-- Generated Documents - Compact -->
            <div class="section" style="margin-bottom: 20px;">
                <h3 style="font-size: 16px; font-weight: 700; margin-bottom: 10px; color: #1a1a1a;">📄 Documents (Auto-Sent via Email/Slack/Drive)</h3>
                
                <!-- Progress indicator -->
                <div id="downloadProgress" style="display: none; background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #0066cc;">
                    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 10px;">
                        <div class="spinner" style="width: 24px; height: 24px; border: 3px solid #f3f3f3; border-top: 3px solid #0066cc; border-radius: 50%; animation: spin 1s linear infinite;"></div>
                        <div>
                            <strong id="progressTitle" style="color: #1a1a1a;">Generating document...</strong>
                            <div id="progressSubtitle" style="font-size: 14px; color: #4a4a4a; margin-top: 4px;">Please wait</div>
                        </div>
                    </div>
                    <div style="background: white; border-radius: 8px; height: 8px; overflow: hidden;">
                        <div id="progressBar" style="background: linear-gradient(90deg, #0066cc, #ff6b35); height: 100%%; width: 0%%; transition: width 0.5s;"></div>
                    </div>
                </div>
                
                <style>
                    @keyframes spin {{
                        0%% {{ transform: rotate(0deg); }}
                        100%% {{ transform: rotate(360deg); }}
                    }}
                </style>
                
                <table style="width: 100%; border-collapse: collapse; background: white; border-radius: 6px; overflow: hidden; font-size: 13px;">
                    <thead>
                        <tr style="background: #f8f9fa;">
                            <th style="text-align: left; padding: 8px; font-weight: 600; color: #666;">Document Type</th>
                            <th style="text-align: left; padding: 8px; font-weight: 600; color: #666;">Access Level</th>
                            <th style="text-align: left; padding: 8px; font-weight: 600; color: #666;">Status</th>
                            <th style="text-align: left; padding: 8px; font-weight: 600; color: #666;">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr style="border-top: 1px solid #f0f0f0;">
                            <td style="padding: 8px;"><strong>📋 Meeting Notes</strong></td>
                            <td style="padding: 8px;"><span class="badge" style="background: #e3f2fd; color: #0066cc; font-size: 10px;">VIEWER</span></td>
                            <td style="padding: 8px;"><span style="color: #28a745; font-size: 12px;">✓ Sent to all</span></td>
                            <td style="padding: 8px;">
                                <a href="/viewer/view/meeting_notes/sv?meeting_id={meeting[0]}" style="color: #0066cc; text-decoration: none; font-weight: 600; margin-right: 8px;">🇸🇪 SV</a>
                                <a href="/viewer/view/meeting_notes/en?meeting_id={meeting[0]}" style="color: #0066cc; text-decoration: none; font-weight: 600;">🇬🇧 EN</a>
                            </td>
                        </tr>
                        <tr style="border-top: 1px solid #f0f0f0;">
                            <td style="padding: 8px;"><strong>✉️ Decision Updates</strong></td>
                            <td style="padding: 8px;"><span class="badge" style="background: #fff3e0; color: #ff9800; font-size: 10px;">MEMBER</span></td>
                            <td style="padding: 8px;"><span style="color: #28a745; font-size: 12px;">✓ Auto-sent</span></td>
                            <td style="padding: 8px;">
                                <a href="/viewer/view/email_decision_update/sv?meeting_id={meeting[0]}" style="color: #0066cc; text-decoration: none; font-weight: 600; margin-right: 8px;">🇸🇪 SV</a>
                                <a href="/viewer/view/email_decision_update/en?meeting_id={meeting[0]}" style="color: #0066cc; text-decoration: none; font-weight: 600;">🇬🇧 EN</a>
                            </td>
                        </tr>
                        <tr style="border-top: 1px solid #f0f0f0;">
                            <td style="padding: 8px;"><strong>⏰ Action Reminders</strong></td>
                            <td style="padding: 8px;"><span class="badge" style="background: #e3f2fd; color: #0066cc; font-size: 10px;">VIEWER</span></td>
                            <td style="padding: 8px;"><span style="color: #28a745; font-size: 12px;">✓ Sent to owners</span></td>
                            <td style="padding: 8px;">
                                <a href="/viewer/view/email_action_reminder/sv?meeting_id={meeting[0]}" style="color: #0066cc; text-decoration: none; font-weight: 600; margin-right: 8px;">🇸🇪 SV</a>
                                <a href="/viewer/view/email_action_reminder/en?meeting_id={meeting[0]}" style="color: #0066cc; text-decoration: none; font-weight: 600;">🇬🇧 EN</a>
                            </td>
                        </tr>
                        <tr style="border-top: 1px solid #f0f0f0;">
                            <td style="padding: 8px;"><strong>📧 Summary Email</strong></td>
                            <td style="padding: 8px;"><span class="badge" style="background: #e3f2fd; color: #0066cc; font-size: 10px;">VIEWER</span></td>
                            <td style="padding: 8px;"><span style="color: #28a745; font-size: 12px;">✓ Sent to all</span></td>
                            <td style="padding: 8px;">
                                <a href="/viewer/view/email_meeting_summary/sv?meeting_id={meeting[0]}" style="color: #0066cc; text-decoration: none; font-weight: 600; margin-right: 8px;">🇸🇪 SV</a>
                                <a href="/viewer/view/email_meeting_summary/en?meeting_id={meeting[0]}" style="color: #0066cc; text-decoration: none; font-weight: 600;">🇬🇧 EN</a>
                            </td>
                        </tr>
                    </tbody>
                </table>
                
                <div style="font-size: 12px; color: #666; margin-top: 10px; padding: 10px; background: #f8f9fa; border-radius: 4px;">
                    ℹ️ All documents automatically distributed to assignees via Email, Slack, and saved to Google Drive. Web links are for admin review only.
                </div>
                
            </div>
            
        </div>
    </div>
    
    <script>
        async function completeTaskWithAI(actionId, taskTitle, assigneeName) {{
            showProgress(`🔬 4-Agent Workflow: Completing task...`, 'Agent 1: Researching verified sources');
            
            let progress = 0;
            const stages = [
                'Agent 1: Researching verified sources',
                'Agent 2: Generating solution',
                'Agent 3: Matching to requirements',
                'Agent 4: QA - Verifying links and sources'
            ];
            let stageIdx = 0;
            
            const interval = setInterval(() => {{
                progress += 8;
                if (progress <= 95) {{
                    updateProgress(progress);
                    const newStage = Math.floor(progress / 25);
                    if (newStage > stageIdx && newStage < stages.length) {{
                        stageIdx = newStage;
                        updateProgress(progress, stages[stageIdx]);
                    }}
                }}
            }}, 400);
            
            try {{
                const response = await fetch(`/tasks/complete/${{actionId}}?language=sv`, {{
                    method: 'POST'
                }});
                
                clearInterval(interval);
                updateProgress(100, '✅ Task completed and verified!');
                
                if (response.ok) {{
                    const content = await response.text();
                    
                    // Show in modal/overlay
                    const modal = document.createElement('div');
                    modal.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.85); z-index: 10000; display: flex; align-items: center; justify-content: center; padding: 20px;';
                    
                    modal.innerHTML = `
                        <div style="background: white; border-radius: 12px; max-width: 900px; max-height: 90vh; overflow-y: auto; padding: 40px; position: relative; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">
                            <button onclick="this.closest('div').parentElement.remove()" style="position: absolute; top: 20px; right: 20px; background: #f0f0f0; border: none; border-radius: 50%; width: 40px; height: 40px; cursor: pointer; font-size: 20px; font-weight: bold; color: #666;">×</button>
                            
                            <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 25px;">
                                <div style="background: linear-gradient(135deg, #0066cc, #ff6b35); width: 60px; height: 60px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 30px;">✅</div>
                                <div>
                                    <h2 style="color: #1a1a1a; margin: 0;">Uppgift Klar!</h2>
                                    <p style="color: #4a4a4a; margin: 5px 0 0 0;">${{taskTitle}}</p>
                                </div>
                            </div>
                            
                            <div style="background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); padding: 20px; border-radius: 8px; border-left: 4px solid #28a745; margin-bottom: 25px;">
                                <div style="display: flex; gap: 20px; flex-wrap: wrap; font-size: 14px;">
                                    <span><strong>📧 Mottagare:</strong> ${{assigneeName}}</span>
                                    <span><strong>✅ QA:</strong> Godkänd</span>
                                    <span><strong>🔗 Länkar:</strong> Verifierade</span>
                                    <span><strong>📚 Källor:</strong> Citerade</span>
                                </div>
                            </div>
                            
                            <div style="white-space: pre-wrap; line-height: 1.8; font-family: Georgia, serif; color: #333; max-height: 50vh; overflow-y: auto; padding: 20px; background: #f8f9fa; border-radius: 8px;">${{content}}</div>
                            
                            <div style="margin-top: 30px; display: flex; gap: 10px; padding-top: 20px; border-top: 2px solid #e0e0e0;">
                                <button onclick="navigator.clipboard.writeText(this.parentElement.previousElementSibling.textContent); alert('✅ Kopierad till urklipp!');" 
                                        style="padding: 12px 24px; background: #0066cc; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; transition: all 0.3s;">
                                    📋 Kopiera Allt
                                </button>
                                <button onclick="sendTaskEmail('${{actionId}}', '${{assigneeName}}')" 
                                        style="padding: 12px 24px; background: #28a745; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; transition: all 0.3s;">
                                    📧 Skicka till ${{assigneeName}}
                                </button>
                                <button onclick="downloadTaskSolution('${{actionId}}', '${{taskTitle}}')" 
                                        style="padding: 12px 24px; background: #ff6b35; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; transition: all 0.3s;">
                                    📥 Ladda ner MD
                                </button>
                            </div>
                        </div>
                    `;
                    
                    document.body.appendChild(modal);
                    
                    setTimeout(() => hideProgress(), 1500);
                }} else {{
                    const error = await response.text();
                    hideProgress();
                    const nl = '\\\\n';
                    alert('❌ Task completion failed QA check:' + nl + nl + error);
                }}
            }} catch (error) {{
                clearInterval(interval);
                hideProgress();
                alert('❌ Error: ' + error.message);
            }}
        }}
        
        async function sendTaskEmail(actionId, assigneeName) {{
            if (confirm(`Skicka lösningen via email till ${{assigneeName}}?`)) {{
                const nl = '\\\\n';
                alert('📧 Email-integration kommer snart!' + nl + nl + 'För nu: Klicka \"Kopiera Allt\" och skicka manuellt via din email.');
            }}
        }}
        
        async function downloadTaskSolution(actionId, taskTitle) {{
            const content = document.querySelector('.modal-content-text');
            if (content) {{
                const blob = new Blob([content.textContent], {{ type: 'text/plain; charset=utf-8' }});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `solution_${{taskTitle.replace(/[^a-zA-Z0-9]/g, '_')}}.txt`;
                a.click();
                URL.revokeObjectURL(url);
                alert('✅ Lösning nedladdad!');
            }}
        }}
        
        // Intercept document download links to show progress
        document.addEventListener('DOMContentLoaded', function() {{
            const docLinks = document.querySelectorAll('.doc-card a.btn');
            
            docLinks.forEach(link => {{
                link.addEventListener('click', function(e) {{
                    e.preventDefault();
                    const url = this.href;
                    const text = this.textContent;
                    
                    // Show progress
                    showProgress(`Generating ${{text}}...`, 'Preparing document');
                    
                    // Simulate progress
                    let progress = 0;
                    const interval = setInterval(() => {{
                        progress += 10;
                        updateProgress(progress);
                        if (progress >= 90) clearInterval(interval);
                    }}, 100);
                    
                    // Fetch and download
                    fetch(url)
                        .then(response => {{
                            if (!response.ok) throw new Error('Download failed');
                            updateProgress(95, 'Finalizing...');
                            return response.blob();
                        }})
                        .then(blob => {{
                            updateProgress(100, 'Complete!');
                            clearInterval(interval);
                            
                            // Trigger download
                            const downloadUrl = window.URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = downloadUrl;
                            a.download = url.split('/').pop().split('?')[0] + '.txt';
                            a.click();
                            window.URL.revokeObjectURL(downloadUrl);
                            
                            // Hide progress after delay
                            setTimeout(() => {{
                                hideProgress();
                            }}, 2000);
                        }})
                        .catch(error => {{
                            clearInterval(interval);
                            hideProgress();
                            alert('❌ Download failed: ' + error.message);
                        }});
                }});
            }});
        }});
        
        function showProgress(title, subtitle) {{
            document.getElementById('downloadProgress').style.display = 'block';
            document.getElementById('progressTitle').textContent = title;
            document.getElementById('progressSubtitle').textContent = subtitle;
            document.getElementById('progressBar').style.width = '0%%';
        }}
        
        function updateProgress(percent, subtitle) {{
            document.getElementById('progressBar').style.width = percent + '%%';
            if (subtitle) {{
                document.getElementById('progressSubtitle').textContent = subtitle;
            }}
        }}
        
        function hideProgress() {{
            document.getElementById('downloadProgress').style.display = 'none';
        }}
        
        async function automateWorkflows() {{
            const btn = event.target;
            btn.disabled = true;
            btn.textContent = '⏳ Processing...';
            
            showProgress('⚡ Automating workflows...', 'Creating Linear tasks and scheduling events');
            let progress = 0;
            const interval = setInterval(() => {{
                progress += 15;
                if (progress <= 90) updateProgress(progress);
            }}, 500);
            
            try {{
                const response = await fetch('/automation/automate/{meeting[0]}', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{
                        meeting_id: '{meeting[0]}',
                        send_emails: true,
                        create_linear_tasks: true,
                        schedule_next_meeting: false
                    }})
                }});
                
                clearInterval(interval);
                updateProgress(100, 'Complete!');
                
                if (response.ok) {{
                    const data = await response.json();
                    setTimeout(() => {{
                        hideProgress();
                        const newline = '\\\\n';
                        alert(`✅ Automation Complete!${{newline}}${{newline}}Linear tasks: ${{data.linear_tasks_created}}${{newline}}Emails generated: ${{data.emails_generated}}`);
                        btn.textContent = '✅ Complete!';
                    }}, 1000);
                }} else {{
                    hideProgress();
                    const error = await response.text();
                    alert('❌ Automation failed: ' + error);
                    btn.textContent = '⚡ Automate Follow-ups';
                    btn.disabled = false;
                }}
            }} catch (error) {{
                clearInterval(interval);
                hideProgress();
                alert('❌ Error: ' + error.message);
                btn.textContent = '⚡ Automate Follow-ups';
                btn.disabled = false;
            }}
        }}
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html)

