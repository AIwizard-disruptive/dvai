# 🎨 User-Level Integrations (Automagic Setup)

**Transform integrations from admin-configured to user self-service**

---

## 🎯 Goal: Zero Manual Admin Configuration

Users should be able to:
1. Log into the platform
2. Click "Connect Linear" / "Connect Google"
3. Authorize via OAuth
4. ✅ Done! Everything works

**No .env file editing, no API key copying, no manual setup.**

---

## 🏗️ Architecture Overview

### Current (Manual)
```
.env file (one set of credentials)
      ↓
Backend uses same credentials for all users
      ↓
All tasks created under same Linear account
```

### New (Automatic)
```
User logs in
      ↓
Clicks "Connect Linear"
      ↓
OAuth flow → Linear authorizes
      ↓
Store user's Linear token in database
      ↓
System uses USER'S Linear account
      ↓
Tasks created under USER'S account
      ↓
✅ Each user has own integrations
```

---

## 📊 Database Schema Changes

### Add Integration Table

```sql
-- Store user-level integration credentials
CREATE TABLE user_integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    org_id UUID REFERENCES orgs(id) ON DELETE CASCADE,
    
    -- Integration type
    integration_type TEXT NOT NULL, -- 'linear', 'google', 'slack'
    
    -- OAuth tokens (encrypted)
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMPTZ,
    
    -- Integration-specific data
    integration_data JSONB, -- Store team_id, workspace_id, etc.
    
    -- Metadata
    connected_at TIMESTAMPTZ DEFAULT NOW(),
    last_used_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    
    -- Constraints
    UNIQUE(user_id, integration_type),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS policies
ALTER TABLE user_integrations ENABLE ROW LEVEL SECURITY;

-- Users can only see/manage their own integrations
CREATE POLICY "Users can view own integrations"
    ON user_integrations FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own integrations"
    ON user_integrations FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own integrations"
    ON user_integrations FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own integrations"
    ON user_integrations FOR DELETE
    USING (auth.uid() = user_id);
```

---

## 🔌 Implementation: Linear OAuth

### Step 1: Create Linear OAuth App

Linear supports OAuth 2.0. Here's how:

```bash
# Linear OAuth app creation
# 1. Go to: https://linear.app/settings/api/applications
# 2. Click "Create OAuth application"
# 3. Fill in:

Name: Meeting Intelligence
Description: Automated meeting task creation
Homepage URL: http://localhost:8000
Callback URLs: http://localhost:8000/integrations/linear/callback
Scopes:
  - read
  - write
  - issues:create
  - comments:create
```

You'll get:
- **Client ID**: `abc123...`
- **Client Secret**: `secret456...`

Add to `.env`:
```env
LINEAR_OAUTH_CLIENT_ID=abc123...
LINEAR_OAUTH_CLIENT_SECRET=secret456...
LINEAR_OAUTH_REDIRECT_URI=http://localhost:8000/integrations/linear/callback
```

### Step 2: Linear OAuth Flow

```python
# backend/app/api/linear_oauth.py
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import RedirectResponse
import httpx
from app.config import settings
from app.middleware.auth import get_current_user
from supabase import create_client

router = APIRouter(prefix="/integrations/linear")

@router.get("/connect")
async def connect_linear(user = Depends(get_current_user)):
    """Start Linear OAuth flow."""
    
    # Build authorization URL
    auth_url = (
        "https://linear.app/oauth/authorize"
        f"?client_id={settings.linear_oauth_client_id}"
        f"&redirect_uri={settings.linear_oauth_redirect_uri}"
        "&response_type=code"
        "&scope=read,write,issues:create"
        f"&state={user.id}"  # Pass user ID for callback
    )
    
    return {"authorization_url": auth_url}


@router.get("/callback")
async def linear_callback(
    code: str = Query(...),
    state: str = Query(...),  # user_id
):
    """Handle Linear OAuth callback."""
    
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
            raise HTTPException(400, "Failed to exchange code for token")
        
        token_data = response.json()
    
    # Store in database
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    supabase.table('user_integrations').upsert({
        'user_id': state,  # user_id from state
        'integration_type': 'linear',
        'access_token': token_data['access_token'],
        'token_expires_at': None,  # Linear tokens don't expire
        'integration_data': {
            'scope': token_data.get('scope'),
        },
        'is_active': True,
        'connected_at': 'now()',
    }).execute()
    
    # Redirect to dashboard with success message
    return RedirectResponse(
        url="/dashboard-ui?integration=linear&status=connected",
        status_code=302
    )


@router.get("/disconnect")
async def disconnect_linear(user = Depends(get_current_user)):
    """Disconnect Linear integration."""
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    supabase.table('user_integrations').delete().match({
        'user_id': user.id,
        'integration_type': 'linear'
    }).execute()
    
    return {"success": True, "message": "Linear disconnected"}


@router.get("/status")
async def linear_status(user = Depends(get_current_user)):
    """Check user's Linear connection status."""
    
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
```

---

## 🎨 Frontend: Integration Settings Page

Create a beautiful settings page where users manage integrations:

```html
<!-- Integration Settings Page -->
<!DOCTYPE html>
<html>
<head>
    <title>Integrations - Meeting Intelligence</title>
    <style>
        .integration-card {
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            padding: 24px;
            margin: 16px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .integration-card.connected {
            border-color: #4caf50;
            background: #f1f8f4;
        }
        
        .connect-btn {
            padding: 12px 24px;
            background: linear-gradient(135deg, #0066cc, #00c853);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
        }
        
        .disconnect-btn {
            padding: 12px 24px;
            background: #f44336;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔌 Your Integrations</h1>
        <p>Connect your tools to enable automatic task creation and notifications</p>
        
        <!-- Linear Integration -->
        <div class="integration-card" id="linear-card">
            <div>
                <h3>📊 Linear</h3>
                <p>Automatically create tasks from meeting action items</p>
                <span id="linear-status">Not connected</span>
            </div>
            <button class="connect-btn" id="linear-btn" onclick="connectLinear()">
                Connect Linear
            </button>
        </div>
        
        <!-- Google Integration -->
        <div class="integration-card" id="google-card">
            <div>
                <h3>📧 Google Workspace</h3>
                <p>Send emails, create calendar events, save documents</p>
                <span id="google-status">Not connected</span>
            </div>
            <button class="connect-btn" id="google-btn" onclick="connectGoogle()">
                Connect Google
            </button>
        </div>
        
        <!-- Slack Integration -->
        <div class="integration-card" id="slack-card">
            <div>
                <h3>💬 Slack</h3>
                <p>Get notifications in Slack when meetings are processed</p>
                <span id="slack-status">Not connected</span>
            </div>
            <button class="connect-btn" id="slack-btn" onclick="connectSlack()">
                Connect Slack
            </button>
        </div>
    </div>
    
    <script>
        // Check integration status on page load
        async function checkIntegrations() {
            // Check Linear
            const linearStatus = await fetch('/integrations/linear/status');
            const linearData = await linearStatus.json();
            
            if (linearData.connected) {
                document.getElementById('linear-card').classList.add('connected');
                document.getElementById('linear-status').textContent = 
                    `✅ Connected since ${new Date(linearData.connected_at).toLocaleDateString()}`;
                document.getElementById('linear-btn').textContent = 'Disconnect';
                document.getElementById('linear-btn').className = 'disconnect-btn';
                document.getElementById('linear-btn').onclick = disconnectLinear;
            }
            
            // Check Google
            const googleStatus = await fetch('/integrations/google/status');
            const googleData = await googleStatus.json();
            
            if (googleData.user_connected) {
                document.getElementById('google-card').classList.add('connected');
                document.getElementById('google-status').textContent = '✅ Connected';
                document.getElementById('google-btn').textContent = 'Disconnect';
                document.getElementById('google-btn').className = 'disconnect-btn';
                document.getElementById('google-btn').onclick = disconnectGoogle;
            }
            
            // Check Slack
            const slackStatus = await fetch('/integrations/slack/status');
            const slackData = await slackStatus.json();
            
            if (slackData.connected) {
                document.getElementById('slack-card').classList.add('connected');
                document.getElementById('slack-status').textContent = '✅ Connected';
                document.getElementById('slack-btn').textContent = 'Disconnect';
                document.getElementById('slack-btn').className = 'disconnect-btn';
                document.getElementById('slack-btn').onclick = disconnectSlack;
            }
        }
        
        async function connectLinear() {
            const response = await fetch('/integrations/linear/connect');
            const data = await response.json();
            window.location.href = data.authorization_url;
        }
        
        async function disconnectLinear() {
            if (confirm('Disconnect Linear? Tasks will no longer be created automatically.')) {
                await fetch('/integrations/linear/disconnect');
                location.reload();
            }
        }
        
        async function connectGoogle() {
            const response = await fetch('/integrations/google/connect');
            const data = await response.json();
            window.location.href = data.authorization_url;
        }
        
        async function disconnectGoogle() {
            if (confirm('Disconnect Google? Emails and calendar events will stop.')) {
                await fetch('/integrations/google/disconnect');
                location.reload();
            }
        }
        
        async function connectSlack() {
            const response = await fetch('/integrations/slack/connect');
            const data = await response.json();
            window.location.href = data.authorization_url;
        }
        
        async function disconnectSlack() {
            if (confirm('Disconnect Slack? Notifications will stop.')) {
                await fetch('/integrations/slack/disconnect');
                location.reload();
            }
        }
        
        // Check on page load
        checkIntegrations();
    </script>
</body>
</html>
```

---

## 🔄 Updated Auto-Distribution Logic

Now use user's personal integrations instead of global config:

```python
# backend/app/services/auto_distribution.py

async def _create_linear_task_for_user(self, action: Dict, meeting: Dict, user_id: str) -> Optional[Dict]:
    """Create Linear task using USER'S Linear credentials."""
    
    # Get user's Linear integration
    integration = self.supabase.table('user_integrations').select('*').match({
        'user_id': user_id,
        'integration_type': 'linear',
        'is_active': True
    }).execute()
    
    if not integration.data:
        print(f"   ⚠ User {user_id} hasn't connected Linear")
        return None
    
    # Use user's access token
    user_token = integration.data[0]['access_token']
    
    # Create Linear client with user's token
    from app.integrations.linear import LinearClient
    client = LinearClient(api_key=user_token)
    
    # ... rest of task creation logic
    # Now task is created in USER's Linear workspace!
```

---

## 🎯 User Experience Flow

### 1. New User Signs Up

```
User creates account
      ↓
Redirected to onboarding
      ↓
"Connect your tools to get started"
      ↓
Shows integration cards (all disconnected)
```

### 2. User Connects Linear

```
Clicks "Connect Linear"
      ↓
Redirected to Linear OAuth
      ↓
"Meeting Intelligence wants to access your Linear workspace"
      ↓
User clicks "Allow"
      ↓
Redirected back to app
      ↓
✅ "Linear connected! You're all set."
```

### 3. User Uploads Meeting

```
Uploads transcript
      ↓
System uses USER'S Linear credentials
      ↓
Tasks created in USER'S Linear workspace
      ↓
User sees tasks in THEIR Linear
```

---

## 🏢 Org-Level vs User-Level Integrations

You can support both:

### Org-Level (Admin configures for everyone)
```sql
CREATE TABLE org_integrations (
    org_id UUID REFERENCES orgs(id),
    integration_type TEXT,
    access_token TEXT,
    -- Only org owners can configure
);
```

### User-Level (Each user configures own)
```sql
CREATE TABLE user_integrations (
    user_id UUID REFERENCES auth.users(id),
    integration_type TEXT,
    access_token TEXT,
    -- Each user manages own
);
```

### Logic:
```python
# Try user-level first, fall back to org-level
user_integration = get_user_integration(user_id, 'linear')
if not user_integration:
    org_integration = get_org_integration(org_id, 'linear')
    use(org_integration if org_integration else None)
else:
    use(user_integration)
```

---

## 🔐 Security Best Practices

### 1. Encrypt Tokens

```python
from cryptography.fernet import Fernet

def encrypt_token(token: str) -> str:
    f = Fernet(settings.encryption_key)
    return f.encrypt(token.encode()).decode()

def decrypt_token(encrypted: str) -> str:
    f = Fernet(settings.encryption_key)
    return f.decrypt(encrypted.encode()).decode()
```

### 2. Token Refresh

```python
async def refresh_linear_token(integration_id: str):
    """Refresh Linear OAuth token if needed."""
    # Linear tokens don't expire, but for Google:
    if token_expired(integration):
        new_token = await refresh_oauth_token(integration)
        update_integration(integration_id, new_token)
```

### 3. Revoke on Disconnect

```python
async def disconnect_integration(user_id: str, integration_type: str):
    # Revoke token with provider
    await revoke_oauth_token(integration)
    
    # Delete from database
    delete_integration(user_id, integration_type)
```

---

## 📱 Mobile-Friendly Integration Page

Add QR codes for mobile setup:

```python
import qrcode
import io
import base64

@router.get("/linear/qr")
async def get_linear_qr(user = Depends(get_current_user)):
    """Get QR code for mobile Linear connection."""
    
    # Generate connection URL
    url = f"{settings.base_url}/integrations/linear/connect?user={user.id}"
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return {"qr_code": f"data:image/png;base64,{img_str}"}
```

---

## ✅ Migration Path

### Phase 1: Keep current system (backward compatible)
- Global .env config still works
- Add user-level integrations as option
- Users can choose

### Phase 2: Encourage user-level
- Show banner: "Connect your own Linear for better experience"
- One-click migration from global to personal

### Phase 3: Deprecate global config
- All users on personal integrations
- Remove .env API key requirement

---

## 🎯 Benefits of User-Level Integrations

✅ **Better Security** - Each user uses own credentials
✅ **Better Privacy** - Tasks/emails use user's account
✅ **Better UX** - No admin setup needed
✅ **Better Scalability** - Per-user rate limits
✅ **Better Personalization** - Tasks created as user, not bot
✅ **Easier Onboarding** - Click to connect, done!

---

## 🚀 Implementation Checklist

- [ ] Add `user_integrations` table to database
- [ ] Implement Linear OAuth flow
- [ ] Implement Google OAuth flow (already have client ID)
- [ ] Implement Slack OAuth flow
- [ ] Create integration settings page
- [ ] Update auto-distribution to use user tokens
- [ ] Add token encryption
- [ ] Add token refresh logic
- [ ] Update dashboard to show integration status
- [ ] Add onboarding flow
- [ ] Test with multiple users
- [ ] Document new flow

---

## 📖 Documentation for Users

**Setup Guide:**
```
1. Log in to Meeting Intelligence
2. Go to Settings → Integrations
3. Click "Connect Linear"
4. Authorize in Linear
5. ✅ Done! Upload a meeting to test.
```

**Time required:** 30 seconds per integration

---

**This transforms your system from admin-configured to truly self-service!** ✨


