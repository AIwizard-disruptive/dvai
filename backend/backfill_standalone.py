"""
Standalone backfill script for display_name.
No dependencies on app code - uses environment variables directly.
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


def clean_document_name(filename):
    """
    Clean and standardize document name for display.
    Simplified version that works standalone.
    """
    # Remove file extension
    name_no_ext = re.sub(r'\.[^.]+$', '', filename)
    
    # Split by common delimiters
    parts = re.split(r'[_\-\s]+|__+', name_no_ext)
    
    # Remove empty parts
    filtered_parts = []
    seen_parts = set()
    common_prefixes = {'ik', 'möte', 'meeting', 'online', 'partner'}
    
    date_str = None
    names = []
    meeting_type = None
    
    for part in parts:
        part_clean = part.strip().strip(',')
        part_lower = part_clean.lower()
        
        # Skip empty or very short parts
        if not part_clean or len(part_clean) < 2:
            continue
        
        # Extract date
        date_match = re.match(r'(\d{4})[-/]?(\d{2})[-/]?(\d{2})', part_clean)
        if date_match:
            try:
                year, month, day = date_match.groups()
                date_obj = datetime(int(year), int(month), int(day))
                date_str = date_obj.strftime("%b %d, %Y")
            except ValueError:
                pass
            continue
        
        # Identify meeting types
        if part_lower in ['möte', 'meeting', 'intro', 'call', 'discussion']:
            meeting_type = 'Meeting'
            continue
        
        # Skip common prefixes and duplicates
        if part_lower in common_prefixes:
            continue
        
        # Check for duplicates (case-insensitive)
        if part_lower not in seen_parts:
            seen_parts.add(part_lower)
            
            # Capitalize properly
            if part_clean.isupper() or part_clean.islower():
                part_clean = part_clean.title()
            
            names.append(part_clean)
    
    # Build final name
    result_parts = []
    
    if names:
        primary = names[0]
        result_parts.append(primary)
        
        if meeting_type:
            result_parts.append(meeting_type)
        
        if len(names) > 1:
            additional = ', '.join(names[1:3])
            if additional.lower() not in primary.lower():
                result_parts.append(f"({additional})")
    elif meeting_type:
        result_parts.append(meeting_type)
    
    # Build final string
    final_name = ' - '.join(result_parts) if result_parts else 'Document'
    
    # Add date if found
    if date_str:
        final_name += f" - {date_str}"
    
    # Clean up
    final_name = re.sub(r'\s+', ' ', final_name)
    final_name = re.sub(r'\s*-\s*-\s*', ' - ', final_name)
    final_name = final_name.strip(' -')
    
    # Limit length
    if len(final_name) > 100:
        final_name = final_name[:97] + '...'
    
    return final_name


def backfill_display_names(dry_run=False):
    """Backfill display_name for all documents."""
    
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
    print("BACKFILL DISPLAY NAMES FOR EXISTING DOCUMENTS")
    print("=" * 80)
    print()
    
    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        print()
    
    # Connect to Supabase
    print("📡 Connecting to Supabase...")
    supabase = create_client(supabase_url, supabase_key)
    
    # Fetch documents without display_name
    print("📥 Fetching documents without display_name...")
    try:
        response = supabase.table('uploaded_documents')\
            .select('id, filename, org_id')\
            .is_('display_name', 'null')\
            .execute()
        documents = response.data
    except Exception as e:
        print(f"❌ Error fetching documents: {e}")
        return
    
    if not documents:
        print("✅ No documents need updating. All documents have display_name set!")
        print()
        return
    
    print(f"Found {len(documents)} documents to update")
    print()
    
    # Process each document
    print("-" * 80)
    print(f"{'ORIGINAL FILENAME':<50} | {'CLEANED NAME':<40}")
    print("-" * 80)
    
    updated_count = 0
    failed_count = 0
    
    for doc in documents:
        doc_id = doc['id']
        filename = doc['filename']
        
        # Clean the filename
        cleaned_name = clean_document_name(filename)
        
        # Display the transformation
        filename_short = filename[:47] + "..." if len(filename) > 47 else filename
        cleaned_short = cleaned_name[:37] + "..." if len(cleaned_name) > 37 else cleaned_name
        
        print(f"{filename_short:<50} | {cleaned_short:<40}")
        
        # Update if not dry run
        if not dry_run:
            try:
                supabase.table('uploaded_documents')\
                    .update({'display_name': cleaned_name})\
                    .eq('id', doc_id)\
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
        print(f"   Would update: {updated_count} documents")
    else:
        print("✅ UPDATE COMPLETE:")
        print(f"   Successfully updated: {updated_count} documents")
        if failed_count > 0:
            print(f"   Failed: {failed_count} documents")
    
    print()
    print("=" * 80)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Backfill display_name for existing documents')
    parser.add_argument('--dry-run', action='store_true', help='Preview without making changes')
    parser.add_argument('--run', action='store_true', help='Actually run the backfill')
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.run:
        print("Use --dry-run to preview or --run to apply changes")
        exit(0)
    
    try:
        backfill_display_names(dry_run=args.dry_run)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


