"""
Simple backfill script for display_name using Supabase directly.
No dependencies on SQLAlchemy or complex imports.
"""

import sys
import os

# Add parent to path
sys.path.insert(0, '.')

from supabase import create_client
from app.config import settings
from app.services.document import DocumentService


def backfill_display_names(dry_run=False):
    """Backfill display_name for all documents."""
    
    print("=" * 80)
    print("BACKFILL DISPLAY NAMES FOR EXISTING DOCUMENTS")
    print("=" * 80)
    print()
    
    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        print()
    
    # Connect to Supabase
    print("📡 Connecting to Supabase...")
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    # Fetch documents without display_name
    print("📥 Fetching documents without display_name...")
    response = supabase.table('uploaded_documents')\
        .select('id, filename, org_id')\
        .is_('display_name', 'null')\
        .execute()
    
    documents = response.data
    
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
        cleaned_name = DocumentService.clean_document_name(filename)
        
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
    
    args = parser.parse_args()
    
    try:
        backfill_display_names(dry_run=args.dry_run)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("  1. You're in the backend directory")
        print("  2. SUPABASE_URL and SUPABASE_SERVICE_KEY are set")
        print("  3. Migration 014 has been run")
        sys.exit(1)

