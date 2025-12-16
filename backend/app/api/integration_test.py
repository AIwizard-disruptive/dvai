"""Integration testing endpoints."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/integrations", tags=["Integrations"])


# ============================================================================
# LINEAR INTEGRATION
# ============================================================================

@router.get("/linear/status")
async def linear_status():
    """Check Linear integration status."""
    from app.config import settings
    
    if not settings.linear_api_key:
        return JSONResponse({
            "status": "not_configured",
            "message": "LINEAR_API_KEY not set in .env file",
            "instructions": "Get API key from https://linear.app/settings/api"
        }, status_code=200)
    
    try:
        from app.integrations.linear import get_linear_client
        
        client = get_linear_client()
        teams = await client.get_teams()
        
        return {
            "status": "connected",
            "api_key_configured": True,
            "teams": teams,
            "message": "Linear integration is working!"
        }
    
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "api_key_configured": True,
            "error": str(e),
            "message": "Linear API key is set but connection failed"
        }, status_code=500)


class LinearTestIssue(BaseModel):
    title: str
    description: Optional[str] = None
    team_id: Optional[str] = None


@router.post("/linear/test")
async def test_linear_create_issue(data: LinearTestIssue):
    """Test creating a Linear issue."""
    from app.config import settings
    
    if not settings.linear_api_key:
        raise HTTPException(status_code=400, detail="Linear API key not configured")
    
    try:
        from app.integrations.linear import get_linear_client
        
        client = get_linear_client()
        
        # Get team ID if not provided
        team_id = data.team_id
        if not team_id:
            teams = await client.get_teams()
            if not teams:
                raise HTTPException(status_code=400, detail="No teams found in Linear")
            team_id = teams[0]['id']
        
        # Create test issue
        issue = await client.create_issue(
            team_id=team_id,
            title=data.title,
            description=data.description or "Test issue from Meeting Intelligence Platform",
            priority=3,  # Normal
        )
        
        return {
            "success": True,
            "issue": issue,
            "message": f"Created Linear issue: {issue['identifier']}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Linear API error: {str(e)}")


# ============================================================================
# GOOGLE WORKSPACE INTEGRATION
# ============================================================================

@router.get("/google/status")
async def google_status():
    """Check Google Workspace integration status."""
    from app.config import settings
    
    if not settings.google_client_id or not settings.google_client_secret:
        return JSONResponse({
            "status": "not_configured",
            "message": "Google OAuth credentials not set in .env file",
            "instructions": "Get credentials from https://console.cloud.google.com/apis/credentials"
        }, status_code=200)
    
    # Check if user has connected their Google account
    # TODO: Check integrations table for stored tokens
    
    return {
        "status": "configured",
        "oauth_configured": True,
        "user_connected": False,  # TODO: Check database
        "message": "Google OAuth is configured. User needs to connect account.",
        "connect_url": "/integrations/google/connect"
    }


@router.get("/google/connect")
async def google_connect():
    """Initiate Google OAuth flow."""
    from app.config import settings
    from google_auth_oauthlib.flow import Flow
    
    if not settings.google_client_id:
        raise HTTPException(status_code=400, detail="Google OAuth not configured")
    
    # Define scopes
    scopes = [
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.compose',
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events',
        'https://www.googleapis.com/auth/drive.file',
    ]
    
    # Create flow
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.google_redirect_uri],
            }
        },
        scopes=scopes,
    )
    
    flow.redirect_uri = settings.google_redirect_uri
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    return {
        "authorization_url": authorization_url,
        "state": state,
        "message": "Redirect user to authorization_url to grant permissions"
    }


@router.get("/google/callback")
async def google_callback(code: str, state: str):
    """Handle Google OAuth callback - properly handle all scope variations."""
    from app.config import settings
    from google.oauth2.credentials import Credentials
    from supabase import create_client
    import httpx
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    # Exchange authorization code for tokens directly via HTTP
    # This avoids the oauthlib scope validation issues
    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "redirect_uri": settings.google_redirect_uri,
                    "grant_type": "authorization_code",
                }
            )
            
            if response.status_code != 200:
                return HTMLResponse(
                    content=f"""
                    <html>
                    <body>
                        <h1>❌ OAuth Error</h1>
                        <p>Failed to exchange code for token</p>
                        <p>Error: {response.text}</p>
                        <a href="/integrations/google/connect">Try again</a>
                    </body>
                    </html>
                    """,
                    status_code=500
                )
            
            token_data = response.json()
        
        # Create credentials object
        credentials = Credentials(
            token=token_data['access_token'],
            refresh_token=token_data.get('refresh_token'),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
            scopes=token_data.get('scope', '').split() if token_data.get('scope') else []
        )
        
        # Store in database (or integrations table if user_integrations doesn't exist)
        try:
            # Try user_integrations first (if migrations run)
            supabase.table('user_integrations').insert({
                'user_id': '00000000-0000-0000-0000-000000000000',
                'org_id': '00000000-0000-0000-0000-000000000000',
                'integration_type': 'google',
                'access_token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'integration_data': {
                    'scopes': credentials.scopes,
                    'token_type': token_data.get('token_type', 'Bearer'),
                },
                'is_active': True,
            }).execute()
            print("✅ Google credentials stored in user_integrations")
        except:
            # Fall back to old integrations table
            try:
                supabase.table('integrations').upsert({
                    'org_id': '00000000-0000-0000-0000-000000000000',
                    'integration_type': 'google',
                    'credentials': {
                        'access_token': credentials.token,
                        'refresh_token': credentials.refresh_token,
                        'scopes': credentials.scopes,
                    },
                    'is_active': True,
                }, on_conflict='org_id,integration_type').execute()
                print("✅ Google credentials stored in integrations table")
            except Exception as e2:
                # Just save to a temp location for now
                import json
                with open('/tmp/google_credentials.json', 'w') as f:
                    json.dump({
                        'access_token': credentials.token,
                        'refresh_token': credentials.refresh_token,
                        'scopes': credentials.scopes,
                    }, f)
                print("✅ Google credentials saved to /tmp/google_credentials.json")
        
        # Return success page
        return HTMLResponse(content=f"""
<!DOCTYPE html>
<html>
<head>
    <title>Google Connected!</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            max-width: 600px;
            margin: 100px auto;
            padding: 40px;
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .card {{
            background: white;
            color: #333;
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{ color: #4caf50; margin-bottom: 20px; }}
        .btn {{
            display: inline-block;
            background: linear-gradient(135deg, #0066cc, #00c853);
            color: white;
            padding: 14px 28px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            margin: 10px;
        }}
    </style>
</head>
<body>
    <div class="card">
        <h1>✅ Google Account Connected!</h1>
        <p style="font-size: 18px; margin: 20px 0;">Your Google account is now connected to Meeting Intelligence.</p>
        
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: left;">
            <strong>You can now:</strong>
            <ul style="margin: 10px 0;">
                <li>✓ Create Google Drive folders automatically</li>
                <li>✓ Upload meeting documents as Google Docs</li>
                <li>✓ Create Gmail drafts</li>
                <li>✓ Add Calendar events</li>
            </ul>
        </div>
        
        <div style="margin-top: 30px;">
            <a href="/marcus-test" class="btn">🧪 Test Drive & Gmail</a>
            <a href="/dashboard-ui" class="btn">📊 Dashboard</a>
        </div>
        
        <div style="margin-top: 30px; padding: 20px; background: #e8f5e9; border-radius: 8px;">
            <strong style="color: #2e7d32;">🚀 Next Step:</strong>
            <p style="color: #2e7d32; margin: 10px 0;">Run the complete sync to create Drive folders + Linear tasks:</p>
            <code style="background: #fff; padding: 10px; border-radius: 4px; display: block; color: #333; font-family: monospace;">
                cd backend<br>
                source venv/bin/activate<br>
                python3 sync_with_drive_links.py
            </code>
        </div>
    </div>
</body>
</html>
        """)
        
    except Exception as e:
        return HTMLResponse(
            content=f"""
            <html>
            <body style="font-family: Arial; max-width: 600px; margin: 100px auto; padding: 40px; text-align: center;">
                <h1 style="color: #f44336;">❌ Connection Failed</h1>
                <p>Error: {str(e)}</p>
                <a href="/integrations/google/connect" style="color: #0066cc;">Try again</a>
            </body>
            </html>
            """,
            status_code=500
        )


class EmailTest(BaseModel):
    to: list[str]
    subject: str
    body: str


@router.post("/google/test-email")
async def test_google_email(data: EmailTest):
    """Test sending email via Gmail."""
    # TODO: Get user's stored credentials
    # TODO: Use GoogleClient to send email
    
    return {
        "success": False,
        "message": "Email sending requires user to connect Google account first",
        "connect_url": "/integrations/google/connect"
    }


class CalendarTest(BaseModel):
    summary: str
    start: str  # ISO format
    end: str    # ISO format
    description: Optional[str] = None


@router.post("/google/test-calendar")
async def test_google_calendar(data: CalendarTest):
    """Test creating calendar event."""
    # TODO: Get user's stored credentials
    # TODO: Use GoogleClient to create event
    
    return {
        "success": False,
        "message": "Calendar integration requires user to connect Google account first",
        "connect_url": "/integrations/google/connect"
    }


class DriveTest(BaseModel):
    filename: str
    content: str


@router.post("/google/test-drive")
async def test_google_drive(data: DriveTest):
    """Test saving file to Google Drive."""
    # TODO: Get user's stored credentials  
    # TODO: Use Google Drive API to save file
    
    return {
        "success": False,
        "message": "Drive integration requires user to connect Google account first",
        "connect_url": "/integrations/google/connect"
    }


# ============================================================================
# SLACK INTEGRATION
# ============================================================================

@router.get("/slack/status")
async def slack_status():
    """Check Slack integration status."""
    from app.config import settings
    
    # Check for webhook URL in environment
    slack_webhook = getattr(settings, 'slack_webhook_url', None)
    
    if not slack_webhook:
        return JSONResponse({
            "status": "not_configured",
            "message": "SLACK_WEBHOOK_URL not set in .env file",
            "instructions": "Get webhook URL from https://api.slack.com/apps"
        }, status_code=200)
    
    return {
        "status": "configured",
        "webhook_configured": True,
        "message": "Slack webhook is configured"
    }


class SlackTest(BaseModel):
    message: str


@router.post("/slack/test")
async def test_slack(data: SlackTest):
    """Test sending Slack message."""
    from app.config import settings
    import httpx
    
    slack_webhook = getattr(settings, 'slack_webhook_url', None)
    
    if not slack_webhook:
        raise HTTPException(status_code=400, detail="Slack webhook not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                slack_webhook,
                json={"text": data.message}
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Slack notification sent successfully!"
                }
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Slack API error: {response.text}"
                )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Slack error: {str(e)}")


# ============================================================================
# INTEGRATION SUMMARY
# ============================================================================

@router.get("/summary")
async def integration_summary():
    """Get summary of all integrations."""
    from app.config import settings
    
    integrations = {
        "linear": {
            "name": "Linear",
            "configured": bool(settings.linear_api_key),
            "purpose": "Create tasks for action items",
            "test_endpoint": "/integrations/linear/test"
        },
        "google": {
            "name": "Google Workspace",
            "configured": bool(settings.google_client_id and settings.google_client_secret),
            "services": ["Gmail", "Calendar", "Drive"],
            "purpose": "Send emails, create events, save documents",
            "connect_endpoint": "/integrations/google/connect"
        },
        "slack": {
            "name": "Slack",
            "configured": bool(getattr(settings, 'slack_webhook_url', None)),
            "purpose": "Send notifications to team",
            "test_endpoint": "/integrations/slack/test"
        }
    }
    
    configured_count = sum(1 for i in integrations.values() if i['configured'])
    
    return {
        "integrations": integrations,
        "summary": {
            "total": len(integrations),
            "configured": configured_count,
            "not_configured": len(integrations) - configured_count
        },
        "next_steps": [
            "Configure missing integrations in .env file",
            "Test each integration using test endpoints",
            "Connect Google account if using Google services"
        ]
    }


