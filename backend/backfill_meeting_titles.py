"""
Backfill display_title for meetings with messy titles.
Standalone script - no app dependencies.
"""

import os
import re
from datetime import datetime


def load_env():
    """Load environment variables from env.local.configured"""
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
    Clean and standardize meeting title for display.
    Improved version that preserves meaning.
    """
    original = title
    
    # Split by underscores and double underscores
    parts = re.split(r'__+|_', title)
    
    # Extract dates and remove them from parts
    dates_found = []
    cleaned_parts = []
    
    for part in parts:
        # Check if this part is a date
        date_match = re.search(r'(\d{4})-?(\d{2})-?(\d{2})', part)
        if date_match:
            try:
                year, month, day = date_match.groups()
                date_obj = datetime(int(year), int(month), int(day))
                dates_found.append(date_obj.strftime("%b %d, %Y"))
            except:
                pass
            # Remove just the date part, keep the rest
            part = re.sub(r'\d{4}-?\d{2}-?\d{2}', '', part).strip(' -_,')
        
        if part.strip():
            cleaned_parts.append(part.strip())
    
    # Remove duplicates while preserving order (case-insensitive)
    seen = set()
    unique_parts = []
    for part in cleaned_parts:
        part_lower = part.lower().strip(' ,.')
        if part_lower and part_lower not in seen and len(part_lower) > 1:
            seen.add(part_lower)
            unique_parts.append(part)
    
    # Keep only the first non-empty part as main subject
    if unique_parts:
        main_part = unique_parts[0]
        
        # Remove common prefixes
        main_part = re.sub(r'^(IK|ik|Möte|möte|Meeting|meeting|Online|online)\s*[,_-]?\s*', '', main_part, flags=re.IGNORECASE)
        
        # Replace underscores with spaces
        main_part = main_part.replace('_', ' ')
        
        # Clean up multiple spaces
        main_part = re.sub(r'\s+', ' ', main_part).strip()
        
        # Capitalize if needed
        if main_part and not main_part[0].isupper():
            main_part = main_part.title()
        
        result = main_part
    else:
        result = title
    
    # Add date if found (use first unique date)
    if dates_found:
        unique_dates = list(dict.fromkeys(dates_found))  # Remove duplicates
        if unique_dates:
            result += f" - {unique_dates[0]}"
    
    # Limit length
    if len(result) > 100:
        result = result[:97] + '...'
    
    # Fallback to original if result is too short
    if len(result) < 5:
        result = original
    
    return result


def backfill_meeting_titles(dry_run=False):
    """Backfill display_title for all meetings."""
    
    # Load environment
    load_env()
    
    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        return
    
    try:
        from supabase import create_client
    except ImportError:
        print("❌ Error: supabase-py not installed")
        print("   Run: pip install supabase")
        return
    
    print("=" * 80)
    print("BACKFILL DISPLAY_TITLE FOR MEETINGS")
    print("=" * 80)
    print()
    
    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        print()
    
    # Connect to Supabase
    print("📡 Connecting to Supabase...")
    supabase = create_client(supabase_url, supabase_key)
    
    # Fetch meetings without display_title
    print("📥 Fetching meetings without display_title...")
    try:
        response = supabase.table('meetings')\
            .select('id, title, meeting_date')\
            .is_('display_title', 'null')\
            .execute()
        meetings = response.data
    except Exception as e:
        print(f"❌ Error fetching meetings: {e}")
        return
    
    if not meetings:
        print("✅ No meetings need updating. All meetings have display_title set!")
        print()
        return
    
    print(f"Found {len(meetings)} meetings to update")
    print()
    
    # Process each meeting
    print("-" * 80)
    print(f"{'ORIGINAL TITLE':<60} | {'CLEANED TITLE':<40}")
    print("-" * 80)
    
    updated_count = 0
    failed_count = 0
    
    for meeting in meetings:
        meeting_id = meeting['id']
        title = meeting['title']
        
        # Clean the title
        cleaned_title = clean_meeting_title(title)
        
        # Display the transformation
        title_short = title[:57] + "..." if len(title) > 57 else title
        cleaned_short = cleaned_title[:37] + "..." if len(cleaned_title) > 37 else cleaned_title
        
        print(f"{title_short:<60} | {cleaned_short:<40}")
        
        # Update if not dry run
        if not dry_run:
            try:
                supabase.table('meetings')\
                    .update({'display_title': cleaned_title})\
                    .eq('id', meeting_id)\
                    .execute()
                updated_count += 1
            except Exception as e:
                print(f"  ✗ Error: {e}")
                failed_count += 1
        else:
            updated_count += 1
    
    print("-" * 80)
    print()
    
    # Summary
    if dry_run:
        print("🔍 DRY RUN SUMMARY:")
        print(f"   Would update: {updated_count} meetings")
    else:
        print("✅ UPDATE COMPLETE:")
        print(f"   Successfully updated: {updated_count} meetings")
        if failed_count > 0:
            print(f"   Failed: {failed_count} meetings")
    
    print()
    print("=" * 80)
    print()
    print("💡 TIP: Update your UI to use 'display_title || title'")
    print("   Example: <h3>{meeting.display_title || meeting.title}</h3>")
    print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Backfill display_title for meetings')
    parser.add_argument('--dry-run', action='store_true', help='Preview without making changes')
    parser.add_argument('--run', action='store_true', help='Actually run the backfill')
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.run:
        print("Use --dry-run to preview or --run to apply changes")
        exit(0)
    
    try:
        backfill_meeting_titles(dry_run=args.dry_run)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


