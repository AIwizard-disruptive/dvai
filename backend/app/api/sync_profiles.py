"""
Admin API endpoint for syncing user profiles from Google Workspace.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import os
import asyncio

from app.config import settings
from app.api.styles import get_dv_styles
from app.api.sidebar_component import get_admin_sidebar
from supabase import create_client

router = APIRouter(prefix="/admin", tags=["admin"])


class SyncRequest(BaseModel):
    """Request model for profile sync."""
    email: Optional[str] = None
    domain: str = "disruptiveventures.se"
    dry_run: bool = False


class SyncResponse(BaseModel):
    """Response model for profile sync."""
    status: str
    message: str
    results: list


@router.post("/sync-google-profiles")
async def sync_google_profiles(request: SyncRequest, background_tasks: BackgroundTasks):
    """
    Sync user profiles from Google Workspace to Supabase.
    
    Can sync all users in a domain or a specific user by email.
    Use dry_run=true to preview changes without updating the database.
    """
    try:
        # Check if Google credentials are configured
        service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
        if not service_account_file:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Google Workspace credentials not configured. Set GOOGLE_SERVICE_ACCOUNT_FILE in environment.",
                    "results": []
                }
            )
        
        # Import here to avoid issues if not configured
        from app.integrations.google_workspace_directory import GoogleWorkspaceDirectoryClient
        
        # Initialize clients
        admin_email = os.getenv('GOOGLE_ADMIN_EMAIL', 'admin@disruptiveventures.se')
        directory_client = GoogleWorkspaceDirectoryClient(service_account_file, admin_email)
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        results = []
        
        if request.email:
            # Sync specific user
            result = await sync_user(directory_client, supabase, request.email, request.dry_run)
            results.append(result)
            message = f"Synced user {request.email}"
        else:
            # Sync all users in domain
            google_users = await directory_client.list_all_users(domain=request.domain)
            
            for user in google_users:
                email = user.get('primaryEmail')
                if email:
                    result = await sync_user(directory_client, supabase, email, request.dry_run)
                    results.append(result)
            
            message = f"Synced {len(results)} users from {request.domain}"
        
        # Count results
        success = len([r for r in results if r['status'] == 'success'])
        errors = len([r for r in results if r['status'] == 'error'])
        skipped = len([r for r in results if r['status'] == 'skipped'])
        
        return {
            "status": "success",
            "message": message,
            "summary": {
                "total": len(results),
                "success": success,
                "errors": errors,
                "skipped": skipped,
                "dry_run": request.dry_run
            },
            "results": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def sync_user(directory_client, supabase, email: str, dry_run: bool = False) -> dict:
    """Sync a single user profile."""
    try:
        # Get profile from Google Workspace
        google_profile = await directory_client.get_user_profile(email)
        
        # Extract relevant fields
        name = google_profile.get('name', {})
        full_name = name.get('fullName', '')
        
        # Get primary organization (job info)
        organizations = google_profile.get('organizations', [])
        primary_org = next((org for org in organizations if org.get('primary')), {}) if organizations else {}
        
        title = primary_org.get('title', '')
        department = primary_org.get('department', '')
        description = primary_org.get('description', '')
        
        # Get phone
        phones = google_profile.get('phones', [])
        phone = phones[0].get('value', '') if phones else ''
        
        # Get location
        locations = google_profile.get('locations', [])
        location = locations[0].get('area', '') if locations else ''
        
        # Get custom schema data
        custom_schemas = google_profile.get('customSchemas', {})
        dv_data = custom_schemas.get('DV_Data', {})
        linkedin_url = dv_data.get('linkedin', '')
        
        # Check if user exists in Supabase
        existing = supabase.table('people').select('*').eq('email', email).execute()
        
        if existing.data and len(existing.data) > 0:
            person_id = existing.data[0]['id']
            
            # Prepare update data
            update_data = {
                'title': title or None,
                'role': title or None,
                'department': department or None,
                'bio': description or None,
                'phone': phone or None,
                'location': location or None,
                'google_workspace_id': google_profile.get('id')
            }
            
            # Only update linkedin if we have it and it's not already set
            if linkedin_url and not existing.data[0].get('linkedin_url'):
                update_data['linkedin_url'] = linkedin_url
            
            if full_name:
                update_data['name'] = full_name
            
            if not dry_run:
                supabase.table('people').update(update_data).eq('id', person_id).execute()
            
            return {
                'email': email,
                'status': 'success',
                'action': 'preview' if dry_run else 'updated',
                'changes': update_data
            }
        else:
            return {
                'email': email,
                'status': 'skipped',
                'reason': 'not_in_database'
            }
    
    except Exception as e:
        return {
            'email': email,
            'status': 'error',
            'error': str(e)
        }


@router.get("/sync-profiles-ui", response_class=HTMLResponse)
async def sync_profiles_ui():
    """Admin UI for syncing Google Workspace profiles."""
    
    # Check if Google credentials are configured
    service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
    credentials_configured = bool(service_account_file)
    
    # Get incomplete profiles count
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    all_people = supabase.table('people').select('*').execute()
    
    incomplete_count = 0
    for person in all_people.data:
        name = person.get('name', '').strip()
        email = person.get('email', '').strip()
        title = person.get('title') or person.get('role')
        
        if not name or not email or not title or str(title).lower() == 'none':
            incomplete_count += 1
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sync Google Profiles - Admin</title>
    {get_dv_styles()}
    <style>
        .sync-card {{
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 24px;
        }}
        
        .sync-header {{
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 16px;
            color: var(--gray-900);
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
            margin-bottom: 16px;
        }}
        
        .status-ok {{
            background: #f0fdf4;
            color: #166534;
        }}
        
        .status-warning {{
            background: #fef3c7;
            color: #92400e;
        }}
        
        .status-error {{
            background: #fef2f2;
            color: #991b1b;
        }}
        
        .sync-button {{
            padding: 12px 24px;
            background: var(--gray-900);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            margin-right: 12px;
            margin-bottom: 8px;
        }}
        
        .sync-button:hover {{
            background: var(--gray-700);
        }}
        
        .sync-button:disabled {{
            background: var(--gray-300);
            cursor: not-allowed;
        }}
        
        .sync-button.secondary {{
            background: white;
            color: var(--gray-900);
            border: 1px solid var(--gray-300);
        }}
        
        .sync-button.secondary:hover {{
            background: var(--gray-50);
        }}
        
        .sync-results {{
            margin-top: 24px;
            padding: 16px;
            background: var(--gray-50);
            border-radius: 6px;
            border: 1px solid var(--gray-200);
            display: none;
            max-height: 400px;
            overflow-y: auto;
        }}
        
        .sync-results.show {{
            display: block;
        }}
        
        .result-item {{
            padding: 8px;
            border-bottom: 1px solid var(--gray-200);
            font-size: 13px;
        }}
        
        .result-item:last-child {{
            border-bottom: none;
        }}
        
        .result-success {{
            color: #166534;
        }}
        
        .result-error {{
            color: #991b1b;
        }}
        
        .result-skipped {{
            color: var(--gray-600);
        }}
    </style>
</head>
<body>
    {get_admin_sidebar('admin', 'Admin User', '', '')}
    
    <div class="main-content">
        <div class="page-header">
            <h1>Sync Google Workspace Profiles</h1>
            <p style="color: var(--gray-600); margin-top: 8px;">
                Pull user titles, departments, and profile data from Google Workspace Directory to Supabase
            </p>
        </div>
        
        <div class="sync-card">
            <div class="sync-header">Configuration Status</div>
            
            {"<span class='status-badge status-ok'>✓ Google Workspace credentials configured</span>" if credentials_configured else "<span class='status-badge status-error'>✗ Google Workspace credentials not configured</span>"}
            
            <p style="color: var(--gray-600); margin-top: 16px;">
                {"Ready to sync profiles from Google Workspace Directory." if credentials_configured else "Set GOOGLE_SERVICE_ACCOUNT_FILE environment variable to enable sync."}
            </p>
        </div>
        
        <div class="sync-card">
            <div class="sync-header">Database Status</div>
            
            <p style="color: var(--gray-600); margin-bottom: 16px;">
                Total users: {len(all_people.data)}
            </p>
            
            {"<span class='status-badge status-warning'>⚠ " + str(incomplete_count) + " users with incomplete profiles</span>" if incomplete_count > 0 else "<span class='status-badge status-ok'>✓ All users have complete profiles</span>"}
            
            <p style="color: var(--gray-600); margin-top: 16px;">
                Users with missing name, email, or title will be hidden from the Knowledge Bank display.
            </p>
        </div>
        
        <div class="sync-card">
            <div class="sync-header">Sync Actions</div>
            
            <button class="sync-button" onclick="syncProfiles(false)" {"disabled" if not credentials_configured else ""}>
                Sync All Users
            </button>
            
            <button class="sync-button secondary" onclick="syncProfiles(true)" {"disabled" if not credentials_configured else ""}>
                Preview (Dry Run)
            </button>
            
            <div id="syncResults" class="sync-results"></div>
        </div>
    </div>
    
    <script>
        async function syncProfiles(dryRun) {{
            const button = event.target;
            const resultsDiv = document.getElementById('syncResults');
            
            button.disabled = true;
            button.textContent = 'Syncing...';
            
            resultsDiv.innerHTML = '<div style="text-align: center; padding: 20px;">⏳ Syncing profiles from Google Workspace...</div>';
            resultsDiv.classList.add('show');
            
            try {{
                const response = await fetch('/admin/sync-google-profiles', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{
                        domain: 'disruptiveventures.se',
                        dry_run: dryRun
                    }})
                }});
                
                const data = await response.json();
                
                if (data.status === 'success') {{
                    let html = '<div style="margin-bottom: 16px; font-weight: 600;">';
                    html += dryRun ? 'Preview Results (Dry Run)' : 'Sync Complete';
                    html += '</div>';
                    
                    html += `<div style="margin-bottom: 16px;">
                        Total: ${{data.summary.total}} | 
                        Success: ${{data.summary.success}} | 
                        Errors: ${{data.summary.errors}} | 
                        Skipped: ${{data.summary.skipped}}
                    </div>`;
                    
                    data.results.forEach(result => {{
                        let className = 'result-item';
                        if (result.status === 'success') className += ' result-success';
                        if (result.status === 'error') className += ' result-error';
                        if (result.status === 'skipped') className += ' result-skipped';
                        
                        html += `<div class="${{className}}">`;
                        html += `${{result.email}} - ${{result.status}}`;
                        if (result.reason) html += ` (${{result.reason}})`;
                        html += '</div>';
                    }});
                    
                    resultsDiv.innerHTML = html;
                    
                    if (!dryRun) {{
                        setTimeout(() => {{
                            window.location.reload();
                        }}, 3000);
                    }}
                }} else {{
                    resultsDiv.innerHTML = `<div class="result-error">Error: ${{data.message}}</div>`;
                }}
            }} catch (error) {{
                resultsDiv.innerHTML = `<div class="result-error">Error: ${{error.message}}</div>`;
            }} finally {{
                button.disabled = false;
                button.textContent = dryRun ? 'Preview (Dry Run)' : 'Sync All Users';
            }}
        }}
    </script>
</body>
</html>
"""
    
    return HTMLResponse(content=html)



