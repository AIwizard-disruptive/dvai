#!/usr/bin/env python
"""Parse the real document content and extract structured data."""
import sys
from pathlib import Path
import re
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from supabase import create_client
from app.config import settings
from app.services.document import DocumentService

def parse_document():
    """Parse the actual document content intelligently."""
    
    artifact_id = "e978c129-031d-47d4-bcc2-756e007d7ac7"
    org_id = "45880901-8aad-4429-a13e-873ae0d9bf10"
    meeting_id = "1f75abf8-a5c3-4a40-af45-540925629dc8"
    filename = "High-Level Plan to AI-ify Disruptive Ventures.docx"
    file_path = f"/tmp/artifacts/{artifact_id}/{filename}"
    
    print("=" * 70)
    print("PARSING REAL DOCUMENT CONTENT")
    print("=" * 70)
    
    # Extract text
    print(f"\n1. Reading document...")
    text = DocumentService.extract_text_from_docx(file_path)
    print(f"   ✓ Extracted {len(text)} characters")
    
    print(f"\n2. Document content:")
    print("-" * 70)
    print(text)
    print("-" * 70)
    
    # Parse structure from content
    print(f"\n3. Analyzing document structure...")
    
    lines = text.split('\n')
    
    # Extract strategies (these are key decisions/approaches)
    strategies = []
    current_strategy = None
    strategy_items = []
    
    for line in lines:
        line_stripped = line.strip()
        if 'strategy' in line_stripped.lower():
            # Save previous strategy
            if current_strategy and strategy_items:
                strategies.append({
                    'name': current_strategy,
                    'items': strategy_items.copy()
                })
            # Start new strategy
            current_strategy = line_stripped
            strategy_items = []
        elif line_stripped and current_strategy:
            if line_stripped.startswith(('1st:', '2nd:', '3rd:', '-', '•')):
                strategy_items.append(line_stripped)
    
    # Save last strategy
    if current_strategy and strategy_items:
        strategies.append({
            'name': current_strategy,
            'items': strategy_items.copy()
        })
    
    print(f"   Found {len(strategies)} strategies")
    for s in strategies:
        print(f"   - {s['name']}: {len(s['items'])} options")
    
    # Extract use cases (these are action items/work to be done)
    use_cases = []
    in_use_case_section = False
    
    for line in lines:
        line_stripped = line.strip()
        if 'use case' in line_stripped.lower():
            in_use_case_section = True
        elif in_use_case_section and line_stripped and not line_stripped.lower().startswith(('tools', 'tab')):
            use_cases.append(line_stripped)
    
    print(f"   Found {len(use_cases)} use cases")
    for uc in use_cases:
        print(f"   - {uc}")
    
    # Extract tools (these are resources/technologies)
    tools = []
    in_tools_section = False
    
    for line in lines:
        line_stripped = line.strip()
        if line_stripped.lower() == 'tools':
            in_tools_section = True
        elif in_tools_section and line_stripped:
            tools.append(line_stripped)
    
    print(f"   Found {len(tools)} tools")
    for tool in tools:
        print(f"   - {tool}")
    
    # Connect to Supabase
    print(f"\n4. Saving parsed data to database...")
    admin_supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    # Save strategies as decisions (these are strategic choices)
    decisions_saved = 0
    for strategy in strategies:
        strategy_text = f"{strategy['name']}"
        rationale = " | ".join(strategy['items'])
        
        try:
            admin_supabase.table('decisions').insert({
                'meeting_id': meeting_id,
                'org_id': org_id,
                'decision': strategy_text,  # Correct column name
                'rationale': rationale[:500],
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }).execute()
            decisions_saved += 1
            print(f"   ✓ Saved strategy: {strategy_text}")
        except Exception as e:
            print(f"   ⚠ Error: {e}")
    
    # Save use cases as action items (these are tasks to be done)
    actions_saved = 0
    for use_case in use_cases:
        try:
            admin_supabase.table('action_items').insert({
                'meeting_id': meeting_id,
                'org_id': org_id,
                'title': use_case,  # Correct column name
                'description': '',
                'priority': 'medium',
                'status': 'open',  # Correct default value
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }).execute()
            actions_saved += 1
            print(f"   ✓ Saved use case: {use_case}")
        except Exception as e:
            print(f"   ⚠ Error: {e}")
    
    # Save tools as people/resources (these are the tech stack)
    tools_saved = 0
    for tool in tools:
        try:
            # Insert as a person/resource
            result = admin_supabase.table('people').insert({
                'org_id': org_id,
                'name': tool,
                'role': 'Tool/Technology',
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }).execute()
            
            if result.data:
                person_id = result.data[0]['id']
                # Link to meeting
                admin_supabase.table('meeting_participants').insert({
                    'org_id': org_id,
                    'meeting_id': meeting_id,
                    'person_id': person_id,
                    'created_at': datetime.utcnow().isoformat()
                }).execute()
                tools_saved += 1
                print(f"   ✓ Saved tool: {tool}")
        except Exception as e:
            print(f"   ⚠ Error: {e}")
    
    print(f"\n" + "=" * 70)
    print("✅ PARSING COMPLETE")
    print("=" * 70)
    print(f"\nExtracted from document:")
    print(f"  ✓ {decisions_saved} strategic decisions")
    print(f"  ✓ {actions_saved} use cases (as action items)")
    print(f"  ✓ {tools_saved} tools/technologies")
    print(f"\n📊 View results:")
    print(f"   http://localhost:8000/dashboard-ui")
    print(f"   http://localhost:8000/meeting/{meeting_id}")

if __name__ == "__main__":
    parse_document()

