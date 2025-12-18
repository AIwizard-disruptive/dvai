"""
Role-Based Access Control (RBAC) Service
Implements principle of least privilege for meeting data and documents

ROLES HIERARCHY:
- Owner: Full access to everything in org
- Admin: Access to all meetings, can manage users, cannot delete org
- Member: Access to meetings they attended, can view assigned tasks
- Viewer: Read-only access to meetings they attended
"""
from typing import List, Optional, Dict
from enum import Enum


class Role(str, Enum):
    """User roles in organization."""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class Permission(str, Enum):
    """Granular permissions."""
    # Meeting permissions
    VIEW_ALL_MEETINGS = "view_all_meetings"
    VIEW_OWN_MEETINGS = "view_own_meetings"
    EDIT_MEETINGS = "edit_meetings"
    DELETE_MEETINGS = "delete_meetings"
    
    # Document permissions
    VIEW_ALL_DOCUMENTS = "view_all_documents"
    VIEW_OWN_DOCUMENTS = "view_own_documents"
    GENERATE_DOCUMENTS = "generate_documents"
    DELETE_DOCUMENTS = "delete_documents"
    
    # Decision permissions
    VIEW_ALL_DECISIONS = "view_all_decisions"
    VIEW_OWN_DECISIONS = "view_own_decisions"
    EDIT_DECISIONS = "edit_decisions"
    
    # Action item permissions
    VIEW_ALL_ACTIONS = "view_all_actions"
    VIEW_OWN_ACTIONS = "view_own_actions"
    EDIT_OWN_ACTIONS = "edit_own_actions"
    EDIT_ALL_ACTIONS = "edit_all_actions"
    
    # People/Attendee permissions
    VIEW_ALL_PEOPLE = "view_all_people"
    VIEW_PII = "view_pii"  # Access to emails/phones in source files
    EXPORT_DATA = "export_data"
    
    # Admin permissions
    MANAGE_USERS = "manage_users"
    MANAGE_ORG = "manage_org"


# Role → Permissions mapping
ROLE_PERMISSIONS = {
    Role.OWNER: [
        # Everything
        Permission.VIEW_ALL_MEETINGS,
        Permission.EDIT_MEETINGS,
        Permission.DELETE_MEETINGS,
        Permission.VIEW_ALL_DOCUMENTS,
        Permission.GENERATE_DOCUMENTS,
        Permission.DELETE_DOCUMENTS,
        Permission.VIEW_ALL_DECISIONS,
        Permission.EDIT_DECISIONS,
        Permission.VIEW_ALL_ACTIONS,
        Permission.EDIT_ALL_ACTIONS,
        Permission.VIEW_ALL_PEOPLE,
        Permission.VIEW_PII,
        Permission.EXPORT_DATA,
        Permission.MANAGE_USERS,
        Permission.MANAGE_ORG,
    ],
    
    Role.ADMIN: [
        # Most things, but cannot manage org
        Permission.VIEW_ALL_MEETINGS,
        Permission.EDIT_MEETINGS,
        Permission.DELETE_MEETINGS,
        Permission.VIEW_ALL_DOCUMENTS,
        Permission.GENERATE_DOCUMENTS,
        Permission.DELETE_DOCUMENTS,
        Permission.VIEW_ALL_DECISIONS,
        Permission.EDIT_DECISIONS,
        Permission.VIEW_ALL_ACTIONS,
        Permission.EDIT_ALL_ACTIONS,
        Permission.VIEW_ALL_PEOPLE,
        Permission.EXPORT_DATA,
        Permission.MANAGE_USERS,
    ],
    
    Role.MEMBER: [
        # Own meetings and assigned tasks
        Permission.VIEW_OWN_MEETINGS,
        Permission.VIEW_OWN_DOCUMENTS,
        Permission.GENERATE_DOCUMENTS,
        Permission.VIEW_OWN_DECISIONS,
        Permission.VIEW_OWN_ACTIONS,
        Permission.EDIT_OWN_ACTIONS,
        Permission.VIEW_ALL_PEOPLE,
    ],
    
    Role.VIEWER: [
        # Read-only for own meetings
        Permission.VIEW_OWN_MEETINGS,
        Permission.VIEW_OWN_DOCUMENTS,
        Permission.VIEW_OWN_DECISIONS,
        Permission.VIEW_OWN_ACTIONS,
    ],
}


class RBACService:
    """Service for role-based access control."""
    
    @staticmethod
    def has_permission(user_role: str, permission: Permission) -> bool:
        """
        Check if role has specific permission.
        
        Args:
            user_role: User's role in organization
            permission: Permission to check
        
        Returns:
            True if role has permission
        """
        try:
            role = Role(user_role)
        except ValueError:
            return False
        
        return permission in ROLE_PERMISSIONS.get(role, [])
    
    @staticmethod
    def can_view_meeting(user_role: str, user_id: str, meeting_attendees: List[str]) -> bool:
        """
        Check if user can view a specific meeting.
        
        Args:
            user_role: User's role
            user_id: User's ID
            meeting_attendees: List of attendee IDs for this meeting
        
        Returns:
            True if user can view meeting
        """
        # Owners and Admins can view all meetings
        if RBACService.has_permission(user_role, Permission.VIEW_ALL_MEETINGS):
            return True
        
        # Members and Viewers can view if they attended
        if RBACService.has_permission(user_role, Permission.VIEW_OWN_MEETINGS):
            return user_id in meeting_attendees
        
        return False
    
    @staticmethod
    def can_view_document(
        user_role: str,
        user_id: str,
        document_type: str,
        meeting_attendees: List[str]
    ) -> bool:
        """
        Check if user can view a specific document.
        
        Args:
            user_role: User's role
            user_id: User's ID  
            document_type: Type of document
            meeting_attendees: List of attendee IDs for this meeting
        
        Returns:
            True if user can view document
        """
        # Sensitive documents (contracts, financial data)
        sensitive_docs = ['contract_draft', 'financial_report', 'term_sheet']
        
        if document_type in sensitive_docs:
            # Only Owners and Admins can view sensitive documents
            return RBACService.has_permission(user_role, Permission.VIEW_ALL_DOCUMENTS)
        
        # Regular documents follow meeting access rules
        if RBACService.has_permission(user_role, Permission.VIEW_ALL_DOCUMENTS):
            return True
        
        if RBACService.has_permission(user_role, Permission.VIEW_OWN_DOCUMENTS):
            return user_id in meeting_attendees
        
        return False
    
    @staticmethod
    def can_view_action(user_role: str, user_id: str, action_owner_id: Optional[str]) -> bool:
        """
        Check if user can view a specific action item.
        
        Args:
            user_role: User's role
            user_id: User's ID
            action_owner_id: ID of person assigned to action
        
        Returns:
            True if user can view action
        """
        # Owners and Admins see all actions
        if RBACService.has_permission(user_role, Permission.VIEW_ALL_ACTIONS):
            return True
        
        # Members and Viewers see only their assigned actions
        if RBACService.has_permission(user_role, Permission.VIEW_OWN_ACTIONS):
            return user_id == action_owner_id
        
        return False
    
    @staticmethod
    def filter_actions_by_role(
        user_role: str,
        user_id: str,
        all_actions: List[Dict]
    ) -> List[Dict]:
        """
        Filter action items based on user's role and permissions.
        
        Args:
            user_role: User's role
            user_id: User's ID
            all_actions: List of all action items
        
        Returns:
            Filtered list of actions user can see
        """
        # Owners and Admins see everything
        if RBACService.has_permission(user_role, Permission.VIEW_ALL_ACTIONS):
            return all_actions
        
        # Members and Viewers see only their assigned actions
        if RBACService.has_permission(user_role, Permission.VIEW_OWN_ACTIONS):
            return [
                action for action in all_actions
                if action.get('owner_id') == user_id or action.get('owner_email') == user_id
            ]
        
        return []
    
    @staticmethod
    def get_accessible_document_types(user_role: str) -> List[str]:
        """
        Get list of document types user can access/generate.
        
        Args:
            user_role: User's role
        
        Returns:
            List of document types user can access
        """
        # All users can access basic documents
        basic_docs = [
            'meeting_notes',
            'email_meeting_summary',
            'email_action_reminder'
        ]
        
        # Members and above can access decision emails
        member_docs = basic_docs + [
            'email_decision_update',
        ]
        
        # Admins and Owners can access sensitive documents
        admin_docs = member_docs + [
            'contract_draft',
            'market_analysis',
            'status_report',
            'proposal',
            'financial_report'
        ]
        
        role_docs = {
            Role.OWNER: admin_docs,
            Role.ADMIN: admin_docs,
            Role.MEMBER: member_docs,
            Role.VIEWER: basic_docs,
        }
        
        try:
            role = Role(user_role)
        except ValueError:
            return basic_docs
        
        return role_docs.get(role, basic_docs)
    
    @staticmethod
    def can_access_pii(user_role: str) -> bool:
        """
        Check if user can access PII (emails/phones from source files).
        
        Only Owners and Admins can access PII for GDPR compliance.
        
        Args:
            user_role: User's role
        
        Returns:
            True if user can access PII
        """
        return RBACService.has_permission(user_role, Permission.VIEW_PII)


# Document access levels
DOCUMENT_ACCESS_LEVELS = {
    'meeting_notes': 'viewer',  # Everyone who attended
    'email_meeting_summary': 'viewer',
    'email_action_reminder': 'viewer',
    'email_decision_update': 'member',
    'contract_draft': 'admin',
    'market_analysis': 'admin',
    'status_report': 'admin',
    'proposal': 'admin',
    'financial_report': 'owner',
    'term_sheet': 'owner',
}


def get_minimum_role_for_document(doc_type: str) -> str:
    """Get minimum role required to access document type."""
    return DOCUMENT_ACCESS_LEVELS.get(doc_type, 'viewer')





