"""
Google Contacts as CRM Backend for DV VC Operating System.
Stores all contacts (team, leads, portfolio) with rich custom fields.
No separate CRM system needed!
"""
from typing import List, Dict, Optional, Any
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

logger = logging.getLogger(__name__)


class GoogleContactsCRMClient:
    """
    Use Google Contacts as CRM backend.
    
    Benefits:
    - Native in Gmail (see contacts while composing)
    - Works in Calendar, Meet automatically
    - Mobile apps exist (iOS/Android)
    - Rich custom fields for CRM data
    - Organized with labels/groups
    - Your database → Google Contacts (source of truth)
    
    Contact Groups:
    - DV_Team: Internal team members
    - Leads: All inbound leads
    - High_Priority_Leads: Qualified leads (score > 70)
    - Portfolio_CEOs: Portfolio company CEOs
    - Portfolio_Green/Yellow/Red: Qualification status
    - Advisors, Partners_External: Other contacts
    """
    
    def __init__(self, service_account_file: str, admin_email: str):
        """
        Initialize Google Contacts client.
        
        Args:
            service_account_file: Path to service account JSON file
            admin_email: Admin email to impersonate with domain-wide delegation
        """
        self.credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=['https://www.googleapis.com/auth/contacts']
        )
        self.credentials = self.credentials.with_subject(admin_email)
        self.people_service = build('people', 'v1', credentials=self.credentials)
    
    async def create_contact(self, contact_data: Dict) -> Dict[str, Any]:
        """
        Create contact with comprehensive CRM custom fields.
        
        Args:
            contact_data: Contact data with structure:
                {
                    "names": [{"givenName": "...", "familyName": "..."}],
                    "emailAddresses": [{"value": "...", "type": "work"}],
                    "organizations": [{"name": "...", "title": "..."}],
                    "phoneNumbers": [...],
                    "urls": [...],
                    "userDefined": [  # Custom CRM fields
                        {"key": "Deal_Stage", "value": "meeting_scheduled"},
                        {"key": "Qualification_Score", "value": "85"},
                        ...
                    ],
                    "memberships": [  # Contact groups
                        {"contactGroupMembership": {"contactGroupResourceName": "contactGroups/..."}}
                    ]
                }
        
        Returns:
            Created contact with resourceName
        
        Example:
            contact = await google_contacts.create_contact({
                "names": [{"givenName": "John", "familyName": "Doe"}],
                "emailAddresses": [{"value": "john@example.com", "type": "work"}],
                "organizations": [{"name": "Acme Corp", "title": "CEO"}],
                "userDefined": [
                    {"key": "Deal_Stage", "value": "meeting_scheduled"},
                    {"key": "Qualification_Score", "value": "85"}
                ],
                "memberships": [
                    {"contactGroupMembership": {"contactGroupResourceName": "contactGroups/leads"}}
                ]
            })
        """
        try:
            contact = self.people_service.people().createContact(
                body=contact_data
            ).execute()
            
            logger.info(f"Created contact: {contact.get('resourceName')}")
            return contact
        
        except HttpError as e:
            logger.error(f"Error creating contact: {e}")
            raise
    
    async def update_contact(
        self,
        resource_name: str,
        contact_data: Dict,
        update_mask: str
    ) -> Dict[str, Any]:
        """
        Update existing contact.
        
        Args:
            resource_name: Contact resource name (people/c1234567890)
            contact_data: Updated contact data
            update_mask: Comma-separated fields to update
                e.g., "names,emailAddresses,userDefined,memberships"
        
        Returns:
            Updated contact
        
        Example:
            # Update lead stage
            await google_contacts.update_contact(
                "people/c1234567890",
                {
                    "userDefined": [
                        {"key": "Deal_Stage", "value": "diligence"},
                        {"key": "Qualification_Score", "value": "90"}
                    ]
                },
                "userDefined"
            )
        """
        try:
            contact = self.people_service.people().updateContact(
                resourceName=resource_name,
                updatePersonFields=update_mask,
                body=contact_data
            ).execute()
            
            logger.info(f"Updated contact: {resource_name}")
            return contact
        
        except HttpError as e:
            logger.error(f"Error updating contact {resource_name}: {e}")
            raise
    
    async def get_contact(
        self,
        resource_name: str,
        person_fields: str = "names,emailAddresses,phoneNumbers,organizations,urls,userDefined,memberships"
    ) -> Dict[str, Any]:
        """
        Get contact by resource name.
        
        Args:
            resource_name: Contact resource name
            person_fields: Comma-separated fields to retrieve
        
        Returns:
            Contact data
        """
        try:
            contact = self.people_service.people().get(
                resourceName=resource_name,
                personFields=person_fields
            ).execute()
            
            return contact
        
        except HttpError as e:
            logger.error(f"Error getting contact {resource_name}: {e}")
            raise
    
    async def search_contacts(self, query: str, page_size: int = 100) -> List[Dict[str, Any]]:
        """
        Search contacts by text.
        
        Args:
            query: Search query (name, email, company, etc.)
            page_size: Max results per page
        
        Returns:
            List of matching contacts
        
        Example:
            # Search for company
            contacts = await google_contacts.search_contacts("Acme Corp")
            
            # Search for person
            contacts = await google_contacts.search_contacts("john@example.com")
        """
        try:
            results = self.people_service.people().searchContacts(
                query=query,
                pageSize=page_size,
                readMask='names,emailAddresses,organizations,userDefined'
            ).execute()
            
            return results.get('results', [])
        
        except HttpError as e:
            logger.error(f"Error searching contacts: {e}")
            raise
    
    async def find_contact_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Find contact by email address.
        
        Args:
            email: Email address to search
        
        Returns:
            Contact or None if not found
        
        Example:
            contact = await google_contacts.find_contact_by_email("john@example.com")
            if contact:
                resource_name = contact['person']['resourceName']
        """
        try:
            results = await self.search_contacts(email)
            
            for result in results:
                person = result.get('person', {})
                emails = person.get('emailAddresses', [])
                
                for email_obj in emails:
                    if email_obj.get('value', '').lower() == email.lower():
                        return result
            
            return None
        
        except Exception as e:
            logger.error(f"Error finding contact by email {email}: {e}")
            return None
    
    async def create_contact_group(self, group_name: str) -> Dict[str, Any]:
        """
        Create contact group/label.
        
        Args:
            group_name: Group name (e.g., "Leads", "Portfolio_CEOs")
        
        Returns:
            Created group with resourceName
        
        Example:
            group = await google_contacts.create_contact_group("High_Priority_Leads")
            group_id = group['resourceName']
        """
        try:
            group = self.people_service.contactGroups().create(
                body={"contactGroup": {"name": group_name}}
            ).execute()
            
            logger.info(f"Created contact group: {group_name}")
            return group
        
        except HttpError as e:
            logger.error(f"Error creating contact group {group_name}: {e}")
            raise
    
    async def list_contact_groups(self) -> List[Dict[str, Any]]:
        """
        List all contact groups.
        
        Returns:
            List of contact groups
        """
        try:
            result = self.people_service.contactGroups().list().execute()
            return result.get('contactGroups', [])
        
        except HttpError as e:
            logger.error(f"Error listing contact groups: {e}")
            raise
    
    async def add_to_group(self, contact_resource: str, group_resource: str):
        """
        Add contact to group/label.
        
        Args:
            contact_resource: Contact resource name (people/c123...)
            group_resource: Group resource name (contactGroups/g123...)
        
        Example:
            await google_contacts.add_to_group(
                "people/c1234567890",
                "contactGroups/high_priority_leads"
            )
        """
        try:
            self.people_service.contactGroups().members().modify(
                resourceName=group_resource,
                body={"resourceNamesToAdd": [contact_resource]}
            ).execute()
            
            logger.info(f"Added {contact_resource} to {group_resource}")
        
        except HttpError as e:
            logger.error(f"Error adding contact to group: {e}")
            raise
    
    async def remove_from_group(self, contact_resource: str, group_resource: str):
        """
        Remove contact from group.
        
        Args:
            contact_resource: Contact resource name
            group_resource: Group resource name
        """
        try:
            self.people_service.contactGroups().members().modify(
                resourceName=group_resource,
                body={"resourceNamesToRemove": [contact_resource]}
            ).execute()
            
            logger.info(f"Removed {contact_resource} from {group_resource}")
        
        except HttpError as e:
            logger.error(f"Error removing contact from group: {e}")
            raise
    
    async def get_contacts_by_group(
        self,
        group_resource: str,
        page_size: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Get all contacts in a specific group.
        
        Args:
            group_resource: Group resource name
            page_size: Max contacts per page
        
        Returns:
            List of contacts in group
        
        Example:
            # Get all leads
            leads = await google_contacts.get_contacts_by_group("contactGroups/leads")
            
            # Get portfolio companies
            portfolio = await google_contacts.get_contacts_by_group("contactGroups/portfolio_ceos")
        """
        try:
            contacts = []
            page_token = None
            
            while True:
                result = self.people_service.people().connections().list(
                    resourceName='people/me',
                    pageSize=page_size,
                    pageToken=page_token,
                    personFields='names,emailAddresses,organizations,userDefined,memberships'
                ).execute()
                
                for connection in result.get('connections', []):
                    # Check if contact is in the specified group
                    memberships = connection.get('memberships', [])
                    for membership in memberships:
                        group_membership = membership.get('contactGroupMembership', {})
                        if group_membership.get('contactGroupResourceName') == group_resource:
                            contacts.append(connection)
                            break
                
                page_token = result.get('nextPageToken')
                if not page_token:
                    break
            
            return contacts
        
        except HttpError as e:
            logger.error(f"Error getting contacts by group {group_resource}: {e}")
            raise
    
    async def get_leads_pipeline(self) -> Dict[str, List[Dict]]:
        """
        Get all leads organized by deal stage.
        
        Returns:
            Dict with stage names as keys, contacts as values
        
        Example:
            pipeline = await google_contacts.get_leads_pipeline()
            # Returns: {
            #   'new': [...],
            #   'meeting_scheduled': [...],
            #   'diligence': [...],
            #   ...
            # }
        """
        try:
            # Get all contacts in Leads group
            all_leads = await self.get_contacts_by_group("contactGroups/leads")
            
            # Organize by Deal_Stage custom field
            pipeline = {
                'new': [],
                'researching': [],
                'meeting_scheduled': [],
                'diligence': [],
                'term_sheet': [],
                'closed_won': [],
                'closed_lost': []
            }
            
            for lead in all_leads:
                stage = self._get_custom_field(lead, 'Deal_Stage')
                if stage and stage in pipeline:
                    pipeline[stage].append(lead)
                else:
                    pipeline['new'].append(lead)
            
            return pipeline
        
        except Exception as e:
            logger.error(f"Error getting leads pipeline: {e}")
            raise
    
    async def get_portfolio_companies(self) -> List[Dict[str, Any]]:
        """
        Get all portfolio company contacts.
        
        Returns:
            List of portfolio CEO contacts
        
        Example:
            portfolio = await google_contacts.get_portfolio_companies()
            for company in portfolio:
                name = company['names'][0]['displayName']
                status = _get_custom_field(company, 'Qualification_Status')
        """
        try:
            return await self.get_contacts_by_group("contactGroups/portfolio_ceos")
        except Exception as e:
            logger.error(f"Error getting portfolio companies: {e}")
            raise
    
    def _get_custom_field(self, contact: Dict, field_key: str) -> Optional[str]:
        """
        Extract custom field value from contact.
        
        Args:
            contact: Contact data
            field_key: Custom field key (e.g., "Deal_Stage")
        
        Returns:
            Field value or None
        """
        for field in contact.get('userDefined', []):
            if field.get('key') == field_key:
                return field.get('value')
        return None
    
    async def delete_contact(self, resource_name: str):
        """
        Delete a contact.
        
        Args:
            resource_name: Contact resource name
        """
        try:
            self.people_service.people().deleteContact(
                resourceName=resource_name
            ).execute()
            
            logger.info(f"Deleted contact: {resource_name}")
        
        except HttpError as e:
            logger.error(f"Error deleting contact {resource_name}: {e}")
            raise


# Helper functions for building contact data structures

def build_lead_contact(lead_data: Dict) -> Dict:
    """
    Build Google Contacts format for a dealflow lead.
    
    Args:
        lead_data: Lead data from database
    
    Returns:
        Contact data ready for create_contact()
    """
    return {
        "names": [{
            "givenName": lead_data.get('founder_name', '').split()[0] if lead_data.get('founder_name') else "",
            "familyName": " ".join(lead_data.get('founder_name', '').split()[1:]) if lead_data.get('founder_name') else "",
            "displayName": lead_data.get('founder_name', 'Unknown')
        }],
        "emailAddresses": [
            {"value": lead_data['founder_email'], "type": "work"}
        ] if lead_data.get('founder_email') else [],
        "organizations": [{
            "name": lead_data['company_name'],
            "title": "Founder/CEO",
            "type": "work"
        }],
        "urls": [
            {"value": lead_data.get('website', ''), "type": "work"},
            {"value": lead_data.get('founder_linkedin', ''), "type": "profile"}
        ],
        "userDefined": [
            {"key": "Deal_Stage", "value": lead_data.get('stage', 'new')},
            {"key": "Qualification_Score", "value": str(lead_data.get('ai_qualification_score', 0))},
            {"key": "Investment_Thesis_Match", "value": "yes" if lead_data.get('meets_thesis') else "no"},
            {"key": "Company_Stage", "value": lead_data.get('company_stage', '')},
            {"key": "Source", "value": lead_data.get('source', '')},
            {"key": "One_Liner", "value": lead_data.get('one_liner', '')},
            {"key": "Pitch_Deck", "value": lead_data.get('pitch_deck_url', '')}
        ]
    }


def build_person_contact(person_data: Dict, competencies: List[str] = None) -> Dict:
    """
    Build Google Contacts format for internal team member.
    
    Args:
        person_data: Person data from database
        competencies: List of skills
    
    Returns:
        Contact data ready for create_contact()
    """
    skills_text = ", ".join(competencies) if competencies else ""
    
    return {
        "names": [{
            "givenName": person_data.get('first_name', ''),
            "familyName": person_data.get('last_name', ''),
            "displayName": person_data.get('full_name', '')
        }],
        "emailAddresses": [
            {"value": person_data['email'], "type": "work"}
        ],
        "phoneNumbers": [
            {"value": person_data.get('phone', ''), "type": "work"}
        ] if person_data.get('phone') else [],
        "organizations": [{
            "name": "Disruptive Ventures",
            "title": person_data.get('job_title', ''),
            "department": person_data.get('department', ''),
            "type": "work"
        }],
        "urls": [
            {"value": person_data.get('linkedin_url', ''), "type": "profile"}
        ] if person_data.get('linkedin_url') else [],
        "userDefined": [
            {"key": "Person_Type", "value": person_data.get('person_type', 'internal')},
            {"key": "Department", "value": person_data.get('department', '')},
            {"key": "Start_Date", "value": str(person_data.get('start_date', ''))},
            {"key": "Employment_Type", "value": person_data.get('employment_type', '')},
            {"key": "Skills", "value": skills_text}
        ]
    }


