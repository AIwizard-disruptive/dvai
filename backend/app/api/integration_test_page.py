"""Integration Test Page - Standalone route at /integration-test."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from supabase import create_client
from app.config import settings
from app.api.styles import get_dv_styles
from app.api.sidebar_component import get_admin_sidebar

router = APIRouter()


@router.get("/integration-test", response_class=HTMLResponse)
async def integration_test_page():
    """Integration testing interface with left sidebar and monochrome design."""
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Integration Tests - Admin</title>
    {get_dv_styles()}
    <style>
        .test-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        
        .test-card {{
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 8px;
            padding: 16px;
        }}
        
        .test-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}
        
        .test-title {{
            font-size: 14px;
            font-weight: 600;
            color: var(--gray-900);
        }}
        
        .status-badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 500;
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
        
        .test-button {{
            width: 100%;
            padding: 10px;
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
            background: var(--gray-50);
            font-size: 11px;
            font-family: 'SF Mono', Monaco, monospace;
            white-space: pre-wrap;
            margin-top: 8px;
            max-height: 200px;
            overflow-y: auto;
            display: none;
        }}
        
        .test-result.success {{
            background: var(--gray-50);
            border-color: var(--gray-300);
            color: var(--gray-900);
        }}
        
        .test-result.error {{
            background: var(--gray-50);
            border-color: var(--gray-300);
            color: var(--gray-700);
        }}
    </style>
</head>
<body>
    {get_admin_sidebar('integrations', 'Markus Löwegren', 'markus.lowegren@disruptiveventures.se', '')}
    
    <div class="main-content">
        <div class="page-header">
            <div class="page-header-left">
                <h1 class="page-title">Integration Tests</h1>
                <p class="page-description">Test connections to external services</p>
            </div>
        </div>
        
        <div class="container">
            <div class="test-grid">
                <!-- Supabase Test -->
                <div class="test-card">
                    <div class="test-header">
                        <div class="test-title">Supabase Database</div>
                        <span id="supabase-status" class="status-badge status-unknown">Unknown</span>
                    </div>
                    <button class="test-button" onclick="testSupabase()">Test Connection</button>
                    <div id="supabase-result" class="test-result"></div>
                </div>
                
                <!-- Google Test -->
                <div class="test-card">
                    <div class="test-header">
                        <div class="test-title">Google Workspace</div>
                        <span id="google-status" class="status-badge status-unknown">Unknown</span>
                    </div>
                    <button class="test-button" onclick="testGoogle()">Test APIs</button>
                    <div id="google-result" class="test-result"></div>
                </div>
                
                <!-- Linear Test -->
                <div class="test-card">
                    <div class="test-header">
                        <div class="test-title">Linear</div>
                        <span id="linear-status" class="status-badge status-unknown">Unknown</span>
                    </div>
                    <button class="test-button" onclick="testLinear()">Test API</button>
                    <div id="linear-result" class="test-result"></div>
                </div>
                
                <!-- OpenAI Test -->
                <div class="test-card">
                    <div class="test-header">
                        <div class="test-title">OpenAI</div>
                        <span id="openai-status" class="status-badge status-unknown">Unknown</span>
                    </div>
                    <button class="test-button" onclick="testOpenAI()">Test API</button>
                    <div id="openai-result" class="test-result"></div>
                </div>
            </div>
            
            <!-- Run All Button -->
            <div style="margin-top: 24px; padding-top: 24px; border-top: 1px solid var(--gray-200);">
                <button class="test-button" onclick="testAll()">Run All Tests</button>
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
            result.textContent = 'Testing Supabase connection...';
            
            try {{
                const response = await fetch('/test-supabase');
                const data = await response.json();
                
                if (data.success || data.tables) {{
                    result.className = 'test-result success';
                    result.textContent = 'Supabase Connected\\n\\nTables: ' + (data.table_count || 0) + '\\nOrgs: ' + (data.org_count || 0);
                    status.className = 'status-badge status-connected';
                    status.textContent = 'Connected';
                }} else {{
                    result.className = 'test-result error';
                    result.textContent = 'Connection failed\\n\\n' + (data.error || 'Unknown error');
                    status.className = 'status-badge status-error';
                    status.textContent = 'Error';
                }}
            }} catch (error) {{
                result.className = 'test-result error';
                result.textContent = '✗ Request failed: ' + error.message;
                status.className = 'status-badge status-error';
                status.textContent = 'Error';
            }}
            
            btn.disabled = false;
            btn.textContent = 'Test Connection';
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
                const response = await fetch('/integrations/google/status');
                const data = await response.json();
                
                if (data.status === 'configured' || data.status === 'connected') {{
                    result.className = 'test-result success';
                    result.textContent = '✓ Google Configured\\n\\n' + JSON.stringify(data, null, 2);
                    status.className = 'status-badge status-connected';
                    status.textContent = 'Configured';
                }} else {{
                    result.className = 'test-result error';
                    result.textContent = '✗ Not configured\\n\\n' + JSON.stringify(data, null, 2);
                    status.className = 'status-badge status-error';
                    status.textContent = 'Not Configured';
                }}
            }} catch (error) {{
                result.className = 'test-result error';
                result.textContent = '✗ Request failed: ' + error.message;
                status.className = 'status-badge status-error';
                status.textContent = 'Error';
            }}
            
            btn.disabled = false;
            btn.textContent = 'Test APIs';
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
                const response = await fetch('/integrations/linear/status');
                const data = await response.json();
                
                if (data.status === 'connected') {{
                    result.className = 'test-result success';
                    result.textContent = '✓ Linear Connected\\n\\nTeams: ' + (data.teams ? data.teams.length : 0) + '\\n\\n' + JSON.stringify(data, null, 2);
                    status.className = 'status-badge status-connected';
                    status.textContent = 'Connected';
                }} else {{
                    result.className = 'test-result error';
                    result.textContent = '✗ ' + (data.message || 'Not configured') + '\\n\\n' + JSON.stringify(data, null, 2);
                    status.className = 'status-badge status-error';
                    status.textContent = data.status || 'Error';
                }}
            }} catch (error) {{
                result.className = 'test-result error';
                result.textContent = '✗ Request failed: ' + error.message;
                status.className = 'status-badge status-error';
                status.textContent = 'Error';
            }}
            
            btn.disabled = false;
            btn.textContent = 'Test API';
        }}
        
        async function testOpenAI() {{
            const btn = event.target;
            const result = document.getElementById('openai-result');
            const status = document.getElementById('openai-status');
            
            btn.disabled = true;
            btn.textContent = 'Testing...';
            result.style.display = 'block';
            result.className = 'test-result';
            result.textContent = 'Testing OpenAI API...';
            
            try {{
                const response = await fetch('/test-openai');
                const data = await response.json();
                
                if (data.success) {{
                    result.className = 'test-result success';
                    result.textContent = '✓ OpenAI Connected\\n\\n' + JSON.stringify(data, null, 2);
                    status.className = 'status-badge status-connected';
                    status.textContent = 'Connected';
                }} else {{
                    result.className = 'test-result error';
                    result.textContent = '✗ ' + (data.error || 'Not configured') + '\\n\\n' + JSON.stringify(data, null, 2);
                    status.className = 'status-badge status-error';
                    status.textContent = data.error ? 'Error' : 'Not Configured';
                }}
            }} catch (error) {{
                result.className = 'test-result error';
                result.textContent = '✗ Request failed: ' + error.message;
                status.className = 'status-badge status-error';
                status.textContent = 'Error';
            }}
            
            btn.disabled = false;
            btn.textContent = 'Test API';
        }}
        
        async function testAll() {{
            await testSupabase();
            await new Promise(r => setTimeout(r, 500));
            await testGoogle();
            await new Promise(r => setTimeout(r, 500));
            await testLinear();
            await new Promise(r => setTimeout(r, 500));
            await testOpenAI();
        }}
        
        // Auto-run on page load
        window.addEventListener('load', testAll);
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html)


@router.get("/test-supabase", response_class=JSONResponse)
async def test_supabase_endpoint():
    """Test Supabase connection."""
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Get orgs count
        orgs = supabase.table('orgs').select('id').execute()
        
        # Get table count
        tables = ['orgs', 'people', 'meetings', 'decisions', 'action_items']
        
        return {
            "success": True,
            "message": "Supabase connected",
            "org_count": len(orgs.data),
            "table_count": len(tables)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


