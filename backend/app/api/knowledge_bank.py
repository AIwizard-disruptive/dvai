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
    
    # Get all people for profiles
    people = supabase.table('people').select('*').order('name').execute().data
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Knowledge Bank - Disruptive Ventures</title>
    {get_dv_styles()}
    <style>
        .knowledge-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 24px;
            padding: 30px;
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .policy-card {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: all 0.3s;
            border-left: 4px solid #635BFF;
        }}
        
        .policy-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        }}
        
        .policy-type {{
            display: inline-block;
            background: #635BFF;
            color: white;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            margin-bottom: 12px;
        }}
        
        .policy-title {{
            font-size: 20px;
            font-weight: 700;
            color: #0A2540;
            margin-bottom: 12px;
        }}
        
        .policy-description {{
            color: #425466;
            line-height: 1.6;
            margin-bottom: 16px;
        }}
        
        .policy-meta {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid #EDF2F7;
        }}
        
        .policy-tag {{
            background: #F7FAFC;
            color: #425466;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 12px;
        }}
        
        .policy-actions {{
            margin-top: 16px;
            display: flex;
            gap: 12px;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #635BFF, #00D4FF);
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            display: inline-block;
        }}
        
        .btn-secondary {{
            background: white;
            color: #635BFF;
            padding: 10px 20px;
            border-radius: 8px;
            border: 2px solid #635BFF;
            text-decoration: none;
            font-weight: 600;
            display: inline-block;
        }}
        
        .people-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .person-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .person-avatar {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: linear-gradient(135deg, #635BFF, #00D4FF);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            font-weight: 700;
            margin: 0 auto 16px;
        }}
        
        .person-name {{
            font-size: 18px;
            font-weight: 700;
            color: #0A2540;
            margin-bottom: 8px;
        }}
        
        .person-role {{
            color: #635BFF;
            font-size: 14px;
            margin-bottom: 12px;
        }}
        
        .tabs {{
            display: flex;
            gap: 0;
            background: white;
            border-radius: 12px;
            padding: 4px;
            max-width: 400px;
            margin: 20px auto;
        }}
        
        .tab {{
            flex: 1;
            padding: 12px 24px;
            border: none;
            background: transparent;
            color: #425466;
            font-weight: 600;
            cursor: pointer;
            border-radius: 8px;
            transition: all 0.3s;
        }}
        
        .tab.active {{
            background: #635BFF;
            color: white;
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
    <div class="header">
        <div class="logo">
            <span class="logo-accent">Disruptive</span> Ventures
        </div>
        <h1>📚 Knowledge Bank</h1>
        <p>Company policies, playbooks, and team profiles</p>
    </div>
    
    <div class="nav">
        <a href="/dashboard-ui">← Dashboard</a>
        <a href="/knowledge/upload-policy">+ Add Policy</a>
        <a href="/knowledge/people">👥 Team Directory</a>
    </div>
    
    <div class="tabs">
        <button class="tab active" onclick="showTab('policies')">📋 Policies</button>
        <button class="tab" onclick="showTab('people')">👥 People</button>
    </div>
    
    <!-- POLICIES TAB -->
    <div id="policies-tab" class="tab-content active">
        <div class="knowledge-grid">
            {generate_policy_cards(policies) if policies else '<div style="grid-column: 1/-1; text-align: center; padding: 60px; color: #666;"><h3>No policies yet</h3><p>Add your first policy document to get started</p><a href="/knowledge/add-policy" class="btn-primary">+ Add Policy</a></div>'}
        </div>
    </div>
    
    <!-- PEOPLE TAB -->
    <div id="people-tab" class="tab-content">
        <div class="people-grid">
            {generate_people_cards(people) if people else '<div style="grid-column: 1/-1; text-align: center; padding: 60px; color: #666;"><h3>No team members yet</h3></div>'}
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
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html)


def generate_policy_cards(policies: list) -> str:
    """Generate HTML for policy cards."""
    cards = []
    
    for policy in policies:
        tags_html = ' '.join([f'<span class="policy-tag">{tag}</span>' for tag in (policy.get('tags') or [])])
        
        required_badge = '<span style="background: #FFA726; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; margin-left: 8px;">REQUIRED</span>' if policy.get('is_required_reading') else ''
        
        card = f"""
        <div class="policy-card">
            <div class="policy-type">{policy.get('policy_type', 'policy').upper()}</div>
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
                    📄 Open Document
                </a>
                <button onclick="acknowledgePolicy('{policy['id']}')" class="btn-secondary">
                    ✓ Mark as Read
                </button>
            </div>
            <div style="margin-top: 12px; font-size: 12px; color: #999;">
                {f"Owner: {policy.get('owner_name', 'Unknown')}" if policy.get('owner_name') else ''}
                | Added: {str(policy.get('created_at', ''))[:10]}
            </div>
        </div>
        """
        cards.append(card)
    
    return '\n'.join(cards)


def generate_people_cards(people: list) -> str:
    """Generate HTML for people profile cards."""
    cards = []
    
    for person in people:
        initials = ''.join([n[0].upper() for n in person['name'].split()[:2]]) if person.get('name') else '?'
        
        card = f"""
        <div class="person-card">
            <div class="person-avatar">{initials}</div>
            <div class="person-name">{person['name']}</div>
            <div class="person-role">{person.get('title', person.get('role', 'Team Member'))}</div>
            <div style="color: #666; font-size: 13px; margin-bottom: 12px;">
                {person.get('email', '')}
            </div>
            <a href="/knowledge/person/{person['id']}" class="btn-primary" style="font-size: 14px; padding: 8px 16px;">
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

