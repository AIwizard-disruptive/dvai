"""
Settings Page with Submenu Navigation
======================================
General | API | Portfolio Companies
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from supabase import create_client
from app.config import settings
from app.api.styles import get_dv_styles
from app.api.sidebar_component import get_admin_sidebar
from cryptography.fernet import Fernet

router = APIRouter(prefix="/settings", tags=["Settings"])


class IntegrationCredentials(BaseModel):
    portfolio_company_id: str
    integration_type: str
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


@router.get("", response_class=HTMLResponse)
async def settings_page():
    """Main settings page with submenu navigation."""
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Get current user
        people = supabase.table('people').select('*').execute().data
        current_user = next((p for p in people if 'marcus' in p.get('name', '').lower() or 'markus' in p.get('name', '').lower()), None)
        if not current_user:
            current_user = {'name': 'Markus Löwegren', 'email': 'markus.lowegren@disruptiveventures.se', 'linkedin_url': ''}
        
        # Get DV org info
        orgs_result = supabase.table('orgs').select('*').execute()
        dv_org = None
        if orgs_result.data:
            for org in orgs_result.data:
                if 'disruptive' in org.get('name', '').lower():
                    dv_org = org
                    break
            if not dv_org:
                dv_org = orgs_result.data[0]
        
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
            
            if integrations_result.data:
                for integration in integrations_result.data:
                    pc_id = integration['portfolio_company_id']
                    if pc_id not in integrations_by_company:
                        integrations_by_company[pc_id] = []
                    integrations_by_company[pc_id].append(integration)
        except Exception as e:
            print(f"Note: portfolio_company_integrations table not yet created")
        
        # Count portfolio companies
        portfolio_count = len(portfolio_result.data)
        
        # Build portfolio companies HTML
        portfolio_companies_html = ""
        for pc in portfolio_result.data:
            org = pc.get('organizations', {})
            company_name = org.get('name', 'Unknown')
            company_logo = org.get('logo_url', '')
            pc_id = pc['id']
            
            existing_integrations = integrations_by_company.get(pc_id, [])
            has_pipedrive = any(i['integration_type'] == 'pipedrive' for i in existing_integrations)
            has_fortnox = any(i['integration_type'] == 'fortnox' for i in existing_integrations)
            has_sheets = any(i['integration_type'] == 'google_sheets' for i in existing_integrations)
            has_workspace = any(i['integration_type'] == 'google_workspace' for i in existing_integrations)
            has_office365 = any(i['integration_type'] == 'office365' for i in existing_integrations)
            has_custom = any(i['integration_type'] == 'custom' for i in existing_integrations)
            
            # No longer need to check .env since it's now in database
            
            pipedrive_status = "✅ Connected" if has_pipedrive else "➕ Add"
            fortnox_status = "✅ Connected" if has_fortnox else "➕ Add"
            sheets_status = "✅ Connected" if has_sheets else "➕ Add"
            workspace_status = "✅ Connected" if has_workspace else "➕ Add"
            office365_status = "✅ Connected" if has_office365 else "➕ Add"
            custom_status = "✅ Connected" if has_custom else "➕ Add"
            
            portfolio_companies_html += f"""
            <div class="company-settings-card">
                <div class="company-header">
                    <img src="{company_logo}" alt="{company_name}" class="company-logo-small" onerror="this.style.display='none'">
                    <div style="flex: 1;">
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
                        <p class="integration-desc">Deal pipeline tracking</p>
                        <button class="btn-secondary btn-sm" onclick="openIntegrationModal('{pc_id}', 'pipedrive', '{company_name}')">
                            {'Configure' if has_pipedrive else 'Connect'}
                        </button>
                    </div>
                    
                    <div class="integration-item">
                        <div class="integration-header">
                            <span class="integration-name">Fortnox</span>
                            <span class="integration-status {'connected' if has_fortnox else 'not-connected'}">{fortnox_status}</span>
                        </div>
                        <p class="integration-desc">Financial data</p>
                        <button class="btn-secondary btn-sm" onclick="openIntegrationModal('{pc_id}', 'fortnox', '{company_name}')">
                            {'Configure' if has_fortnox else 'Connect'}
                        </button>
                    </div>
                    
                    <div class="integration-item">
                        <div class="integration-header">
                            <span class="integration-name">Google Sheets</span>
                            <span class="integration-status {'connected' if has_sheets else 'not-connected'}">{sheets_status}</span>
                        </div>
                        <p class="integration-desc">KPI reports</p>
                        <button class="btn-secondary btn-sm" onclick="openIntegrationModal('{pc_id}', 'google_sheets', '{company_name}')">
                            {'Configure' if has_sheets else 'Connect'}
                        </button>
                    </div>
                    
                    <div class="integration-item">
                        <div class="integration-header">
                            <span class="integration-name">Google Workspace</span>
                            <span class="integration-status {'connected' if has_workspace else 'not-connected'}">{workspace_status}</span>
                        </div>
                        <p class="integration-desc">Gmail, Drive, Calendar</p>
                        <button class="btn-secondary btn-sm" onclick="openIntegrationModal('{pc_id}', 'google_workspace', '{company_name}')">
                            {'Configure' if has_workspace else 'Connect'}
                        </button>
                    </div>
                    
                    <div class="integration-item">
                        <div class="integration-header">
                            <span class="integration-name">Office 365</span>
                            <span class="integration-status {'connected' if has_office365 else 'not-connected'}">{office365_status}</span>
                        </div>
                        <p class="integration-desc">Outlook, OneDrive, Teams</p>
                        <button class="btn-secondary btn-sm" onclick="openIntegrationModal('{pc_id}', 'office365', '{company_name}')">
                            {'Configure' if has_office365 else 'Connect'}
                        </button>
                    </div>
                    
                    <div class="integration-item">
                        <div class="integration-header">
                            <span class="integration-name">Custom Integration</span>
                            <span class="integration-status {'connected' if has_custom else 'not-connected'}">{custom_status}</span>
                        </div>
                        <p class="integration-desc">Custom API endpoint</p>
                        <button class="btn-secondary btn-sm" onclick="openIntegrationModal('{pc_id}', 'custom', '{company_name}')">
                            {'Configure' if has_custom else 'Connect'}
                        </button>
                    </div>
                </div>
            </div>
            """
        
    except Exception as e:
        current_user = {'name': 'Markus Löwegren', 'email': 'markus.lowegren@disruptiveventures.se', 'linkedin_url': ''}
        dv_org = {'name': 'Disruptive Ventures'}
        portfolio_count = 0
        portfolio_companies_html = "<p>Error loading portfolio companies</p>"
        print(f"Error: {e}")
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Settings - Admin</title>
    {get_dv_styles()}
    <style>
        .settings-submenu {{
            display: flex;
            gap: 8px;
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 8px;
            padding: 4px;
            margin-bottom: 32px;
            max-width: 600px;
        }}
        
        .submenu-btn {{
            flex: 1;
            padding: 10px 20px;
            border: none;
            background: transparent;
            color: var(--gray-600);
            font-size: 14px;
            font-weight: 500;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.15s;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
        }}
        
        .submenu-btn:hover {{
            background: var(--gray-100);
            color: var(--gray-900);
        }}
        
        .submenu-btn.active {{
            background: var(--gray-900);
            color: white;
            font-weight: 600;
        }}
        
        .settings-section {{
            display: none;
        }}
        
        .settings-section.active {{
            display: block;
        }}
        
        .company-settings-card {{
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
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
        
        .btn-sm {{
            padding: 6px 12px;
            font-size: 12px;
        }}
        
        .integration-item button {{
            width: 100%;
            cursor: pointer;
        }}
        
        .setting-item {{
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 16px;
        }}
        
        .setting-label {{
            font-size: 14px;
            font-weight: 600;
            color: var(--gray-900);
            margin-bottom: 8px;
        }}
        
        .setting-description {{
            font-size: 13px;
            color: var(--gray-600);
            margin-bottom: 12px;
        }}
        
        .setting-value {{
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 13px;
            color: var(--gray-700);
            background: var(--gray-50);
            padding: 10px 12px;
            border-radius: 6px;
            border: 1px solid var(--gray-200);
        }}
        
        .api-key-item {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 16px;
            background: var(--gray-50);
            border-radius: 8px;
            border: 1px solid var(--gray-200);
            margin-bottom: 12px;
        }}
        
        .api-key-info {{
            flex: 1;
        }}
        
        .api-key-name {{
            font-size: 14px;
            font-weight: 600;
            color: var(--gray-900);
            margin-bottom: 4px;
        }}
        
        .api-key-service {{
            font-size: 12px;
            color: var(--gray-500);
        }}
        
        .api-key-value {{
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 11px;
            color: var(--gray-600);
            background: white;
            padding: 6px 10px;
            border-radius: 4px;
            border: 1px solid var(--gray-200);
            margin-right: 12px;
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
        
        body.dark-mode .settings-submenu {{
            background: #2a2a2a;
            border-color: #404040;
        }}
        
        body.dark-mode .submenu-btn {{
            color: #999;
        }}
        
        body.dark-mode .submenu-btn:hover {{
            background: #1a1a1a;
            color: #e5e5e5;
        }}
        
        body.dark-mode .submenu-btn.active {{
            background: #e5e5e5;
            color: #1a1a1a;
        }}
        
        body.dark-mode .modal {{
            background: #2a2a2a;
        }}
        
        body.dark-mode .company-settings-card,
        body.dark-mode .setting-item,
        body.dark-mode .api-key-item {{
            background: #2a2a2a;
            border-color: #404040;
        }}
        
        body.dark-mode .integration-item {{
            background: #1a1a1a;
            border-color: #404040;
        }}
        
        body.dark-mode .form-input,
        body.dark-mode .setting-value,
        body.dark-mode .api-key-value {{
            background: #1a1a1a;
            border-color: #404040;
            color: #e5e5e5;
        }}
        
        body.dark-mode .company-name,
        body.dark-mode .integration-name,
        body.dark-mode .modal-title,
        body.dark-mode .setting-label,
        body.dark-mode .api-key-name {{
            color: #e5e5e5;
        }}
        
        body.dark-mode .company-meta,
        body.dark-mode .integration-desc,
        body.dark-mode .form-hint,
        body.dark-mode .setting-description,
        body.dark-mode .api-key-service {{
            color: #999;
        }}
    </style>
</head>
<body>
    {get_admin_sidebar('settings', current_user.get('name', 'Admin User'), current_user.get('email', ''), current_user.get('linkedin_url', ''))}
    
    <div class="main-content">
        <div class="page-header">
            <div class="page-header-left">
                <h1 class="page-title">Settings</h1>
                <p class="page-description">Manage platform configuration and integrations</p>
            </div>
        </div>
        
        <div class="container">
            <!-- Settings Submenu -->
            <div class="settings-submenu">
                <button class="submenu-btn active" onclick="switchSettingsTab('general')">General</button>
                <button class="submenu-btn" onclick="switchSettingsTab('api')">API Keys</button>
                <button class="submenu-btn" onclick="switchSettingsTab('portfolio')">Portfolio Companies ({portfolio_count})</button>
            </div>
            
            <!-- General Settings Section -->
            <div id="general-section" class="settings-section active">
                <h2 style="font-size: 18px; font-weight: 600; color: var(--gray-900); margin-bottom: 20px;">General Settings</h2>
                
                <div class="setting-item">
                    <div class="setting-label">Organization Name</div>
                    <div class="setting-description">Your fund or organization name</div>
                    <div class="setting-value">{dv_org.get('name', 'Disruptive Ventures') if dv_org else 'Disruptive Ventures'}</div>
                </div>
                
                <div class="setting-item">
                    <div class="setting-label">Platform Environment</div>
                    <div class="setting-description">Current deployment environment</div>
                    <div class="setting-value">{settings.env}</div>
                </div>
                
                <div class="setting-item">
                    <div class="setting-label">Debug Mode</div>
                    <div class="setting-description">Enable detailed error logging</div>
                    <div class="setting-value">{'Enabled' if settings.debug else 'Disabled'}</div>
                </div>
                
                <div class="setting-item">
                    <div class="setting-label">Database</div>
                    <div class="setting-description">Supabase connection status</div>
                    <div class="setting-value">✅ Connected</div>
                </div>
            </div>
            
            <!-- API Keys Section -->
            <div id="api-section" class="settings-section">
                <h2 style="font-size: 18px; font-weight: 600; color: var(--gray-900); margin-bottom: 20px;">API Keys & Credentials</h2>
                <p style="font-size: 14px; color: var(--gray-600); margin-bottom: 24px;">
                    Global API keys used by the platform. For company-specific keys, see Portfolio Companies tab.
                </p>
                
                <div class="api-key-item">
                    <div class="api-key-info">
                        <div class="api-key-name">Linear API</div>
                        <div class="api-key-service">Task management and activity tracking</div>
                    </div>
                    <div class="api-key-value">{'***' + settings.linear_api_key[-8:] if settings.linear_api_key else 'Not configured'}</div>
                    <button class="btn-secondary btn-sm">Configure</button>
                </div>
                
                <div class="api-key-item">
                    <div class="api-key-info">
                        <div class="api-key-name">OpenAI API</div>
                        <div class="api-key-service">AI processing and transcription</div>
                    </div>
                    <div class="api-key-value">{'***' + settings.openai_api_key[-8:] if settings.openai_api_key else 'Not configured'}</div>
                    <button class="btn-secondary btn-sm">Configure</button>
                </div>
                
                <div class="api-key-item">
                    <div class="api-key-info">
                        <div class="api-key-name">Google OAuth</div>
                        <div class="api-key-service">Calendar, Gmail, and Drive integration</div>
                    </div>
                    <div class="api-key-value">{'***' + settings.google_client_id[-8:] if settings.google_client_id else 'Not configured'}</div>
                    <button class="btn-secondary btn-sm">Configure</button>
                </div>
                
                <div class="api-key-item">
                    <div class="api-key-info">
                        <div class="api-key-name">Pipedrive (Coeo)</div>
                        <div class="api-key-service">Currently showing Coeo's pipeline</div>
                    </div>
                    <div class="api-key-value">{'***' + settings.pipedrive_api_token[-8:] if settings.pipedrive_api_token else 'Not configured'}</div>
                    <span style="padding: 4px 8px; background: #f0fdf4; color: #16a34a; border-radius: 4px; font-size: 11px; font-weight: 600;">ACTIVE</span>
                </div>
                
                <div style="margin-top: 24px; padding: 16px; background: var(--amber-50); border: 1px solid #fde68a; border-radius: 8px; font-size: 13px; color: var(--gray-700);">
                    <strong>Note:</strong> Global API keys are configured in the .env file. Company-specific integrations can be managed in the Portfolio Companies tab.
                </div>
            </div>
            
            <!-- Portfolio Companies Section -->
            <div id="portfolio-section" class="settings-section">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <div>
                        <h2 style="font-size: 18px; font-weight: 600; color: var(--gray-900); margin-bottom: 4px;">Portfolio Companies</h2>
                        <p style="font-size: 13px; color: var(--gray-600);">Manage API integrations for each portfolio company</p>
                    </div>
                    <button class="btn-primary" onclick="alert('Add company feature coming soon!')">
                        + Add Company
                    </button>
                </div>
                
                {portfolio_companies_html}
            </div>
        </div>
    </div>
    
    <!-- Integration Modal (same as before) -->
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
                
                <div id="workspace-fields" style="display: none;">
                    <div class="form-group">
                        <label class="form-label">Client ID</label>
                        <input type="text" class="form-input" id="workspace-client-id" placeholder="Enter Google Workspace Client ID">
                        <p class="form-hint">From Google Cloud Console OAuth credentials</p>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Client Secret</label>
                        <input type="password" class="form-input" id="workspace-secret" placeholder="Enter client secret">
                        <p class="form-hint">OAuth client secret</p>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Service Account Email (optional)</label>
                        <input type="text" class="form-input" id="workspace-email" placeholder="service-account@project.iam.gserviceaccount.com">
                        <p class="form-hint">For server-to-server interactions</p>
                    </div>
                </div>
                
                <div id="office365-fields" style="display: none;">
                    <div class="form-group">
                        <label class="form-label">Tenant ID</label>
                        <input type="text" class="form-input" id="office365-tenant" placeholder="Enter Microsoft 365 Tenant ID">
                        <p class="form-hint">From Azure Active Directory</p>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Client ID (Application ID)</label>
                        <input type="text" class="form-input" id="office365-client-id" placeholder="Enter application ID">
                        <p class="form-hint">From App registrations in Azure AD</p>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Client Secret</label>
                        <input type="password" class="form-input" id="office365-secret" placeholder="Enter client secret">
                        <p class="form-hint">OAuth client secret</p>
                    </div>
                </div>
                
                <div id="custom-fields" style="display: none;">
                    <div class="form-group">
                        <label class="form-label">Integration Name</label>
                        <input type="text" class="form-input" id="custom-name" placeholder="e.g., Internal CRM, Custom ERP">
                        <p class="form-hint">Give your custom integration a name</p>
                    </div>
                    <div class="form-group">
                        <label class="form-label">API Endpoint URL</label>
                        <input type="text" class="form-input" id="custom-url" placeholder="https://api.example.com/v1">
                        <p class="form-hint">Base URL for API calls</p>
                    </div>
                    <div class="form-group">
                        <label class="form-label">API Token / Key</label>
                        <input type="password" class="form-input" id="custom-token" placeholder="Enter API token">
                        <p class="form-hint">Authentication token or API key</p>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Additional Headers (JSON)</label>
                        <textarea class="form-input" id="custom-headers" rows="3" placeholder='{{"X-Custom-Header": "value"}}'></textarea>
                        <p class="form-hint">Optional: Custom HTTP headers as JSON</p>
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
        
        // Switch between settings tabs
        function switchSettingsTab(tabName) {{
            console.log('Switching to settings tab:', tabName);
            
            // Update submenu buttons
            document.querySelectorAll('.submenu-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // Hide all sections
            document.querySelectorAll('.settings-section').forEach(section => {{
                section.classList.remove('active');
                section.style.display = 'none';
            }});
            
            // Show selected section
            const selectedSection = document.getElementById(`${{tabName}}-section`);
            if (selectedSection) {{
                selectedSection.classList.add('active');
                selectedSection.style.display = 'block';
            }}
            
            // Save preference
            localStorage.setItem('settings-active-tab', tabName);
        }}
        
        // Restore tab preference
        window.addEventListener('load', () => {{
            const savedTab = localStorage.getItem('settings-active-tab') || 'general';
            if (savedTab !== 'general') {{
                const btn = Array.from(document.querySelectorAll('.submenu-btn')).find(b => 
                    b.textContent.toLowerCase().includes(savedTab)
                );
                if (btn) {{
                    document.querySelectorAll('.submenu-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    
                    document.querySelectorAll('.settings-section').forEach(s => {{
                        s.classList.remove('active');
                        s.style.display = 'none';
                    }});
                    
                    const section = document.getElementById(`${{savedTab}}-section`);
                    if (section) {{
                        section.classList.add('active');
                        section.style.display = 'block';
                    }}
                }}
            }}
        }});
        
        function openIntegrationModal(companyId, integrationType, companyName) {{
            console.log('Opening modal:', companyId, integrationType, companyName);
            
            currentCompanyId = companyId;
            currentIntegrationType = integrationType;
            
            const modal = document.getElementById('integration-modal');
            if (!modal) {{
                console.error('Modal not found!');
                return;
            }}
            
            document.getElementById('modal-title').textContent = `Configure ${{integrationType}} for ${{companyName}}`;
            document.getElementById('modal-subtitle').textContent = `Add API credentials to connect ${{integrationType}}`;
            
            document.getElementById('form-company-id').value = companyId;
            document.getElementById('form-integration-type').value = integrationType;
            
            document.getElementById('pipedrive-fields').style.display = 'none';
            document.getElementById('fortnox-fields').style.display = 'none';
            document.getElementById('sheets-fields').style.display = 'none';
            document.getElementById('workspace-fields').style.display = 'none';
            document.getElementById('office365-fields').style.display = 'none';
            document.getElementById('custom-fields').style.display = 'none';
            
            if (integrationType === 'pipedrive') {{
                document.getElementById('pipedrive-fields').style.display = 'block';
            }} else if (integrationType === 'fortnox') {{
                document.getElementById('fortnox-fields').style.display = 'block';
            }} else if (integrationType === 'google_sheets') {{
                document.getElementById('sheets-fields').style.display = 'block';
            }} else if (integrationType === 'google_workspace') {{
                document.getElementById('workspace-fields').style.display = 'block';
            }} else if (integrationType === 'office365') {{
                document.getElementById('office365-fields').style.display = 'block';
            }} else if (integrationType === 'custom') {{
                document.getElementById('custom-fields').style.display = 'block';
            }}
            
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
            }} else if (integrationType === 'google_workspace') {{
                credentials.client_id = document.getElementById('workspace-client-id').value;
                credentials.client_secret = document.getElementById('workspace-secret').value;
                credentials.company_domain = document.getElementById('workspace-email').value;
                credentials.api_url = 'https://www.googleapis.com';
            }} else if (integrationType === 'office365') {{
                credentials.client_id = document.getElementById('office365-client-id').value;
                credentials.client_secret = document.getElementById('office365-secret').value;
                credentials.company_domain = document.getElementById('office365-tenant').value;
                credentials.api_url = 'https://graph.microsoft.com/v1.0';
            }} else if (integrationType === 'custom') {{
                credentials.integration_name = document.getElementById('custom-name').value;
                credentials.api_url = document.getElementById('custom-url').value;
                credentials.api_token = document.getElementById('custom-token').value;
                credentials.company_domain = document.getElementById('custom-headers').value;
            }}
            
            try {{
                const response = await fetch('/settings/integrations', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify(credentials)
                }});
                
                if (response.ok) {{
                    alert('✅ Integration saved successfully!');
                    closeModal();
                    location.reload();
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


@router.post("/integrations")
async def save_integration(credentials: IntegrationCredentials):
    """Save integration credentials (encrypted)."""
    
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
            supabase.table('portfolio_company_integrations') \
                .update(integration_data) \
                .eq('id', existing.data[0]['id']) \
                .execute()
        else:
            supabase.table('portfolio_company_integrations') \
                .insert(integration_data) \
                .execute()
        
        return JSONResponse(content={"message": "Integration saved successfully", "status": "success"})
    
    except Exception as e:
        print(f"Error saving integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/integrations/{integration_id}")
async def delete_integration(integration_id: str):
    """Delete an integration."""
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Delete integration
        supabase.table('portfolio_company_integrations') \
            .delete() \
            .eq('id', integration_id) \
            .execute()
        
        return JSONResponse(content={"message": "Integration deleted successfully", "status": "success"})
    
    except Exception as e:
        print(f"Error deleting integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/integrations/{integration_id}")
async def update_integration(integration_id: str, credentials: IntegrationCredentials):
    """Update existing integration credentials."""
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Encrypt sensitive data
        encrypted_token = encrypt_value(credentials.api_token) if credentials.api_token else None
        encrypted_secret = encrypt_value(credentials.client_secret) if credentials.client_secret else None
        
        integration_data = {
            'api_token_encrypted': encrypted_token,
            'client_secret_encrypted': encrypted_secret,
            'client_id': credentials.client_id,
            'api_url': credentials.api_url,
            'company_domain': credentials.company_domain,
            'is_active': True,
            'last_sync_status': 'pending',
        }
        
        supabase.table('portfolio_company_integrations') \
            .update(integration_data) \
            .eq('id', integration_id) \
            .execute()
        
        return JSONResponse(content={"message": "Integration updated successfully", "status": "success"})
    
    except Exception as e:
        print(f"Error updating integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

