"""Building Companies Wheel - Portfolio Company Support."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from supabase import create_client
from app.config import settings
from app.api.styles import get_dv_styles
from app.api.sidebar_component import get_admin_sidebar
import httpx
import json
from datetime import datetime, timedelta

router = APIRouter(prefix="/wheels", tags=["Wheels - Building"])


@router.get("/building", response_class=HTMLResponse)
async def building_wheel():
    """Building Companies wheel - Multi-board Kanban: Activities | Dealflow | Financial."""
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Get current user
        people = supabase.table('people').select('*').execute().data
        current_user = next((p for p in people if 'marcus' in p.get('name', '').lower() or 'markus' in p.get('name', '').lower()), None)
        if not current_user:
            current_user = {'name': 'Markus Löwegren', 'email': 'markus.lowegren@disruptiveventures.se', 'linkedin_url': ''}
        
        # ===== FETCH PORTFOLIO COMPANIES =====
        portfolio_companies_result = supabase.table('portfolio_companies') \
            .select('*, organizations(*)') \
            .eq('status', 'active') \
            .execute()
        
        portfolio_companies = []
        portfolio_financial_data = {}
        
        if portfolio_companies_result.data:
            for pc in portfolio_companies_result.data:
                org = pc.get('organizations', {})
                company_name = org.get('name', 'Unknown')
                
                # Calculate financial metrics
                investment_amt = pc.get('investment_amount') or 0
                valuation = pc.get('current_valuation') or 0
                ownership = pc.get('ownership_percentage') or 0
                
                # Estimate ARR from valuation (rough estimate)
                arr_estimate = valuation / 6 if valuation > 0 else 0
                mrr_estimate = arr_estimate / 12 if arr_estimate > 0 else 0
                
                portfolio_companies.append({
                    'id': pc['id'],
                    'organization_id': pc['organization_id'],
                    'name': company_name,
                    'website_url': org.get('website_url'),
                    'logo_url': org.get('logo_url'),
                    'investment_stage': pc.get('investment_stage', 'seed'),
                    'status': pc.get('status', 'active'),
                })
                
                # Store financial data separately for JavaScript
                portfolio_financial_data[pc['id']] = {
                    'name': company_name,
                    'ownership': round(ownership, 1),
                    'invested': round(investment_amt / 1000, 0),  # Convert to tkr
                    'valuation': round(valuation / 1000000, 1),   # Convert to Mkr
                    'mrr': round(mrr_estimate / 1000, 0),          # Estimate in tkr
                    'arr': round(arr_estimate / 1000, 0),          # Estimate in tkr
                }
        
        # Sort by name
        portfolio_companies.sort(key=lambda x: x['name'])
        
        # ===== FETCH TEAM MEMBERS FOR ALL COMPANIES =====
        # Get all people with their organization associations
        people_result = supabase.table('people').select('*').execute()
        
        # Organize people by organization_id
        team_members_by_org = {}
        for person in people_result.data:
            org_id = person.get('primary_organization_id')
            if org_id:
                if org_id not in team_members_by_org:
                    team_members_by_org[org_id] = []
                
                # Get initials
                name = person.get('name', 'Unknown')
                initials = ''.join(word[0].upper() for word in name.split()[:2]) if name else 'UN'
                
                team_members_by_org[org_id].append({
                    'id': person.get('id'),
                    'name': name,
                    'email': person.get('email', ''),
                    'job_title': person.get('job_title', person.get('person_type', 'Team Member')),
                    'linkedin_url': person.get('linkedin_url', ''),
                    'photo_url': person.get('photo_url', ''),
                    'initials': initials,
                    'person_type': person.get('person_type', 'team_member'),
                })
        
        # Add DV team (internal employees)
        dv_team = []
        for person in people_result.data:
            if person.get('person_type') == 'internal' or person.get('email', '').endswith('@disruptiveventures.se'):
                name = person.get('name', 'Unknown')
                initials = ''.join(word[0].upper() for word in name.split()[:2]) if name else 'UN'
                
                dv_team.append({
                    'id': person.get('id'),
                    'name': name,
                    'email': person.get('email', ''),
                    'job_title': person.get('job_title', 'Team Member'),
                    'linkedin_url': person.get('linkedin_url', ''),
                    'photo_url': person.get('photo_url', ''),
                    'initials': initials,
                })
        
        # ===== ACTIVITIES BOARD (Linear Tasks) =====
        linear_tasks = await fetch_linear_tasks()
        
        # Fallback to action_items if Linear fails
        if not linear_tasks:
            db_tasks = supabase.table('action_items').select('*').order('created_at', desc=True).limit(50).execute().data
            linear_tasks = db_tasks
        
        # Organize by status
        activities_columns = {
            'backlog': [t for t in linear_tasks if t.get('status') in ['backlog', 'Backlog']],
            'todo': [t for t in linear_tasks if t.get('status') in ['todo', 'Todo', 'To Do']],
            'in_progress': [t for t in linear_tasks if t.get('status') in ['in_progress', 'In Progress', 'Started']],
            'done': [t for t in linear_tasks if t.get('status') in ['done', 'Done', 'Completed']],
            'canceled': [t for t in linear_tasks if t.get('status') in ['canceled', 'Canceled']],
            'duplicate': [t for t in linear_tasks if t.get('status') in ['duplicate', 'Duplicate']]
        }
        
        # ===== DEALFLOW BOARD (Pipedrive CRM) =====
        # Fetch deals from Pipedrive API (view-only, no database storage)
        pipedrive_deals = await fetch_pipedrive_deals()
        
        dealflow_columns = {
            'lead': [d for d in pipedrive_deals if d.get('stage') == 'lead'],
            'qualified': [d for d in pipedrive_deals if d.get('stage') == 'qualified'],
            'meeting': [d for d in pipedrive_deals if d.get('stage') == 'meeting'],
            'due_diligence': [d for d in pipedrive_deals if d.get('stage') == 'due_diligence'],
            'proposal': [d for d in pipedrive_deals if d.get('stage') == 'proposal'],
            'closed_won': [d for d in pipedrive_deals if d.get('stage') == 'closed_won']
        }
        
        # ===== FINANCIAL BOARD (Fortnox) =====
        # Fetch invoices from Fortnox API (view-only)
        fortnox_invoices = await fetch_fortnox_invoices()
        
        financial_columns = {
            'draft': [i for i in fortnox_invoices if i.get('status') == 'draft'],
            'sent': [i for i in fortnox_invoices if i.get('status') == 'sent'],
            'overdue': [i for i in fortnox_invoices if i.get('status') == 'overdue'],
            'paid': [i for i in fortnox_invoices if i.get('status') == 'paid'],
            'reconciled': [i for i in fortnox_invoices if i.get('status') == 'reconciled']
        }
        
    except Exception as e:
        current_user = {'name': 'Markus Löwegren', 'email': 'markus.lowegren@disruptiveventures.se', 'linkedin_url': ''}
        portfolio_companies = []
        portfolio_financial_data = {}
        team_members_by_org = {}
        dv_team = []
        activities_columns = {'backlog': [], 'todo': [], 'in_progress': [], 'done': [], 'canceled': [], 'duplicate': []}
        dealflow_columns = {'lead': [], 'qualified': [], 'meeting': [], 'due_diligence': [], 'proposal': [], 'closed_won': []}
        financial_columns = {'draft': [], 'sent': [], 'overdue': [], 'paid': [], 'reconciled': []}
        print(f"Error: {e}")
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Building Companies - Admin</title>
    {get_dv_styles()}
    <style>
        /* Override container max-width for Kanban board - needs full width */
        .container {{
            max-width: none;
            padding: 24px 32px;
        }}
        
        .company-selector {{
            margin-bottom: 24px;
            padding: 16px 20px;
            background: white;
            border-radius: 12px;
            border: 1px solid var(--gray-200);
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 24px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }}
        
        .company-selector-left {{
            flex: 1;
            min-width: 0;
            display: flex;
            align-items: center;
            gap: 16px;
        }}
        
        .company-logo-preview {{
            width: 48px;
            height: 48px;
            border-radius: 8px;
            object-fit: contain;
            flex-shrink: 0;
            border: 1px solid var(--gray-200);
            padding: 6px;
            background: white;
            transition: all 0.2s ease;
        }}
        
        .company-logo-preview:hover {{
            border-color: var(--gray-300);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
        }}
        
        .company-info-wrapper {{
            flex: 1;
            min-width: 0;
        }}
        
        .company-selector-label {{
            font-size: 10px;
            font-weight: 600;
            color: var(--gray-500);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
        }}
        
        .company-dropdown {{
            width: 100%;
            max-width: 380px;
            padding: 8px 12px;
            padding-right: 36px;
            border: 1px solid var(--gray-300);
            border-radius: 8px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
            font-size: 14px;
            font-weight: 500;
            background: white;
            cursor: pointer;
            transition: all 0.2s ease;
            appearance: none;
            background-image: url("data:image/svg+xml,%3Csvg width='12' height='8' viewBox='0 0 12 8' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1.5L6 6.5L11 1.5' stroke='%23666' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 12px center;
            background-size: 12px;
            color: var(--gray-900);
            letter-spacing: -0.01em;
        }}
        
        .company-dropdown:hover {{
            border-color: var(--gray-400);
        }}
        
        .company-dropdown:focus {{
            outline: none;
            border-color: var(--gray-900);
            box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.05);
        }}
        
        .company-dropdown option {{
            padding: 10px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
            font-size: 14px;
            font-weight: 400;
        }}
        
        .company-selector-right {{
            display: flex;
            gap: 12px;
            align-items: center;
        }}
        
        .sync-status-wrapper {{
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 4px;
        }}
        
        .sync-status-label {{
            font-size: 10px;
            font-weight: 600;
            color: var(--gray-500);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .company-name {{
            font-size: 16px;
            font-weight: 600;
            color: var(--gray-900);
        }}
        
        .filters {{
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
            align-items: center;
        }}
        
        .filter-btn {{
            padding: 6px 12px;
            background: var(--gray-100);
            border: 1px solid var(--gray-200);
            border-radius: 6px;
            font-size: 12px;
            color: var(--gray-700);
            cursor: pointer;
            transition: all 0.15s;
        }}
        
        .filter-btn:hover {{
            background: var(--gray-200);
        }}
        
        .filter-btn.active {{
            background: var(--gray-900);
            color: white;
            border-color: var(--gray-900);
        }}
        
        .kanban-board {{
            display: flex;
            gap: 16px;
            min-height: calc(100vh - 280px);
            overflow-x: auto;
            padding-bottom: 16px;
            width: 100%;
        }}
        
        .kanban-board.active {{
            display: flex;
        }}
        
        .kanban-column {{
            flex: 1;
            min-width: 320px;
            max-width: 400px;
            background: var(--gray-50);
            border-radius: 8px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            transition: all 0.3s ease;
        }}
        
        /* Expand columns when sidebar is collapsed */
        .sidebar.collapsed ~ .main-content .kanban-column {{
            max-width: 450px;
        }}
        
        .column-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--gray-200);
        }}
        
        .column-title {{
            font-size: 13px;
            font-weight: 600;
            color: var(--gray-700);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .column-count {{
            font-size: 12px;
            color: var(--gray-500);
            background: var(--gray-200);
            padding: 2px 6px;
            border-radius: 4px;
        }}
        
        .kanban-tasks {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        
        .task-card {{
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 6px;
            padding: 12px;
            cursor: pointer;
            transition: all 0.15s;
            user-select: none;
        }}
        
        .task-card:hover {{
            border-color: var(--gray-300);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .task-card:active {{
            opacity: 0.9;
        }}
        
        .task-card.dragging-active {{
            cursor: grabbing;
        }}
        
        .task-card.dragging {{
            opacity: 0.5;
        }}
        
        .task-title {{
            font-size: 13px;
            font-weight: 500;
            color: var(--gray-900);
            margin-bottom: 8px;
            line-height: 1.4;
        }}
        
        .task-meta {{
            display: flex;
            gap: 8px;
            align-items: center;
            flex-wrap: wrap;
            margin-top: 8px;
            font-size: 11px;
            color: var(--gray-500);
        }}
        
        .task-assignee {{
            display: flex;
            align-items: center;
            gap: 4px;
            padding: 2px 6px;
            background: var(--gray-100);
            border-radius: 3px;
            font-size: 11px;
            color: var(--gray-700);
        }}
        
        .task-deadline {{
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 11px;
            color: var(--gray-600);
        }}
        
        .sync-status {{
            font-size: 11px;
            color: var(--gray-500);
            padding: 4px 8px;
            background: var(--gray-100);
            border-radius: 4px;
        }}
        
        /* Timeline View (Asana-style) */
        .timeline-view {{
            display: none;
            padding: 24px 0;
        }}
        
        .timeline-view.active {{
            display: block;
        }}
        
        .timeline-header {{
            display: grid;
            grid-template-columns: 200px 1fr;
            gap: 16px;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--gray-200);
        }}
        
        .timeline-months {{
            display: flex;
            gap: 8px;
            overflow-x: auto;
        }}
        
        .timeline-month {{
            flex: 1;
            min-width: 120px;
            text-align: center;
            font-size: 12px;
            font-weight: 500;
            color: var(--gray-700);
            padding: 8px;
        }}
        
        .timeline-tasks {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        
        .timeline-task {{
            display: grid;
            grid-template-columns: 200px 1fr;
            gap: 16px;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid var(--gray-100);
        }}
        
        .timeline-task-info {{
            font-size: 13px;
            color: var(--gray-900);
        }}
        
        .timeline-task-name {{
            font-weight: 500;
            margin-bottom: 4px;
        }}
        
        .timeline-task-meta {{
            font-size: 11px;
            color: var(--gray-500);
        }}
        
        .timeline-bar-container {{
            position: relative;
            height: 32px;
            background: var(--gray-50);
            border-radius: 4px;
        }}
        
        .timeline-bar {{
            position: absolute;
            height: 100%;
            background: var(--gray-900);
            border-radius: 4px;
            display: flex;
            align-items: center;
            padding: 0 8px;
            font-size: 11px;
            color: white;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.15s;
        }}
        
        .timeline-bar:hover {{
            background: var(--gray-700);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .view-switcher {{
            display: flex;
            gap: 4px;
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 6px;
            padding: 4px;
        }}
        
        .view-switcher-btn {{
            padding: 6px 12px;
            background: transparent;
            border: none;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
            color: var(--gray-600);
            cursor: pointer;
            transition: all 0.15s;
        }}
        
        .view-switcher-btn:hover {{
            background: var(--gray-100);
            color: var(--gray-900);
        }}
        
        .view-switcher-btn.active {{
            background: var(--gray-100);
            color: var(--gray-900);
        }}
        
        /* Tab buttons for board types */
        .tab-btn {{
            padding: 8px 20px;
            background: transparent;
            border: none;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
            color: var(--gray-600);
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .tab-btn:hover {{
            background: var(--gray-50);
            color: var(--gray-900);
        }}
        
        .tab-btn.active {{
            background: var(--gray-900);
            color: white;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        /* KPI Dashboard Styles */
        .kpi-card {{
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 8px;
            padding: 20px;
            transition: all 0.15s;
        }}
        
        .kpi-card:hover {{
            border-color: var(--gray-300);
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        
        .team-member-card {{
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 12px;
            padding: 20px;
            transition: all 0.2s ease;
        }}
        
        .team-member-card:hover {{
            border-color: var(--gray-300);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }}
        
        .profile-avatar {{
            width: 56px;
            height: 56px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            font-weight: 600;
            flex-shrink: 0;
        }}
        
        .kpi-label {{
            font-size: 12px;
            color: var(--gray-600);
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 500;
        }}
        
        .kpi-value {{
            font-size: 32px;
            font-weight: 700;
            color: var(--gray-900);
            margin-bottom: 8px;
            line-height: 1;
        }}
        
        .kpi-change {{
            font-size: 13px;
            font-weight: 500;
        }}
        
        .kpi-change.positive {{
            color: #16a34a;
        }}
        
        .kpi-change.negative {{
            color: #dc2626;
        }}
        
        .kpi-change.neutral {{
            color: var(--gray-600);
        }}
        
        .kpi-section {{
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 8px;
            padding: 20px;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 6px;
            background: var(--gray-100);
            border-radius: 3px;
            overflow: hidden;
        }}
        
        .progress-fill {{
            height: 100%;
            background: var(--gray-900);
            border-radius: 3px;
        }}
        
        .customer-row, .invoice-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            background: var(--gray-50);
            border-radius: 6px;
            transition: all 0.15s;
        }}
        
        .customer-row:hover, .invoice-row:hover {{
            background: var(--gray-100);
        }}
        
        /* Dark mode KPI styles */
        body.dark-mode .kpi-card,
        body.dark-mode .kpi-section,
        body.dark-mode .team-member-card {{
            background: #2a2a2a;
            border-color: #404040;
        }}
        
        body.dark-mode .kpi-label {{
            color: #999999;
        }}
        
        body.dark-mode .kpi-value {{
            color: #e5e5e5;
        }}
        
        body.dark-mode .progress-bar {{
            background: #404040;
        }}
        
        body.dark-mode .progress-fill {{
            background: #e5e5e5;
        }}
        
        body.dark-mode .customer-row,
        body.dark-mode .invoice-row {{
            background: #333333;
        }}
        
        body.dark-mode .customer-row:hover,
        body.dark-mode .invoice-row:hover {{
            background: #404040;
        }}
        
        /* Right Panel (Linear-style task detail) */
        .task-panel {{
            position: fixed;
            top: 0;
            right: -500px;
            width: 500px;
            height: 100vh;
            background: white;
            border-left: 1px solid var(--gray-200);
            box-shadow: -2px 0 8px rgba(0,0,0,0.1);
            z-index: 2000;
            transition: right 0.3s ease;
            overflow-y: auto;
        }}
        
        .task-panel.open {{
            right: 0;
        }}
        
        .task-panel-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100vh;
            background: rgba(0,0,0,0.3);
            z-index: 1999;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
        }}
        
        .task-panel-overlay.open {{
            opacity: 1;
            pointer-events: all;
        }}
        
        .task-panel-header {{
            padding: 20px;
            border-bottom: 1px solid var(--gray-200);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .task-panel-close {{
            padding: 8px;
            background: transparent;
            border: none;
            cursor: pointer;
            color: var(--gray-600);
            font-size: 20px;
        }}
        
        .task-panel-close:hover {{
            background: var(--gray-100);
            border-radius: 4px;
        }}
        
        .task-panel-body {{
            padding: 20px;
        }}
        
        .task-field {{
            margin-bottom: 24px;
        }}
        
        .task-field-label {{
            font-size: 12px;
            font-weight: 600;
            color: var(--gray-700);
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .task-field input,
        .task-field textarea,
        .task-field select {{
            width: 100%;
            padding: 10px;
            border: 1px solid var(--gray-200);
            border-radius: 6px;
            font-size: 14px;
            color: var(--gray-900);
            background: white;
            font-family: inherit;
        }}
        
        .task-field input:focus,
        .task-field textarea:focus,
        .task-field select:focus {{
            outline: none;
            border-color: var(--gray-400);
        }}
        
        .task-field textarea {{
            min-height: 100px;
            resize: vertical;
        }}
        
        .task-actions {{
            display: flex;
            gap: 12px;
            padding: 24px;
            border-top: 1px solid var(--gray-200);
            position: sticky;
            bottom: 0;
            background: white;
        }}
        
        .task-save-btn {{
            flex: 1;
            padding: 12px 24px;
            background: var(--gray-900);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            font-family: inherit;
        }}
        
        .task-save-btn:hover {{
            background: var(--gray-700);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .task-save-btn:active {{
            transform: translateY(0);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .task-save-btn:disabled {{
            background: var(--gray-300);
            cursor: not-allowed;
            transform: none;
        }}
        
        .task-cancel-btn {{
            flex: 1;
            padding: 12px 24px;
            background: white;
            color: var(--gray-700);
            border: 1.5px solid var(--gray-300);
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            font-family: inherit;
        }}
        
        .task-cancel-btn:hover {{
            background: var(--gray-50);
            border-color: var(--gray-400);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }}
        
        .task-cancel-btn:active {{
            transform: translateY(0);
            background: var(--gray-100);
        }}
        
        /* Dark mode panel */
        body.dark-mode .task-panel {{
            background: #2a2a2a;
            border-left-color: #404040;
        }}
        
        body.dark-mode .task-panel-header {{
            border-bottom-color: #404040;
        }}
        
        body.dark-mode .task-panel-close {{
            color: #999999;
        }}
        
        body.dark-mode .task-panel-close:hover {{
            background: #333333;
        }}
        
        body.dark-mode .task-field-label {{
            color: #cccccc;
        }}
        
        body.dark-mode .task-field input,
        body.dark-mode .task-field textarea,
        body.dark-mode .task-field select {{
            background: #333333;
            border-color: #404040;
            color: #e5e5e5;
        }}
        
        body.dark-mode .task-actions {{
            background: #2a2a2a;
            border-top-color: #404040;
        }}
        
        body.dark-mode .task-save-btn {{
            background: #e5e5e5;
            color: #1a1a1a;
        }}
        
        body.dark-mode .task-save-btn:hover {{
            background: #ffffff;
            box-shadow: 0 4px 12px rgba(255,255,255,0.15);
        }}
        
        body.dark-mode .task-cancel-btn {{
            background: #2a2a2a;
            color: #cccccc;
            border-color: #4a4a4a;
        }}
        
        body.dark-mode .task-cancel-btn:hover {{
            background: #333333;
            border-color: #555555;
        }}
        
        /* Dark mode tabs */
        body.dark-mode .tab-btn {{
            color: #999999;
        }}
        
        body.dark-mode .tab-btn:hover {{
            background: #333333;
            color: #e5e5e5;
        }}
        
        body.dark-mode .tab-btn.active {{
            background: #e5e5e5;
            color: #1a1a1a;
        }}
        
        .task-priority {{
            padding: 2px 6px;
            background: var(--gray-100);
            border-radius: 3px;
            font-size: 10px;
            font-weight: 500;
            color: var(--gray-700);
        }}
        
        /* Markdown preview styling */
        #description-preview {{
            word-wrap: break-word;
        }}
        
        #description-preview strong {{
            font-weight: 600;
            color: var(--gray-900);
        }}
        
        #description-preview em {{
            font-style: italic;
        }}
        
        #description-preview a {{
            color: #2563eb;
            text-decoration: underline;
        }}
        
        #description-preview a:hover {{
            color: #1d4ed8;
        }}
        
        /* Dark mode kanban */
        body.dark-mode .company-selector {{
            background: #1a1a1a;
            border-color: #333;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
        }}
        
        body.dark-mode .company-selector-label {{
            color: #888;
        }}
        
        body.dark-mode .company-logo-preview {{
            border-color: #333;
            background: #1a1a1a;
        }}
        
        body.dark-mode .company-logo-preview:hover {{
            border-color: #444;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }}
        }}
        
        body.dark-mode .company-dropdown {{
            background: #1a1a1a;
            border-color: #404040;
            color: #cccccc;
            background-image: url("data:image/svg+xml,%3Csvg width='12' height='8' viewBox='0 0 12 8' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1.5L6 6.5L11 1.5' stroke='%23999' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
        }}
        
        body.dark-mode .company-dropdown:hover {{
            border-color: #666;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
        }}
        
        body.dark-mode .company-dropdown:focus {{
            border-color: #888;
            box-shadow: 0 0 0 4px rgba(255, 255, 255, 0.08), 0 2px 8px rgba(0, 0, 0, 0.5);
        }}
        
        body.dark-mode .company-dropdown option {{
            background: #1a1a1a;
            color: #e5e5e5;
        }}
        
        body.dark-mode .sync-status-label {{
            color: #666;
        }}

        body.dark-mode .company-name {{
            color: #e5e5e5;
        }}
        
        body.dark-mode .kanban-column {{
            background: #2a2a2a;
        }}
        
        body.dark-mode .column-header {{
            border-bottom-color: #404040;
        }}
        
        body.dark-mode .column-title {{
            color: #cccccc;
        }}
        
        body.dark-mode .column-count {{
            background: #404040;
            color: #999999;
        }}
        
        body.dark-mode .task-card {{
            background: #333333;
            border-color: #4a4a4a;
        }}
        
        body.dark-mode .task-card:hover {{
            border-color: #555555;
            box-shadow: 0 2px 4px rgba(255,255,255,0.05);
        }}
        
        body.dark-mode .task-title {{
            color: #e5e5e5;
        }}
        
        body.dark-mode .task-meta {{
            color: #999999;
        }}
        
        body.dark-mode .task-assignee,
        body.dark-mode .task-priority {{
            background: #404040;
            color: #cccccc;
        }}
        
        @media (max-width: 1200px) {{
            .kanban-board {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
        
        @media (max-width: 768px) {{
            .kanban-board {{
                grid-template-columns: 1fr;
            }}
            
            .company-selector {{
                flex-direction: column;
                gap: 16px;
                padding: 16px;
                align-items: stretch;
            }}
            
            .company-selector-left {{
                width: 100%;
                flex-direction: row;
            }}
            
            .company-logo-preview {{
                width: 40px;
                height: 40px;
            }}
            
            .company-dropdown {{
                max-width: none;
            }}
            
            .company-selector-right {{
                width: 100%;
                justify-content: space-between;
            }}
            
            .sync-status-wrapper {{
                align-items: flex-start;
            }}
        }}
    </style>
</head>
<body>
    {get_admin_sidebar('building', current_user.get('name', 'Admin User'), current_user.get('email', ''), current_user.get('linkedin_url', ''))}
    
    <div class="main-content">
        <div class="page-header">
            <div class="page-header-left">
                <h1 class="page-title">Building Companies</h1>
                <p class="page-description">Activity tracking and compliance management</p>
            </div>
        </div>
        
        <div class="container">
            <!-- Company Selector & Filters -->
            <div class="company-selector">
                <div class="company-selector-left">
                    <img id="company-logo-preview" class="company-logo-preview" src="/static/dv-logo.png" alt="Company Logo">
                    <div class="company-info-wrapper">
                        <div class="company-selector-label">
                            SELECT PORTFOLIO COMPANY
                        </div>
                        <select id="company-selector" class="company-dropdown" onchange="switchCompany(this.value)">
                            <option value="dv" data-logo="/static/dv-logo.png" selected>Disruptive Ventures</option>
                            {''.join([f'<option value="{pc["id"]}" data-logo="{pc.get("logo_url", "")}">{pc["name"]}</option>' for pc in portfolio_companies])}
                        </select>
                    </div>
                </div>
                <div class="company-selector-right">
                    <div class="sync-status-wrapper">
                        <span class="sync-status-label">STATUS</span>
                        <span id="sync-status" class="sync-status" style="font-size: 13px; font-weight: 600;">Last synced: 01:07:14</span>
                    </div>
                    <button onclick="syncLinear()" class="btn-primary" style="padding: 10px 20px; font-size: 14px; font-weight: 600;">
                        Sync Now
                    </button>
                </div>
            </div>
            
            <!-- Tabs: Activities | Dealflow | Financial | Team -->
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
                <div style="display: flex; gap: 4px; background: white; border: 1px solid var(--gray-200); border-radius: 8px; padding: 4px;">
                    <button class="tab-btn active" onclick="switchTab('activities')">Activities</button>
                    <button class="tab-btn" onclick="switchTab('dealflow')">Dealflow</button>
                    <button class="tab-btn" onclick="switchTab('financial')">Financial</button>
                    <button class="tab-btn" onclick="switchTab('team')">Team</button>
                </div>
                
                <div id="task-filters" class="filters">
                    <button class="filter-btn active" onclick="filterBy('all')">All</button>
                    <button class="filter-btn" onclick="filterBy('mine')">My Tasks</button>
                    <button class="filter-btn" onclick="filterBy('high')">High Priority</button>
                    <button class="filter-btn" onclick="filterBy('overdue')">Overdue</button>
                </div>
            </div>
            
            <!-- Activities Tab Content -->
            <div id="activities-tab" class="tab-content active">
                <div style="margin-bottom: 16px;">
                    <h2 id="activities-header" style="font-size: 20px; font-weight: 600; color: var(--gray-900); margin-bottom: 4px;">Activities</h2>
                    <p id="activities-subtitle" style="font-size: 14px; color: var(--gray-600);">Linear tasks and action items</p>
                </div>
                <!-- Kanban Board View -->
                <div class="kanban-board active" id="kanban-view">
                <!-- Backlog -->
                <div class="kanban-column" data-status="backlog" ondrop="drop(event)" ondragover="allowDrop(event)">
                    <div class="column-header">
                        <div class="column-title">Backlog</div>
                        <div class="column-count">{len(activities_columns['backlog'])}</div>
                    </div>
                    <div class="kanban-tasks" id="backlog">
                        {generate_task_cards(activities_columns['backlog'])}
                    </div>
                </div>
                
                <!-- To Do -->
                <div class="kanban-column" data-status="todo" ondrop="drop(event)" ondragover="allowDrop(event)">
                    <div class="column-header">
                        <div class="column-title">To Do</div>
                        <div class="column-count">{len(activities_columns['todo'])}</div>
                    </div>
                    <div class="kanban-tasks" id="todo">
                        {generate_task_cards(activities_columns['todo'])}
                    </div>
                </div>
                
                <!-- In Progress -->
                <div class="kanban-column" data-status="in_progress" ondrop="drop(event)" ondragover="allowDrop(event)">
                    <div class="column-header">
                        <div class="column-title">In Progress</div>
                        <div class="column-count">{len(activities_columns['in_progress'])}</div>
                    </div>
                    <div class="kanban-tasks" id="in_progress">
                        {generate_task_cards(activities_columns['in_progress'])}
                    </div>
                </div>
                
                <!-- Done -->
                <div class="kanban-column" data-status="done" ondrop="drop(event)" ondragover="allowDrop(event)">
                    <div class="column-header">
                        <div class="column-title">Done</div>
                        <div class="column-count">{len(activities_columns['done'])}</div>
                    </div>
                    <div class="kanban-tasks" id="done">
                        {generate_task_cards(activities_columns['done'])}
                    </div>
                </div>
                
                <!-- Canceled -->
                <div class="kanban-column" data-status="canceled" ondrop="drop(event)" ondragover="allowDrop(event)" style="opacity: 0.7;">
                    <div class="column-header">
                        <div class="column-title">Canceled</div>
                        <div class="column-count">{len(activities_columns.get('canceled', []))}</div>
                    </div>
                    <div class="kanban-tasks" id="canceled">
                        {generate_task_cards(activities_columns.get('canceled', []))}
                    </div>
                </div>
            </div>
            
            <!-- Timeline View (Asana-style) - Will be populated -->
            <div class="timeline-view" id="timeline-view" style="display: none;">
                <div style="padding: 48px; text-align: center; background: white; border: 1px solid var(--gray-200); border-radius: 8px; margin: 24px;">
                    <h3 style="font-size: 18px; font-weight: 600; color: var(--gray-900); margin-bottom: 12px;">Timeline View</h3>
                    <p style="color: var(--gray-600); font-size: 14px; margin-bottom: 16px;">
                        Gantt-style timeline view coming soon. Tasks will be displayed on a calendar timeline with dependencies.
                    </p>
                    <button class="view-switcher-btn active" onclick="switchView('kanban', this)" style="margin-top: 16px;">
                        ← Back to Board View
                    </button>
                </div>
            </div>
            </div>
            <!-- End Activities Tab -->
            
            <!-- Dealflow Tab Content (CRM Pipeline) -->
            <div id="dealflow-tab" class="tab-content">
                <div style="margin-bottom: 16px;">
                    <h2 id="dealflow-header" style="font-size: 20px; font-weight: 600; color: var(--gray-900); margin-bottom: 4px;">Dealflow</h2>
                    <p id="dealflow-subtitle" style="font-size: 14px; color: var(--gray-600);">Investment pipeline and opportunities</p>
                </div>
                <div class="kanban-board active">
                    <!-- Lead -->
                    <div class="kanban-column" data-status="lead">
                        <div class="column-header">
                            <div class="column-title">Lead</div>
                            <div class="column-count">{len(dealflow_columns['lead'])}</div>
                        </div>
                        <div class="kanban-tasks">
                            {''.join([f'''
                            <div class="task-card" data-deal-id="{deal.get('id')}">
                                <div class="task-title" style="font-size: 14px; font-weight: 600; margin-bottom: 8px;">{deal.get('title', 'Untitled')}</div>
                                <div style="font-size: 12px; color: var(--gray-600); margin-bottom: 8px;">{deal.get('organization', 'No org')}</div>
                                <div class="task-meta">
                                    <span style="font-size: 11px; color: var(--gray-500);">{deal.get('value', 0):,.0f} {deal.get('currency', 'SEK')}</span>
                                </div>
                            </div>
                            ''' for deal in dealflow_columns['lead']]) if dealflow_columns['lead'] else '<div style="text-align: center; padding: 24px; color: var(--gray-500); font-size: 12px;">No deals</div>'}
                        </div>
                    </div>
                    
                    <!-- Qualified -->
                    <div class="kanban-column" data-status="qualified">
                        <div class="column-header">
                            <div class="column-title">Qualified</div>
                            <div class="column-count">{len(dealflow_columns['qualified'])}</div>
                        </div>
                        <div class="kanban-tasks">
                            {''.join([f'''
                            <div class="task-card" data-deal-id="{deal.get('id')}">
                                <div class="task-title" style="font-size: 14px; font-weight: 600; margin-bottom: 8px;">{deal.get('title', 'Untitled')}</div>
                                <div style="font-size: 12px; color: var(--gray-600); margin-bottom: 8px;">{deal.get('organization', 'No org')}</div>
                                <div class="task-meta">
                                    <span style="font-size: 11px; color: var(--gray-500);">{deal.get('value', 0):,.0f} {deal.get('currency', 'SEK')}</span>
                                </div>
                            </div>
                            ''' for deal in dealflow_columns['qualified']]) if dealflow_columns['qualified'] else '<div style="text-align: center; padding: 24px; color: var(--gray-500); font-size: 12px;">No deals</div>'}
                        </div>
                    </div>
                    
                    <!-- Meeting -->
                    <div class="kanban-column" data-status="meeting">
                        <div class="column-header">
                            <div class="column-title">Meeting</div>
                            <div class="column-count">{len(dealflow_columns['meeting'])}</div>
                        </div>
                        <div class="kanban-tasks">
                            {''.join([f'''
                            <div class="task-card" data-deal-id="{deal.get('id')}">
                                <div class="task-title" style="font-size: 14px; font-weight: 600; margin-bottom: 8px;">{deal.get('title', 'Untitled')}</div>
                                <div style="font-size: 12px; color: var(--gray-600); margin-bottom: 8px;">{deal.get('organization', 'No org')}</div>
                                <div class="task-meta">
                                    <span style="font-size: 11px; color: var(--gray-500);">{deal.get('value', 0):,.0f} {deal.get('currency', 'SEK')}</span>
                                </div>
                            </div>
                            ''' for deal in dealflow_columns['meeting']]) if dealflow_columns['meeting'] else '<div style="text-align: center; padding: 24px; color: var(--gray-500); font-size: 12px;">No deals</div>'}
                        </div>
                    </div>
                    
                    <!-- Due Diligence -->
                    <div class="kanban-column" data-status="due-diligence">
                        <div class="column-header">
                            <div class="column-title">Due Diligence</div>
                            <div class="column-count">{len(dealflow_columns['due_diligence'])}</div>
                        </div>
                        <div class="kanban-tasks">
                            {''.join([f'''
                            <div class="task-card" data-deal-id="{deal.get('id')}">
                                <div class="task-title" style="font-size: 14px; font-weight: 600; margin-bottom: 8px;">{deal.get('title', 'Untitled')}</div>
                                <div style="font-size: 12px; color: var(--gray-600); margin-bottom: 8px;">{deal.get('organization', 'No org')}</div>
                                <div class="task-meta">
                                    <span style="font-size: 11px; color: var(--gray-500);">{deal.get('value', 0):,.0f} {deal.get('currency', 'SEK')}</span>
                                </div>
                            </div>
                            ''' for deal in dealflow_columns['due_diligence']]) if dealflow_columns['due_diligence'] else '<div style="text-align: center; padding: 24px; color: var(--gray-500); font-size: 12px;">No deals</div>'}
                        </div>
                    </div>
                    
                    <!-- Proposal -->
                    <div class="kanban-column" data-status="proposal">
                        <div class="column-header">
                            <div class="column-title">Proposal</div>
                            <div class="column-count">{len(dealflow_columns['proposal'])}</div>
                        </div>
                        <div class="kanban-tasks">
                            {''.join([f'''
                            <div class="task-card" data-deal-id="{deal.get('id')}">
                                <div class="task-title" style="font-size: 14px; font-weight: 600; margin-bottom: 8px;">{deal.get('title', 'Untitled')}</div>
                                <div style="font-size: 12px; color: var(--gray-600); margin-bottom: 8px;">{deal.get('organization', 'No org')}</div>
                                <div class="task-meta">
                                    <span style="font-size: 11px; color: var(--gray-500);">{deal.get('value', 0):,.0f} {deal.get('currency', 'SEK')}</span>
                                </div>
                            </div>
                            ''' for deal in dealflow_columns['proposal']]) if dealflow_columns['proposal'] else '<div style="text-align: center; padding: 24px; color: var(--gray-500); font-size: 12px;">No deals</div>'}
                        </div>
                    </div>
                    
                    <!-- Closed Won -->
                    <div class="kanban-column" data-status="closed-won" style="opacity: 1;">
                        <div class="column-header">
                            <div class="column-title">Closed Won</div>
                            <div class="column-count">{len(dealflow_columns['closed_won'])}</div>
                        </div>
                        <div class="kanban-tasks">
                            {''.join([f'''
                            <div class="task-card" data-deal-id="{deal.get('id')}">
                                <div class="task-title" style="font-size: 14px; font-weight: 600; margin-bottom: 8px;">{deal.get('title', 'Untitled')}</div>
                                <div style="font-size: 12px; color: var(--gray-600); margin-bottom: 8px;">{deal.get('organization', 'No org')}</div>
                                <div class="task-meta">
                                    <span style="font-size: 11px; color: var(--gray-500);">{deal.get('value', 0):,.0f} {deal.get('currency', 'SEK')}</span>
                                </div>
                            </div>
                            ''' for deal in dealflow_columns['closed_won']]) if dealflow_columns['closed_won'] else '<div style="text-align: center; padding: 24px; color: var(--gray-500); font-size: 12px;">No deals</div>'}
                        </div>
                    </div>
                </div>
            </div>
            <!-- End Dealflow Tab -->
            
            <!-- Financial Tab Content (KPI Dashboard from Fortnox) -->
            <div id="financial-tab" class="tab-content">
                <div style="margin-bottom: 24px;">
                    <h2 id="financial-header" style="font-size: 20px; font-weight: 600; color: var(--gray-900); margin-bottom: 4px;">Financial Metrics</h2>
                    <p id="financial-subtitle" style="font-size: 14px; color: var(--gray-600);">Q3 2025 financial metrics</p>
                </div>
                <!-- Key Metrics Grid -->
                <div id="financial-metrics-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 24px;">
                    <!-- Metrics will be populated by JavaScript -->
                    <div class="kpi-card" style="grid-column: 1 / -1; text-align: center; padding: 40px;">
                        <p style="font-size: 14px; color: var(--gray-600);">Loading financial data...</p>
                    </div>
                </div>
                
                <!-- Revenue & Expenses Chart Area -->
                <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 16px; margin-bottom: 24px;">
                    <!-- Revenue Breakdown -->
                    <div class="kpi-section">
                        <h3 style="font-size: 16px; font-weight: 600; margin-bottom: 16px; color: var(--gray-900);">Revenue Breakdown</h3>
                        <div style="display: flex; flex-direction: column; gap: 12px;">
                            <div class="revenue-item">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                                    <span style="font-size: 13px; color: var(--gray-700);">Subscription Revenue</span>
                                    <span style="font-size: 13px; font-weight: 600; color: var(--gray-900);">1.8M kr</span>
                                </div>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: 75%;"></div>
                                </div>
                            </div>
                            <div class="revenue-item">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                                    <span style="font-size: 13px; color: var(--gray-700);">Professional Services</span>
                                    <span style="font-size: 13px; font-weight: 600; color: var(--gray-900);">480k kr</span>
                                </div>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: 20%;"></div>
                                </div>
                            </div>
                            <div class="revenue-item">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                                    <span style="font-size: 13px; color: var(--gray-700);">One-time Sales</span>
                                    <span style="font-size: 13px; font-weight: 600; color: var(--gray-900);">120k kr</span>
                                </div>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: 5%;"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Key Ratios -->
                    <div class="kpi-section">
                        <h3 style="font-size: 16px; font-weight: 600; margin-bottom: 16px; color: var(--gray-900);">Key Ratios</h3>
                        <div style="display: flex; flex-direction: column; gap: 12px;">
                            <div class="ratio-item">
                                <div style="font-size: 12px; color: var(--gray-600); margin-bottom: 4px;">Gross Margin</div>
                                <div style="font-size: 20px; font-weight: 600; color: var(--gray-900);">72%</div>
                            </div>
                            <div class="ratio-item">
                                <div style="font-size: 12px; color: var(--gray-600); margin-bottom: 4px;">EBITDA Margin</div>
                                <div style="font-size: 20px; font-weight: 600; color: var(--gray-900);">-15%</div>
                            </div>
                            <div class="ratio-item">
                                <div style="font-size: 12px; color: var(--gray-600); margin-bottom: 4px;">LTV/CAC</div>
                                <div style="font-size: 20px; font-weight: 600; color: var(--gray-900);">3.2x</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Top Customers & Recent Invoices -->
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                    <!-- Top Customers -->
                    <div class="kpi-section">
                        <h3 style="font-size: 16px; font-weight: 600; margin-bottom: 16px; color: var(--gray-900);">Top Customers (Last 30 Days)</h3>
                        <div style="display: flex; flex-direction: column; gap: 8px;">
                            <div class="customer-row">
                                <div style="flex: 1;">
                                    <div style="font-size: 13px; font-weight: 500; color: var(--gray-900);">Volvo Group</div>
                                    <div style="font-size: 11px; color: var(--gray-500);">3 invoices</div>
                                </div>
                                <div style="font-size: 14px; font-weight: 600; color: var(--gray-900);">485k kr</div>
                            </div>
                            <div class="customer-row">
                                <div style="flex: 1;">
                                    <div style="font-size: 13px; font-weight: 500; color: var(--gray-900);">Ericsson AB</div>
                                    <div style="font-size: 11px; color: var(--gray-500);">2 invoices</div>
                                </div>
                                <div style="font-size: 14px; font-weight: 600; color: var(--gray-900);">320k kr</div>
                            </div>
                            <div class="customer-row">
                                <div style="flex: 1;">
                                    <div style="font-size: 13px; font-weight: 500; color: var(--gray-900);">Atlas Copco</div>
                                    <div style="font-size: 11px; color: var(--gray-500);">4 invoices</div>
                                </div>
                                <div style="font-size: 14px; font-weight: 600; color: var(--gray-900);">285k kr</div>
                            </div>
                            <div class="customer-row">
                                <div style="flex: 1;">
                                    <div style="font-size: 13px; font-weight: 500; color: var(--gray-900);">IKEA Components</div>
                                    <div style="font-size: 11px; color: var(--gray-500);">2 invoices</div>
                                </div>
                                <div style="font-size: 14px; font-weight: 600; color: var(--gray-900);">240k kr</div>
                            </div>
                            <div class="customer-row">
                                <div style="flex: 1;">
                                    <div style="font-size: 13px; font-weight: 500; color: var(--gray-900);">Scania AB</div>
                                    <div style="font-size: 11px; color: var(--gray-500);">1 invoice</div>
                                </div>
                                <div style="font-size: 14px; font-weight: 600; color: var(--gray-900);">195k kr</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Recent Large Invoices -->
                    <div class="kpi-section">
                        <h3 style="font-size: 16px; font-weight: 600; margin-bottom: 16px; color: var(--gray-900);">Recent Large Invoices</h3>
                        <div style="display: flex; flex-direction: column; gap: 8px;">
                            <div class="invoice-row">
                                <div style="flex: 1;">
                                    <div style="font-size: 13px; font-weight: 500; color: var(--gray-900);">#2024-1247</div>
                                    <div style="font-size: 11px; color: var(--gray-500);">Volvo Group • Due Dec 30</div>
                                </div>
                                <div>
                                    <div style="font-size: 14px; font-weight: 600; color: var(--gray-900); text-align: right;">285k kr</div>
                                    <div style="font-size: 10px; color: #16a34a; text-align: right;">Paid</div>
                                </div>
                            </div>
                            <div class="invoice-row">
                                <div style="flex: 1;">
                                    <div style="font-size: 13px; font-weight: 500; color: var(--gray-900);">#2024-1246</div>
                                    <div style="font-size: 11px; color: var(--gray-500);">Ericsson AB • Due Dec 28</div>
                                </div>
                                <div>
                                    <div style="font-size: 14px; font-weight: 600; color: var(--gray-900); text-align: right;">240k kr</div>
                                    <div style="font-size: 10px; color: #2563eb; text-align: right;">Sent</div>
                                </div>
                            </div>
                            <div class="invoice-row">
                                <div style="flex: 1;">
                                    <div style="font-size: 13px; font-weight: 500; color: var(--gray-900);">#2024-1245</div>
                                    <div style="font-size: 11px; color: var(--gray-500);">Atlas Copco • Due Dec 15</div>
                                </div>
                                <div>
                                    <div style="font-size: 14px; font-weight: 600; color: var(--gray-900); text-align: right;">195k kr</div>
                                    <div style="font-size: 10px; color: #dc2626; text-align: right;">Overdue</div>
                                </div>
                            </div>
                            <div class="invoice-row">
                                <div style="flex: 1;">
                                    <div style="font-size: 13px; font-weight: 500; color: var(--gray-900);">#2024-1244</div>
                                    <div style="font-size: 11px; color: var(--gray-500);">IKEA Components • Due Dec 31</div>
                                </div>
                                <div>
                                    <div style="font-size: 14px; font-weight: 600; color: var(--gray-900); text-align: right;">150k kr</div>
                                    <div style="font-size: 10px; color: #16a34a; text-align: right;">Paid</div>
                                </div>
                            </div>
                            <div class="invoice-row">
                                <div style="flex: 1;">
                                    <div style="font-size: 13px; font-weight: 500; color: var(--gray-900);">#2024-1243</div>
                                    <div style="font-size: 11px; color: var(--gray-500);">Scania AB • Due Jan 5</div>
                                </div>
                                <div>
                                    <div style="font-size: 14px; font-weight: 600; color: var(--gray-900); text-align: right;">125k kr</div>
                                    <div style="font-size: 10px; color: var(--gray-500); text-align: right;">Draft</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Data Source Note -->
                <div style="margin-top: 24px; padding: 12px; background: var(--blue-50); border: 1px solid #dbeafe; border-radius: 8px; font-size: 12px; color: var(--gray-600);">
                    📊 Financial data from Fortnox API • Last synced: Just now • 
                    <a href="https://apps.fortnox.se" target="_blank" style="color: #2563eb; text-decoration: underline;">Open Fortnox →</a>
                </div>
            </div>
            <!-- End Financial Tab -->
            
            <!-- Team Tab -->
            <div id="team-tab" class="tab-content" style="display: none;">
                <div style="margin-bottom: 24px;">
                    <h2 style="font-size: 20px; font-weight: 600; margin-bottom: 8px; color: var(--gray-900);">Team Members</h2>
                    <p style="font-size: 14px; color: var(--gray-600);" id="team-subtitle">View and manage team profiles for the selected company</p>
                </div>
                
                <!-- Team Members Grid (will be populated by JavaScript) -->
                <div id="team-members-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; margin-bottom: 24px;">
                    <!-- Team members loaded dynamically -->
                </div>
                
                <!-- Add Team Member Button -->
                <div style="margin-top: 24px;">
                    <button class="btn-secondary" style="padding: 10px 20px;">
                        + Add Team Member
                    </button>
                </div>
                
                <!-- Data Source Note -->
                <div style="margin-top: 24px; padding: 12px; background: var(--purple-50); border: 1px solid #e9d5ff; border-radius: 8px; font-size: 12px; color: var(--gray-600);">
                    👥 Team data from internal database • Synced with LinkedIn profiles •
                    <a href="/wheels/people" style="color: #9333ea; text-decoration: underline;">Manage People →</a>
                </div>
            </div>
            <!-- End Team Tab -->
            
        </div>
    </div>
    
    <!-- Task Detail Panel (Right Sidebar) -->
    <div id="task-panel-overlay" class="task-panel-overlay" onclick="closeTaskPanel()"></div>
    
    <div id="task-panel" class="task-panel">
        <div class="task-panel-header">
            <h3 id="task-id-display" style="font-size: 16px; font-weight: 600; color: var(--gray-900); margin: 0;">Task Details</h3>
            <button class="task-panel-close" onclick="closeTaskPanel()">×</button>
        </div>
        
        <div class="task-panel-body">
            <!-- Title -->
            <div class="task-field">
                <div class="task-field-label">Title</div>
                <input type="text" id="edit-title" placeholder="Task title">
            </div>
            
            <!-- Description -->
            <div class="task-field">
                <div class="task-field-label">Description</div>
                <textarea id="edit-description" placeholder="Add description..." oninput="updateDescriptionPreview()"></textarea>
                <div id="description-preview" style="margin-top: 8px; padding: 10px; background: var(--gray-50); border-radius: 6px; font-size: 13px; line-height: 1.5; min-height: 40px; color: var(--gray-700);"></div>
            </div>
            
            <!-- Status -->
            <div class="task-field">
                <div class="task-field-label">Status</div>
                <select id="edit-status">
                    <option value="backlog">Backlog</option>
                    <option value="todo">To Do</option>
                    <option value="in_progress">In Progress</option>
                    <option value="done">Done</option>
                    <option value="canceled">Canceled</option>
                </select>
            </div>
            
            <!-- Priority -->
            <div class="task-field">
                <div class="task-field-label">Priority</div>
                <select id="edit-priority">
                    <option value="none">None</option>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                </select>
            </div>
            
            <!-- Assignee -->
            <div class="task-field">
                <div class="task-field-label">Assignee</div>
                <input type="text" id="edit-assignee" placeholder="Assigned to">
            </div>
            
            <!-- Due Date -->
            <div class="task-field">
                <div class="task-field-label">Due Date</div>
                <input type="date" id="edit-due-date">
            </div>
            
            <!-- Meeting Info (if from meeting) -->
            <div class="task-field" id="meeting-info-field" style="display: none;">
                <div class="task-field-label">Meeting</div>
                <div id="meeting-title" style="padding: 10px; background: var(--gray-50); border: 1px solid var(--gray-200); border-radius: 6px; font-size: 13px; color: var(--gray-800); font-weight: 500;"></div>
            </div>
            
            <div class="task-field" id="meeting-date-field" style="display: none;">
                <div class="task-field-label">Meeting Date</div>
                <div id="meeting-date" style="padding: 10px; background: var(--gray-50); border: 1px solid var(--gray-200); border-radius: 6px; font-size: 13px; color: var(--gray-600);"></div>
            </div>
            
            <!-- Linear Link (if exists) -->
            <div class="task-field" id="linear-link-field" style="display: none;">
                <div class="task-field-label">Linear Issue</div>
                <a id="linear-link" href="#" target="_blank" style="color: var(--gray-700); text-decoration: none; display: flex; align-items: center; gap: 8px; padding: 10px; border: 1px solid var(--gray-200); border-radius: 6px; font-size: 13px;">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
                        <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
                    </svg>
                    Open in Linear
                </a>
            </div>
        </div>
        
        <div class="task-actions">
            <button onclick="saveTask()" class="task-save-btn">Save Changes</button>
            <button onclick="closeTaskPanel()" class="task-cancel-btn">Cancel</button>
        </div>
    </div>
    
    <script>
        // Team data from backend
        const teamMembersByOrg = {json.dumps(team_members_by_org)};
        const dvTeam = {json.dumps(dv_team)};
        const portfolioCompanies = {json.dumps([{'id': pc['id'], 'organization_id': pc['organization_id'], 'name': pc['name']} for pc in portfolio_companies])};
        const portfolioFinancialData = {json.dumps(portfolio_financial_data)};
        
        // Function to render financial data
        function renderFinancials(companyId) {{
            const financial = portfolioFinancialData[companyId] || null;
            const companyName = companyId === 'dv' ? 'Disruptive Ventures' : 
                (portfolioCompanies.find(pc => pc.id === companyId)?.name || 'Unknown');
            
            // Update financial subtitle
            const subtitle = document.getElementById('financial-subtitle');
            if (subtitle) {{
                subtitle.textContent = `Q3 2025 financial metrics for ${{companyName}}`;
            }}
            
            const metricsGrid = document.getElementById('financial-metrics-grid');
            if (!metricsGrid) return;
            
            if (!financial || companyId === 'dv') {{
                // Show placeholder message for DV or companies without data
                metricsGrid.innerHTML = `
                    <div class="kpi-card" style="grid-column: 1 / -1; text-align: center; padding: 40px;">
                        <p style="font-size: 14px; color: var(--gray-600); margin-bottom: 8px;">
                            Financial data for ${{companyName}} will be available when connected to Fortnox
                        </p>
                        <p style="font-size: 12px; color: var(--gray-500);">
                            Select a portfolio company to view their Q3 2025 metrics
                        </p>
                    </div>
                `;
                return;
            }}
            
            // Show portfolio company financials
            const ownershipBadge = financial.ownership > 0 ? 
                `<div class="kpi-change neutral" style="background: var(--purple-50); color: var(--purple-600); border: 1px solid #e9d5ff;">${{financial.ownership}}% DV Ownership</div>` 
                : '';
            
            const multiple = financial.invested > 0 ? (financial.valuation / (financial.invested / 1000)).toFixed(1) : '0.0';
            const multiplePercent = financial.invested > 0 ? (((financial.valuation / (financial.invested / 1000)) - 1) * 100).toFixed(0) : '0';
            
            metricsGrid.innerHTML = `
                <div class="kpi-card">
                    <div class="kpi-label">Estimated MRR</div>
                    <div class="kpi-value">${{financial.mrr > 0 ? financial.mrr + 'k kr' : 'Pre-revenue'}}</div>
                    <div class="kpi-change neutral">Monthly recurring</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Estimated ARR</div>
                    <div class="kpi-value">${{financial.arr > 0 ? (financial.arr / 1000).toFixed(1) + 'M kr' : 'Pre-revenue'}}</div>
                    ${{ownershipBadge}}
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">DV Investment</div>
                    <div class="kpi-value">${{financial.invested > 0 ? (financial.invested / 1000).toFixed(1) + 'M kr' : 'N/A'}}</div>
                    <div class="kpi-change neutral">Capital deployed</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Current Valuation</div>
                    <div class="kpi-value">${{financial.valuation > 0 ? financial.valuation + 'M kr' : 'N/A'}}</div>
                    <div class="kpi-change positive">${{multiple}}x Multiple (${{multiplePercent > 0 ? '+' : ''}}${{multiplePercent}}%)</div>
                </div>
            `;
        }}
        
        // Filter activities by company
        async function filterActivitiesByCompany(companyId, companyName) {{
            const header = document.getElementById('activities-header');
            const subtitle = document.getElementById('activities-subtitle');
            
            if (companyId !== 'dv') {{
                if (header) header.textContent = `Activities - ${{companyName}}`;
                if (subtitle) subtitle.textContent = `Pipeline deals and activities for ${{companyName}}`;
            }} else {{
                if (header) header.textContent = 'Activities';
                if (subtitle) subtitle.textContent = 'Linear tasks and action items';
            }}
            
            // Fetch and reload activities board for this company
            try {{
                const response = await fetch(`/wheels/building/company-activities/${{companyId}}`);
                const data = await response.json();
                
                if (data.success) {{
                    reloadActivitiesBoard(data.columns, data.source);
                }} else {{
                    console.error('Failed to fetch activities:', data.error);
                }}
            }} catch (error) {{
                console.error('Error fetching activities:', error);
            }}
        }}
        
        // Reload the activities kanban board with new data
        function reloadActivitiesBoard(columns, source) {{
            const kanbanContainer = document.querySelector('#activities-board .kanban-board');
            if (!kanbanContainer) return;
            
            // Clear existing columns
            kanbanContainer.innerHTML = '';
            
            // Define column configurations
            const columnConfigs = [
                {{ key: 'backlog', title: 'Backlog', color: 'gray' }},
                {{ key: 'todo', title: 'To Do', color: 'blue' }},
                {{ key: 'in_progress', title: 'In Progress', color: 'yellow' }},
                {{ key: 'done', title: 'Done', color: 'green' }}
            ];
            
            // Create columns
            columnConfigs.forEach(config => {{
                const tasks = columns[config.key] || [];
                const columnHtml = `
                    <div class="kanban-column" data-status="${{config.key}}">
                        <div class="kanban-column-header">
                            <div class="column-title">${{config.title}}</div>
                            <div class="column-count">${{tasks.length}}</div>
                        </div>
                        <div class="kanban-tasks">
                            ${{tasks.map(task => `
                                <div class="task-card" 
                                     data-task-id="${{task.id}}" 
                                     data-title="${{task.title}}" 
                                     data-description="${{task.description || ''}}" 
                                     data-status="${{task.status}}" 
                                     data-priority="${{task.priority || 'medium'}}"
                                     draggable="true">
                                    <div class="task-title">${{task.title}}</div>
                                    ${{task.organization ? `<div class="task-org" style="font-size: 12px; color: var(--gray-600); margin-top: 4px;">${{task.organization}}</div>` : ''}}
                                    ${{task.value ? `<div class="task-value" style="font-size: 11px; color: var(--gray-500); margin-top: 4px;">${{task.value.toLocaleString()}} ${{task.currency || 'SEK'}}</div>` : ''}}
                                    ${{task.tags ? `<div class="task-tags" style="margin-top: 8px;">${{task.tags.map(tag => `<span class="task-tag">${{tag}}</span>`).join('')}}</div>` : ''}}
                                </div>
                            `).join('')}}
                            ${{tasks.length === 0 ? `<div class="kanban-placeholder">No tasks</div>` : ''}}
                        </div>
                    </div>
                `;
                kanbanContainer.innerHTML += columnHtml;
            }});
            
            // Re-initialize drag & drop and click handlers
            initializeDragAndDrop();
            setupTaskCardListeners();
        }}
        
        // Filter dealflow by company
        function filterDealflowByCompany(companyId, companyName) {{
            const header = document.getElementById('dealflow-header');
            const subtitle = document.getElementById('dealflow-subtitle');
            
            if (companyId !== 'dv') {{
                if (header) header.textContent = `Dealflow - ${{companyName}}`;
                if (subtitle) subtitle.textContent = `Investment pipeline for ${{companyName}}`;
            }} else {{
                if (header) header.textContent = 'Dealflow';
                if (subtitle) subtitle.textContent = 'Investment pipeline and opportunities';
            }}
        }}
        
        // Function to render team members
        function renderTeamMembers(companyId) {{
            const grid = document.getElementById('team-members-grid');
            grid.innerHTML = '';
            
            let team = [];
            let companyName = 'Disruptive Ventures';
            
            // Get team based on selected company
            if (companyId === 'dv') {{
                team = dvTeam;
            }} else {{
                // Find the organization_id for this portfolio company
                const company = portfolioCompanies.find(pc => pc.id === companyId);
                if (company) {{
                    companyName = company.name;
                    team = teamMembersByOrg[company.organization_id] || [];
                }}
            }}
            
            // Update subtitle
            document.getElementById('team-subtitle').textContent = 
                `${{team.length}} team member${{team.length !== 1 ? 's' : ''}} at ${{companyName}}`;
            
            // Render team members
            if (team.length === 0) {{
                grid.innerHTML = `
                    <div class="team-member-card" style="opacity: 0.6; grid-column: 1 / -1;">
                        <div style="text-align: center; padding: 32px 20px; color: var(--gray-500);">
                            <p style="font-size: 14px; margin-bottom: 8px;">No team members found</p>
                            <p style="font-size: 12px;">Add team members to see them here</p>
                        </div>
                    </div>
                `;
                return;
            }}
            
            team.forEach(member => {{
                const emailBtn = member.email ? 
                    `<a href="mailto:${{member.email}}" style="flex: 1; padding: 6px 12px; background: white; border: 1px solid var(--gray-300); border-radius: 6px; text-align: center; font-size: 12px; color: var(--gray-700); text-decoration: none; transition: all 0.15s; display: inline-block;">Email</a>` 
                    : '';
                
                const linkedinBtn = member.linkedin_url ? 
                    `<a href="${{member.linkedin_url}}" target="_blank" style="flex: 1; padding: 6px 12px; background: white; border: 1px solid var(--gray-300); border-radius: 6px; text-align: center; font-size: 12px; color: var(--gray-700); text-decoration: none; transition: all 0.15s; display: inline-block;">LinkedIn</a>` 
                    : '';
                
                const contactButtons = (emailBtn || linkedinBtn) ? 
                    `<div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--gray-200); display: flex; gap: 8px;">${{emailBtn}}${{linkedinBtn}}</div>` 
                    : '';
                
                const roleType = member.person_type === 'founder' ? 'Founder' : member.job_title || 'Team Member';
                const roleBadge = member.person_type === 'founder' ? 
                    '<span style="padding: 3px 8px; background: var(--purple-50); color: var(--purple-600); font-size: 11px; font-weight: 500; border-radius: 4px; border: 1px solid #e9d5ff;">Founder</span>' 
                    : '';
                
                grid.innerHTML += `
                    <div class="team-member-card">
                        <div style="display: flex; gap: 16px;">
                            <div class="profile-avatar" style="width: 56px; height: 56px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 600; flex-shrink: 0;">
                                ${{member.initials}}
                            </div>
                            <div style="flex: 1; min-width: 0;">
                                <h3 style="font-size: 15px; font-weight: 600; color: var(--gray-900); margin-bottom: 4px;">${{member.name}}</h3>
                                <p style="font-size: 13px; color: var(--gray-600); margin-bottom: 8px;">${{roleType}}</p>
                                ${{roleBadge}}
                            </div>
                        </div>
                        ${{contactButtons}}
                    </div>
                `;
            }});
        }}
        
        let draggedElement = null;
        let isDragging = false;
        let dragStartTime = 0;
        let mouseDownX = 0;
        let mouseDownY = 0;
        
        // Simple markdown renderer
        function renderMarkdown(text) {{
            if (!text) return '';
            
            // Convert markdown to HTML
            let result = text;
            // Bold: **text** or __text__
            result = result.replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>');
            result = result.replace(/__(.+?)__/g, '<strong>$1</strong>');
            // Italic: *text* or _text_
            result = result.replace(/\\*(.+?)\\*/g, '<em>$1</em>');
            result = result.replace(/_(.+?)_/g, '<em>$1</em>');
            // Links: [text](url)
            result = result.replace(/\\[(.+?)\\]\\((.+?)\\)/g, '<a href="$2" target="_blank">$1</a>');
            // Line breaks - use character code to avoid Python f-string issues
            const newline = String.fromCharCode(10);
            result = result.split(newline).join('<br>');
            return result;
        }}
        
        // Strip markdown (for plain text display)
        function stripMarkdown(text) {{
            if (!text) return '';
            
            return text
                // Remove bold/italic markers
                .replace(/\\*\\*(.+?)\\*\\*/g, '$1')
                .replace(/__(.+?)__/g, '$1')
                .replace(/\\*(.+?)\\*/g, '$1')
                .replace(/_(.+?)_/g, '$1')
                // Remove links but keep text
                .replace(/\\[(.+?)\\]\\((.+?)\\)/g, '$1')
                // Clean up extra whitespace
                .replace(/\\s+/g, ' ')
                .trim();
        }}
        
        // Parse meeting info from description
        function parseMeetingInfo(description) {{
            if (!description) return null;
            
            // Look for **From:** pattern
            const fromMatch = description.match(/\*\*From:\*\*\\s*(.+?)(?:\\*\\*|$)/);
            if (!fromMatch) return null;
            
            const fromText = fromMatch[1].trim();
            
            // Extract date (format: Möte_YYYY-MM-DD or similar)
            const dateMatch = fromText.match(/(\\d{{4}}-\\d{{2}}-\\d{{2}})/);
            const meetingDate = dateMatch ? dateMatch[1] : null;
            
            // Clean up meeting title
            // Remove date prefix like "Möte_2023-10-04_"
            let meetingTitle = fromText
                .replace(/^[^_]*_\\d{{4}}-\\d{{2}}-\\d{{2}}_/, '')  // Remove "Möte_2023-10-04_"
                .replace(/_/g, ' ')  // Replace underscores with spaces
                .trim();
            
            // If no title after cleaning, use the original without date
            if (!meetingTitle) {{
                meetingTitle = fromText.replace(/\\d{{4}}-\\d{{2}}-\\d{{2}}/, '').replace(/_/g, ' ').trim();
            }}
            
            return {{
                title: meetingTitle || 'Meeting',
                date: meetingDate
            }};
        }}
        
        // Remove meeting info from description
        function cleanDescription(description) {{
            if (!description) return '';
            
            // Split by newline, filter out From: and Date: lines
            const newline = String.fromCharCode(10);
            const lines = description.split(newline);
            const filtered = lines.filter(line => {{
                const trimmed = line.trim();
                return !trimmed.startsWith('**From:**') && !trimmed.startsWith('**Date:**');
            }});
            
            return filtered.join(newline).trim();
        }}
        
        // Update description preview with rendered markdown
        function updateDescriptionPreview() {{
            const description = document.getElementById('edit-description').value;
            const preview = document.getElementById('description-preview');
            
            if (description) {{
                preview.innerHTML = renderMarkdown(description);
                preview.style.display = 'block';
            }} else {{
                preview.innerHTML = '<em style="color: var(--gray-400);">Preview will appear here...</em>';
            }}
        }}
        
        async function syncLinear() {{
            const btn = event.target;
            btn.disabled = true;
            btn.textContent = 'Syncing...';
            
            try {{
                const response = await fetch('/wheels/building/sync-linear', {{
                    method: 'POST'
                }});
                
                const data = await response.json();
                
                if (data.success) {{
                    // Reload page to show new tasks
                    window.location.reload();
                }} else {{
                    alert('Sync failed. Check console for details.');
                    btn.disabled = false;
                    btn.textContent = 'Sync from Linear';
                }}
            }} catch (error) {{
                console.error('Sync error:', error);
                alert('Sync failed: ' + error.message);
                btn.disabled = false;
                btn.textContent = 'Sync Now';
            }}
        }}
        
        // Auto-sync every minute
        async function autoSync() {{
            try {{
                const response = await fetch('/wheels/building/sync-linear', {{
                    method: 'POST'
                }});
                
                if (response.ok) {{
                    const data = await response.json();
                    document.getElementById('sync-status').textContent = `Last synced: ${{new Date().toLocaleTimeString()}}`;
                    
                    // Silently reload if new tasks
                    if (data.tasks_synced > 0) {{
                        // Could update DOM instead of reload for smoother UX
                    }}
                }}
            }} catch (error) {{
                console.error('Auto-sync error:', error);
            }}
        }}
        
        // Initial sync on load
        window.addEventListener('load', () => {{
            autoSync();
            // Set interval to sync every minute
            setInterval(autoSync, 60000);
        }});
        
        // Filter tasks
        function filterBy(filter) {{
            // Update active button
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            const tasks = document.querySelectorAll('.task-card');
            
            tasks.forEach(task => {{
                const assignee = task.querySelector('.task-assignee')?.textContent || '';
                const priority = task.querySelector('.task-priority')?.textContent || '';
                const deadline = task.querySelector('.task-deadline')?.textContent || '';
                
                let show = true;
                
                if (filter === 'mine') {{
                    show = assignee.includes('Markus') || assignee.includes('Marcus');
                }} else if (filter === 'high') {{
                    show = priority.includes('high') || priority.includes('urgent');
                }} else if (filter === 'overdue') {{
                    const dateMatch = deadline.match(/\\d{{4}}-\\d{{2}}-\\d{{2}}/);
                    if (dateMatch) {{
                        const dueDate = new Date(dateMatch[0]);
                        const today = new Date();
                        show = dueDate < today;
                    }} else {{
                        show = false;
                    }}
                }}
                
                task.style.display = show ? 'block' : 'none';
            }});
            
            updateColumnCounts();
        }}
        
        // Switch between Kanban and Timeline views
        function switchView(view, clickedButton) {{
            // Update buttons
            document.querySelectorAll('.view-switcher-btn').forEach(btn => btn.classList.remove('active'));
            if (clickedButton) {{
                clickedButton.classList.add('active');
            }} else {{
                // Fallback - find and activate the correct button
                const buttons = document.querySelectorAll('.view-switcher-btn');
                if (view === 'kanban') {{
                    buttons[0]?.classList.add('active');
                }} else {{
                    buttons[1]?.classList.add('active');
                }}
            }}
            
            // Show/hide views
            if (view === 'kanban') {{
                const kanbanView = document.getElementById('kanban-view');
                const timelineView = document.getElementById('timeline-view');
                if (kanbanView) {{
                    kanbanView.classList.add('active');
                    kanbanView.style.display = 'flex';
                }}
                if (timelineView) {{
                    timelineView.classList.remove('active');
                    timelineView.style.display = 'none';
                }}
            }} else {{
                const kanbanView = document.getElementById('kanban-view');
                const timelineView = document.getElementById('timeline-view');
                if (kanbanView) {{
                    kanbanView.classList.remove('active');
                    kanbanView.style.display = 'none';
                }}
                if (timelineView) {{
                    timelineView.classList.add('active');
                    timelineView.style.display = 'block';
                }}
            }}
            
            // Save preference
            localStorage.setItem('building-view', view);
        }}
        
        // Open task detail panel
        function openTaskPanel(event, taskCard) {{
            console.log('🔍 openTaskPanel called');
            console.log('  - event:', event);
            console.log('  - taskCard:', taskCard);
            console.log('  - isDragging:', isDragging);
            
            // Prevent if we just dragged (not a click)
            if (isDragging) {{
                console.log('⚠️ Skipping - isDragging = true');
                isDragging = false;
                return;
            }}
            
            // Stop event propagation
            if (event) {{
                event.stopPropagation();
            }}
            
            const panel = document.getElementById('task-panel');
            const overlay = document.getElementById('task-panel-overlay');
            
            console.log('  - panel found:', !!panel);
            console.log('  - overlay found:', !!overlay);
            
            if (!panel || !overlay) {{
                console.error('❌ Panel or overlay not found');
                return;
            }}
            
            // Parse meeting info from description
            const rawDescription = taskCard.dataset.description || '';
            const meetingInfo = parseMeetingInfo(rawDescription);
            const cleanedDescription = cleanDescription(stripMarkdown(rawDescription));
            
            // Populate panel with task data
            document.getElementById('task-id-display').textContent = taskCard.dataset.linearId || 'Task Details';
            document.getElementById('edit-title').value = stripMarkdown(taskCard.dataset.title) || '';
            document.getElementById('edit-description').value = cleanedDescription;
            document.getElementById('edit-status').value = taskCard.dataset.status || 'todo';
            document.getElementById('edit-priority').value = taskCard.dataset.priority || 'medium';
            document.getElementById('edit-assignee').value = taskCard.dataset.assignee || '';
            document.getElementById('edit-due-date').value = taskCard.dataset.dueDate || '';
            
            // Show meeting info if available
            if (meetingInfo) {{
                document.getElementById('meeting-info-field').style.display = 'block';
                document.getElementById('meeting-date-field').style.display = 'block';
                document.getElementById('meeting-title').textContent = meetingInfo.title;
                document.getElementById('meeting-date').textContent = meetingInfo.date ? 
                    new Date(meetingInfo.date).toLocaleDateString('en-US', {{ 
                        year: 'numeric', 
                        month: 'long', 
                        day: 'numeric' 
                    }}) : 'No date';
            }} else {{
                document.getElementById('meeting-info-field').style.display = 'none';
                document.getElementById('meeting-date-field').style.display = 'none';
            }}
            
            // Update description preview
            updateDescriptionPreview();
            
            // Show Linear link if exists
            const linearUrl = taskCard.dataset.linearUrl;
            if (linearUrl) {{
                document.getElementById('linear-link-field').style.display = 'block';
                document.getElementById('linear-link').href = linearUrl;
            }} else {{
                document.getElementById('linear-link-field').style.display = 'none';
            }}
            
            // Store task ID for saving
            panel.dataset.taskId = taskCard.dataset.taskId;
            panel.dataset.taskCard = taskCard.id || '';
            
            // Open panel
            console.log('✅ Opening panel...');
            panel.classList.add('open');
            overlay.classList.add('open');
            document.body.style.overflow = 'hidden';
            console.log('✅ Panel opened successfully');
        }}
        
        // Close task detail panel
        function closeTaskPanel() {{
            console.log('🚪 Closing task panel');
            const panel = document.getElementById('task-panel');
            const overlay = document.getElementById('task-panel-overlay');
            
            panel.classList.remove('open');
            overlay.classList.remove('open');
            document.body.style.overflow = 'auto';
            console.log('✅ Panel closed');
        }}
        
        // Save task changes
        async function saveTask() {{
            const panel = document.getElementById('task-panel');
            const taskId = panel.dataset.taskId;
            
            if (!taskId) {{
                alert('No task ID found');
                return;
            }}
            
            const updates = {{
                title: document.getElementById('edit-title').value,
                description: document.getElementById('edit-description').value,
                status: document.getElementById('edit-status').value,
                priority: document.getElementById('edit-priority').value,
                owner_name: document.getElementById('edit-assignee').value,
                due_date: document.getElementById('edit-due-date').value || null
            }};
            
            // Get Linear ID if this is a Linear task
            const linearIdElement = document.querySelector('.task-card.open, [data-task-id="' + taskId + '"]');
            const linearId = linearIdElement ? linearIdElement.dataset.linearId : null;
            
            // Show saving state
            const saveBtn = event.target;
            const originalText = saveBtn.textContent;
            saveBtn.disabled = true;
            
            if (linearId) {{
                saveBtn.textContent = 'Syncing to Linear...';
            }} else {{
                saveBtn.textContent = 'Saving...';
            }}
            
            try {{
                const response = await fetch('/wheels/building/update-task', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{
                        task_id: taskId,
                        linear_id: linearId,
                        updates: updates
                    }})
                }});
                
                if (response.ok) {{
                    const result = await response.json();
                    console.log('✅ Task saved:', result);
                    
                    // Show success message
                    if (result.synced_to_linear) {{
                        saveBtn.textContent = '✓ Synced to Linear';
                        saveBtn.style.background = '#16a34a';
                        setTimeout(() => {{
                            closeTaskPanel();
                            window.location.reload();
                        }}, 1000);
                    }} else {{
                        // Close panel and reload to show changes
                        closeTaskPanel();
                        window.location.reload();
                    }}
                }} else {{
                    const error = await response.json();
                    alert('Failed to save: ' + (error.error || error.message || 'Unknown error'));
                    saveBtn.disabled = false;
                    saveBtn.textContent = originalText;
                }}
            }} catch (error) {{
                console.error('Save error:', error);
                alert('Failed to save: ' + error.message);
                saveBtn.disabled = false;
                saveBtn.textContent = originalText;
            }}
        }}
        
        // Better drag vs click detection
        document.addEventListener('DOMContentLoaded', () => {{
            console.log('🚀 DOMContentLoaded - Initializing page');
            
            // Initialize company selector and logo
            const selector = document.getElementById('company-selector');
            const logoElement = document.getElementById('company-logo-preview');
            
            // Restore previously selected company if exists
            const savedCompanyId = localStorage.getItem('selected-portfolio-company');
            if (savedCompanyId && selector) {{
                const option = selector.querySelector(`option[value="${{savedCompanyId}}"]`);
                if (option) {{
                    selector.value = savedCompanyId;
                    const logoUrl = option.getAttribute('data-logo');
                    if (logoUrl && logoUrl !== '' && logoElement) {{
                        logoElement.src = logoUrl;
                        logoElement.onerror = function() {{
                            this.src = '/static/dv-logo.png';
                        }};
                    }}
                }}
            }}
            
            // Check if panel elements exist
            const panel = document.getElementById('task-panel');
            const overlay = document.getElementById('task-panel-overlay');
            console.log('📋 Panel check:', {{
                'task-panel exists': !!panel,
                'task-panel-overlay exists': !!overlay
            }});
            
            const cards = document.querySelectorAll('.task-card');
            console.log(`  Found ${{cards.length}} task cards`);
            
            cards.forEach((card, index) => {{
                console.log(`  Setting up listeners for card ${{index}}:`, card.dataset.title);
                
                // Track mouse down
                card.addEventListener('mousedown', (e) => {{
                    console.log(`🖱️ mousedown on card ${{index}}`);
                    isDragging = false;
                    dragStartTime = Date.now();
                    mouseDownX = e.clientX;
                    mouseDownY = e.clientY;
                }});
                
                // Detect if actually dragging
                card.addEventListener('dragstart', (e) => {{
                    console.log(`🎯 dragstart on card ${{index}}`);
                    isDragging = true;
                }});
                
                // Handle click only if not dragging
                card.addEventListener('click', (e) => {{
                    console.log(`👆 click on card ${{index}}`);
                    const timeDiff = Date.now() - dragStartTime;
                    const distanceX = Math.abs(e.clientX - mouseDownX);
                    const distanceY = Math.abs(e.clientY - mouseDownY);
                    
                    console.log(`  - Time diff: ${{timeDiff}}ms`);
                    console.log(`  - Distance X: ${{distanceX}}px`);
                    console.log(`  - Distance Y: ${{distanceY}}px`);
                    console.log(`  - isDragging: ${{isDragging}}`);
                    
                    // If mouse moved more than 5px or took more than 200ms, it's a drag
                    if (distanceX > 5 || distanceY > 5 || timeDiff > 200) {{
                        console.log('  ⚠️ Detected as drag (distance or time threshold exceeded)');
                        isDragging = true;
                    }}
                    
                    if (!isDragging) {{
                        console.log('  ✅ Opening task panel');
                        openTaskPanel(e, card);
                    }} else {{
                        console.log('  ⏭️ Skipping - was a drag');
                    }}
                    
                    // Reset after a short delay
                    setTimeout(() => {{ 
                        console.log(`  🔄 Resetting isDragging for card ${{index}}`);
                        isDragging = false; 
                    }}, 100);
                }});
                
                // Reset on drag end
                card.addEventListener('dragend', () => {{
                    console.log(`🏁 dragend on card ${{index}}`);
                    isDragging = false;
                }});
            }});
            
            console.log('✅ All task card listeners set up');
        }});
        
        // Switch between companies
        async function switchCompany(companyId) {{
            console.log('Switching to company:', companyId);
            
            // Get selected company details
            const selector = document.getElementById('company-selector');
            const selectedOption = selector.selectedOptions[0];
            const logoUrl = selectedOption.getAttribute('data-logo');
            const companyName = selectedOption.text;
            
            // Update logo
            const logoElement = document.getElementById('company-logo-preview');
            if (logoUrl && logoUrl !== '') {{
                logoElement.src = logoUrl;
                logoElement.style.display = 'block';
                logoElement.onerror = function() {{
                    this.src = '/static/dv-logo.png';
                }};
            }} else {{
                logoElement.src = '/static/dv-logo.png';
            }}
            
            // Save selected company
            localStorage.setItem('selected-portfolio-company', companyId);
            
            // Show loading state
            document.getElementById('sync-status').textContent = 'Syncing...';
            document.getElementById('sync-status').classList.add('syncing');
            
            // Update all views with company-specific data
            renderTeamMembers(companyId);
            renderFinancials(companyId);
            await filterActivitiesByCompany(companyId, companyName);
            filterDealflowByCompany(companyId, companyName);
            
            // Update status
            document.getElementById('sync-status').textContent = 'Ready';
            document.getElementById('sync-status').classList.remove('syncing');
            console.log(`Switched to: ${{companyName}}`);
        }}
        
        // Restore selected company and update logo
        window.addEventListener('load', () => {{
            const savedCompany = localStorage.getItem('selected-portfolio-company');
            const selector = document.getElementById('company-selector');
            let currentCompanyId = 'dv';
            
            if (savedCompany) {{
                const option = Array.from(selector.options).find(opt => opt.value === savedCompany);
                if (option) {{
                    selector.value = savedCompany;
                    currentCompanyId = savedCompany;
                }}
            }}
            
            // Update logo and name on page load
            const selectedOption = selector.selectedOptions[0];
            const logoUrl = selectedOption.getAttribute('data-logo');
            const companyName = selectedOption.getAttribute('data-name');
            
            const logoElement = document.getElementById('selected-company-logo');
            if (logoUrl && logoUrl !== '') {{
                logoElement.src = logoUrl;
                logoElement.style.display = 'block';
            }} else {{
                logoElement.style.display = 'none';
            }}
            
            const nameElement = document.getElementById('selected-company-name');
            if (companyName) {{
                nameElement.textContent = companyName;
            }}
            
            // Render all views for current company
            const company = portfolioCompanies.find(pc => pc.id === currentCompanyId);
            const currentCompanyName = currentCompanyId === 'dv' ? 'Disruptive Ventures' : (company?.name || 'Unknown');
            
            renderTeamMembers(currentCompanyId);
            renderFinancials(currentCompanyId);
            filterActivitiesByCompany(currentCompanyId, currentCompanyName);
            filterDealflowByCompany(currentCompanyId, currentCompanyName);
        }});
        
        // Switch between tabs (Activities, Dealflow, Financial)
        function switchTab(tabName) {{
            console.log('Switching to tab:', tabName);
            
            // Update tab buttons
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {{
                content.classList.remove('active');
                content.style.display = 'none';
            }});
            
            // Show selected tab
            const selectedTab = document.getElementById(`${{tabName}}-tab`);
            if (selectedTab) {{
                selectedTab.classList.add('active');
                selectedTab.style.display = 'block';
            }}
            
            // Show/hide filters based on tab (only show for activities and dealflow)
            const filters = document.getElementById('task-filters');
            if (filters) {{
                if (tabName === 'financial' || tabName === 'team') {{
                    filters.style.display = 'none';
                }} else {{
                    filters.style.display = 'flex';
                }}
            }}
            
            // Save preference
            localStorage.setItem('building-active-tab', tabName);
        }}
        
        // Restore tab preference
        window.addEventListener('load', () => {{
            const savedTab = localStorage.getItem('building-active-tab') || 'activities';
            
            // Activate saved tab
            if (savedTab !== 'activities') {{
                const tabBtn = Array.from(document.querySelectorAll('.tab-btn')).find(btn =>
                    btn.textContent.toLowerCase() === savedTab
                );
                if (tabBtn) {{
                    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
                    tabBtn.classList.add('active');
                    
                    document.querySelectorAll('.tab-content').forEach(content => {{
                        content.classList.remove('active');
                        content.style.display = 'none';
                    }});
                    
                    const tabContent = document.getElementById(`${{savedTab}}-tab`);
                    if (tabContent) {{
                        tabContent.classList.add('active');
                        tabContent.style.display = 'block';
                    }}
                }}
            }}
            
            // Show/hide filters based on saved tab
            const filters = document.getElementById('task-filters');
            if (filters) {{
                if (savedTab === 'financial' || savedTab === 'team') {{
                    filters.style.display = 'none';
                }} else {{
                    filters.style.display = 'flex';
                }}
            }}
            
            const savedView = localStorage.getItem('building-view');
            if (savedView === 'timeline') {{
                document.getElementById('timeline-view').classList.add('active');
                document.getElementById('kanban-view').style.display = 'none';
                document.querySelectorAll('.view-switcher-btn')[1].classList.add('active');
                document.querySelectorAll('.view-switcher-btn')[0].classList.remove('active');
            }}
        }});
        
        function allowDrop(ev) {{
            ev.preventDefault();
        }}
        
        function drag(ev) {{
            draggedElement = ev.target;
            ev.target.classList.add('dragging');
            ev.target.classList.add('dragging-active');
            isDragging = true;
        }}
        
        async function drop(ev) {{
            ev.preventDefault();
            
            if (draggedElement) {{
                const column = ev.currentTarget;
                const tasksContainer = column.querySelector('.kanban-tasks');
                
                // Remove "No tasks" placeholder if it exists in target column
                const placeholder = tasksContainer.querySelector('div[style*="No tasks"]');
                if (placeholder && placeholder.textContent.includes('No tasks')) {{
                    placeholder.remove();
                    console.log('✅ Removed "No tasks" placeholder from target column');
                }}
                
                // Append to new column
                tasksContainer.appendChild(draggedElement);
                draggedElement.classList.remove('dragging');
                draggedElement.classList.remove('dragging-active');
                
                // Get new status
                const newStatus = column.dataset.status;
                const taskId = draggedElement.dataset.taskId;
                const linearId = draggedElement.dataset.linearId;
                
                // Update count badges and placeholders
                updateColumnCounts();
                
                // Update status in backend
                try {{
                    const response = await fetch('/wheels/building/update-task-status', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify({{
                            task_id: taskId,
                            linear_id: linearId,
                            new_status: newStatus
                        }})
                    }});
                    
                    if (response.ok) {{
                        const result = await response.json();
                        console.log('Status updated:', result);
                        
                        // Show success feedback
                        const card = draggedElement;
                        const originalBg = card.style.backgroundColor;
                        card.style.backgroundColor = '#dcfce7';
                        setTimeout(() => {{ card.style.backgroundColor = originalBg; }}, 500);
                    }} else {{
                        console.error('Failed to update status');
                        alert('Failed to update task status. Please refresh the page.');
                    }}
                }} catch (error) {{
                    console.error('Error updating status:', error);
                    alert('Error updating task. Please check your connection.');
                }}
                
                draggedElement = null;
            }}
        }}
        
        function updateColumnCounts() {{
            ['backlog', 'todo', 'in_progress', 'done', 'canceled'].forEach(status => {{
                const column = document.querySelector(`[data-status="${{status}}"]`);
                if (column) {{
                    const tasksContainer = column.querySelector('.kanban-tasks');
                    const taskCards = column.querySelectorAll('.task-card');
                    const count = taskCards.length;
                    
                    // Update count badge
                    const badge = column.querySelector('.column-count');
                    if (badge) badge.textContent = count;
                    
                    // Add/remove "No tasks" placeholder
                    const placeholder = tasksContainer.querySelector('div[style*="text-align: center"]');
                    
                    if (count === 0 && !placeholder) {{
                        // Add placeholder if no tasks
                        const noTasksDiv = document.createElement('div');
                        noTasksDiv.style.textAlign = 'center';
                        noTasksDiv.style.padding = '24px';
                        noTasksDiv.style.color = 'var(--gray-500)';
                        noTasksDiv.style.fontSize = '12px';
                        noTasksDiv.textContent = 'No tasks';
                        tasksContainer.appendChild(noTasksDiv);
                        console.log(`✅ Added "No tasks" placeholder to ${{status}}`);
                    }} else if (count > 0 && placeholder) {{
                        // Remove placeholder if tasks exist
                        placeholder.remove();
                        console.log(`✅ Removed "No tasks" placeholder from ${{status}}`);
                    }}
                }}
            }});
        }}
        
        // Update task status in database
        async function updateTaskStatus(taskId, linearId, newStatus) {{
            try {{
                const response = await fetch('/wheels/building/update-task-status', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{
                        task_id: taskId,
                        linear_id: linearId,
                        new_status: newStatus
                    }})
                }});
                
                if (response.ok) {{
                    const result = await response.json();
                    console.log('✅ Status updated:', result.message);
                }} else {{
                    console.error('❌ Failed to update status');
                }}
            }} catch (error) {{
                console.error('❌ Error updating status:', error);
            }}
        }}
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html)


def generate_task_cards(tasks):
    """Generate draggable task cards for Kanban board."""
    if not tasks:
        return '<div style="text-align: center; padding: 24px; color: var(--gray-500); font-size: 12px;">No tasks</div>'
    
    cards = []
    for task in tasks:
        # Get assignee initials
        assignee = task.get('owner_name', 'Unassigned')
        initials = ''.join([n[0].upper() for n in assignee.split()[:2]]) if assignee != 'Unassigned' else '?'
        
        # Format deadline
        deadline = task.get('due_date', '')
        deadline_display = str(deadline)[:10] if deadline else 'No deadline'
        
        # Priority
        priority = task.get('priority', 'medium')
        
        # Description preview - strip markdown for preview
        description = task.get('description', '')
        # Simple markdown stripping for Python
        description_clean = description.replace('**', '').replace('__', '').replace('*', '').replace('_', '')
        description_html = f'<div style="font-size: 12px; color: var(--gray-600); margin-top: 6px; line-height: 1.4;">{description_clean[:80]}{"..." if len(description_clean) > 80 else ""}</div>' if description else ''
        
        # Linear link
        linear_url = task.get('linear_issue_url', '')
        linear_id = task.get('linear_issue_id', '')
        
        # Escape quotes for JavaScript and strip markdown for data attributes
        title_raw = task.get('title', 'Untitled')
        title_clean = title_raw.replace('**', '').replace('__', '').replace('*', '').replace('_', '')
        title_js = title_raw.replace("'", "\\'").replace('"', '\\"')
        description_js = description.replace("'", "\\'").replace('"', '\\"') if description else ''
        
        card = f'''
        <div class="task-card" 
             draggable="true" 
             ondragstart="drag(event)" 
             data-task-id="{task.get('id', '')}"
             data-title="{title_js}"
             data-description="{description_js}"
             data-status="{task.get('status', 'todo')}"
             data-priority="{priority}"
             data-assignee="{assignee}"
             data-due-date="{deadline if deadline and deadline != 'No deadline' else ''}"
             data-linear-url="{linear_url}"
             data-linear-id="{linear_id}">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 4px;">
                <div class="task-title" style="flex: 1;">{title_clean}</div>
                {f'<span style="font-size: 11px; color: var(--gray-500); margin-left: 8px;">{linear_id}</span>' if linear_id else ''}
            </div>
            {description_html}
            <div class="task-meta">
                <div class="task-assignee">
                    <span style="width: 18px; height: 18px; border-radius: 50%; background: var(--gray-200); display: inline-flex; align-items: center; justify-content: center; font-size: 9px; font-weight: 600; color: var(--gray-700);">{initials}</span>
                    <span>{assignee}</span>
                </div>
                {f'<div class="task-deadline">{deadline_display}</div>' if deadline else ''}
                <div class="task-priority">{priority}</div>
            </div>
        </div>
        '''
        cards.append(card)
    
    return '\n'.join(cards)


async def fetch_pipedrive_deals():
    """Fetch deals from Pipedrive API (currently using Coeo's account)."""
    try:
        from app.integrations.pipedrive_client import PipedriveClient
        
        # Use Coeo's Pipedrive credentials from settings
        if not settings.pipedrive_api_token:
            print("⚠️  No Pipedrive API token configured")
            return []
        
        print(f"🔄 Fetching deals from Pipedrive ({settings.pipedrive_company_domain})...")
        
        client = PipedriveClient(
            api_token=settings.pipedrive_api_token,
            company_domain=settings.pipedrive_company_domain
        )
        
        # First, fetch stages to get ID -> Name mapping
        stages = await client.get_stages()
        stage_id_to_name = {stage['id']: stage['name'] for stage in stages}
        
        # Fetch all open deals
        deals = await client.get_deals(status="all_not_deleted", limit=200)
        
        if not deals:
            return []
        
        # Map Pipedrive stages to our standard stages
        # Use keyword matching for better coverage
        def map_stage(stage_name):
            """Map Pipedrive stage to standard dealflow stage."""
            if not stage_name:
                return 'lead'
            
            stage_lower = stage_name.lower()
            
            # Skip negative stages
            if any(neg in stage_lower for neg in ['nej', 'inte nu', 'inte just nu', 'fel typ', 'irrelevant', 'avvakta', 'soptunna']):
                return None  # Will be filtered out
            
            # Closed Won (verbal acceptance, confirmed deals)
            if any(won in stage_lower for won in ['ok, verbal', 'verbal acceptans', 'genomfört', 'ja vi kör', 'affär nära']):
                return 'closed_won'
            
            # Proposal / Negotiation
            if any(prop in stage_lower for prop in ['förhandling', 'nästan där', 'affär nära']):
                return 'proposal'
            
            # Due Diligence / Offer sent
            if any(dd in stage_lower for dd in ['trolig affär', 'offert', 'utvärdering']):
                return 'due_diligence'
            
            # Meeting / Demo stage
            if any(meet in stage_lower for meet in ['demo', 'bokat möte', 'intresserad', 'försäljning pågår', 'samtal', 'dialog']):
                return 'meeting'
            
            # Qualified / First contact made
            if any(qual in stage_lower for qual in ['prospekt', 'kontakt', 'kontaktade', 'ringt', 'första', 'kvalificerade', 'status högst oklar']):
                return 'qualified'
            
            # Default to Lead (not yet contacted, early stage)
            return 'lead'
        
        # Normalize deals
        normalized_deals = []
        for deal in deals:
            # Get stage name from stage_id
            stage_id = deal.get('stage_id')
            stage_name = stage_id_to_name.get(stage_id, 'Unknown')
            mapped_stage = map_stage(stage_name)
            
            # Skip deals that mapped to None (negative stages)
            if mapped_stage is None:
                continue
            
            normalized_deals.append({
                'id': deal.get('id'),
                'title': deal.get('title', 'Untitled'),
                'value': deal.get('value', 0),
                'currency': deal.get('currency', 'SEK'),
                'stage': mapped_stage,
                'stage_name': stage_name,
                'organization': deal.get('org_name', 'No organization'),
                'person': deal.get('person_name', 'No contact'),
                'owner': deal.get('owner_name', 'Unassigned'),
                'created_at': deal.get('add_time', ''),
                'updated_at': deal.get('update_time', ''),
                'expected_close_date': deal.get('expected_close_date', ''),
            })
        
        print(f"✅ Fetched {len(normalized_deals)} deals from Pipedrive (Coeo)")
        return normalized_deals
        
    except Exception as e:
        print(f"Error fetching Pipedrive deals: {e}")
        return []


async def fetch_fortnox_invoices():
    """Fetch invoices from Fortnox API (view-only)."""
    try:
        # TODO: Add Fortnox API integration
        # For now, return empty list
        # When ready:
        # 1. Use Fortnox API credentials
        # 2. GET /3/invoices with filters
        # 3. Map status to our columns
        # 4. Format for display
        return []
    except Exception as e:
        print(f"Error fetching Fortnox invoices: {e}")
        return []


async def fetch_linear_tasks():
    """Fetch tasks from Linear API and sync to database."""
    try:
        if not settings.linear_api_key:
            print("Linear API key not configured")
            return []
        
        # GraphQL query to get issues
        query = """
        query {
          issues(
            first: 100
            filter: {
              team: { name: { contains: "Disruptive" } }
            }
          ) {
            nodes {
              id
              identifier
              title
              description
              priority
              state {
                name
              }
              assignee {
                name
                email
              }
              dueDate
              url
            }
          }
        }
        """
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://api.linear.app/graphql',
                json={'query': query},
                headers={
                    'Authorization': settings.linear_api_key,
                    'Content-Type': 'application/json'
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                issues = data.get('data', {}).get('issues', {}).get('nodes', [])
                
                # Get org_id (Disruptive Ventures)
                supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
                org_result = supabase.table('orgs').select('id').eq('name', 'Disruptive Ventures').execute()
                org_id = org_result.data[0]['id'] if org_result.data else None
                
                if not org_id:
                    print("⚠️ No org_id found for Disruptive Ventures - tasks won't be saved to database")
                    print("   Tasks will display but editing won't work until org exists")
                else:
                    print(f"✅ Using org_id: {org_id}")
                
                # Convert Linear issues to our format and sync to database
                tasks = []
                for issue in issues:
                    task_data = {
                        'id': issue.get('id'),
                        'title': issue.get('title'),
                        'description': issue.get('description', ''),
                        'owner_name': issue.get('assignee', {}).get('name') if issue.get('assignee') else 'Unassigned',
                        'due_date': issue.get('dueDate'),
                        'priority': map_linear_priority(issue.get('priority', 0)),
                        'status': map_linear_status(issue.get('state', {}).get('name', 'Todo')),
                        'linear_issue_url': issue.get('url'),
                        'linear_issue_id': issue.get('identifier')
                    }
                    
                    # Sync to database (upsert based on Linear ID)
                    if org_id:
                        try:
                            # Get assignee email if available
                            assignee_email = issue.get('assignee', {}).get('email') if issue.get('assignee') else None
                            
                            result = supabase.table('tasks').upsert({
                                'id': issue.get('id'),
                                'org_id': org_id,
                                'title': issue.get('title'),
                                'description': issue.get('description', ''),
                                'status': task_data['status'],
                                'priority': task_data['priority'],
                                'due_date': issue.get('dueDate'),
                                'assigned_to_email': assignee_email,
                                'linear_issue_id': issue.get('identifier'),
                                'source': 'linear',
                                'last_synced_to_linear_at': datetime.utcnow().isoformat(),
                                'sync_enabled': True
                            }, on_conflict='id').execute()
                            print(f"  ✅ Synced to DB: {issue.get('title')[:40]}...")
                        except Exception as e:
                            print(f"  ❌ DB sync error: {str(e)[:100]}")
                    
                    tasks.append(task_data)
                
                print(f"✅ Fetched and synced {len(tasks)} tasks from Linear")
                return tasks
            else:
                print(f"Linear API error: {response.status_code}")
                return []
                
    except Exception as e:
        print(f"Error fetching Linear tasks: {e}")
        return []


def map_linear_priority(priority_num):
    """Map Linear priority (0-4) to our format."""
    priority_map = {
        0: 'none',
        1: 'low',
        2: 'medium',
        3: 'high',
        4: 'urgent'
    }
    return priority_map.get(priority_num, 'medium')


def map_linear_status(status_name):
    """Map Linear status names to our kanban columns."""
    status_name_lower = status_name.lower()
    
    if any(x in status_name_lower for x in ['backlog', 'icebox', 'triage']):
        return 'backlog'
    elif any(x in status_name_lower for x in ['todo', 'planned', 'ready']):
        return 'todo'
    elif any(x in status_name_lower for x in ['progress', 'started', 'doing']):
        return 'in_progress'
    elif any(x in status_name_lower for x in ['done', 'completed', 'canceled', 'closed']):
        return 'done'
    else:
        return 'todo'


@router.post("/building/sync-linear")
async def sync_linear_tasks():
    """Manual sync button - fetch latest tasks from Linear."""
    tasks = await fetch_linear_tasks()
    
    return {
        "success": True,
        "tasks_synced": len(tasks),
        "message": f"Synced {len(tasks)} tasks from Linear"
    }


async def update_linear_issue_status(issue_id: str, new_status: str) -> bool:
    """Update Linear issue status via GraphQL API."""
    try:
        if not settings.linear_api_key:
            print("Linear API key not configured")
            return False
        
        # Map our status to Linear state names
        status_map = {
            'backlog': 'Backlog',
            'todo': 'Todo',
            'in_progress': 'In Progress',
            'done': 'Done',
            'canceled': 'Canceled'
        }
        
        state_name = status_map.get(new_status, 'Todo')
        
        # First, get the team's workflow states to find the correct state ID
        query = """
        query {
          workflowStates {
            nodes {
              id
              name
            }
          }
        }
        """
        
        async with httpx.AsyncClient() as client:
            # Get workflow states
            response = await client.post(
                'https://api.linear.app/graphql',
                json={'query': query},
                headers={
                    'Authorization': settings.linear_api_key,
                    'Content-Type': 'application/json'
                },
                timeout=10.0
            )
            
            if response.status_code != 200:
                return False
            
            states = response.json().get('data', {}).get('workflowStates', {}).get('nodes', [])
            state_id = next((s['id'] for s in states if s['name'].lower() == state_name.lower()), None)
            
            if not state_id:
                print(f"Could not find Linear state for: {state_name}")
                return False
            
            # Update the issue status
            mutation = """
            mutation UpdateIssueState($issueId: String!, $stateId: String!) {
                issueUpdate(
                    id: $issueId
                    input: { stateId: $stateId }
                ) {
                    success
                }
            }
            """
            
            response = await client.post(
                'https://api.linear.app/graphql',
                json={
                    'query': mutation,
                    'variables': {'issueId': issue_id, 'stateId': state_id}
                },
                headers={
                    'Authorization': settings.linear_api_key,
                    'Content-Type': 'application/json'
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', {}).get('issueUpdate', {}).get('success', False)
            else:
                return False
                
    except Exception as e:
        print(f"Error updating Linear issue status: {e}")
        return False


@router.post("/building/update-task-status")
async def update_task_status(request: Request):
    """Update task status when dragged to a new column. Two-way sync with Linear."""
    
    try:
        body = await request.json()
        
        task_id = body.get('task_id')
        linear_id = body.get('linear_id')
        new_status = body.get('new_status')
        
        if not task_id or not new_status:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "task_id and new_status required"}
            )
        
        # If this is a Linear task, sync status to Linear
        synced_to_linear = False
        if linear_id:
            print(f"Syncing status to Linear: {linear_id} -> {new_status}")
            synced_to_linear = await update_linear_issue_status(linear_id, new_status)
            
            if synced_to_linear:
                print(f"✅ Status synced to Linear successfully")
            else:
                print(f"⚠️ Failed to sync to Linear, but continuing...")
        
        # Update in database (try both tables)
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        updated = False
        try:
            # Try tasks table first
            try:
                result = supabase.table('tasks').update({
                    'status': new_status,
                    'updated_at': datetime.utcnow().isoformat(),
                    'last_synced_to_linear_at': datetime.utcnow().isoformat() if synced_to_linear else None
                }).eq('id', task_id).execute()
                if result.data and len(result.data) > 0:
                    updated = True
            except Exception as e:
                print(f"tasks table not available: {e}")
            
            # Try action_items as fallback
            if not updated:
                result = supabase.table('action_items').update({
                    'status': new_status,
                    'updated_at': datetime.utcnow().isoformat()
                }).eq('id', task_id).execute()
                if result.data and len(result.data) > 0:
                    updated = True
        except Exception as e:
            print(f"Database update error: {e}")
        
        return JSONResponse(content={
            "success": True,
            "task_id": task_id,
            "new_status": new_status,
            "synced_to_linear": synced_to_linear,
            "message": f"Task moved to {new_status.replace('_', ' ').title()}" + 
                      (" (synced to Linear)" if synced_to_linear else "")
        })
        
    except Exception as e:
        print(f"Error updating task status: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


async def update_linear_issue(issue_id: str, updates: dict) -> bool:
    """Update a Linear issue via GraphQL API."""
    try:
        if not settings.linear_api_key:
            print("Linear API key not configured")
            return False
        
        # Build mutation based on what's being updated
        mutations = []
        variables = {"issueId": issue_id}
        
        if 'title' in updates:
            mutations.append('title: $title')
            variables['title'] = updates['title']
        
        if 'description' in updates:
            mutations.append('description: $description')
            variables['description'] = updates['description']
        
        if 'priority' in updates:
            # Map our priority to Linear's 0-4 scale
            priority_map = {'none': 0, 'low': 1, 'medium': 2, 'high': 3, 'urgent': 4}
            mutations.append('priority: $priority')
            variables['priority'] = priority_map.get(updates['priority'], 2)
        
        if not mutations:
            return True  # Nothing to update
        
        # Build GraphQL mutation
        mutation = f"""
        mutation UpdateIssue(
            $issueId: String!
            {"$title: String" if 'title' in updates else ""}
            {"$description: String" if 'description' in updates else ""}
            {"$priority: Int" if 'priority' in updates else ""}
        ) {{
            issueUpdate(
                id: $issueId
                input: {{ {', '.join(mutations)} }}
            ) {{
                success
                issue {{
                    id
                    title
                }}
            }}
        }}
        """
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://api.linear.app/graphql',
                json={'query': mutation, 'variables': variables},
                headers={
                    'Authorization': settings.linear_api_key,
                    'Content-Type': 'application/json'
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', {}).get('issueUpdate', {}).get('success', False)
            else:
                print(f"Linear API error: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"Error updating Linear issue: {e}")
        return False


@router.get("/building/company-activities/{company_id}")
async def get_company_activities(company_id: str):
    """Fetch activities/deals for a specific portfolio company from Pipedrive."""
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Special case for DV - return Linear tasks
        if company_id == 'dv':
            linear_tasks = await fetch_linear_tasks()
            if not linear_tasks:
                db_tasks = supabase.table('action_items').select('*').order('created_at', desc=True).limit(50).execute().data
                linear_tasks = db_tasks
            
            # Organize by status
            activities_columns = {
                'backlog': [t for t in linear_tasks if t.get('status') in ['backlog', 'Backlog']],
                'todo': [t for t in linear_tasks if t.get('status') in ['todo', 'To Do']],
                'in_progress': [t for t in linear_tasks if t.get('status') in ['in_progress', 'In Progress']],
                'done': [t for t in linear_tasks if t.get('status') in ['done', 'Done', 'Completed']]
            }
            
            return JSONResponse(content={
                "success": True,
                "columns": activities_columns,
                "source": "linear"
            })
        
        # For portfolio companies, get Pipedrive integration
        integration = supabase.table('portfolio_company_integrations') \
            .select('*') \
            .eq('portfolio_company_id', company_id) \
            .eq('integration_type', 'pipedrive') \
            .eq('is_active', True) \
            .execute()
        
        if not integration.data:
            return JSONResponse(content={
                "success": False,
                "error": "No Pipedrive integration found for this company",
                "columns": {'backlog': [], 'todo': [], 'in_progress': [], 'done': []}
            })
        
        # Get decryption key and decrypt API token
        from cryptography.fernet import Fernet
        fernet = Fernet(settings.encryption_key.encode())
        encrypted_token = integration.data[0].get('api_token_encrypted', '')
        api_token = fernet.decrypt(encrypted_token.encode()).decode()
        
        # Fetch deals from Pipedrive
        from app.integrations.pipedrive_client import PipedriveClient
        pipedrive = PipedriveClient(api_token=api_token)
        deals = await pipedrive.get_deals(status="all_not_deleted", limit=100)
        
        # Organize deals by stage (map to our columns)
        columns = {'backlog': [], 'todo': [], 'in_progress': [], 'done': []}
        
        for deal in deals:
            stage_name = deal.get('stage_name', '').lower()
            status_mapping = {
                'backlog': 'backlog',
                'lead': 'todo',
                'qualified': 'todo',
                'meeting': 'in_progress',
                'demo': 'in_progress',
                'proposal': 'in_progress',
                'negotiation': 'in_progress',
                'closed won': 'done',
                'won': 'done'
            }
            
            # Map stage to column
            column = 'backlog'
            for key, value in status_mapping.items():
                if key in stage_name:
                    column = value
                    break
            
            # Format deal as task
            task = {
                'id': str(deal.get('id')),
                'title': deal.get('title', 'Untitled Deal'),
                'description': f"Value: {deal.get('value', 0):,.0f} {deal.get('currency', 'SEK')}\nOrg: {deal.get('org_name', 'N/A')}",
                'status': column,
                'priority': 'medium',
                'tags': [deal.get('stage_name', 'Unknown')],
                'organization': deal.get('org_name', ''),
                'value': deal.get('value', 0),
                'currency': deal.get('currency', 'SEK')
            }
            
            columns[column].append(task)
        
        return JSONResponse(content={
            "success": True,
            "columns": columns,
            "source": "pipedrive",
            "total_deals": len(deals)
        })
        
    except Exception as e:
        print(f"Error fetching company activities: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


@router.post("/building/update-task")
async def update_task(request: Request):
    """Update task details from the task panel. Supports two-way sync with Linear."""
    
    try:
        body = await request.json()
        
        task_id = body.get('task_id')
        linear_id = body.get('linear_id')
        updates = body.get('updates', {})
        
        if not task_id:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "task_id required"}
            )
        
        if not updates:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "No updates provided"}
            )
        
        # For Linear tasks, sync directly to Linear API only
        if linear_id:
            print(f"📝 Updating Linear task: {linear_id}")
            synced_to_linear = await update_linear_issue(linear_id, updates)
            
            if synced_to_linear:
                print(f"✅ Changes synced to Linear successfully")
                return JSONResponse(content={
                    "success": True,
                    "task_id": task_id,
                    "linear_id": linear_id,
                    "message": "Task updated in Linear successfully",
                    "synced_to_linear": True,
                    "updated_fields": list(updates.keys())
                })
            else:
                print(f"❌ Failed to sync to Linear")
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "error": "Failed to update Linear task"}
                )
        
        # For non-Linear tasks (action_items), update database
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        updates['updated_at'] = datetime.utcnow().isoformat()
        
        try:
            result = supabase.table('action_items').update(updates).eq('id', task_id).execute()
            
            if result.data and len(result.data) > 0:
                return JSONResponse(content={
                    "success": True,
                    "task_id": task_id,
                    "message": "Task updated successfully",
                    "updated_fields": list(updates.keys())
                })
            else:
                return JSONResponse(
                    status_code=404,
                    content={"success": False, "error": "Task not found"}
                )
        except Exception as e:
            print(f"Error updating task: {e}")
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": str(e)}
            )
        
    except Exception as e:
        print(f"Error updating task: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


def generate_timeline_view(columns):
    """Generate Asana-style timeline view."""
    from datetime import datetime, timedelta
    
    # Get all tasks with dates
    all_tasks = []
    for status_tasks in columns.values():
        all_tasks.extend(status_tasks)
    
    # Filter tasks with due dates
    tasks_with_dates = [t for t in all_tasks if t.get('due_date')]
    
    if not tasks_with_dates:
        return '<div class="empty-state"><div class="empty-state-title">No tasks with deadlines</div><p style="font-size: 13px; color: var(--gray-500); margin-top: 8px;">Add due dates to tasks to see them in timeline view.</p></div>'
    
    # Sort by due date
    tasks_with_dates.sort(key=lambda t: t.get('due_date', ''))
    
    # Generate timeline header (next 3 months)
    today = datetime.now()
    months = []
    for i in range(3):
        month_date = today + timedelta(days=30*i)
        months.append(month_date.strftime('%B %Y'))
    
    # Generate timeline HTML
    html = f'''
    <div class="timeline-header">
        <div style="font-size: 12px; font-weight: 600; color: var(--gray-700);">TASK</div>
        <div class="timeline-months">
            {' '.join([f'<div class="timeline-month">{month}</div>' for month in months])}
        </div>
    </div>
    
    <div class="timeline-tasks">
    '''
    
    for task in tasks_with_dates:
        assignee = task.get('owner_name', 'Unassigned')
        initials = ''.join([n[0].upper() for n in assignee.split()[:2]]) if assignee != 'Unassigned' else '?'
        due_date = task.get('due_date', '')
        
        # Calculate position and width
        try:
            task_date = datetime.fromisoformat(str(due_date)[:10])
            days_from_now = (task_date - today).days
            
            # Position as percentage (90 days = 100%)
            position = max(0, min(100, (days_from_now / 90) * 100))
            width = 10  # Default width in percentage
            
        except:
            position = 0
            width = 10
        
        html += f'''
        <div class="timeline-task">
            <div class="timeline-task-info">
                <div class="timeline-task-name">{task.get('title', 'Untitled')[:40]}</div>
                <div class="timeline-task-meta">
                    <span style="width: 18px; height: 18px; border-radius: 50%; background: var(--gray-200); display: inline-flex; align-items: center; justify-content: center; font-size: 9px; font-weight: 600; color: var(--gray-700); margin-right: 4px;">{initials}</span>
                    {assignee}
                </div>
            </div>
            <div class="timeline-bar-container">
                <div class="timeline-bar" style="left: {position}%; width: {width}%;" title="{task.get('title', '')}">
                    {str(due_date)[:10]}
                </div>
            </div>
        </div>
        '''
    
    html += '</div>'
    
    return html



