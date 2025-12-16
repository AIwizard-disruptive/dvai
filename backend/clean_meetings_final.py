"""
Final version - Clean meeting titles properly
Based on actual examples from screenshot
"""

import os
import re
from datetime import datetime


def load_env():
    env_file = 'env.local.configured'
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip('"').strip("'")


def clean_meeting_title(title):
    """
    Clean meeting title - final version.
    
    Examples:
    "IK_Disruptive_Ventures_möte_20231005_10-05__IK, Disruptive Ventures"
    -> "Disruptive Ventures - Oct 5, 2023"
    
    "Möte_2023-10-04_Serge_Guelnoji_Peo__2023-10-04__serge _ guelnoji _ peo"
    -> "Serge Guelnoji - Oct 4, 2023"
    
    "Online_Partner_disruptiveventures_Gemini Enterprise SKU, Online Part"
    -> "Gemini Enterprise SKU"
    
    "Pokalen_styrelsemöte_2023-11-15__2023-11-15__Styrelsen"
    -> "Pokalen Board Meeting - Nov 15, 2023"
    
    "High-Level Plan to AI-ify Disruptive Ventures"
    -> "High-Level Plan to AI-ify Disruptive Ventures"
    
    "Veckomöte - Team Meeting (Marcus intro, AI-projekt, uppföljningar)"
    -> "Team Meeting - Weekly"
    """
    
    original = title
    
    # If it's already clean (has parentheses, proper spacing), keep it mostly
    if '(' in title and ')' in title and title.count('_') < 3:
        # Just extract the main part before parentheses
        main = title.split('(')[0].strip(' -')
        return main if len(main) > 10 else title
    
    # Extract all dates first
    dates = []
    for match in re.finditer(r'(\d{4})[-/]?(\d{2})[-/]?(\d{2})', title):
        try:
            year, month, day = match.groups()
            date_obj = datetime(int(year), int(month), int(day))
            dates.append(date_obj.strftime("%b %d, %Y"))
        except:
            pass
    
    # Remove file extension
    title = re.sub(r'\.(ics|pdf|docx?)$', '', title, flags=re.IGNORECASE)
    
    # Split by __ first (strong delimiter)
    parts = title.split('__')
    
    # Use the first meaningful part
    main_part = parts[0] if parts else title
    
    # Split by single underscore
    tokens = main_part.split('_')
    
    # Remove dates and times from tokens
    clean_tokens = []
    for token in tokens:
        # Skip pure dates
        if re.match(r'^\d{4}-?\d{2}-?\d{2}$', token):
            continue
        # Skip times
        if re.match(r'^\d{2}[-:]\d{2}$', token):
            continue
        # Skip very short tokens
        if len(token) < 2:
            continue
        # Skip common prefixes at start
        if token.lower() in ['ik', 'möte', 'meeting'] and not clean_tokens:
            continue
        
        clean_tokens.append(token)
    
    # Join tokens with spaces
    result = ' '.join(clean_tokens)
    
    # Handle special Swedish meeting types
    if 'styrelsemöte' in result.lower():
        result = result.replace('styrelsemöte', 'Board Meeting')
        result = result.replace('Styrelsemöte', 'Board Meeting')
    
    if result.lower().startswith('veckomöte'):
        result = result.replace('Veckomöte', 'Weekly Meeting')
        result = result.replace('veckomöte', 'Weekly Meeting')
    
    # Capitalize first letter
    if result and not result[0].isupper():
        result = result[0].upper() + result[1:]
    
    # Add date if found
    if dates:
        result += f" - {dates[0]}"
    
    # Clean up
    result = result.strip(' -_,')
    
    # If result is too short or empty, return original
    if len(result) < 5:
        return original
    
    # Limit length
    if len(result) > 100:
        result = result[:97] + '...'
    
    return result


def main():
    load_env()
    
    from supabase import create_client
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    print("=" * 80)
    print("CLEAN MEETING TITLES - FINAL VERSION")
    print("=" * 80)
    print()
    
    supabase = create_client(supabase_url, supabase_key)
    
    # Get all meetings
    response = supabase.table('meetings').select('id, title').execute()
    meetings = response.data
    
    print(f"Found {len(meetings)} meetings")
    print()
    print("-" * 80)
    print(f"{'ORIGINAL':<60} | {'CLEANED':<40}")
    print("-" * 80)
    
    for meeting in meetings:
        original = meeting['title']
        cleaned = clean_meeting_title(original)
        
        orig_short = original[:57] + "..." if len(original) > 57 else original
        clean_short = cleaned[:37] + "..." if len(cleaned) > 37 else cleaned
        
        print(f"{orig_short:<60} | {clean_short:<40}")
        
        # Update
        supabase.table('meetings').update({'display_title': cleaned}).eq('id', meeting['id']).execute()
    
    print("-" * 80)
    print()
    print("✅ All meetings updated!")
    print()


if __name__ == "__main__":
    main()

