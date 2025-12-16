"""
Google Workspace Directory integration for DV VC Operating System.
Populates rich employee profiles with AI-generated bios and competencies.
Makes everyone searchable by skills natively in Google Workspace.
"""
from typing import List, Dict, Optional, Any
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

logger = logging.getLogger(__name__)


class GoogleWorkspaceDirectoryClient:
    """
    Manages Google Workspace Directory profiles.
    
    Benefits:
    - AI-generated bios from CVs
    - Competencies automatically extracted
    - Searchable by skills in Gmail
    - Profile cards show up across Gmail, Calendar, Drive, Meet
    - No separate "My Profile" system needed
    """
    
    def __init__(self, service_account_file: str, admin_email: str):
        """
        Initialize Directory client.
        
        Args:
            service_account_file: Path to service account JSON
            admin_email: Admin email for domain-wide delegation
        """
        self.credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=[
                'https://www.googleapis.com/auth/admin.directory.user',
                'https://www.googleapis.com/auth/directory.readonly'
            ]
        )
        self.credentials = self.credentials.with_subject(admin_email)
        self.directory_service = build('admin', 'directory_v1', credentials=self.credentials)
    
    async def get_user_profile(self, user_email: str) -> Dict[str, Any]:
        """
        Get current Google Workspace profile.
        
        Args:
            user_email: User's email address
        
        Returns:
            User profile data
        """
        try:
            user = self.directory_service.users().get(
                userKey=user_email
            ).execute()
            
            return user
        
        except HttpError as e:
            logger.error(f"Error getting user profile for {user_email}: {e}")
            raise
    
    async def update_user_profile(
        self,
        user_email: str,
        profile_data: Dict
    ) -> Dict[str, Any]:
        """
        Update Google Workspace profile with rich data.
        
        Args:
            user_email: User's email
            profile_data: Profile data with structure:
                {
                    "name": {"fullName": "Marcus Andersson"},
                    "organizations": [{
                        "title": "Partner",
                        "department": "Investments",
                        "description": "AI-generated compelling bio"
                    }],
                    "locations": [{
                        "type": "desk",
                        "area": "Stockholm Office"
                    }],
                    "customSchemas": {
                        "Skills": {
                            "technical_skills": ["Python", "ML"],
                            "domain_expertise": ["B2B SaaS", "Fintech"],
                            "languages": ["Swedish", "English"]
                        },
                        "DV_Data": {
                            "cv_link": "https://drive.google.com/...",
                            "linkedin": "https://linkedin.com/in/...",
                            "portfolio_companies": ["Company A", "Company B"],
                            "investment_focus": "Early-stage B2B SaaS"
                        }
                    }
                }
        
        Returns:
            Updated user profile
        
        Example:
            await directory.update_user_profile(
                "marcus@disruptiveventures.se",
                {
                    "organizations": [{
                        "title": "Partner",
                        "department": "Investments",
                        "description": "Seasoned investor with 10+ years in B2B SaaS"
                    }],
                    "customSchemas": {
                        "Skills": {
                            "technical_skills": ["Python", "ML", "Startup Scaling"],
                            "domain_expertise": ["B2B SaaS", "Fintech"]
                        }
                    }
                }
            )
        """
        try:
            updated = self.directory_service.users().update(
                userKey=user_email,
                body=profile_data
            ).execute()
            
            logger.info(f"Updated profile for {user_email}")
            return updated
        
        except HttpError as e:
            logger.error(f"Error updating user profile for {user_email}: {e}")
            raise
    
    async def create_custom_schema(
        self,
        schema_name: str,
        fields: List[Dict]
    ) -> Dict[str, Any]:
        """
        Create custom fields in Google Workspace Directory.
        
        Args:
            schema_name: Schema name (e.g., "Skills", "DV_Data")
            fields: List of field definitions
        
        Field format:
            {
                "fieldName": "technical_skills",
                "fieldType": "STRING",  # STRING, INT64, BOOL, DOUBLE, DATE, EMAIL, PHONE
                "multiValued": True,  # Allow multiple values
                "indexed": True,  # Make searchable
                "readAccessType": "ALL_DOMAIN_USERS"
            }
        
        Returns:
            Created schema
        
        Example:
            # Create Skills schema
            await directory.create_custom_schema("Skills", [
                {"fieldName": "technical_skills", "fieldType": "STRING", "multiValued": True},
                {"fieldName": "domain_expertise", "fieldType": "STRING", "multiValued": True},
                {"fieldName": "languages", "fieldType": "STRING", "multiValued": True}
            ])
        """
        try:
            schema = {
                "schemaName": schema_name,
                "fields": fields
            }
            
            created = self.directory_service.schemas().insert(
                customerId='my_customer',
                body=schema
            ).execute()
            
            logger.info(f"Created custom schema: {schema_name}")
            return created
        
        except HttpError as e:
            logger.error(f"Error creating custom schema {schema_name}: {e}")
            raise
    
    async def list_custom_schemas(self) -> List[Dict[str, Any]]:
        """
        List all custom schemas.
        
        Returns:
            List of schemas
        """
        try:
            result = self.directory_service.schemas().list(
                customerId='my_customer'
            ).execute()
            
            return result.get('schemas', [])
        
        except HttpError as e:
            logger.error(f"Error listing custom schemas: {e}")
            raise
    
    async def search_users_by_skill(self, skill: str) -> List[Dict[str, Any]]:
        """
        Search Google Workspace Directory for users with specific skill.
        
        Args:
            skill: Skill to search for
        
        Returns:
            List of users with that skill
        
        Example:
            # Find who knows Python
            users = await directory.search_users_by_skill("Python")
            for user in users:
                print(f"{user['name']['fullName']} knows Python")
        """
        try:
            query = f'customSchemas.Skills.technical_skills:{skill}'
            
            users = self.directory_service.users().list(
                customer='my_customer',
                query=query,
                projection='full'
            ).execute()
            
            return users.get('users', [])
        
        except HttpError as e:
            logger.error(f"Error searching users by skill {skill}: {e}")
            raise
    
    async def list_all_users(
        self,
        domain: str = None,
        max_results: int = 500
    ) -> List[Dict[str, Any]]:
        """
        List all users in the organization.
        
        Args:
            domain: Optional domain to filter
            max_results: Max users to return
        
        Returns:
            List of users
        """
        try:
            kwargs = {
                'customer': 'my_customer',
                'maxResults': max_results,
                'projection': 'full'
            }
            
            if domain:
                kwargs['domain'] = domain
            
            result = self.directory_service.users().list(**kwargs).execute()
            return result.get('users', [])
        
        except HttpError as e:
            logger.error(f"Error listing users: {e}")
            raise


# Helper functions for building profile data

def build_profile_data(
    person_data: Dict,
    bio: str,
    competencies: Dict[str, List[str]],
    cv_link: str = None,
    portfolio_companies: List[str] = None
) -> Dict:
    """
    Build Google Workspace Directory profile data structure.
    
    Args:
        person_data: Person data from database
        bio: AI-generated professional bio
        competencies: Dict with categorized skills
            {
                "technical": ["Python", "ML"],
                "business": ["Fundraising", "Strategy"],
                "language": ["Swedish", "English"],
                "domain": ["B2B SaaS", "Fintech"]
            }
        cv_link: Google Drive link to CV
        portfolio_companies: List of portfolio company names
    
    Returns:
        Profile data ready for update_user_profile()
    """
    return {
        "name": {
            "fullName": person_data.get('full_name', ''),
            "givenName": person_data.get('first_name', ''),
            "familyName": person_data.get('last_name', '')
        },
        "organizations": [{
            "title": person_data.get('job_title', 'Team Member'),
            "department": person_data.get('department', 'DV Team'),
            "description": bio,  # AI-generated compelling bio
            "primary": True
        }],
        "phones": [
            {"value": person_data.get('phone', ''), "type": "work"}
        ] if person_data.get('phone') else [],
        "locations": [
            {"type": "desk", "area": person_data.get('location', 'Stockholm')}
        ],
        "customSchemas": {
            "Skills": {
                "technical_skills": competencies.get('technical', []),
                "domain_expertise": competencies.get('domain', []),
                "languages": competencies.get('language', []),
                "business_skills": competencies.get('business', [])
            },
            "DV_Data": {
                "cv_link": cv_link or "",
                "linkedin": person_data.get('linkedin_url', ''),
                "portfolio_companies": portfolio_companies or [],
                "investment_focus": person_data.get('investment_focus', ''),
                "years_at_dv": str(calculate_tenure(person_data.get('start_date'))) if person_data.get('start_date') else ""
            }
        }
    }


def calculate_tenure(start_date) -> float:
    """Calculate years at DV from start date."""
    if not start_date:
        return 0
    
    from datetime import datetime
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date)
    
    years = (datetime.now() - start_date).days / 365.25
    return round(years, 1)


# Setup function to create required custom schemas

async def setup_custom_schemas(directory_client: GoogleWorkspaceDirectoryClient):
    """
    One-time setup: Create custom schemas for Skills and DV_Data.
    
    Args:
        directory_client: Initialized directory client
    
    Example:
        directory = GoogleWorkspaceDirectoryClient(service_account_file, admin_email)
        await setup_custom_schemas(directory)
    """
    try:
        # Check if schemas already exist
        existing_schemas = await directory_client.list_custom_schemas()
        existing_names = [s.get('schemaName') for s in existing_schemas]
        
        # Create Skills schema if doesn't exist
        if 'Skills' not in existing_names:
            await directory_client.create_custom_schema('Skills', [
                {
                    "fieldName": "technical_skills",
                    "fieldType": "STRING",
                    "multiValued": True,
                    "indexed": True,
                    "readAccessType": "ALL_DOMAIN_USERS"
                },
                {
                    "fieldName": "domain_expertise",
                    "fieldType": "STRING",
                    "multiValued": True,
                    "indexed": True,
                    "readAccessType": "ALL_DOMAIN_USERS"
                },
                {
                    "fieldName": "languages",
                    "fieldType": "STRING",
                    "multiValued": True,
                    "indexed": True,
                    "readAccessType": "ALL_DOMAIN_USERS"
                },
                {
                    "fieldName": "business_skills",
                    "fieldType": "STRING",
                    "multiValued": True,
                    "indexed": True,
                    "readAccessType": "ALL_DOMAIN_USERS"
                }
            ])
            logger.info("Created Skills schema")
        
        # Create DV_Data schema if doesn't exist
        if 'DV_Data' not in existing_names:
            await directory_client.create_custom_schema('DV_Data', [
                {
                    "fieldName": "cv_link",
                    "fieldType": "STRING",
                    "readAccessType": "ALL_DOMAIN_USERS"
                },
                {
                    "fieldName": "linkedin",
                    "fieldType": "STRING",
                    "readAccessType": "ALL_DOMAIN_USERS"
                },
                {
                    "fieldName": "portfolio_companies",
                    "fieldType": "STRING",
                    "multiValued": True,
                    "readAccessType": "ALL_DOMAIN_USERS"
                },
                {
                    "fieldName": "investment_focus",
                    "fieldType": "STRING",
                    "readAccessType": "ALL_DOMAIN_USERS"
                },
                {
                    "fieldName": "years_at_dv",
                    "fieldType": "STRING",
                    "readAccessType": "ALL_DOMAIN_USERS"
                }
            ])
            logger.info("Created DV_Data schema")
        
        logger.info("Custom schemas setup complete")
    
    except Exception as e:
        logger.error(f"Error setting up custom schemas: {e}")
        raise

