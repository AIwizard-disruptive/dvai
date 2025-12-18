"""Portfolio Company Settings - Manage API Integrations."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from supabase import create_client
from app.config import settings
from app.api.styles import get_dv_styles
from app.api.sidebar_component import get_admin_sidebar
import base64
from cryptography.fernet import Fernet

router = APIRouter(prefix="/settings", tags=["Portfolio Settings"])


class IntegrationCredentials(BaseModel):
    portfolio_company_id: str
    integration_type: str  # 'pipedrive', 'fortnox', 'google_sheets'
    api_token: str = ""
    client_id: str = ""
    client_secret: str = ""
    api_url: str = ""
    company_domain: str = ""


def encrypt_value(value: str) -> str:
    """Encrypt a value using the encryption key."""
    if not value:
        return ""
    f = Fernet(settings.encryption_key.encode())
    return f.encrypt(value.encode()).decode()


def decrypt_value(encrypted_value: str) -> str:
    """Decrypt a value using the encryption key."""
    if not encrypted_value:
        return ""
    f = Fernet(settings.encryption_key.encode())
    return f.decrypt(encrypted_value.encode()).decode()


@router.get("/portfolio", response_class=HTMLResponse)
async def portfolio_settings():
    """Portfolio company settings page - Manage API integrations."""
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Get current user
        people = supabase.table('people').select('*').execute().data
        current_user = next((p for p in people if 'marcus' in p.get('name', '').lower() or 'markus' in p.get('name', '').lower()), None)
        if not current_user:
            current_user = {'name': 'Markus Löwegren', 'email': 'markus.lowegren@disruptiveventures.se', 'linkedin_url': ''}
        
        # Get DV org
        dv_org_result = supabase.table('orgs').select('*').execute()
        dv_org = None
        if dv_org_result.data:
            for org in dv_org_result.data:
                if 'disruptive' in org.get('name', '').lower():
                    dv_org = org
                    break
            if not dv_org:
                dv_org = dv_org_result.data[0]
        
        # Get portfolio companies
        portfolio_result = supabase.table('portfolio_companies') \
            .select('*, organizations(*)') \
            .eq('status', 'active') \
            .execute()
        
        # Get existing integrations (if table exists)
        integrations_by_company = {}
        try:
            integrations_result = supabase.table('portfolio_company_integrations') \
                .select('*') \
                .execute()
            
            for integration in integrations_result.data:
                pc_id = integration['portfolio_company_id']
                if pc_id not in integrations_by_company:
                    integrations_by_company[pc_id] = []
                integrations_by_company[pc_id].append(integration)
        except Exception as e:
            print(f"Note: portfolio_company_integrations table not yet created: {e}")
            # Continue without integrations - will show all as "Add"
        
        # Build company cards HTML
        company_cards_html = ""
        
        # Add DV (Disruptive Ventures) as first card
        if dv_org:
            dv_integrations = integrations_by_company.get('dv-org', [])
            has_pipedrive_dv = any(i['integration_type'] == 'pipedrive' for i in dv_integrations)
            has_fortnox_dv = any(i['integration_type'] == 'fortnox' for i in dv_integrations)
            has_sheets_dv = any(i['integration_type'] == 'google_sheets' for i in dv_integrations)
            
            pipedrive_status_dv = "✅ Connected" if has_pipedrive_dv else "➕ Add"
            fortnox_status_dv = "✅ Connected" if has_fortnox_dv else "➕ Add"
            sheets_status_dv = "✅ Connected" if has_sheets_dv else "➕ Add"
            
            company_cards_html += f"""
            <div class="company-settings-card dv-card" style="border: 2px solid var(--purple-600); background: linear-gradient(135deg, #faf5ff 0%, #ffffff 100%);">
                <div class="company-header">
                    <img src="/static/dv-logo.png" alt="Disruptive Ventures" class="company-logo-small">
                    <div>
                        <h3 class="company-name">Disruptive Ventures</h3>
                        <p class="company-meta">Our Fund • Global Integrations</p>
                    </div>
                    <span style="margin-left: auto; padding: 6px 12px; background: var(--purple-600); color: white; border-radius: 6px; font-size: 11px; font-weight: 600; text-transform: uppercase;">Primary</span>
                </div>
                
                <div class="integrations-grid">
                    <div class="integration-item">
                        <div class="integration-header">
                            <span class="integration-name">Pipedrive CRM</span>
                            <span class="integration-status {'connected' if has_pipedrive_dv else 'not-connected'}">{pipedrive_status_dv}</span>
                        </div>
                        <p class="integration-desc">Our deal pipeline (investor view)</p>
                        <button class="btn-secondary btn-sm" onclick="openIntegrationModal('dv-org', 'pipedrive', 'Disruptive Ventures')">
                            {'Configure' if has_pipedrive_dv else 'Connect'}
                        </button>
                    </div>
                    
                    <div class="integration-item">
                        <div class="integration-header">
                            <span class="integration-name">Fortnox</span>
                            <span class="integration-status {'connected' if has_fortnox_dv else 'not-connected'}">{fortnox_status_dv}</span>
                        </div>
                        <p class="integration-desc">DV fund accounting</p>
                        <button class="btn-secondary btn-sm" onclick="openIntegrationModal('dv-org', 'fortnox', 'Disruptive Ventures')">
                            {'Configure' if has_fortnox_dv else 'Connect'}
                        </button>
                    </div>
                    
                    <div class="integration-item">
                        <div class="integration-header">
                            <span class="integration-name">Google Sheets</span>
                            <span class="integration-status {'connected' if has_sheets_dv else 'not-connected'}">{sheets_status_dv}</span>
                        </div>
                        <p class="integration-desc">Fund KPI reports</p>
                        <button class="btn-secondary btn-sm" onclick="openIntegrationModal('dv-org', 'google_sheets', 'Disruptive Ventures')">
                            {'Configure' if has_sheets_dv else 'Connect'}
                        </button>
                    </div>
                </div>
            </div>
            
            <!-- Portfolio Companies Section Header -->
            <div style="margin: 32px 0 16px 0;">
                <h2 style="font-size: 16px; font-weight: 600; color: var(--gray-900); margin-bottom: 4px;">Portfolio Companies</h2>
                <p style="font-size: 13px; color: var(--gray-600);">Manage integrations for each portfolio company</p>
            </div>
            """
        for pc in portfolio_result.data:
            org = pc.get('organizations', {})
            company_name = org.get('name', 'Unknown')
            company_logo = org.get('logo_url', '')
            pc_id = pc['id']
            
            existing_integrations = integrations_by_company.get(pc_id, [])
            
            # Check which integrations exist
            has_pipedrive = any(i['integration_type'] == 'pipedrive' for i in existing_integrations)
            has_fortnox = any(i['integration_type'] == 'fortnox' for i in existing_integrations)
            has_sheets = any(i['integration_type'] == 'google_sheets' for i in existing_integrations)
            
            pipedrive_status = "✅ Connected" if has_pipedrive else "➕ Add"
            fortnox_status = "✅ Connected" if has_fortnox else "➕ Add"
            sheets_status = "✅ Connected" if has_sheets else "➕ Add"
            
            company_cards_html += f"""
            <div class="company-settings-card">
                <div class="company-header">
                    <img src="{company_logo}" alt="{company_name}" class="company-logo-small" onerror="this.style.display='none'">
                    <div>
                        <h3 class="company-name">{company_name}</h3>
                        <p class="company-meta">{pc.get('investment_stage', 'seed').title()} • {(pc.get('ownership_percentage') or 0):.0f}% ownership</p>
                    </div>
                </div>
                
                <div class="integrations-grid">
                    <div class="integration-item">
                        <div class="integration-header">
                            <span class="integration-name">Pipedrive CRM</span>
                            <span class="integration-status {'connected' if has_pipedrive else 'not-connected'}">{pipedrive_status}</span>
                        </div>
                        <p class="integration-desc">Deal pipeline and customer tracking</p>
                        <button class="btn-secondary btn-sm" onclick="openIntegrationModal('{pc_id}', 'pipedrive', '{company_name}')">
                            {'Configure' if has_pipedrive else 'Connect'}
                        </button>
                    </div>
                    
                    <div class="integration-item">
                        <div class="integration-header">
                            <span class="integration-name">Fortnox</span>
                            <span class="integration-status {'connected' if has_fortnox else 'not-connected'}">{fortnox_status}</span>
                        </div>
                        <p class="integration-desc">Financial data and invoicing</p>
                        <button class="btn-secondary btn-sm" onclick="openIntegrationModal('{pc_id}', 'fortnox', '{company_name}')">
                            {'Configure' if has_fortnox else 'Connect'}
                        </button>
                    </div>
                    
                    <div class="integration-item">
                        <div class="integration-header">
                            <span class="integration-name">Google Sheets</span>
                            <span class="integration-status {'connected' if has_sheets else 'not-connected'}">{sheets_status}</span>
                        </div>
                        <p class="integration-desc">KPI reporting spreadsheets</p>
                        <button class="btn-secondary btn-sm" onclick="openIntegrationModal('{pc_id}', 'google_sheets', '{company_name}')">
                            {'Configure' if has_sheets else 'Connect'}
                        </button>
                    </div>
                </div>
            </div>
            """
        
    except Exception as e:
        current_user = {'name': 'Markus Löwegren', 'email': 'markus.lowegren@disruptiveventures.se', 'linkedin_url': ''}
        company_cards_html = f"<p>Error loading portfolio companies: {str(e)}</p>"
        print(f"Error in portfolio_settings: {e}")
        import traceback
        traceback.print_exc()
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portfolio Settings - Admin</title>
    {get_dv_styles()}
    <style>
        .companies-settings-grid {{
            display: grid;
            gap: 24px;
            max-width: 1200px;
        }}
        
        .company-settings-card {{
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 12px;
            padding: 24px;
            transition: all 0.2s;
        }}
        
        .company-settings-card:hover {{
            border-color: var(--gray-300);
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        
        .company-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--gray-200);
        }}
        
        .company-logo-small {{
            width: 40px;
            height: 40px;
            border-radius: 8px;
            object-fit: contain;
        }}
        
        .company-name {{
            font-size: 18px;
            font-weight: 600;
            color: var(--gray-900);
            margin: 0 0 4px 0;
        }}
        
        .company-meta {{
            font-size: 12px;
            color: var(--gray-500);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin: 0;
        }}
        
        .integrations-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
        }}
        
        .integration-item {{
            padding: 16px;
            background: var(--gray-50);
            border-radius: 8px;
            border: 1px solid var(--gray-200);
        }}
        
        .integration-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}
        
        .integration-name {{
            font-size: 14px;
            font-weight: 600;
            color: var(--gray-900);
        }}
        
        .integration-status {{
            font-size: 11px;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .integration-status.connected {{
            background: #f0fdf4;
            color: #16a34a;
        }}
        
        .integration-status.not-connected {{
            background: var(--gray-200);
            color: var(--gray-600);
        }}
        
        .integration-desc {{
            font-size: 12px;
            color: var(--gray-600);
            margin-bottom: 12px;
        }}
        
        .modal-overlay {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }}
        
        .modal-overlay.active {{
            display: flex;
        }}
        
        .modal {{
            background: white;
            border-radius: 12px;
            padding: 32px;
            max-width: 500px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }}
        
        .modal-header {{
            margin-bottom: 24px;
        }}
        
        .modal-title {{
            font-size: 20px;
            font-weight: 600;
            color: var(--gray-900);
            margin-bottom: 4px;
        }}
        
        .modal-subtitle {{
            font-size: 13px;
            color: var(--gray-600);
        }}
        
        .form-group {{
            margin-bottom: 20px;
        }}
        
        .form-label {{
            display: block;
            font-size: 13px;
            font-weight: 600;
            color: var(--gray-700);
            margin-bottom: 8px;
        }}
        
        .form-input {{
            width: 100%;
            padding: 10px 14px;
            border: 2px solid var(--gray-300);
            border-radius: 6px;
            font-size: 14px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
            transition: all 0.15s;
        }}
        
        .form-input:focus {{
            outline: none;
            border-color: var(--gray-900);
            box-shadow: 0 0 0 3px rgba(0,0,0,0.05);
        }}
        
        .form-hint {{
            font-size: 12px;
            color: var(--gray-500);
            margin-top: 6px;
        }}
        
        .modal-actions {{
            display: flex;
            gap: 12px;
            justify-content: flex-end;
            margin-top: 24px;
            padding-top: 20px;
            border-top: 1px solid var(--gray-200);
        }}
        
        .dv-card {{
            border: 2px solid var(--purple-600) !important;
            background: linear-gradient(135deg, #faf5ff 0%, #ffffff 100%) !important;
        }}
        
        body.dark-mode .modal {{
            background: #2a2a2a;
        }}
        
        body.dark-mode .company-settings-card {{
            background: #2a2a2a;
            border-color: #404040;
        }}
        
        body.dark-mode .dv-card {{
            background: linear-gradient(135deg, #2a1a3d 0%, #2a2a2a 100%) !important;
            border-color: #764ba2 !important;
        }}
        
        body.dark-mode .integration-item {{
            background: #1a1a1a;
            border-color: #404040;
        }}
        
        body.dark-mode .form-input {{
            background: #1a1a1a;
            border-color: #404040;
            color: #e5e5e5;
        }}
        
        body.dark-mode .company-name,
        body.dark-mode .integration-name,
        body.dark-mode .modal-title {{
            color: #e5e5e5;
        }}
        
        body.dark-mode .company-meta,
        body.dark-mode .integration-desc,
        body.dark-mode .form-hint {{
            color: #999;
        }}
    </style>
</head>
<body>
    {get_admin_sidebar('settings', current_user.get('name', 'Admin User'), current_user.get('email', ''), current_user.get('linkedin_url', ''))}
    
    <div class="main-content">
        <div class="page-header">
            <div class="page-header-left">
                <h1 class="page-title">Portfolio Company Settings</h1>
                <p class="page-description">Manage API integrations and credentials for each portfolio company</p>
            </div>
        </div>
        
        <div class="container">
            <div class="companies-settings-grid">
                {company_cards_html}
            </div>
        </div>
    </div>
    
    <!-- Integration Modal -->
    <div id="integration-modal" class="modal-overlay" onclick="if(event.target===this) closeModal()">
        <div class="modal">
            <div class="modal-header">
                <h2 class="modal-title" id="modal-title">Configure Integration</h2>
                <p class="modal-subtitle" id="modal-subtitle">Add API credentials</p>
            </div>
            
            <form id="integration-form" onsubmit="saveIntegration(event)">
                <input type="hidden" id="form-company-id">
                <input type="hidden" id="form-integration-type">
                
                <div id="pipedrive-fields" style="display: none;">
                    <div class="form-group">
                        <label class="form-label">API Token</label>
                        <input type="password" class="form-input" id="pipedrive-token" placeholder="Enter Pipedrive API token">
                        <p class="form-hint">Get from: Settings → Personal Preferences → API</p>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Company Domain</label>
                        <input type="text" class="form-input" id="pipedrive-domain" placeholder="yourcompany.pipedrive.com">
                        <p class="form-hint">Your Pipedrive company URL</p>
                    </div>
                </div>
                
                <div id="fortnox-fields" style="display: none;">
                    <div class="form-group">
                        <label class="form-label">Access Token</label>
                        <input type="password" class="form-input" id="fortnox-token" placeholder="Enter Fortnox access token">
                        <p class="form-hint">OAuth access token from authorization flow</p>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Client Secret</label>
                        <input type="password" class="form-input" id="fortnox-secret" placeholder="Enter client secret">
                        <p class="form-hint">From your Fortnox developer application</p>
                    </div>
                </div>
                
                <div id="sheets-fields" style="display: none;">
                    <div class="form-group">
                        <label class="form-label">Spreadsheet URL</label>
                        <input type="text" class="form-input" id="sheets-url" placeholder="https://docs.google.com/spreadsheets/d/...">
                        <p class="form-hint">Google Sheets URL with KPI data</p>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Service Account JSON</label>
                        <textarea class="form-input" id="sheets-credentials" rows="4" placeholder='{{"type": "service_account", ...}}'></textarea>
                        <p class="form-hint">Service account JSON from Google Cloud Console</p>
                    </div>
                </div>
                
                <div class="modal-actions">
                    <button type="button" class="btn-secondary" onclick="closeModal()">Cancel</button>
                    <button type="submit" class="btn-primary">Save Integration</button>
                </div>
            </form>
        </div>
    </div>
    
    <script>
        let currentCompanyId = null;
        let currentIntegrationType = null;
        
        function openIntegrationModal(companyId, integrationType, companyName) {{
            currentCompanyId = companyId;
            currentIntegrationType = integrationType;
            
            // Update modal title
            document.getElementById('modal-title').textContent = `Configure ${{integrationType}} for ${{companyName}}`;
            document.getElementById('modal-subtitle').textContent = `Add API credentials to connect ${{integrationType}}`;
            
            // Set form values
            document.getElementById('form-company-id').value = companyId;
            document.getElementById('form-integration-type').value = integrationType;
            
            // Show appropriate fields
            document.getElementById('pipedrive-fields').style.display = 'none';
            document.getElementById('fortnox-fields').style.display = 'none';
            document.getElementById('sheets-fields').style.display = 'none';
            
            if (integrationType === 'pipedrive') {{
                document.getElementById('pipedrive-fields').style.display = 'block';
            }} else if (integrationType === 'fortnox') {{
                document.getElementById('fortnox-fields').style.display = 'block';
            }} else if (integrationType === 'google_sheets') {{
                document.getElementById('sheets-fields').style.display = 'block';
            }}
            
            // Show modal
            document.getElementById('integration-modal').classList.add('active');
        }}
        
        function closeModal() {{
            document.getElementById('integration-modal').classList.remove('active');
            document.getElementById('integration-form').reset();
        }}
        
        async function saveIntegration(event) {{
            event.preventDefault();
            
            const companyId = document.getElementById('form-company-id').value;
            const integrationType = document.getElementById('form-integration-type').value;
            
            let credentials = {{
                portfolio_company_id: companyId,
                integration_type: integrationType,
            }};
            
            // Get credentials based on type
            if (integrationType === 'pipedrive') {{
                credentials.api_token = document.getElementById('pipedrive-token').value;
                credentials.company_domain = document.getElementById('pipedrive-domain').value;
                credentials.api_url = 'https://api.pipedrive.com/v1';
            }} else if (integrationType === 'fortnox') {{
                credentials.api_token = document.getElementById('fortnox-token').value;
                credentials.client_secret = document.getElementById('fortnox-secret').value;
                credentials.api_url = 'https://api.fortnox.se/3';
            }} else if (integrationType === 'google_sheets') {{
                credentials.api_url = document.getElementById('sheets-url').value;
                credentials.api_token = document.getElementById('sheets-credentials').value;
            }}
            
            try {{
                const response = await fetch('/settings/portfolio/integrations', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify(credentials)
                }});
                
                if (response.ok) {{
                    alert('✅ Integration saved successfully!');
                    closeModal();
                    location.reload(); // Refresh to show updated status
                }} else {{
                    const error = await response.json();
                    alert('❌ Error: ' + (error.detail || 'Failed to save integration'));
                }}
            }} catch (error) {{
                console.error('Error:', error);
                alert('❌ Error saving integration');
            }}
        }}
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html)


@router.post("/portfolio/integrations")
async def save_integration(credentials: IntegrationCredentials):
    """Save portfolio company integration credentials (encrypted)."""
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Encrypt sensitive data
        encrypted_token = encrypt_value(credentials.api_token) if credentials.api_token else None
        encrypted_secret = encrypt_value(credentials.client_secret) if credentials.client_secret else None
        
        # Check if integration already exists
        existing = supabase.table('portfolio_company_integrations') \
            .select('id') \
            .eq('portfolio_company_id', credentials.portfolio_company_id) \
            .eq('integration_type', credentials.integration_type) \
            .execute()
        
        integration_data = {
            'portfolio_company_id': credentials.portfolio_company_id,
            'integration_type': credentials.integration_type,
            'api_token_encrypted': encrypted_token,
            'client_secret_encrypted': encrypted_secret,
            'client_id': credentials.client_id,
            'api_url': credentials.api_url,
            'company_domain': credentials.company_domain,
            'is_active': True,
            'last_sync_status': 'pending',
        }
        
        if existing.data:
            # Update existing
            supabase.table('portfolio_company_integrations') \
                .update(integration_data) \
                .eq('id', existing.data[0]['id']) \
                .execute()
        else:
            # Insert new
            supabase.table('portfolio_company_integrations') \
                .insert(integration_data) \
                .execute()
        
        return JSONResponse(content={"message": "Integration saved successfully", "status": "success"})
    
    except Exception as e:
        print(f"Error saving integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portfolio/integrations/{company_id}")
async def get_company_integrations(company_id: str):
    """Get integrations for a portfolio company (credentials decrypted)."""
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        result = supabase.table('portfolio_company_integrations') \
            .select('*') \
            .eq('portfolio_company_id', company_id) \
            .execute()
        
        # Decrypt credentials
        integrations = []
        for integration in result.data:
            decrypted = {
                'id': integration['id'],
                'integration_type': integration['integration_type'],
                'api_url': integration.get('api_url'),
                'company_domain': integration.get('company_domain'),
                'is_active': integration.get('is_active'),
                'last_sync_at': integration.get('last_sync_at'),
                'last_sync_status': integration.get('last_sync_status'),
            }
            
            # Only decrypt if requesting (be careful with this)
            # In production, never return decrypted tokens via API
            
            integrations.append(decrypted)
        
        return JSONResponse(content={"integrations": integrations})
    
    except Exception as e:
        print(f"Error getting integrations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

