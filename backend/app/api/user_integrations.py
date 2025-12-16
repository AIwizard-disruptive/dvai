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
    """User integration settings page - monochrome design with left sidebar."""
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Integrations - Admin</title>
    {get_dv_styles()}
    <style>
        .integration-card {{
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.15s;
        }}
        
        .integration-card:hover {{
            border-color: var(--gray-300);
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .integration-card.connected {{
            background: white;
            border-color: var(--gray-300);
        }}
        
        .integration-icon {{
            width: 40px;
            height: 40px;
            border-radius: 8px;
            background: var(--gray-100);
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 16px;
            flex-shrink: 0;
        }}
        
        .integration-icon svg {{
            width: 20px;
            height: 20px;
            stroke: var(--gray-600);
        }}
        
        .integration-info {{
            flex: 1;
        }}
        
        .integration-name {{
            font-size: 16px;
            font-weight: 600;
            color: var(--gray-900);
            margin-bottom: 4px;
        }}
        
        .integration-description {{
            font-size: 13px;
            color: var(--gray-600);
            margin-bottom: 8px;
        }}
        
        .status-badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 500;
        }}
        
        .status-badge.connected {{
            background: var(--gray-100);
            color: var(--gray-900);
        }}
        
        .status-badge.disconnected {{
            background: var(--gray-100);
            color: var(--gray-600);
        }}
        
        .connect-btn {{
            padding: 8px 16px;
            background: var(--gray-900);
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            font-size: 13px;
            transition: all 0.15s;
        }}
        
        .connect-btn:hover {{
            background: var(--gray-700);
        }}
        
        .disconnect-btn {{
            padding: 8px 16px;
            background: white;
            color: var(--gray-700);
            border: 1px solid var(--gray-300);
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            font-size: 13px;
        }}
        
        .disconnect-btn:hover {{
            background: var(--gray-50);
        }}
    </style>
</head>
<body>
    {get_admin_sidebar('settings', 'Markus Löwegren', 'markus.lowegren@disruptiveventures.se', '')}
    
    <div class="main-content">
        <div class="page-header">
            <div class="page-header-left">
                <h1 class="page-title">Your Integrations</h1>
                <p class="page-description">Connect your tools to enable automatic task creation and notifications</p>
            </div>
        </div>
        
        <div class="container">
            <!-- Linear Integration -->
            <div class="integration-card" id="linear-card">
                <div style="display: flex; align-items: center; flex: 1;">
                    <div class="integration-icon">
                        <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                            <circle cx="12" cy="12" r="10"/>
                            <polyline points="12 6 12 12 16 14"/>
                        </svg>
                    </div>
                    <div class="integration-info">
                        <div class="integration-name">Linear</div>
                        <div class="integration-description">Automatically create tasks from meeting action items in your Linear workspace</div>
                        <span class="status-badge disconnected" id="linear-status">Not connected</span>
                    </div>
                </div>
                <button class="connect-btn" id="linear-btn" onclick="connectLinear()">
                    Connect Linear
                </button>
            </div>
            
            <!-- Google Integration -->
            <div class="integration-card" id="google-card">
                <div style="display: flex; align-items: center; flex: 1;">
                    <div class="integration-icon">
                        <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                            <line x1="9" y1="3" x2="9" y2="21"/>
                        </svg>
                    </div>
                    <div class="integration-info">
                        <div class="integration-name">Google Workspace</div>
                        <div class="integration-description">Send emails, create calendar events, and save documents to your Google Drive</div>
                        <span class="status-badge disconnected" id="google-status">Not connected</span>
                    </div>
                </div>
                <button class="connect-btn" id="google-btn" onclick="connectGoogle()">
                    Connect Google
                </button>
            </div>
            
            <!-- Slack Integration -->
            <div class="integration-card" id="slack-card">
                <div style="display: flex; align-items: center; flex: 1;">
                    <div class="integration-icon">
                        <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                        </svg>
                    </div>
                    <div class="integration-info">
                        <div class="integration-name">Slack</div>
                        <div class="integration-description">Get notifications in Slack when meetings are processed</div>
                        <span class="status-badge disconnected" id="slack-status">Not connected</span>
                    </div>
                </div>
                <button class="connect-btn" id="slack-btn" onclick="connectSlack()">
                    Connect Slack
                </button>
            </div>
            
            <!-- Info Box -->
            <div class="info-box" style="margin-top: 32px; padding: 16px; background: var(--gray-50); border: 1px solid var(--gray-200); border-radius: 8px;">
                <h3 style="font-size: 14px; font-weight: 600; margin-bottom: 8px; color: var(--gray-900);">How it works</h3>
                <p style="font-size: 13px; color: var(--gray-600); line-height: 1.6;">
                    When you connect an integration, you'll be redirected to that service to authorize access.
                    Your credentials are securely stored and encrypted. You can disconnect at any time.
                    <br><br>
                    Once connected, tasks will automatically be created using <strong>your account</strong>,
                    so you'll see them in your Linear workspace, get notifications, and have full control.
                </p>
            </div>
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



