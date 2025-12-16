"""
Sync user profiles FROM Google Workspace TO Supabase database.

Pulls title, department, phone, location, and other profile data from 
Google Workspace Directory and updates the people table in Supabase.

Usage:
    python backend/sync_google_profiles.py [--dry-run] [--email user@domain.com]
    
Examples:
    # Sync all users
    python backend/sync_google_profiles.py
    
    # Preview without making changes
    python backend/sync_google_profiles.py --dry-run
    
    # Sync specific user
    python backend/sync_google_profiles.py --email marcus@disruptiveventures.se
"""
import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
import argparse

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from supabase import create_client
from app.integrations.google_workspace_directory import GoogleWorkspaceDirectoryClient

# Load environment
load_dotenv()


class GoogleProfileSyncer:
    """Sync user profiles from Google Workspace to Supabase."""
    
    def __init__(self, dry_run: bool = False):
        """
        Initialize syncer.
        
        Args:
            dry_run: If True, only preview changes without updating Supabase
        """
        self.dry_run = dry_run
        self.supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        )
        
        # Check for Google service account credentials
        self.service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
        self.admin_email = os.getenv('GOOGLE_ADMIN_EMAIL', 'admin@disruptiveventures.se')
        
        if not self.service_account_file:
            print("⚠️  Warning: GOOGLE_SERVICE_ACCOUNT_FILE not set in environment")
            print("   Set this to use Google Workspace Directory API")
            self.directory_client = None
        else:
            self.directory_client = GoogleWorkspaceDirectoryClient(
                self.service_account_file,
                self.admin_email
            )
    
    async def sync_user_profile(self, email: str) -> Dict:
        """
        Sync a single user profile from Google Workspace to Supabase.
        
        Args:
            email: User's email address
            
        Returns:
            Dict with sync results
        """
        if not self.directory_client:
            return {
                'email': email,
                'status': 'skipped',
                'reason': 'Google Workspace credentials not configured'
            }
        
        try:
            # Get profile from Google Workspace
            google_profile = await self.directory_client.get_user_profile(email)
            
            # Extract relevant fields
            name = google_profile.get('name', {})
            full_name = name.get('fullName', '')
            
            # Get primary organization (job info)
            organizations = google_profile.get('organizations', [])
            primary_org = next((org for org in organizations if org.get('primary')), {}) if organizations else {}
            
            title = primary_org.get('title', '')
            department = primary_org.get('department', '')
            description = primary_org.get('description', '')  # Bio
            
            # Get phone
            phones = google_profile.get('phones', [])
            phone = phones[0].get('value', '') if phones else ''
            
            # Get location
            locations = google_profile.get('locations', [])
            location = locations[0].get('area', '') if locations else ''
            
            # Get custom schema data (if available)
            custom_schemas = google_profile.get('customSchemas', {})
            dv_data = custom_schemas.get('DV_Data', {})
            linkedin_url = dv_data.get('linkedin', '')
            
            # Check if user exists in Supabase
            existing = self.supabase.table('people').select('*').eq('email', email).execute()
            
            if existing.data and len(existing.data) > 0:
                person_id = existing.data[0]['id']
                
                # Prepare update data
                update_data = {
                    'title': title or None,
                    'role': title or None,  # Update both fields
                    'department': department or None,
                    'bio': description or None,
                    'phone': phone or None,
                    'location': location or None,
                    'google_workspace_id': google_profile.get('id'),
                    'google_directory_synced_at': 'now()'
                }
                
                # Only update linkedin if we have it and it's not already set
                if linkedin_url and not existing.data[0].get('linkedin_url'):
                    update_data['linkedin_url'] = linkedin_url
                
                # Update full name if available
                if full_name:
                    update_data['name'] = full_name
                
                if self.dry_run:
                    print(f"✓ Would update {email}:")
                    print(f"  Title: {title or '(none)'}")
                    print(f"  Department: {department or '(none)'}")
                    print(f"  Phone: {phone or '(none)'}")
                    print(f"  Location: {location or '(none)'}")
                    return {
                        'email': email,
                        'status': 'preview',
                        'action': 'update',
                        'changes': update_data
                    }
                else:
                    # Update in Supabase
                    self.supabase.table('people').update(update_data).eq('id', person_id).execute()
                    
                    print(f"✓ Updated {email}")
                    print(f"  Title: {title or '(unchanged)'}")
                    print(f"  Department: {department or '(unchanged)'}")
                    
                    return {
                        'email': email,
                        'status': 'success',
                        'action': 'updated',
                        'changes': update_data
                    }
            else:
                print(f"⚠️  User {email} not found in Supabase - skipping")
                return {
                    'email': email,
                    'status': 'skipped',
                    'reason': 'not_in_database'
                }
        
        except Exception as e:
            print(f"❌ Error syncing {email}: {str(e)}")
            return {
                'email': email,
                'status': 'error',
                'error': str(e)
            }
    
    async def sync_all_users(self, domain: str = 'disruptiveventures.se') -> List[Dict]:
        """
        Sync all users in the domain from Google Workspace to Supabase.
        
        Args:
            domain: Email domain to sync
            
        Returns:
            List of sync results
        """
        if not self.directory_client:
            print("❌ Google Workspace credentials not configured")
            return []
        
        print(f"\n🔄 Syncing all users from Google Workspace to Supabase...")
        print(f"   Domain: {domain}")
        print(f"   Mode: {'DRY RUN (preview only)' if self.dry_run else 'LIVE (will update database)'}")
        print()
        
        try:
            # Get all users from Google Workspace
            google_users = await self.directory_client.list_all_users(domain=domain)
            
            print(f"Found {len(google_users)} users in Google Workspace\n")
            
            # Sync each user
            results = []
            for user in google_users:
                email = user.get('primaryEmail')
                if email:
                    result = await self.sync_user_profile(email)
                    results.append(result)
            
            # Summary
            print("\n" + "="*60)
            print("SYNC SUMMARY")
            print("="*60)
            
            success = len([r for r in results if r['status'] == 'success'])
            preview = len([r for r in results if r['status'] == 'preview'])
            skipped = len([r for r in results if r['status'] == 'skipped'])
            errors = len([r for r in results if r['status'] == 'error'])
            
            if self.dry_run:
                print(f"Would update: {preview}")
            else:
                print(f"✓ Successfully updated: {success}")
            
            print(f"⚠️  Skipped: {skipped}")
            
            if errors > 0:
                print(f"❌ Errors: {errors}")
            
            print("="*60)
            
            return results
        
        except Exception as e:
            print(f"❌ Error syncing users: {str(e)}")
            return []
    
    async def find_incomplete_profiles(self) -> List[Dict]:
        """
        Find users in Supabase with incomplete profile data.
        
        Returns:
            List of users missing title, email, or name
        """
        print("\n🔍 Finding users with incomplete profiles in Supabase...")
        
        # Get all people from Supabase
        all_people = self.supabase.table('people').select('*').execute()
        
        incomplete = []
        for person in all_people.data:
            issues = []
            
            if not person.get('name') or not person.get('name').strip():
                issues.append('missing_name')
            
            if not person.get('email') or not person.get('email').strip():
                issues.append('missing_email')
            
            if not person.get('title') and not person.get('role'):
                issues.append('missing_title')
            
            if issues:
                incomplete.append({
                    'id': person.get('id'),
                    'name': person.get('name', '(no name)'),
                    'email': person.get('email', '(no email)'),
                    'title': person.get('title') or person.get('role', '(no title)'),
                    'issues': issues
                })
        
        if incomplete:
            print(f"\nFound {len(incomplete)} users with incomplete profiles:\n")
            for user in incomplete:
                print(f"  • {user['name']} ({user['email']})")
                print(f"    Issues: {', '.join(user['issues'])}")
                print()
        else:
            print("✓ All users have complete profiles!")
        
        return incomplete


async def main():
    """Main sync function."""
    parser = argparse.ArgumentParser(description='Sync user profiles from Google Workspace to Supabase')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without updating database')
    parser.add_argument('--email', type=str, help='Sync specific user by email')
    parser.add_argument('--find-incomplete', action='store_true', help='Find users with incomplete profiles')
    parser.add_argument('--domain', type=str, default='disruptiveventures.se', help='Domain to sync')
    
    args = parser.parse_args()
    
    syncer = GoogleProfileSyncer(dry_run=args.dry_run)
    
    if args.find_incomplete:
        # Find incomplete profiles
        await syncer.find_incomplete_profiles()
    elif args.email:
        # Sync specific user
        print(f"\n🔄 Syncing user: {args.email}")
        await syncer.sync_user_profile(args.email)
    else:
        # Sync all users
        await syncer.sync_all_users(domain=args.domain)
    
    print("\n✅ Done!")


if __name__ == '__main__':
    asyncio.run(main())

