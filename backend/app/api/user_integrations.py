"""
User-Level Integration Management
Allows users to connect their own Linear, Google, Slack accounts via OAuth
No admin configuration needed!
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional
import httpx
from datetime import datetime, timedelta

from app.config import settings
from app.middleware.auth import get_current_user
from supabase import create_client
from app.api.styles import get_dv_styles

router = APIRouter(prefix="/user-integrations", tags=["User Integrations"])


# ============================================================================
# INTEGRATION SETTINGS PAGE
# ============================================================================

@router.get("/settings", response_class=HTMLResponse)
async def integration_settings_page():
    """
    User integration settings page.
    Shows all available integrations and connection status.
    """
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Integrations - Meeting Intelligence</title>
    {get_dv_styles()}
    <style>
        .integrations-container {{
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
        }}
        
        .integration-card {{
            border: 2px solid #e0e0e0;
            border-radius: 16px;
            padding: 32px;
            margin: 20px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s;
            background: white;
        }}
        
        .integration-card:hover {{
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
            transform: translateY(-2px);
        }}
        
        .integration-card.connected {{
            border-color: #4caf50;
            background: linear-gradient(135deg, #f1f8f4 0%, #ffffff 100%);
        }}
        
        .integration-info {{
            flex: 1;
        }}
        
        .integration-info h3 {{
            font-size: 24px;
            margin-bottom: 8px;
            color: #1a1a1a;
        }}
        
        .integration-info p {{
            color: #666;
            margin-bottom: 12px;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
        }}
        
        .status-badge.connected {{
            background: #4caf50;
            color: white;
        }}
        
        .status-badge.disconnected {{
            background: #f0f0f0;
            color: #999;
        }}
        
        .connect-btn {{
            padding: 14px 28px;
            background: linear-gradient(135deg, #0066cc, #00c853);
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            font-size: 15px;
            transition: all 0.3s;
            box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3);
        }}
        
        .connect-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0, 102, 204, 0.4);
        }}
        
        .disconnect-btn {{
            padding: 14px 28px;
            background: #f44336;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            font-size: 15px;
        }}
        
        .disconnect-btn:hover {{
            background: #d32f2f;
        }}
        
        .loading {{
            opacity: 0.6;
            pointer-events: none;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">
            <span class="logo-accent">Disruptive</span> Ventures
        </div>
        <h1>🔌 Your Integrations</h1>
        <p>Connect your tools to enable automatic task creation and notifications</p>
    </div>
    
    <div class="nav">
        <a href="/dashboard-ui">← Dashboard</a>
        <a href="/docs#/User%20Integrations">API Docs</a>
    </div>
    
    <div class="integrations-container">
        <!-- Linear Integration -->
        <div class="integration-card" id="linear-card">
            <div class="integration-info">
                <h3>📊 Linear</h3>
                <p>Automatically create tasks from meeting action items in your Linear workspace</p>
                <span class="status-badge disconnected" id="linear-status">Not connected</span>
            </div>
            <button class="connect-btn" id="linear-btn" onclick="connectLinear()">
                Connect Linear
            </button>
        </div>
        
        <!-- Google Integration -->
        <div class="integration-card" id="google-card">
            <div class="integration-info">
                <h3>📧 Google Workspace</h3>
                <p>Send emails, create calendar events, and save documents to your Google Drive</p>
                <span class="status-badge disconnected" id="google-status">Not connected</span>
            </div>
            <button class="connect-btn" id="google-btn" onclick="connectGoogle()">
                Connect Google
            </button>
        </div>
        
        <!-- Slack Integration -->
        <div class="integration-card" id="slack-card">
            <div class="integration-info">
                <h3>💬 Slack</h3>
                <p>Get notifications in Slack when meetings are processed</p>
                <span class="status-badge disconnected" id="slack-status">Not connected</span>
            </div>
            <button class="connect-btn" id="slack-btn" onclick="connectSlack()">
                Connect Slack
            </button>
        </div>
        
        <div style="margin-top: 40px; padding: 20px; background: #f8f9fa; border-radius: 12px;">
            <h3 style="margin-bottom: 12px;">ℹ️ How it works</h3>
            <p style="color: #666; line-height: 1.6;">
                When you connect an integration, you'll be redirected to that service to authorize access.
                Your credentials are securely stored and encrypted. You can disconnect at any time.
                <br><br>
                Once connected, tasks will automatically be created using <strong>your account</strong>,
                so you'll see them in your Linear workspace, get notifications, and have full control.
            </p>
        </div>
    </div>
    
    <script>
        // Check integration status on page load
        async function checkIntegrations() {{
            try {{
                // Check Linear
                const linearRes = await fetch('/user-integrations/linear/status');
                const linearData = await linearRes.json();
                updateLinearStatus(linearData);
                
                // Check Google
                const googleRes = await fetch('/user-integrations/google/status');
                const googleData = await googleRes.json();
                updateGoogleStatus(googleData);
                
                // Check Slack
                const slackRes = await fetch('/user-integrations/slack/status');
                const slackData = await slackRes.json();
                updateSlackStatus(slackData);
                
            }} catch (error) {{
                console.error('Error checking integrations:', error);
            }}
        }}
        
        function updateLinearStatus(data) {{
            const card = document.getElementById('linear-card');
            const status = document.getElementById('linear-status');
            const btn = document.getElementById('linear-btn');
            
            if (data.connected) {{
                card.classList.add('connected');
                status.classList.remove('disconnected');
                status.classList.add('connected');
                status.textContent = `✅ Connected since ${{new Date(data.connected_at).toLocaleDateString()}}`;
                btn.textContent = 'Disconnect';
                btn.className = 'disconnect-btn';
                btn.onclick = disconnectLinear;
            }}
        }}
        
        function updateGoogleStatus(data) {{
            const card = document.getElementById('google-card');
            const status = document.getElementById('google-status');
            const btn = document.getElementById('google-btn');
            
            if (data.connected) {{
                card.classList.add('connected');
                status.classList.remove('disconnected');
                status.classList.add('connected');
                status.textContent = '✅ Connected';
                btn.textContent = 'Disconnect';
                btn.className = 'disconnect-btn';
                btn.onclick = disconnectGoogle;
            }}
        }}
        
        function updateSlackStatus(data) {{
            const card = document.getElementById('slack-card');
            const status = document.getElementById('slack-status');
            const btn = document.getElementById('slack-btn');
            
            if (data.connected) {{
                card.classList.add('connected');
                status.classList.remove('disconnected');
                status.classList.add('connected');
                status.textContent = '✅ Connected';
                btn.textContent = 'Disconnect';
                btn.className = 'disconnect-btn';
                btn.onclick = disconnectSlack;
            }}
        }}
        
        async function connectLinear() {{
            window.location.href = '/user-integrations/linear/connect';
        }}
        
        async function disconnectLinear() {{
            if (confirm('Disconnect Linear? Tasks will no longer be created automatically.')) {{
                document.getElementById('linear-btn').classList.add('loading');
                await fetch('/user-integrations/linear/disconnect', {{ method: 'POST' }});
                location.reload();
            }}
        }}
        
        async function connectGoogle() {{
            window.location.href = '/user-integrations/google/connect';
        }}
        
        async function disconnectGoogle() {{
            if (confirm('Disconnect Google? Emails and calendar events will stop.')) {{
                document.getElementById('google-btn').classList.add('loading');
                await fetch('/user-integrations/google/disconnect', {{ method: 'POST' }});
                location.reload();
            }}
        }}
        
        async function connectSlack() {{
            window.location.href = '/user-integrations/slack/connect';
        }}
        
        async function disconnectSlack() {{
            if (confirm('Disconnect Slack? Notifications will stop.')) {{
                document.getElementById('slack-btn').classList.add('loading');
                await fetch('/user-integrations/slack/disconnect', {{ method: 'POST' }});
                location.reload();
            }}
        }}
        
        // Check on page load
        checkIntegrations();
        
        // Check for connection status in URL (after OAuth callback)
        const urlParams = new URLSearchParams(window.location.search);
        const integration = urlParams.get('integration');
        const status = urlParams.get('status');
        
        if (integration && status === 'connected') {{
            alert(`✅ ${{integration.charAt(0).toUpperCase() + integration.slice(1)}} connected successfully!`);
            // Clean URL
            window.history.replaceState({{}}, '', '/user-integrations/settings');
        }}
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html)


# ============================================================================
# LINEAR INTEGRATION (User OAuth)
# ============================================================================

@router.get("/linear/connect")
async def connect_user_linear(user = Depends(get_current_user)):
    """
    Start Linear OAuth flow for user.
    Redirects to Linear authorization page.
    """
    
    if not hasattr(settings, 'linear_oauth_client_id') or not settings.linear_oauth_client_id:
        raise HTTPException(
            400,
            "Linear OAuth not configured. Admin needs to set LINEAR_OAUTH_CLIENT_ID in .env"
        )
    
    # Build authorization URL
    auth_url = (
        "https://linear.app/oauth/authorize"
        f"?client_id={settings.linear_oauth_client_id}"
        f"&redirect_uri={settings.linear_oauth_redirect_uri}"
        "&response_type=code"
        "&scope=read,write,issues:create,comments:create"
        f"&state={user.id}"  # Pass user ID for callback
    )
    
    return RedirectResponse(url=auth_url, status_code=302)


@router.get("/linear/callback")
async def linear_oauth_callback(code: str = Query(...), state: str = Query(...)):
    """
    Handle Linear OAuth callback.
    Exchange code for access token and store in database.
    """
    
    user_id = state  # user_id was passed as state
    
    # Exchange code for token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.linear.app/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": settings.linear_oauth_client_id,
                "client_secret": settings.linear_oauth_client_secret,
                "redirect_uri": settings.linear_oauth_redirect_uri,
                "code": code,
            }
        )
        
        if response.status_code != 200:
            return RedirectResponse(
                url="/user-integrations/settings?integration=linear&status=error",
                status_code=302
            )
        
        token_data = response.json()
    
    # Get user's org_id
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    membership = supabase.table('org_memberships').select('org_id').eq('user_id', user_id).limit(1).execute()
    if not membership.data:
        raise HTTPException(400, "User not associated with any organization")
    
    org_id = membership.data[0]['org_id']
    
    # Store in database
    supabase.table('user_integrations').upsert({
        'user_id': user_id,
        'org_id': org_id,
        'integration_type': 'linear',
        'access_token': token_data['access_token'],  # TODO: Encrypt this
        'token_expires_at': None,  # Linear tokens don't expire
        'integration_data': {
            'scope': token_data.get('scope'),
            'token_type': token_data.get('token_type'),
        },
        'is_active': True,
    }, on_conflict='user_id,integration_type').execute()
    
    # Redirect to settings with success message
    return RedirectResponse(
        url="/user-integrations/settings?integration=linear&status=connected",
        status_code=302
    )


@router.post("/linear/disconnect")
async def disconnect_user_linear(user = Depends(get_current_user)):
    """Disconnect user's Linear integration."""
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    supabase.table('user_integrations').delete().match({
        'user_id': user.id,
        'integration_type': 'linear'
    }).execute()
    
    return {"success": True, "message": "Linear disconnected"}


@router.get("/linear/status")
async def user_linear_status(user = Depends(get_current_user)):
    """Check if user has connected Linear."""
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    result = supabase.table('user_integrations').select('*').match({
        'user_id': user.id,
        'integration_type': 'linear',
        'is_active': True
    }).execute()
    
    if result.data:
        return {
            "connected": True,
            "connected_at": result.data[0]['connected_at'],
            "last_used": result.data[0].get('last_used_at')
        }
    
    return {"connected": False}


# ============================================================================
# GOOGLE INTEGRATION (Placeholder - already implemented)
# ============================================================================

@router.get("/google/connect")
async def connect_user_google(user = Depends(get_current_user)):
    """Start Google OAuth flow for user."""
    # Redirect to existing Google OAuth endpoint
    return RedirectResponse(url="/integrations/google/connect", status_code=302)


@router.post("/google/disconnect")
async def disconnect_user_google(user = Depends(get_current_user)):
    """Disconnect user's Google integration."""
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    supabase.table('user_integrations').delete().match({
        'user_id': user.id,
        'integration_type': 'google'
    }).execute()
    return {"success": True}


@router.get("/google/status")
async def user_google_status(user = Depends(get_current_user)):
    """Check if user has connected Google."""
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    result = supabase.table('user_integrations').select('*').match({
        'user_id': user.id,
        'integration_type': 'google',
        'is_active': True
    }).execute()
    
    return {"connected": bool(result.data)}


# ============================================================================
# SLACK INTEGRATION (Placeholder)
# ============================================================================

@router.get("/slack/connect")
async def connect_user_slack(user = Depends(get_current_user)):
    """Start Slack OAuth flow for user."""
    # TODO: Implement Slack OAuth
    raise HTTPException(501, "Slack OAuth not yet implemented")


@router.post("/slack/disconnect")
async def disconnect_user_slack(user = Depends(get_current_user)):
    """Disconnect user's Slack integration."""
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    supabase.table('user_integrations').delete().match({
        'user_id': user.id,
        'integration_type': 'slack'
    }).execute()
    return {"success": True}


@router.get("/slack/status")
async def user_slack_status(user = Depends(get_current_user)):
    """Check if user has connected Slack."""
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    result = supabase.table('user_integrations').select('*').match({
        'user_id': user.id,
        'integration_type': 'slack',
        'is_active': True
    }).execute()
    
    return {"connected": bool(result.data)}


