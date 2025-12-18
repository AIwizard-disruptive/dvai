"""
Backfill display_name for existing documents that don't have cleaned names.

This script updates all documents in the uploaded_documents table that have NULL
display_name values with automatically cleaned names.

Usage:
    python backfill_display_names.py
"""

import asyncio
import sys
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, '.')

from app.database import get_supabase_client
from app.services.document import DocumentService


async def get_documents_without_display_names() -> List[Dict[str, Any]]:
    """Fetch all documents that don't have display_name set."""
    supabase = get_supabase_client()
    
    try:
        # Query documents without display_name
        response = supabase.table('uploaded_documents')\
            .select('id, filename, org_id')\
            .is_('display_name', 'null')\
            .execute()
        
        return response.data
    except Exception as e:
        print(f"❌ Error fetching documents: {e}")
        return []


async def update_display_name(doc_id: str, cleaned_name: str) -> bool:
    """Update a single document's display_name."""
    supabase = get_supabase_client()
    
    try:
        response = supabase.table('uploaded_documents')\
            .update({'display_name': cleaned_name})\
            .eq('id', doc_id)\
            .execute()
        
        return True
    except Exception as e:
        print(f"❌ Error updating document {doc_id}: {e}")
        return False


async def backfill_all_display_names(dry_run: bool = False):
    """
    Backfill display_name for all documents that don't have it.
    
    Args:
        dry_run: If True, show what would be updated without making changes
    """
    print("=" * 80)
    print("BACKFILL DISPLAY NAMES FOR EXISTING DOCUMENTS")
    print("=" * 80)
    print()
    
    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        print()
    
    # Fetch documents
    print("📥 Fetching documents without display_name...")
    documents = await get_documents_without_display_names()
    
    if not documents:
        print("✅ No documents need updating. All documents have display_name set!")
        return
    
    print(f"Found {len(documents)} documents to update")
    print()
    
    # Process each document
    updated_count = 0
    failed_count = 0
    
    print("-" * 80)
    print(f"{'ORIGINAL FILENAME':<50} | {'CLEANED NAME':<40}")
    print("-" * 80)
    
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
            success = await update_display_name(doc_id, cleaned_name)
            if success:
                updated_count += 1
            else:
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


async def backfill_specific_org(org_id: str, dry_run: bool = False):
    """
    Backfill display_name for documents in a specific org.
    
    Args:
        org_id: Organization UUID
        dry_run: If True, show what would be updated without making changes
    """
    print("=" * 80)
    print(f"BACKFILL DISPLAY NAMES FOR ORG: {org_id}")
    print("=" * 80)
    print()
    
    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        print()
    
    supabase = get_supabase_client()
    
    try:
        # Query documents for specific org
        response = supabase.table('uploaded_documents')\
            .select('id, filename, org_id')\
            .eq('org_id', org_id)\
            .is_('display_name', 'null')\
            .execute()
        
        documents = response.data
    except Exception as e:
        print(f"❌ Error fetching documents: {e}")
        return
    
    if not documents:
        print("✅ No documents need updating for this org!")
        return
    
    print(f"Found {len(documents)} documents to update")
    print()
    
    # Process each document
    updated_count = 0
    failed_count = 0
    
    print("-" * 80)
    print(f"{'ORIGINAL FILENAME':<50} | {'CLEANED NAME':<40}")
    print("-" * 80)
    
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
            success = await update_display_name(doc_id, cleaned_name)
            if success:
                updated_count += 1
            else:
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


async def show_examples():
    """Show examples of name cleaning without updating database."""
    test_filenames = [
        "IK_Disruptive_Ventures_möte_20231005_10-05__IK, Disruptive Ventures",
        "Möte_2023-10-04_Serge_Guelnoji_Peo__2023-10-04__serge _ guelnoji _ peo",
        "Online_Partner_disruptiveventures_Gemini Enterprise SKU, Online Part",
        "Pokalen_styrelsemöte_2023-11-15__2023-11-15__Styrelsen",
        "High-Level Plan to AI-ify Disruptive Ventures",
        "Veckomöte - Team Meeting (Marcus intro, AI-projekt, uppföljningar)",
    ]
    
    print("=" * 80)
    print("DOCUMENT NAME CLEANING EXAMPLES")
    print("=" * 80)
    print()
    print("-" * 80)
    print(f"{'ORIGINAL FILENAME':<60} | {'CLEANED NAME':<40}")
    print("-" * 80)
    
    for filename in test_filenames:
        cleaned = DocumentService.clean_document_name(filename)
        
        filename_short = filename[:57] + "..." if len(filename) > 57 else filename
        cleaned_short = cleaned[:37] + "..." if len(cleaned) > 37 else cleaned
        
        print(f"{filename_short:<60} | {cleaned_short:<40}")
    
    print("-" * 80)
    print()


def main():
    """Main entry point with CLI argument parsing."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Backfill display_name for existing documents',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show what would be updated (dry run)
  python backfill_display_names.py --dry-run
  
  # Actually update all documents
  python backfill_display_names.py
  
  # Update documents for specific org
  python backfill_display_names.py --org-id <uuid>
  
  # Show examples of name cleaning
  python backfill_display_names.py --examples
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be updated without making changes'
    )
    
    parser.add_argument(
        '--org-id',
        type=str,
        help='Only update documents for specific organization'
    )
    
    parser.add_argument(
        '--examples',
        action='store_true',
        help='Show examples of name cleaning'
    )
    
    args = parser.parse_args()
    
    # Show examples
    if args.examples:
        asyncio.run(show_examples())
        return
    
    # Backfill specific org or all
    if args.org_id:
        asyncio.run(backfill_specific_org(args.org_id, dry_run=args.dry_run))
    else:
        asyncio.run(backfill_all_display_names(dry_run=args.dry_run))


if __name__ == "__main__":
    main()


