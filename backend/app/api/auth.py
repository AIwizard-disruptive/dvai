"""Authentication endpoints."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from supabase import create_client, Client

from app.config import settings
from app.database import get_db

router = APIRouter()


class SignupRequest(BaseModel):
    """Signup request."""
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request."""
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """Auth response."""
    access_token: str
    refresh_token: str
    user: dict
    message: str


def get_supabase_client() -> Client:
    """Get Supabase client."""
    return create_client(
        settings.supabase_url,
        settings.supabase_anon_key
    )


@router.post("/signup", response_model=AuthResponse)
async def signup(
    request: SignupRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Sign up a new user with email and password.
    
    This uses Supabase Auth which handles:
    - Password hashing
    - Email verification
    - User management
    
    Also auto-creates an organization for the new user.
    """
    try:
        supabase = get_supabase_client()
        
        # Sign up with Supabase Auth
        response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "full_name": request.full_name
                }
            }
        })
        
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
        
        # Auto-create organization for new user
        import uuid
        from supabase import create_client
        
        user_name = request.full_name or request.email.split("@")[0]
        org_name = f"{user_name}'s Organization"
        org_id = str(uuid.uuid4())
        
        # Use service role key to bypass RLS
        admin_supabase = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key
        )
        
        # Create org
        admin_supabase.table('orgs').insert({
            'id': org_id,
            'name': org_name,
            'settings': {}
        }).execute()
        
        # Create membership (user as owner)
        admin_supabase.table('org_memberships').insert({
            'org_id': org_id,
            'user_id': response.user.id,
            'role': 'owner'
        }).execute()
        
        return AuthResponse(
            access_token=response.session.access_token if response.session else "",
            refresh_token=response.session.refresh_token if response.session else "",
            user={
                "id": response.user.id,
                "email": response.user.email,
                "full_name": request.full_name
            },
            message="Account created successfully. Please check your email to verify your account."
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Log in with email and password.
    
    Returns JWT access token and refresh token.
    """
    try:
        supabase = get_supabase_client()
        
        # Sign in with Supabase Auth
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if not response.user or not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Handle user_metadata safely
        user_metadata = response.user.user_metadata
        full_name = None
        if isinstance(user_metadata, dict):
            full_name = user_metadata.get("full_name")
        
        return AuthResponse(
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            user={
                "id": response.user.id,
                "email": response.user.email,
                "full_name": full_name
            },
            message="Logged in successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/logout")
async def logout(request: Request):
    """Log out the current user."""
    try:
        # Get token from header
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No authorization token provided"
            )
        
        token = auth_header.replace("Bearer ", "")
        supabase = get_supabase_client()
        
        # Sign out from Supabase
        supabase.auth.sign_out()
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/google")
async def google_auth():
    """
    Initiate Google OAuth flow using Supabase.
    Returns HTML page that uses Supabase JS client for OAuth.
    """
    from fastapi.responses import HTMLResponse
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Signing in with Google...</title>
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
</head>
<body>
    <div style="font-family: sans-serif; text-align: center; padding: 50px;">
        <h2>Redirecting to Google...</h2>
        <p>Please wait...</p>
    </div>
    
    <script>
        const supabase = window.supabase.createClient(
            '{settings.supabase_url}',
            '{settings.supabase_anon_key}'
        );
        
        // Sign in with Google using Supabase client
        supabase.auth.signInWithOAuth({{
            provider: 'google',
            options: {{
                redirectTo: 'http://localhost:8000/auth/callback'
            }}
        }}).then(response => {{
            if (response.error) {{
                console.error('OAuth error:', response.error);
                window.location.href = '/login?error=' + encodeURIComponent(response.error.message);
            }}
        }});
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html)


@router.get("/callback")
async def auth_callback():
    """
    OAuth callback - Supabase puts tokens in URL hash.
    Use Supabase JS client to handle the session.
    """
    from fastapi.responses import HTMLResponse
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Completing Login...</title>
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 500px;
        }}
        .spinner {{
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }}
        @keyframes spin {{
            0%% {{ transform: rotate(0deg); }}
            100%% {{ transform: rotate(360deg); }}
        }}
        h2 {{ color: #333; }}
        #status {{ color: #666; margin-top: 15px; }}
        #error {{ color: #d32f2f; margin-top: 15px; display: none; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>✅ Login Successful!</h2>
        <div class="spinner"></div>
        <p id="status">Setting up your account...</p>
        <p id="error"></p>
    </div>
    
    <script>
        const supabase = window.supabase.createClient(
            '{settings.supabase_url}',
            '{settings.supabase_anon_key}'
        );
        
        async function handleCallback() {{
            const statusEl = document.getElementById('status');
            const errorEl = document.getElementById('error');
            
            try {{
                // Get session from URL hash (Supabase puts tokens there)
                const {{ data, error }} = await supabase.auth.getSession();
                
                if (error) throw error;
                
                if (!data.session) {{
                    throw new Error('No session found. Please try logging in again.');
                }}
                
                const accessToken = data.session.access_token;
                const refreshToken = data.session.refresh_token;
                const user = data.session.user;
                
                console.log('✓ Session retrieved:', {{ userId: user.id, email: user.email }});
                
                // Store tokens in localStorage for API calls
                localStorage.setItem('access_token', accessToken);
                if (refreshToken) {{
                    localStorage.setItem('refresh_token', refreshToken);
                }}
                
                statusEl.textContent = 'Creating your organization...';
                
                // Call backend to create organization
                const response = await fetch('/auth/ensure-org', {{
                    method: 'POST',
                    headers: {{
                        'Authorization': `Bearer ${{accessToken}}`,
                        'Content-Type': 'application/json'
                    }}
                }});
                
                if (response.ok) {{
                    const orgData = await response.json();
                    console.log('✓ Organization ready:', orgData);
                    statusEl.textContent = `✓ Organization ready: ${{orgData.org_name}}`;
                }} else {{
                    console.warn('Organization creation will happen on first upload');
                    statusEl.textContent = '✓ Account ready!';
                }}
                
                // Redirect to upload page
                setTimeout(() => {{
                    window.location.href = '/upload-ui';
                }}, 1500);
                
            }} catch (error) {{
                console.error('Auth error:', error);
                document.querySelector('.spinner').style.display = 'none';
                errorEl.textContent = `❌ Error: ${{error.message}}`;
                errorEl.style.display = 'block';
                statusEl.style.display = 'none';
                
                setTimeout(() => {{
                    window.location.href = '/login?error=' + encodeURIComponent(error.message);
                }}, 3000);
            }}
        }}
        
        // Run when page loads
        handleCallback();
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html)


@router.post("/ensure-org")
async def ensure_user_has_org(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Ensure the authenticated user has an organization. Create one if not."""
    try:
        # Get token from header
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No authorization token provided"
            )
        
        token = auth_header.replace("Bearer ", "")
        supabase = get_supabase_client()
        
        # Get user from token
        response = supabase.auth.get_user(token)
        
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user_id = response.user.id
        user_email = response.user.email
        user_name = user_email.split("@")[0] if user_email else "User"
        
        # Check if user already has an org using Supabase client
        membership_response = supabase.table('org_memberships').select('org_id, role').eq('user_id', user_id).limit(1).execute()
        
        if not membership_response.data:
            # Auto-create org for new user
            import uuid
            from supabase import create_client
            
            org_name = f"{user_name}'s Organization"
            org_id = str(uuid.uuid4())
            
            # Use service role key to bypass RLS
            admin_supabase = create_client(
                settings.supabase_url,
                settings.supabase_service_role_key
            )
            
            # Create org
            admin_supabase.table('orgs').insert({
                'id': org_id,
                'name': org_name,
                'settings': {}
            }).execute()
            
            # Create membership (user as owner)
            admin_supabase.table('org_memberships').insert({
                'org_id': org_id,
                'user_id': user_id,
                'role': 'owner'
            }).execute()
            
            return {
                "created": True,
                "org_id": org_id,
                "org_name": org_name,
                "role": "owner"
            }
        else:
            # User already has org
            membership = membership_response.data[0]
            org_id = membership['org_id']
            
            # Get org details
            org_response = supabase.table('orgs').select('id, name').eq('id', org_id).limit(1).execute()
            org = org_response.data[0] if org_response.data else None
            
            return {
                "created": False,
                "org_id": org_id,
                "org_name": org['name'] if org else "Unknown",
                "role": membership['role']
            }
        
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{str(e)} | {traceback.format_exc()[:200]}"
        )


@router.get("/me")
async def get_current_user(request: Request):
    """
    Get current authenticated user.
    
    Requires Authorization header with Bearer token.
    """
    try:
        # Get token from header
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No authorization token provided"
            )
        
        token = auth_header.replace("Bearer ", "")
        supabase = get_supabase_client()
        
        # Get user from token
        response = supabase.auth.get_user(token)
        
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        # Handle user_metadata safely
        user_metadata = response.user.user_metadata
        full_name = None
        if isinstance(user_metadata, dict):
            full_name = user_metadata.get("full_name")
        
        return {
            "id": response.user.id,
            "email": response.user.email,
            "full_name": full_name,
            "email_verified": response.user.email_confirmed_at is not None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """
    Refresh access token using refresh token.
    """
    try:
        supabase = get_supabase_client()
        
        response = supabase.auth.refresh_session(refresh_token)
        
        if not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

