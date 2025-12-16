"""
Knowledge Bank - Policy Documents & Organizational Knowledge
Searchable repository of company policies, playbooks, and best practices
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from supabase import create_client
from app.config import settings
from app.api.styles import get_dv_styles
from app.api.sidebar_component import get_admin_sidebar

router = APIRouter(prefix="/knowledge", tags=["Knowledge Bank"])


class PolicyDocument(BaseModel):
    title: str
    policy_type: str  # 'culture', 'hr', 'security', 'playbook', 'process'
    google_drive_url: str
    description: Optional[str] = None
    owner_name: Optional[str] = None
    tags: Optional[List[str]] = None
    is_required_reading: bool = False


# ============================================================================
# KNOWLEDGE BANK UI
# ============================================================================

@router.get("/", response_class=HTMLResponse)
async def knowledge_bank_ui():
    """
    Knowledge Bank UI - Browse all policy documents and organizational knowledge.
    """
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    # Get all policy documents
    policies = supabase.table('policy_documents').select('*').order('created_at', desc=True).execute().data
    
    # Get all people for profiles - will deduplicate in generate_people_cards
    people = supabase.table('people').select('*').order('name').execute().data
    
    # Get current user info - Markus Löwegren
    current_user = next((p for p in people if 'marcus' in p.get('name', '').lower() or 'markus' in p.get('name', '').lower()), None)
    if not current_user:
        current_user = {'name': 'Markus Löwegren', 'email': 'markus.lowegren@disruptiveventures.se', 'linkedin_url': ''}
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin: Knowledge Bank - Disruptive Ventures</title>
    {get_dv_styles()}
    <style>
        .knowledge-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }}
        
        .policy-card {{
            background: white;
            border-radius: 8px;
            padding: 16px;
            border: 1px solid var(--gray-200);
            transition: all 0.15s;
        }}
        
        .policy-card:hover {{
            border-color: var(--gray-300);
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .policy-type {{
            display: inline-block;
            background: var(--gray-100);
            color: var(--gray-700);
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 500;
            text-transform: uppercase;
            margin-bottom: 12px;
        }}
        
        .policy-title {{
            font-size: 14px;
            font-weight: 600;
            color: var(--gray-900);
            margin-bottom: 8px;
        }}
        
        .policy-description {{
            color: var(--gray-600);
            line-height: 1.5;
            margin-bottom: 12px;
            font-size: 13px;
        }}
        
        .policy-meta {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid var(--gray-100);
        }}
        
        .policy-tag {{
            background: var(--gray-100);
            color: var(--gray-600);
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
        }}
        
        .policy-actions {{
            margin-top: 12px;
            display: flex;
            gap: 8px;
        }}
        
        .btn-primary {{
            background: var(--gray-900);
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 500;
            font-size: 13px;
            display: inline-block;
            border: none;
        }}
        
        .btn-primary:hover {{
            background: var(--gray-700);
        }}
        
        .btn-secondary {{
            background: white;
            color: var(--gray-700);
            padding: 8px 12px;
            border-radius: 6px;
            border: 1px solid var(--gray-300);
            text-decoration: none;
            font-weight: 500;
            font-size: 13px;
            display: inline-block;
        }}
        
        .btn-secondary:hover {{
            background: var(--gray-50);
        }}
        
        .people-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
        }}
        
        @media (max-width: 1024px) {{
            .people-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
        
        @media (max-width: 640px) {{
            .people-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        
        .person-card {{
            background: white;
            border-radius: 8px;
            padding: 16px;
            text-align: center;
            border: 1px solid var(--gray-200);
        }}
        
        .person-avatar {{
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: var(--gray-200);
            color: var(--gray-600);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: 600;
            margin: 0 auto 12px;
            overflow: hidden;
        }}
        
        .person-avatar img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        .person-name {{
            font-size: 14px;
            font-weight: 600;
            color: var(--gray-900);
            margin-bottom: 4px;
        }}
        
        .person-role {{
            color: var(--gray-600);
            font-size: 12px;
            margin-bottom: 8px;
        }}
        
        .tabs {{
            display: flex;
            gap: 8px;
            margin-bottom: 24px;
        }}
        
        .tab {{
            padding: 8px 12px;
            border: none;
            background: transparent;
            color: var(--gray-700);
            font-weight: 500;
            cursor: pointer;
            border-radius: 6px;
            transition: all 0.15s;
            font-size: 13px;
        }}
        
        .tab:hover {{
            background: var(--gray-100);
        }}
        
        .tab.active {{
            background: var(--gray-100);
            color: var(--gray-900);
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
    </style>
</head>
<body>
    {get_admin_sidebar('knowledge', current_user.get('name', 'Admin User'), current_user.get('email', ''), current_user.get('linkedin_url', ''))}
    
    <div class="main-content">
        <div class="page-header">
            <h1 class="page-title">Knowledge Bank</h1>
            <p class="page-description">Company policies, playbooks, and team profiles</p>
        </div>
        
        <div class="container">
            <div class="tabs">
                <button class="tab active" onclick="showTab('policies')">Policies</button>
                <button class="tab" onclick="showTab('people')">People</button>
            </div>
            
            <!-- POLICIES TAB -->
            <div id="policies-tab" class="tab-content active">
                <div class="section-header">
                    <h2>Policies ({len(policies) if policies else 0})</h2>
                    <div class="view-toggle">
                        <button class="view-toggle-btn active" onclick="toggleView('policies', 'card')" title="Card View">
                            <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                                <rect x="3" y="3" width="7" height="7"/>
                                <rect x="14" y="3" width="7" height="7"/>
                                <rect x="14" y="14" width="7" height="7"/>
                                <rect x="3" y="14" width="7" height="7"/>
                            </svg>
                        </button>
                        <button class="view-toggle-btn" onclick="toggleView('policies', 'list')" title="List View">
                            <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                                <line x1="8" y1="6" x2="21" y2="6"/>
                                <line x1="8" y1="12" x2="21" y2="12"/>
                                <line x1="8" y1="18" x2="21" y2="18"/>
                                <line x1="3" y1="6" x2="3.01" y2="6"/>
                                <line x1="3" y1="12" x2="3.01" y2="12"/>
                                <line x1="3" y1="18" x2="3.01" y2="18"/>
                            </svg>
                        </button>
                    </div>
                </div>
                <div id="policies-container" class="card-view">
                    {generate_policy_cards(policies) if policies else '<div style="grid-column: 1/-1; text-align: center; padding: 48px; color: var(--gray-600);"><div style="font-size: 14px; font-weight: 500; margin-bottom: 8px;">No policies yet</div><p style="font-size: 13px; margin-bottom: 16px;">Add your first policy document to get started</p><a href="/knowledge/add-policy" class="btn-primary">+ Add Policy</a></div>'}
                </div>
            </div>
            
            <!-- PEOPLE TAB -->
            <div id="people-tab" class="tab-content">
                <div class="section-header">
                    <h2>People</h2>
                    <div class="view-toggle">
                        <button class="view-toggle-btn active" onclick="toggleView('people', 'card')" title="Card View">
                            <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                                <rect x="3" y="3" width="7" height="7"/>
                                <rect x="14" y="3" width="7" height="7"/>
                                <rect x="14" y="14" width="7" height="7"/>
                                <rect x="3" y="14" width="7" height="7"/>
                            </svg>
                        </button>
                        <button class="view-toggle-btn" onclick="toggleView('people', 'list')" title="List View">
                            <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                                <line x1="8" y1="6" x2="21" y2="6"/>
                                <line x1="8" y1="12" x2="21" y2="12"/>
                                <line x1="8" y1="18" x2="21" y2="18"/>
                                <line x1="3" y1="6" x2="3.01" y2="6"/>
                                <line x1="3" y1="12" x2="3.01" y2="12"/>
                                <line x1="3" y1="18" x2="3.01" y2="18"/>
                            </svg>
                        </button>
                    </div>
                </div>
                <div id="people-container" class="card-view three-col">
                    {generate_people_cards(people) if people else '<div style="grid-column: 1/-1; text-align: center; padding: 48px; color: var(--gray-600);"><div style="font-size: 14px; font-weight: 500;">No team members yet</div></div>'}
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function showTab(tabName) {{
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            
            // Show selected tab
            document.getElementById(tabName + '-tab').classList.add('active');
            event.target.classList.add('active');
        }}
        
        function toggleView(section, view) {{
            const container = document.getElementById(section + '-container');
            const buttons = event.currentTarget.parentElement.querySelectorAll('.view-toggle-btn');
            
            // Update active button
            buttons.forEach(b => b.classList.remove('active'));
            event.currentTarget.classList.add('active');
            
            // Toggle view
            if (view === 'list') {{
                container.className = 'list-view';
            }} else {{
                if (section === 'people') {{
                    container.className = 'card-view three-col';
                }} else {{
                    container.className = 'card-view';
                }}
            }}
            
            // Save preference
            localStorage.setItem(section + '-view', view);
        }}
        
        // Restore view preferences on load
        window.addEventListener('load', () => {{
            const peopleView = localStorage.getItem('people-view') || 'card';
            const policiesView = localStorage.getItem('policies-view') || 'card';
            
            // Restore people view
            if (peopleView === 'list') {{
                const peopleContainer = document.getElementById('people-container');
                if (peopleContainer) peopleContainer.className = 'list-view';
                // Update button
                document.querySelectorAll('#people-tab .view-toggle-btn')[1]?.classList.add('active');
                document.querySelectorAll('#people-tab .view-toggle-btn')[0]?.classList.remove('active');
            }}
            
            // Restore policies view
            if (policiesView === 'list') {{
                const policiesContainer = document.getElementById('policies-container');
                if (policiesContainer) policiesContainer.className = 'list-view';
                // Update button
                document.querySelectorAll('#policies-tab .view-toggle-btn')[1]?.classList.add('active');
                document.querySelectorAll('#policies-tab .view-toggle-btn')[0]?.classList.remove('active');
            }}
        }});
    </script>
        
        function toggleView(section, view) {{
            const container = document.getElementById(section + '-container');
            const buttons = event.currentTarget.parentElement.querySelectorAll('.view-toggle-btn');
            
            // Update active button
            buttons.forEach(b => b.classList.remove('active'));
            event.currentTarget.classList.add('active');
            
            // Toggle view
            if (view === 'list') {{
                container.className = 'list-view';
            }} else {{
                if (section === 'people') {{
                    container.className = 'card-view three-col';
                }} else {{
                    container.className = 'card-view';
                }}
            }}
            
            // Save preference
            localStorage.setItem(section + '-view', view);
        }}
        
        // Restore view preferences on load
        window.addEventListener('load', () => {{
            const peopleView = localStorage.getItem('people-view') || 'card';
            const policiesView = localStorage.getItem('policies-view') || 'card';
            
            // Restore people view
            if (peopleView === 'list') {{
                const peopleContainer = document.getElementById('people-container');
                if (peopleContainer) peopleContainer.className = 'list-view';
            }}
            
            // Restore policies view
            if (policiesView === 'list') {{
                const policiesContainer = document.getElementById('policies-container');
                if (policiesContainer) policiesContainer.className = 'list-view';
            }}
        }});
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html)


def generate_policy_cards(policies: list) -> str:
    """Generate HTML for policy cards - monochrome design."""
    cards = []
    
    for policy in policies:
        tags_html = ' '.join([f'<span class="policy-tag">{tag}</span>' for tag in (policy.get('tags') or [])])
        
        required_badge = '<span style="background: var(--gray-200); color: var(--gray-700); padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-left: 8px; font-weight: 500;">REQUIRED</span>' if policy.get('is_required_reading') else ''
        
        card = f"""
        <div class="policy-card">
            <div class="policy-type">{policy.get('policy_type', 'policy')}</div>
            <div class="policy-title">
                {policy['title']}
                {required_badge}
            </div>
            <div class="policy-description">
                {policy.get('description', 'No description')}
            </div>
            {f'<div class="policy-meta">{tags_html}</div>' if tags_html else ''}
            <div class="policy-actions">
                <a href="{policy['google_drive_url']}" target="_blank" class="btn-primary">
                    Open Document
                </a>
                <button onclick="acknowledgePolicy('{policy['id']}')" class="btn-secondary">
                    Mark as Read
                </button>
            </div>
            <div style="margin-top: 12px; font-size: 11px; color: var(--gray-500);">
                {f"Owner: {policy.get('owner_name', 'Unknown')}" if policy.get('owner_name') else ''}
                | Added: {str(policy.get('created_at', ''))[:10]}
            </div>
        </div>
        """
        cards.append(card)
    
    return '\n'.join(cards)


def generate_people_cards(people: list) -> str:
    """
    Generate HTML for people profile cards - deduplicated by name, with LinkedIn images.
    
    Filters out users with incomplete profiles (missing name, email, or title).
    """
    cards = []
    seen_names = set()
    
    for person in people:
        name = person.get('name', '').strip()
        email = person.get('email', '').strip()
        
        # Filter: Skip users with missing critical data
        if not name:
            continue
        
        if not email:
            continue
        
        # Get title/role with proper None handling
        title = person.get('title') or person.get('role')
        if not title or str(title).lower() == 'none':
            # Skip users with no title/role data
            continue
        
        # Skip duplicates (case-insensitive)
        name_lower = name.lower()
        if name_lower in seen_names:
            continue
        seen_names.add(name_lower)
        
        # Get initials for fallback
        initials = ''.join([n[0].upper() for n in name.split()[:2]])
        
        # Use LinkedIn image if available, otherwise show initials
        linkedin_url = person.get('linkedin_url', '')
        avatar_html = f'<img src="{linkedin_url}" alt="{name}" onerror="this.style.display=\'none\'; this.parentElement.textContent=\'{initials}\';">' if linkedin_url else initials
        
        card = f"""
        <div class="person-card">
            <div class="person-avatar">{avatar_html}</div>
            <div class="person-name">{name}</div>
            <div class="person-role">{title}</div>
            <div style="color: var(--gray-600); font-size: 12px; margin-bottom: 12px;">
                {email}
            </div>
            <a href="/knowledge/person/{person['id']}" class="btn-primary" style="font-size: 13px; padding: 6px 12px;">
                View Profile
            </a>
        </div>
        """
        cards.append(card)
    
    return '\n'.join(cards)


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/add-policy")
async def add_policy(policy: PolicyDocument):
    """Add a policy document to the knowledge bank."""
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    # Get org_id (for now use first org)
    orgs = supabase.table('orgs').select('id').limit(1).execute()
    if not orgs.data:
        raise HTTPException(400, "No organization found")
    
    org_id = orgs.data[0]['id']
    
    # Insert policy
    result = supabase.table('policy_documents').insert({
        'org_id': org_id,
        'title': policy.title,
        'policy_type': policy.policy_type,
        'google_drive_url': policy.google_drive_url,
        'description': policy.description,
        'tags': policy.tags or [],
        'is_required_reading': policy.is_required_reading,
        'status': 'active',
        'effective_date': datetime.now().date().isoformat(),
    }).execute()
    
    return {
        "success": True,
        "policy_id": result.data[0]['id'],
        "message": "Policy added to knowledge bank"
    }


@router.get("/search")
async def search_knowledge(q: str):
    """Search across all policy documents and people profiles."""
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    # Search policies
    policies = supabase.table('policy_documents').select('*').or_(
        f"title.ilike.%{q}%,description.ilike.%{q}%"
    ).execute().data
    
    # Search people
    people = supabase.table('people').select('*').or_(
        f"name.ilike.%{q}%,bio.ilike.%{q}%"
    ).execute().data
    
    return {
        "policies": policies,
        "people": people,
        "query": q
    }


@router.post("/acknowledge/{policy_id}")
async def acknowledge_policy(policy_id: str):
    """Mark a policy as read by current user."""
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    # For now, use placeholder user
    # In production, get from auth
    user_id = "00000000-0000-0000-0000-000000000000"
    
    try:
        supabase.table('policy_acknowledgments').insert({
            'policy_id': policy_id,
            'user_id': user_id,
            'acknowledged_at': datetime.now().isoformat()
        }).execute()
        
        return {"success": True, "message": "Policy acknowledged"}
    
    except:
        # Already acknowledged
        return {"success": True, "message": "Already acknowledged"}


@router.get("/add-culture-playbook", response_class=HTMLResponse)
async def add_culture_playbook_form():
    """Quick form to add the culture playbook Marcus shared."""
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Add Culture Playbook</title>
    {get_dv_styles()}
</head>
<body>
    <div class="header">
        <h1>📖 Add Culture Playbook</h1>
    </div>
    
    <div style="max-width: 600px; margin: 40px auto; padding: 20px;">
        <div style="background: white; padding: 30px; border-radius: 12px;">
            <h2>Culture & Values Playbook</h2>
            
            <form id="policyForm">
                <div style="margin: 20px 0;">
                    <label style="display: block; margin-bottom: 8px; font-weight: 600;">Title:</label>
                    <input type="text" id="title" value="Culture & Values Playbook" 
                           style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 16px;">
                </div>
                
                <div style="margin: 20px 0;">
                    <label style="display: block; margin-bottom: 8px; font-weight: 600;">Google Drive URL:</label>
                    <input type="text" id="url" value="https://docs.google.com/document/d/1eqvNGT3sDUA-NH7jA6WGzb3n1t3dFipK7d41pcX_IJ8/edit"
                           style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px;">
                </div>
                
                <div style="margin: 20px 0;">
                    <label style="display: block; margin-bottom: 8px; font-weight: 600;">Type:</label>
                    <select id="type" style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px;">
                        <option value="culture">Culture</option>
                        <option value="playbook">Playbook</option>
                        <option value="hr">HR Policy</option>
                        <option value="security">Security</option>
                        <option value="process">Process Document</option>
                    </select>
                </div>
                
                <div style="margin: 20px 0;">
                    <label style="display: block; margin-bottom: 8px; font-weight: 600;">Description:</label>
                    <textarea id="description" rows="3"
                              style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px;">Core values, culture principles, and how we build great teams at Disruptive Ventures.</textarea>
                </div>
                
                <div style="margin: 20px 0;">
                    <label style="display: flex; align-items: center; gap: 8px;">
                        <input type="checkbox" id="required" checked>
                        <span>Required reading for all team members</span>
                    </label>
                </div>
                
                <button type="submit" style="background: #635BFF; color: white; padding: 14px 32px; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; width: 100%;">
                    📚 Add to Knowledge Bank
                </button>
            </form>
            
            <div id="result" style="margin-top: 20px; padding: 16px; border-radius: 8px; display: none;"></div>
        </div>
    </div>
    
    <script>
        document.getElementById('policyForm').addEventListener('submit', async (e) => {{
            e.preventDefault();
            
            const data = {{
                title: document.getElementById('title').value,
                google_drive_url: document.getElementById('url').value,
                policy_type: document.getElementById('type').value,
                description: document.getElementById('description').value,
                is_required_reading: document.getElementById('required').checked,
                tags: ['culture', 'values', 'team building']
            }};
            
            try {{
                const response = await fetch('/knowledge/add-policy', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify(data)
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    document.getElementById('result').style.display = 'block';
                    document.getElementById('result').style.background = '#d4edda';
                    document.getElementById('result').style.color = '#155724';
                    document.getElementById('result').innerHTML = '✅ Policy added to Knowledge Bank!<br><br><a href="/knowledge" style="color: #155724; font-weight: 600;">View Knowledge Bank →</a>';
                }} else {{
                    document.getElementById('result').style.display = 'block';
                    document.getElementById('result').style.background = '#f8d7da';
                    document.getElementById('result').style.color = '#721c24';
                    document.getElementById('result').innerHTML = '❌ Error: ' + (result.error || 'Unknown error');
                }}
            }} catch (error) {{
                document.getElementById('result').style.display = 'block';
                document.getElementById('result').style.background = '#f8d7da';
                document.getElementById('result').innerHTML = '❌ Error: ' + error.message;
            }}
        }});
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html)


