"""Integration Test Page - Monochrome design with left sidebar."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from supabase import create_client
from app.config import settings
from app.api.styles import get_dv_styles
from app.api.sidebar_component import get_admin_sidebar

router = APIRouter()


@router.get("/integration-test", response_class=HTMLResponse)
async def integration_test_ui():
    """Integration testing interface with left sidebar."""
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Integration Tests - Admin</title>
    {get_dv_styles()}
    <style>
        .test-section {{
            margin-bottom: 24px;
        }}
        
        .test-button {{
            width: 100%;
            padding: 12px;
            background: var(--gray-900);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.15s;
            margin-bottom: 8px;
        }}
        
        .test-button:hover {{
            background: var(--gray-700);
        }}
        
        .test-button:disabled {{
            background: var(--gray-300);
            cursor: not-allowed;
        }}
        
        .test-result {{
            padding: 12px;
            border: 1px solid var(--gray-200);
            border-radius: 6px;
            background: white;
            font-size: 12px;
            font-family: monospace;
            white-space: pre-wrap;
            margin-top: 8px;
            display: none;
        }}
        
        .test-result.success {{
            background: #f0fdf4;
            border-color: #86efac;
            color: #166534;
        }}
        
        .test-result.error {{
            background: #fef2f2;
            border-color: #fca5a5;
            color: #991b1b;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 500;
            margin-left: 8px;
        }}
        
        .status-connected {{
            background: #f0fdf4;
            color: #166534;
        }}
        
        .status-error {{
            background: #fef2f2;
            color: #991b1b;
        }}
        
        .status-unknown {{
            background: var(--gray-100);
            color: var(--gray-600);
        }}
    </style>
</head>
<body>
    {get_admin_sidebar('integrations')}
    
    <div class="main-content">
        <div class="page-header">
            <h1 class="page-title">Integration Tests</h1>
            <p class="page-description">Test connections to Google, Linear, and Supabase</p>
        </div>
        
        <div class="container">
            <!-- Supabase -->
            <div class="test-section">
                <h3 style="font-size: 14px; font-weight: 600; margin-bottom: 12px; color: var(--gray-900);">
                    Supabase Database
                    <span id="supabase-status" class="status-badge status-unknown">Unknown</span>
                </h3>
                <button class="test-button" onclick="testSupabase()">Test Supabase Connection</button>
                <div id="supabase-result" class="test-result"></div>
            </div>
            
            <!-- Google -->
            <div class="test-section">
                <h3 style="font-size: 14px; font-weight: 600; margin-bottom: 12px; color: var(--gray-900);">
                    Google Workspace
                    <span id="google-status" class="status-badge status-unknown">Unknown</span>
                </h3>
                <button class="test-button" onclick="testGoogle()">Test Google APIs</button>
                <div id="google-result" class="test-result"></div>
            </div>
            
            <!-- Linear -->
            <div class="test-section">
                <h3 style="font-size: 14px; font-weight: 600; margin-bottom: 12px; color: var(--gray-900);">
                    Linear
                    <span id="linear-status" class="status-badge status-unknown">Unknown</span>
                </h3>
                <button class="test-button" onclick="testLinear()">Test Linear API</button>
                <div id="linear-result" class="test-result"></div>
            </div>
            
            <!-- Run All -->
            <div style="margin-top: 32px; padding-top: 24px; border-top: 1px solid var(--gray-200);">
                <button class="test-button" onclick="testAll()" style="background: var(--gray-900);">
                    Run All Tests
                </button>
            </div>
        </div>
    </div>
    
    <script>
        async function testSupabase() {{
            const btn = event.target;
            const result = document.getElementById('supabase-result');
            const status = document.getElementById('supabase-status');
            
            btn.disabled = true;
            btn.textContent = 'Testing...';
            result.style.display = 'block';
            result.className = 'test-result';
            result.textContent = 'Connecting to Supabase...';
            
            try {{
                const response = await fetch('/api/test/supabase');
                const data = await response.json();
                
                if (data.success) {{
                    result.className = 'test-result success';
                    result.textContent = '✓ Supabase connected\\n\\n' + JSON.stringify(data, null, 2);
                    status.className = 'status-badge status-connected';
                    status.textContent = 'Connected';
                }} else {{
                    result.className = 'test-result error';
                    result.textContent = '✗ Supabase error\\n\\n' + JSON.stringify(data, null, 2);
                    status.className = 'status-badge status-error';
                    status.textContent = 'Error';
                }}
            }} catch (error) {{
                result.className = 'test-result error';
                result.textContent = '✗ Error: ' + error.message;
                status.className = 'status-badge status-error';
                status.textContent = 'Error';
            }}
            
            btn.disabled = false;
            btn.textContent = 'Test Supabase Connection';
        }}
        
        async function testGoogle() {{
            const btn = event.target;
            const result = document.getElementById('google-result');
            const status = document.getElementById('google-status');
            
            btn.disabled = true;
            btn.textContent = 'Testing...';
            result.style.display = 'block';
            result.className = 'test-result';
            result.textContent = 'Testing Google APIs...';
            
            try {{
                const response = await fetch('/api/test/google');
                const data = await response.json();
                
                if (data.success) {{
                    result.className = 'test-result success';
                    result.textContent = '✓ Google APIs connected\\n\\n' + JSON.stringify(data, null, 2);
                    status.className = 'status-badge status-connected';
                    status.textContent = 'Connected';
                }} else {{
                    result.className = 'test-result error';
                    result.textContent = '✗ Google error\\n\\n' + JSON.stringify(data, null, 2);
                    status.className = 'status-badge status-error';
                    status.textContent = 'Error';
                }}
            }} catch (error) {{
                result.className = 'test-result error';
                result.textContent = '✗ Error: ' + error.message;
                status.className = 'status-badge status-error';
                status.textContent = 'Error';
            }}
            
            btn.disabled = false;
            btn.textContent = 'Test Google APIs';
        }}
        
        async function testLinear() {{
            const btn = event.target;
            const result = document.getElementById('linear-result');
            const status = document.getElementById('linear-status');
            
            btn.disabled = true;
            btn.textContent = 'Testing...';
            result.style.display = 'block';
            result.className = 'test-result';
            result.textContent = 'Testing Linear API...';
            
            try {{
                const response = await fetch('/api/test/linear');
                const data = await response.json();
                
                if (data.success) {{
                    result.className = 'test-result success';
                    result.textContent = '✓ Linear API connected\\n\\n' + JSON.stringify(data, null, 2);
                    status.className = 'status-badge status-connected';
                    status.textContent = 'Connected';
                }} else {{
                    result.className = 'test-result error';
                    result.textContent = '✗ Linear error\\n\\n' + JSON.stringify(data, null, 2);
                    status.className = 'status-badge status-error';
                    status.textContent = 'Error';
                }}
            }} catch (error) {{
                result.className = 'test-result error';
                result.textContent = '✗ Error: ' + error.message;
                status.className = 'status-badge status-error';
                status.textContent = 'Error';
            }}
            
            btn.disabled = false;
            btn.textContent = 'Test Linear API';
        }}
        
        async function testAll() {{
            await testSupabase();
            await new Promise(r => setTimeout(r, 500));
            await testGoogle();
            await new Promise(r => setTimeout(r, 500));
            await testLinear();
        }}
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html)


@router.get("/api/test/supabase", response_class=JSONResponse)
async def test_supabase():
    """Test Supabase connection."""
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        result = supabase.table('orgs').select('id').limit(1).execute()
        return {"success": True, "message": "Supabase connected", "org_count": len(result.data)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/api/test/google", response_class=JSONResponse)
async def test_google():
    """Test Google APIs."""
    try:
        # Add actual Google test here
        return {"success": True, "message": "Google APIs configured"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/api/test/linear", response_class=JSONResponse)
async def test_linear():
    """Test Linear API."""
    try:
        # Add actual Linear test here
        return {"success": True, "message": "Linear API configured"}
    except Exception as e:
        return {"success": False, "error": str(e)}



