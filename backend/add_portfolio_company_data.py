"""
Add Sample Data for Portfolio Companies
========================================
This script adds sample activities, dealflow, and financial data for portfolio companies.
"""

import asyncio
from datetime import date, datetime, timedelta
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


# Sample activities for each company
ACTIVITY_TEMPLATES = [
    {
        "type": "Product Development",
        "tasks": [
            "Complete v2.0 feature specifications",
            "Launch beta testing program",
            "Fix critical bugs reported by users",
            "Implement customer feedback from Q4",
        ]
    },
    {
        "type": "Sales & Marketing",
        "tasks": [
            "Prepare pitch deck for Series A",
            "Launch social media campaign",
            "Follow up with potential customers",
            "Attend industry conference",
        ]
    },
    {
        "type": "Operations",
        "tasks": [
            "Hire new senior developer",
            "Review Q4 financial reports",
            "Update investor dashboard",
            "Prepare board meeting materials",
        ]
    },
]


# Sample dealflow stages for portfolio companies
DEALFLOW_TEMPLATES = [
    {
        "title": "Series A Preparation",
        "stage": "qualified",
        "amount": "5000000",
        "notes": "Preparing documentation and financial projections"
    },
    {
        "title": "Strategic Partnership - Tech Corp",
        "stage": "meeting",
        "amount": "2000000",
        "notes": "Initial discussions ongoing"
    },
    {
        "title": "Government Grant Application",
        "stage": "proposal",
        "amount": "500000",
        "notes": "Submitted, awaiting response"
    },
]


# Sample financial items
FINANCIAL_TEMPLATES = [
    {
        "type": "Revenue",
        "items": [
            {"description": "Q4 Subscription Revenue", "amount": 45000, "status": "reconciled"},
            {"description": "Q1 Subscription Revenue (Projected)", "amount": 52000, "status": "draft"},
        ]
    },
    {
        "type": "Expenses",
        "items": [
            {"description": "Payroll - December", "amount": -35000, "status": "paid"},
            {"description": "Cloud Infrastructure", "amount": -5000, "status": "paid"},
            {"description": "Marketing Campaign", "amount": -8000, "status": "sent"},
        ]
    },
]


async def add_portfolio_data():
    """Add sample data for portfolio companies."""
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        print("❌ Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set")
        return
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    
    print("🚀 Adding sample data for portfolio companies...\n")
    
    # Get DV org_id
    orgs_result = supabase.table('orgs').select('*').execute()
    dv_org = None
    
    if orgs_result.data:
        for org in orgs_result.data:
            if 'disruptive' in org.get('name', '').lower():
                dv_org = org
                break
        if not dv_org:
            dv_org = orgs_result.data[0]
    else:
        print("❌ Error: No organizations found in orgs table")
        return
    
    dv_org_id = dv_org['id']
    
    # Get all portfolio companies
    portfolio_result = supabase.table('portfolio_companies') \
        .select('*, organizations(*)') \
        .eq('status', 'active') \
        .execute()
    
    if not portfolio_result.data:
        print("❌ Error: No portfolio companies found")
        return
    
    print(f"📦 Found {len(portfolio_result.data)} portfolio companies\n")
    
    # Get current user for assignments
    people_result = supabase.table('people').select('*').execute()
    current_user = None
    if people_result.data:
        for person in people_result.data:
            if 'marcus' in person.get('name', '').lower() or 'markus' in person.get('name', '').lower():
                current_user = person
                break
        if not current_user:
            current_user = people_result.data[0]
    
    user_id = current_user['id'] if current_user else None
    
    # Process each portfolio company
    for pc in portfolio_result.data:
        org = pc.get('organizations', {})
        company_name = org.get('name', 'Unknown')
        org_id = pc['organization_id']
        
        print(f"📊 Adding data for: {company_name}")
        
        # 1. Add Activities (as action_items)
        print(f"   → Adding activities...")
        activities_added = 0
        
        for activity_type in ACTIVITY_TEMPLATES:
            # Pick 2 random tasks from this category
            tasks = random.sample(activity_type["tasks"], min(2, len(activity_type["tasks"])))
            
            for task_title in tasks:
                try:
                    # Random status
                    statuses = ['backlog', 'todo', 'in_progress', 'done']
                    status = random.choice(statuses)
                    
                    # Random due date (next 30 days)
                    due_date = date.today() + timedelta(days=random.randint(1, 30))
                    
                    action_data = {
                        'org_id': dv_org_id,
                        'title': task_title,
                        'status': status,
                        'priority': random.choice(['high', 'medium', 'low']),
                        'assignee_id': user_id,
                        'due_date': due_date.isoformat(),
                        'tags': [activity_type["type"], company_name],
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat(),
                    }
                    
                    result = supabase.table('action_items').insert(action_data).execute()
                    if result.data:
                        activities_added += 1
                except Exception as e:
                    print(f"      ⚠️  Error adding task: {e}")
        
        print(f"   ✅ Added {activities_added} activities")
        
        # 2. Add Portfolio Targets (for the company)
        print(f"   → Adding targets...")
        targets_added = 0
        
        target_categories = [
            {
                "category": "Revenue",
                "name": "Monthly Recurring Revenue",
                "target": 100000,
                "current": 75000,
                "unit": "SEK"
            },
            {
                "category": "Growth",
                "name": "Customer Acquisition",
                "target": 50,
                "current": 32,
                "unit": "customers"
            },
            {
                "category": "Product",
                "name": "Feature Completion",
                "target": 100,
                "current": 65,
                "unit": "percent"
            },
        ]
        
        for target in target_categories:
            try:
                target_data = {
                    'portfolio_company_id': pc['id'],
                    'target_category': target['category'],
                    'target_name': target['name'],
                    'target_value': target['target'],
                    'current_value': target['current'],
                    'unit': target['unit'],
                    'deadline': (date.today() + timedelta(days=90)).isoformat(),
                    'is_critical': target['category'] == 'Revenue',
                    'progress_percentage': (target['current'] / target['target']) * 100,
                    'status': 'on_track' if target['current'] / target['target'] > 0.6 else 'at_risk',
                    'update_frequency': 'weekly',
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat(),
                }
                
                result = supabase.table('portfolio_targets').insert(target_data).execute()
                if result.data:
                    targets_added += 1
            except Exception as e:
                print(f"      ⚠️  Error adding target: {e}")
        
        print(f"   ✅ Added {targets_added} targets")
        
        print()
    
    print("\n" + "="*60)
    print("✅ Sample data has been added for all portfolio companies!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(add_portfolio_data())

