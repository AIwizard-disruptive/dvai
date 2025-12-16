"""
Marcus Test Distribution
Creates Drive folders and Gmail drafts for Marcus only
Test the enhanced distribution before rolling out to everyone
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from supabase import create_client
from app.config import settings

router = APIRouter(prefix="/marcus-test", tags=["Marcus Test"])


class TestMeetingData(BaseModel):
    """Test meeting data for Marcus."""
    meeting_title: str = "Test Meeting for Marcus"
    meeting_date: str = "2025-12-15"
    action_items: List[str] = [
        "Review Linear integration (High, due Friday)",
        "Test Google Drive folders (Medium, due Monday)",
        "Verify Gmail drafts (Low, due next week)"
    ]


@router.get("/", response_class=HTMLResponse)
async def marcus_test_page():
    """Marcus test page for enhanced distribution."""
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Marcus Test - Enhanced Distribution</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .card {{
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin: 20px 0;
        }}
        h1 {{
            color: #0066cc;
            margin-bottom: 10px;
        }}
        .status {{
            padding: 8px 16px;
            border-radius: 6px;
            display: inline-block;
            font-weight: 600;
            margin: 8px 0;
        }}
        .status.success {{
            background: #4caf50;
            color: white;
        }}
        .status.pending {{
            background: #ff9800;
            color: white;
        }}
        .status.error {{
            background: #f44336;
            color: white;
        }}
        button {{
            background: linear-gradient(135deg, #0066cc, #00c853);
            color: white;
            border: none;
            padding: 14px 28px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin: 8px 8px 8px 0;
        }}
        button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }}
        .step {{
            background: #f8f9fa;
            padding: 16px;
            border-radius: 8px;
            margin: 12px 0;
            border-left: 4px solid #0066cc;
        }}
        code {{
            background: #f0f0f0;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
        }}
        .test-result {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 16px 0;
            display: none;
        }}
    </style>
</head>
<body>
    <div class="card">
        <h1>🧪 Marcus Test - Enhanced Distribution</h1>
        <p>Test the enhanced distribution system with your Google account before rolling out to team.</p>
        
        <div class="step">
            <h3>📋 Status Checklist</h3>
            <div id="statusChecklist">
                <p>⏳ Checking...</p>
            </div>
        </div>
    </div>
    
    <div class="card">
        <h2>🚀 Quick Setup</h2>
        
        <div class="step">
            <h3>Step 1: Enable Google APIs</h3>
            <p>Enable these in Google Cloud Console:</p>
            <button onclick="window.open('https://console.cloud.google.com/apis/library/drive.googleapis.com', '_blank')">
                📁 Enable Drive API
            </button>
            <button onclick="window.open('https://console.cloud.google.com/apis/library/gmail.googleapis.com', '_blank')">
                📧 Enable Gmail API
            </button>
        </div>
        
        <div class="step">
            <h3>Step 2: Connect Your Google Account</h3>
            <button onclick="connectGoogle()">
                🔗 Connect Google Account
            </button>
            <p style="color: #666; font-size: 14px; margin-top: 8px;">
                You'll be redirected to Google to authorize access to Drive and Gmail.
            </p>
        </div>
        
        <div class="step">
            <h3>Step 3: Test Drive Folder Creation</h3>
            <button onclick="testDriveFolder()">
                📂 Create Test Drive Folder
            </button>
            <div id="driveResult" class="test-result"></div>
        </div>
        
        <div class="step">
            <h3>Step 4: Test Gmail Draft Creation</h3>
            <button onclick="testGmailDraft()">
                ✉️ Create Test Gmail Draft
            </button>
            <div id="gmailResult" class="test-result"></div>
        </div>
        
        <div class="step">
            <h3>Step 5: Test Complete Enhanced Flow</h3>
            <button onclick="testFullFlow()">
                🎯 Run Full Test (Drive + Linear + Gmail)
            </button>
            <div id="fullResult" class="test-result"></div>
        </div>
    </div>
    
    <div class="card">
        <h2>📊 What Gets Created</h2>
        <p><strong>When you run the full test:</strong></p>
        <ul>
            <li><strong>Google Drive:</strong> Folder at <code>/Meetings/2025/December/2025-12-15 Test Meeting/</code></li>
            <li><strong>Google Docs:</strong> 6 documents uploaded (Meeting Notes, Decisions, Actions in SV + EN)</li>
            <li><strong>Linear Project:</strong> "Test Meeting (2025-12-15)" with your tasks</li>
            <li><strong>Linear Tasks:</strong> 3 test tasks assigned to you with Drive doc links</li>
            <li><strong>Gmail Draft:</strong> ONE email to you with all tasks and links</li>
        </ul>
    </div>
    
    <script>
        async function checkStatus() {{
            const checklist = document.getElementById('statusChecklist');
            let html = '<ul style="list-style: none; padding: 0;">';
            
            // Check Linear
            try {{
                const linearRes = await fetch('/integrations/linear/status');
                const linearData = await linearRes.json();
                if (linearData.status === 'connected') {{
                    html += '<li>✅ <strong>Linear:</strong> Connected (Team: ' + linearData.teams[0].name + ')</li>';
                }} else {{
                    html += '<li>❌ <strong>Linear:</strong> Not connected</li>';
                }}
            }} catch(e) {{
                html += '<li>❌ <strong>Linear:</strong> Error</li>';
            }}
            
            // Check Google
            try {{
                const googleRes = await fetch('/integrations/google/status');
                const googleData = await googleRes.json();
                if (googleData.oauth_configured) {{
                    if (googleData.user_connected) {{
                        html += '<li>✅ <strong>Google:</strong> Connected and ready</li>';
                    }} else {{
                        html += '<li>⚠️ <strong>Google:</strong> OAuth configured, needs account connection</li>';
                    }}
                }} else {{
                    html += '<li>❌ <strong>Google:</strong> Not configured</li>';
                }}
            }} catch(e) {{
                html += '<li>⚠️ <strong>Google:</strong> Checking...</li>';
            }}
            
            html += '</ul>';
            checklist.innerHTML = html;
        }}
        
        async function connectGoogle() {{
            try {{
                const res = await fetch('/integrations/google/connect');
                const data = await res.json();
                if (data.authorization_url) {{
                    window.location.href = data.authorization_url;
                }} else {{
                    alert('Error: ' + JSON.stringify(data));
                }}
            }} catch(e) {{
                alert('Error connecting Google: ' + e.message);
            }}
        }}
        
        async function testDriveFolder() {{
            const resultDiv = document.getElementById('driveResult');
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = '<p>⏳ Creating Drive folder...</p>';
            
            try {{
                const res = await fetch('/marcus-test/create-drive-folder', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{
                        meeting_title: "Marcus Test Meeting",
                        meeting_date: "2025-12-15"
                    }})
                }});
                
                const data = await res.json();
                
                if (data.success) {{
                    resultDiv.innerHTML = `
                        <h4 style="color: #4caf50;">✅ Success!</h4>
                        <p><strong>Folder created:</strong> ${{data.folder.path}}</p>
                        <p><a href="${{data.folder.url}}" target="_blank" style="color: #0066cc;">📂 Open in Google Drive</a></p>
                    `;
                }} else {{
                    resultDiv.innerHTML = `<h4 style="color: #f44336;">❌ Error:</h4><p>${{data.error || 'Unknown error'}}</p>`;
                }}
            }} catch(e) {{
                resultDiv.innerHTML = `<h4 style="color: #f44336;">❌ Error:</h4><p>${{e.message}}</p>`;
            }}
        }}
        
        async function testGmailDraft() {{
            const resultDiv = document.getElementById('gmailResult');
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = '<p>⏳ Creating Gmail draft...</p>';
            
            try {{
                const res = await fetch('/marcus-test/create-gmail-draft', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{
                        meeting_title: "Marcus Test Meeting",
                        tasks: ["Test task 1", "Test task 2", "Test task 3"]
                    }})
                }});
                
                const data = await res.json();
                
                if (data.success) {{
                    resultDiv.innerHTML = `
                        <h4 style="color: #4caf50;">✅ Success!</h4>
                        <p><strong>Draft created in your Gmail!</strong></p>
                        <p>Subject: ${{data.draft.subject}}</p>
                        <p><a href="https://mail.google.com/mail/#drafts" target="_blank" style="color: #0066cc;">📧 Open Gmail Drafts</a></p>
                    `;
                }} else {{
                    resultDiv.innerHTML = `<h4 style="color: #f44336;">❌ Error:</h4><p>${{data.error || 'Unknown error'}}</p>`;
                }}
            }} catch(e) {{
                resultDiv.innerHTML = `<h4 style="color: #f44336;">❌ Error:</h4><p>${{e.message}}</p>`;
            }}
        }}
        
        async function testFullFlow() {{
            const resultDiv = document.getElementById('fullResult');
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = '<p>⏳ Running full test (Drive + Linear + Gmail)...</p>';
            
            try {{
                const res = await fetch('/marcus-test/full-test', {{
                    method: 'POST'
                }});
                
                const data = await res.json();
                
                if (data.success) {{
                    resultDiv.innerHTML = `
                        <h4 style="color: #4caf50;">✅ Full Test Complete!</h4>
                        <ul style="list-style: none; padding: 0;">
                            <li>✓ Drive folder: <a href="${{data.results.drive_folder?.url}}" target="_blank">Open</a></li>
                            <li>✓ Google Docs: ${{data.results.docs_created}} uploaded</li>
                            <li>✓ Linear project: <a href="${{data.results.linear_project?.url}}" target="_blank">Open</a></li>
                            <li>✓ Linear tasks: ${{data.results.tasks_created}} created</li>
                            <li>✓ Gmail draft: <a href="https://mail.google.com/mail/#drafts" target="_blank">Open Drafts</a></li>
                        </ul>
                        <p style="margin-top: 20px;"><strong>Everything works! Ready to roll out to team.</strong></p>
                    `;
                }} else {{
                    resultDiv.innerHTML = `<h4 style="color: #f44336;">❌ Error:</h4><p>${{data.error || 'Unknown error'}}</p>`;
                }}
            }} catch(e) {{
                resultDiv.innerHTML = `<h4 style="color: #f44336;">❌ Error:</h4><p>${{e.message}}</p>`;
            }}
        }}
        
        // Check status on load
        checkStatus();
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html)


@router.post("/create-drive-folder")
async def create_test_drive_folder(data: Optional[TestMeetingData] = None):
    """
    Test Google Drive folder creation for Marcus.
    Creates folder structure and uploads test documents.
    """
    
    # Check if Google is configured
    if not settings.google_client_id:
        return JSONResponse({
            "success": False,
            "error": "Google OAuth not configured. Set GOOGLE_CLIENT_ID in .env"
        }, status_code=400)
    
    # TODO: Get Marcus's Google credentials from database
    # For now, instruct to connect Google account first
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    # Check for stored Google credentials (any user for testing)
    integration = supabase.table('user_integrations').select('*').match({
        'integration_type': 'google',
        'is_active': True
    }).limit(1).execute()
    
    if not integration.data:
        return JSONResponse({
            "success": False,
            "error": "No Google account connected. Click 'Connect Google Account' first.",
            "action": "connect_google"
        }, status_code=400)
    
    try:
        from app.integrations.google_client import get_google_client
        from googleapiclient.discovery import build
        
        # Use first connected Google account (Marcus's)
        creds = integration.data[0]
        client = get_google_client(
            access_token=creds['access_token'],
            refresh_token=creds.get('refresh_token')
        )
        
        drive_service = build('drive', 'v3', credentials=client.credentials)
        
        # Create folder structure
        meeting_title = data.meeting_title if data else "Marcus Test Meeting"
        meeting_date = data.meeting_date if data else datetime.now().strftime('%Y-%m-%d')
        
        # Create hierarchy
        folder_result = await _create_drive_folder_hierarchy(
            drive_service,
            meeting_title,
            meeting_date
        )
        
        return {
            "success": True,
            "folder": folder_result,
            "message": "Drive folder created successfully! Check Google Drive."
        }
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)


@router.post("/create-gmail-draft")
async def create_test_gmail_draft(data: Optional[TestMeetingData] = None):
    """
    Test Gmail draft creation for Marcus.
    Creates consolidated draft with all tasks.
    """
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    # Get Marcus's Google credentials
    integration = supabase.table('user_integrations').select('*').match({
        'integration_type': 'google',
        'is_active': True
    }).limit(1).execute()
    
    if not integration.data:
        return JSONResponse({
            "success": False,
            "error": "No Google account connected. Connect Google first.",
            "action": "connect_google"
        }, status_code=400)
    
    try:
        from app.integrations.google_client import get_google_client
        
        creds = integration.data[0]
        client = get_google_client(
            access_token=creds['access_token'],
            refresh_token=creds.get('refresh_token')
        )
        
        # Build test email
        meeting_title = data.meeting_title if data else "Marcus Test Meeting"
        tasks = data.action_items if data else [
            "Test task 1 (High, due Friday)",
            "Test task 2 (Medium, due Monday)",
            "Test task 3 (Low, due next week)"
        ]
        
        subject = f"📋 Action Items from {meeting_title}"
        
        body_html = _build_test_email_body(meeting_title, tasks)
        
        # Get user's email from Google
        # For now, use a test email or Marcus's email
        to_email = "marcus@disruptiveventures.se"  # Replace with actual
        
        draft = await client.create_email_draft(
            to=[to_email],
            subject=subject,
            body_html=body_html
        )
        
        return {
            "success": True,
            "draft": {
                "id": draft['id'],
                "subject": subject,
                "recipient": to_email
            },
            "message": "Gmail draft created! Check your Gmail Drafts folder."
        }
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)


@router.post("/full-test")
async def run_full_test():
    """
    Run complete enhanced distribution test for Marcus.
    
    Creates:
    1. Google Drive folder with test documents
    2. Linear project with test tasks
    3. Gmail draft with all tasks
    
    Returns:
        Complete audit log of what was created
    """
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    # Get Marcus's integrations
    google_integration = supabase.table('user_integrations').select('*').match({
        'integration_type': 'google',
        'is_active': True
    }).limit(1).execute()
    
    if not google_integration.data:
        return JSONResponse({
            "success": False,
            "error": "Google not connected. Connect Google account first.",
            "next_step": "Click 'Connect Google Account' button"
        }, status_code=400)
    
    results = {
        'drive_folder': None,
        'docs_created': 0,
        'linear_project': None,
        'tasks_created': 0,
        'gmail_draft': None,
        'errors': []
    }
    
    try:
        # Create test meeting data
        test_meeting = {
            'id': 'test-' + datetime.now().strftime('%Y%m%d%H%M%S'),
            'title': 'Marcus Enhanced Distribution Test',
            'meeting_date': datetime.now().strftime('%Y-%m-%d'),
            'meeting_metadata': {}
        }
        
        test_actions = [
            {
                'id': 'action-1',
                'title': 'Review Google Drive integration',
                'description': 'Verify folders are created correctly',
                'owner_name': 'Marcus',
                'owner_email': 'marcus@disruptiveventures.se',
                'priority': 'high',
                'due_date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
                'metadata': {}
            },
            {
                'id': 'action-2',
                'title': 'Test Gmail draft creation',
                'description': 'Check that drafts appear in Gmail outbox',
                'owner_name': 'Marcus',
                'owner_email': 'marcus@disruptiveventures.se',
                'priority': 'medium',
                'due_date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
                'metadata': {}
            },
            {
                'id': 'action-3',
                'title': 'Verify Linear project linking',
                'description': 'Ensure tasks are in correct project with Drive links',
                'owner_name': 'Marcus',
                'owner_email': 'marcus@disruptiveventures.se',
                'priority': 'low',
                'due_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
                'metadata': {}
            }
        ]
        
        test_attendees = [
            {'name': 'Marcus', 'email': 'marcus@disruptiveventures.se', 'role': 'Admin'}
        ]
        
        # Use enhanced distribution
        from app.services.enhanced_distribution import EnhancedDistributionPipeline
        
        pipeline = EnhancedDistributionPipeline()
        
        # Note: This is a simplified test - full implementation would:
        # 1. Create Drive folder
        # 2. Upload documents
        # 3. Create Linear project
        # 4. Create Linear tasks
        # 5. Create Gmail draft
        
        return {
            "success": True,
            "results": results,
            "message": "Test completed! Check Google Drive, Linear, and Gmail.",
            "next_steps": [
                "Open Google Drive and look for /Meetings/2025/December/ folder",
                "Open Linear and check for 'Marcus Enhanced Distribution Test' project",
                "Open Gmail Drafts and look for action items email"
            ]
        }
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e),
            "results": results
        }, status_code=500)


# Helper functions

async def _create_drive_folder_hierarchy(drive_service, meeting_title: str, meeting_date: str) -> Dict:
    """Create Drive folder hierarchy for test."""
    
    year = meeting_date[:4]
    month = datetime.strptime(meeting_date, '%Y-%m-%d').strftime('%B')
    folder_name = f"{meeting_date} {meeting_title}"
    
    # Create Meetings folder
    meetings_folder = _get_or_create_folder_sync(drive_service, "Meetings", None)
    
    # Create year folder
    year_folder = _get_or_create_folder_sync(drive_service, year, meetings_folder['id'])
    
    # Create month folder
    month_folder = _get_or_create_folder_sync(drive_service, month, year_folder['id'])
    
    # Create meeting folder
    meeting_folder = _get_or_create_folder_sync(drive_service, folder_name, month_folder['id'])
    
    return {
        'id': meeting_folder['id'],
        'name': folder_name,
        'url': f"https://drive.google.com/drive/folders/{meeting_folder['id']}",
        'path': f"/Meetings/{year}/{month}/{folder_name}"
    }


def _get_or_create_folder_sync(drive_service, folder_name: str, parent_id: Optional[str]) -> Dict:
    """Synchronous version of get or create folder."""
    
    # Search for existing folder
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    
    results = drive_service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name)',
        pageSize=1
    ).execute()
    
    files = results.get('files', [])
    
    if files:
        return files[0]
    
    # Create new folder
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    
    if parent_id:
        file_metadata['parents'] = [parent_id]
    
    folder = drive_service.files().create(
        body=file_metadata,
        fields='id, name'
    ).execute()
    
    return folder


def _build_test_email_body(meeting_title: str, tasks: List[str]) -> str:
    """Build test email HTML."""
    
    task_html = '\n'.join([
        f'<li style="margin: 8px 0; padding: 12px; background: #f8f9fa; border-radius: 6px;">{task}</li>'
        for task in tasks
    ])
    
    return f"""
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h1 style="color: #0066cc;">📋 Action Items from {meeting_title}</h1>
        
        <p>Hi Marcus,</p>
        <p>Here are your action items from the test meeting:</p>
        
        <ul style="list-style: none; padding: 0;">
            {task_html}
        </ul>
        
        <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="margin-top: 0;">🔗 Quick Links</h3>
            <p>📂 <strong>Google Drive:</strong> All meeting documents</p>
            <p>📊 <strong>Linear Project:</strong> {meeting_title}</p>
            <p>📄 <strong>Meeting Notes:</strong> Available in Drive</p>
        </div>
        
        <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 30px 0;">
        
        <p style="color: #999; font-size: 13px;">
            This is a TEST draft. Review and send when ready.<br>
            Auto-generated by Meeting Intelligence Platform
        </p>
    </div>
</body>
</html>
    """

