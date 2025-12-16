"""
Enhanced Auto-Distribution with Proper Organization

Architecture:
1. Google Drive: Create folder per meeting with all docs
2. Gmail: Create drafts (not send) - ready for review
3. Linear: Create project per meeting, all tasks linked
4. Everything cross-linked and organized

User gets:
- Drive folder with all meeting documents
- Linear project with all tasks and links to docs
- Gmail drafts ready to review and send
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from supabase import create_client
from app.config import settings
import re


class EnhancedDistributionPipeline:
    """
    Enhanced auto-distribution with proper organization.
    
    Workflow:
    1. Create Google Drive folder for meeting
    2. Upload all documents to that folder
    3. Create Linear project for meeting
    4. Create Linear tasks linked to project
    5. Add links to Google Drive docs in task descriptions
    6. Create Gmail drafts (not send) for review
    7. All cross-linked and organized
    """
    
    def __init__(self):
        self.supabase = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key
        )
    
    async def distribute_meeting(
        self,
        meeting_id: str,
        org_id: str,
        user_id: str
    ) -> Dict:
        """
        Run enhanced distribution for a meeting.
        
        Args:
            meeting_id: Meeting ID
            org_id: Organization ID
            user_id: User who uploaded (for their integrations)
        
        Returns:
            Audit log with all created resources
        """
        
        print("\n" + "=" * 80)
        print("ENHANCED AUTO-DISTRIBUTION - ORGANIZED & LINKED")
        print("=" * 80)
        
        audit_log = {
            'meeting_id': meeting_id,
            'started_at': datetime.utcnow().isoformat(),
            'google_drive_folder': None,
            'google_docs_created': [],
            'linear_project': None,
            'linear_tasks_created': [],
            'gmail_drafts_created': [],
            'errors': []
        }
        
        # Get meeting data
        meeting = self.supabase.table('meetings').select('*').eq('id', meeting_id).execute().data[0]
        participants = self.supabase.table('meeting_participants').select('people(*)').eq('meeting_id', meeting_id).execute()
        attendees = [p['people'] for p in participants.data if p.get('people')]
        decisions = self.supabase.table('decisions').select('*').eq('meeting_id', meeting_id).execute().data
        actions = self.supabase.table('action_items').select('*').eq('meeting_id', meeting_id).execute().data
        
        # STEP 1: Create Google Drive folder for meeting
        print("\n1. Creating Google Drive folder structure...")
        folder_result = await self._create_drive_folder_structure(
            meeting, user_id
        )
        if folder_result:
            audit_log['google_drive_folder'] = folder_result
            print(f"   ✓ Drive folder: {folder_result['name']}")
            print(f"   ✓ URL: {folder_result.get('url', 'N/A')}")
        
        # STEP 2: Generate and upload all documents to Drive
        print("\n2. Generating and uploading documents to Drive...")
        docs = await self._generate_all_documents(meeting, attendees, decisions, actions)
        
        for doc in docs:
            try:
                drive_doc = await self._upload_document_to_drive(
                    doc,
                    folder_result['id'] if folder_result else None,
                    user_id
                )
                if drive_doc:
                    audit_log['google_docs_created'].append(drive_doc)
                    print(f"   ✓ {doc['title']}: {drive_doc.get('url', 'uploaded')}")
            except Exception as e:
                audit_log['errors'].append(f"Drive upload failed: {doc['title']} - {str(e)}")
        
        # STEP 3: Create Linear project for this meeting
        print("\n3. Creating Linear project for meeting...")
        linear_project = await self._create_linear_project(
            meeting, attendees, user_id
        )
        if linear_project:
            audit_log['linear_project'] = linear_project
            print(f"   ✓ Project: {linear_project['name']}")
            print(f"   ✓ URL: {linear_project.get('url', 'N/A')}")
        
        # STEP 4: Create Linear tasks linked to project with Drive docs
        print("\n4. Creating Linear tasks (linked to project + Drive docs)...")
        for action in actions:
            try:
                task = await self._create_linked_linear_task(
                    action,
                    meeting,
                    linear_project,
                    audit_log['google_docs_created'],
                    user_id
                )
                if task:
                    audit_log['linear_tasks_created'].append(task)
                    print(f"   ✓ {task['identifier']}: {action['title']} → {action.get('owner_name', 'Unassigned')}")
            except Exception as e:
                audit_log['errors'].append(f"Linear task failed: {action['title']} - {str(e)}")
        
        # STEP 5: Create Gmail draft to ALL assignees (single consolidated email)
        print("\n5. Creating consolidated Gmail draft to all assignees...")
        try:
            consolidated_draft = await self._create_consolidated_task_email(
                actions,
                meeting,
                linear_project,
                audit_log['google_docs_created'],
                attendees,
                user_id
            )
            if consolidated_draft:
                audit_log['gmail_drafts_created'].append(consolidated_draft)
                print(f"   ✓ Consolidated draft to: {', '.join(consolidated_draft['recipients'])}")
        except Exception as e:
            audit_log['errors'].append(f"Gmail consolidated draft failed: {str(e)}")
        
        # STEP 6: Create meeting notes draft for all attendees
        print("\n6. Creating meeting notes email drafts...")
        meeting_notes_draft = await self._create_meeting_notes_drafts(
            meeting, attendees, audit_log['google_docs_created'], user_id
        )
        
        # Save audit log
        audit_log['completed_at'] = datetime.utcnow().isoformat()
        
        self.supabase.table('distribution_logs').insert({
            'meeting_id': meeting_id,
            'org_id': org_id,
            'audit_log': audit_log,
            'created_at': datetime.utcnow().isoformat()
        }).execute()
        
        print("\n" + "=" * 80)
        print("✅ ENHANCED DISTRIBUTION COMPLETE")
        print("=" * 80)
        print(f"\n📊 Summary:")
        print(f"  ✓ Drive folder: {folder_result['name'] if folder_result else 'N/A'}")
        print(f"  ✓ Google Docs: {len(audit_log['google_docs_created'])}")
        print(f"  ✓ Linear project: {linear_project['name'] if linear_project else 'N/A'}")
        print(f"  ✓ Linear tasks: {len(audit_log['linear_tasks_created'])}")
        print(f"  ✓ Gmail drafts: {len(audit_log['gmail_drafts_created'])}")
        
        if audit_log['errors']:
            print(f"\n⚠️  {len(audit_log['errors'])} errors")
        
        print(f"\n✨ Everything organized and linked!")
        
        return audit_log
    
    async def _create_drive_folder_structure(
        self,
        meeting: Dict,
        user_id: str
    ) -> Optional[Dict]:
        """
        Create Google Drive folder for meeting.
        
        Structure:
        /Meetings/
          /2025/
            /December/
              /2025-12-15 Team Standup/
                ├─ Meeting_Notes_SV.docx
                ├─ Meeting_Notes_EN.docx
                └─ [other docs]
        
        Returns:
            Folder metadata with ID and URL
        """
        
        # Check if user has Google integration
        integration = await self._get_user_integration(user_id, 'google')
        if not integration:
            print("   ⚠ User hasn't connected Google Drive")
            return None
        
        try:
            from app.integrations.google_client import get_google_client
            from googleapiclient.discovery import build
            
            client = get_google_client(
                access_token=integration['access_token'],
                refresh_token=integration.get('refresh_token')
            )
            
            drive_service = build('drive', 'v3', credentials=client.credentials)
            
            # Create folder hierarchy
            meeting_date = meeting.get('meeting_date', datetime.now().strftime('%Y-%m-%d'))
            year = meeting_date[:4]
            month_name = datetime.strptime(meeting_date, '%Y-%m-%d').strftime('%B')
            
            # Clean meeting title for folder name
            safe_title = re.sub(r'[^\w\s-]', '', meeting['title'])[:50]
            folder_name = f"{meeting_date} {safe_title}"
            
            # Create parent folders if needed
            meetings_folder = await self._get_or_create_folder(
                drive_service, "Meetings", None
            )
            year_folder = await self._get_or_create_folder(
                drive_service, year, meetings_folder['id']
            )
            month_folder = await self._get_or_create_folder(
                drive_service, month_name, year_folder['id']
            )
            
            # Create meeting-specific folder
            meeting_folder = await self._get_or_create_folder(
                drive_service, folder_name, month_folder['id']
            )
            
            return {
                'id': meeting_folder['id'],
                'name': folder_name,
                'url': f"https://drive.google.com/drive/folders/{meeting_folder['id']}",
                'path': f"/Meetings/{year}/{month_name}/{folder_name}"
            }
            
        except Exception as e:
            print(f"   ⚠ Drive folder creation failed: {str(e)}")
            return None
    
    async def _get_or_create_folder(
        self,
        drive_service,
        folder_name: str,
        parent_id: Optional[str]
    ) -> Dict:
        """Get existing folder or create new one."""
        
        # Search for existing folder
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        
        results = drive_service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)',
            pageSize=1
        ).execute()
        
        files = results.get('files', [])
        
        if files:
            return files[0]
        
        # Create new folder
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        if parent_id:
            file_metadata['parents'] = [parent_id]
        
        folder = drive_service.files().create(
            body=file_metadata,
            fields='id, name'
        ).execute()
        
        return folder
    
    async def _upload_document_to_drive(
        self,
        doc: Dict,
        folder_id: Optional[str],
        user_id: str
    ) -> Optional[Dict]:
        """
        Upload document to Google Drive as Google Doc.
        
        Args:
            doc: Document dict with title, content, type, language
            folder_id: Parent folder ID
            user_id: User ID for integration credentials
        
        Returns:
            Created file metadata
        """
        
        integration = await self._get_user_integration(user_id, 'google')
        if not integration:
            return None
        
        try:
            from app.integrations.google_client import get_google_client
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaInMemoryUpload
            
            client = get_google_client(
                access_token=integration['access_token'],
                refresh_token=integration.get('refresh_token')
            )
            
            drive_service = build('drive', 'v3', credentials=client.credentials)
            
            # Create filename
            lang_suffix = f"_{doc['language'].upper()}" if doc.get('language') else ""
            filename = f"{doc['title']}{lang_suffix}"
            
            # Upload as Google Doc
            file_metadata = {
                'name': filename,
                'mimeType': 'application/vnd.google-apps.document'
            }
            
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            media = MediaInMemoryUpload(
                doc['content'].encode('utf-8'),
                mimetype='text/plain',
                resumable=True
            )
            
            file = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()
            
            return {
                'id': file['id'],
                'name': file['name'],
                'url': file.get('webViewLink'),
                'type': doc['type'],
                'language': doc.get('language')
            }
            
        except Exception as e:
            print(f"   ⚠ Drive upload failed: {doc['title']} - {str(e)}")
            return None
    
    async def _create_linear_project(
        self,
        meeting: Dict,
        attendees: List[Dict],
        user_id: str
    ) -> Optional[Dict]:
        """
        Create Linear project for meeting.
        
        Project name: "{Meeting Title} ({Date})"
        Example: "Team Standup (2025-12-15)"
        
        Returns:
            Project metadata with ID and URL
        """
        
        # Get Linear integration (could be user or org level)
        linear_token = await self._get_linear_token(user_id)
        if not linear_token:
            print("   ⚠ Linear not connected")
            return None
        
        try:
            from app.integrations.linear import LinearClient
            
            client = LinearClient(api_key=linear_token)
            
            # Get team ID
            teams = await client.get_teams()
            if not teams:
                print("   ⚠ No Linear teams found")
                return None
            
            team_id = teams[0]['id']
            
            # Format project name
            meeting_date = meeting.get('meeting_date', datetime.now().strftime('%Y-%m-%d'))
            project_name = f"{meeting['title']} ({meeting_date})"
            
            # Create project via GraphQL
            from gql import gql
            
            mutation = gql("""
                mutation CreateProject($input: ProjectCreateInput!) {
                    projectCreate(input: $input) {
                        success
                        project {
                            id
                            name
                            url
                        }
                    }
                }
            """)
            
            # Build project description
            description = f"""Meeting: {meeting['title']}
Date: {meeting_date}
Attendees: {', '.join([a.get('name', 'Unknown') for a in attendees])}

Decisions: {len(decisions)}
Action Items: {len(actions)}

Auto-generated by Meeting Intelligence Platform
"""
            
            result = await client.client.execute_async(
                mutation,
                variable_values={
                    "input": {
                        "teamIds": [team_id],
                        "name": project_name,
                        "description": description,
                    }
                }
            )
            
            project = result['projectCreate']['project']
            
            # Store project ID in meeting metadata
            self.supabase.table('meetings').update({
                'meeting_metadata': {
                    **(meeting.get('meeting_metadata') or {}),
                    'linear_project_id': project['id'],
                    'linear_project_url': project['url']
                }
            }).eq('id', meeting['id']).execute()
            
            return {
                'id': project['id'],
                'name': project['name'],
                'url': project['url']
            }
            
        except Exception as e:
            print(f"   ⚠ Linear project creation failed: {str(e)}")
            return None
    
    async def _create_linked_linear_task(
        self,
        action: Dict,
        meeting: Dict,
        project: Optional[Dict],
        drive_docs: List[Dict],
        user_id: str
    ) -> Optional[Dict]:
        """
        Create Linear task with:
        - Link to Linear project
        - Links to all Google Drive documents
        - Proper assignee
        - Due date and priority
        
        Task description includes:
        - Meeting context
        - Links to relevant Drive docs
        - Original action item details
        """
        
        linear_token = await self._get_linear_token(user_id)
        if not linear_token:
            return None
        
        try:
            from app.integrations.linear import LinearClient
            
            client = LinearClient(api_key=linear_token)
            
            # Get team ID
            teams = await client.get_teams()
            team_id = teams[0]['id']
            
            # Build rich task description with links
            description = self._build_task_description(
                action, meeting, project, drive_docs
            )
            
            # Map priority
            priority_map = {'urgent': 1, 'high': 2, 'medium': 3, 'low': 4}
            priority = priority_map.get(action.get('priority', 'medium').lower(), 3)
            
            # Get assignee ID (if we have mapping)
            assignee_id = await self._get_linear_assignee_id(
                action.get('owner_name'),
                action.get('owner_email'),
                user_id
            )
            
            # Create issue input
            issue_input = {
                "teamId": team_id,
                "title": action['title'],
                "description": description,
                "priority": priority,
            }
            
            # Add project if created
            if project:
                issue_input["projectId"] = project['id']
            
            # Add assignee if found
            if assignee_id:
                issue_input["assigneeId"] = assignee_id
            
            # Add due date if set
            if action.get('due_date'):
                issue_input["dueDate"] = action['due_date']
            
            # Create task
            issue = await client.create_issue(**issue_input)
            
            # Store Linear issue ID in action_items table
            self.supabase.table('action_items').update({
                'metadata': {
                    **(action.get('metadata') or {}),
                    'linear_issue_id': issue['id'],
                    'linear_issue_url': issue['url'],
                    'linear_identifier': issue['identifier']
                }
            }).eq('id', action['id']).execute()
            
            return {
                'id': issue['id'],
                'identifier': issue['identifier'],
                'title': issue['title'],
                'url': issue['url'],
                'assignee': action.get('owner_name'),
                'action_id': action['id']
            }
            
        except Exception as e:
            print(f"   ⚠ Linear task creation failed: {str(e)}")
            return None
    
    def _build_task_description(
        self,
        action: Dict,
        meeting: Dict,
        project: Optional[Dict],
        drive_docs: List[Dict]
    ) -> str:
        """
        Build rich task description with all context and links.
        
        Returns markdown description for Linear task.
        """
        
        description_parts = []
        
        # Meeting context
        description_parts.append(f"**From Meeting:** {meeting['title']}")
        if meeting.get('meeting_date'):
            description_parts.append(f"**Date:** {meeting['meeting_date']}")
        
        description_parts.append("")  # Blank line
        
        # Action item details
        if action.get('description'):
            description_parts.append(f"**Task Details:**")
            description_parts.append(action['description'])
            description_parts.append("")
        
        # Priority and due date
        if action.get('priority'):
            description_parts.append(f"**Priority:** {action['priority'].upper()}")
        if action.get('due_date'):
            description_parts.append(f"**Due Date:** {action['due_date']}")
        
        description_parts.append("")
        
        # Links to Google Drive documents
        if drive_docs:
            description_parts.append("**📁 Meeting Documents:**")
            
            # Find Swedish docs (primary)
            sv_docs = [d for d in drive_docs if d.get('language') == 'sv']
            en_docs = [d for d in drive_docs if d.get('language') == 'en']
            
            # Add Swedish docs first
            for doc in sv_docs:
                if doc.get('url'):
                    doc_name = doc['name'].replace('_SV', ' (Swedish)')
                    description_parts.append(f"- [{doc_name}]({doc['url']})")
            
            # Add English docs
            for doc in en_docs:
                if doc.get('url'):
                    doc_name = doc['name'].replace('_EN', ' (English)')
                    description_parts.append(f"- [{doc_name}]({doc['url']})")
            
            description_parts.append("")
        
        # Link to project if exists
        if project and project.get('url'):
            description_parts.append(f"**📊 Project:** [{project['name']}]({project['url']})")
            description_parts.append("")
        
        # Footer
        description_parts.append("---")
        description_parts.append("*Auto-generated by Meeting Intelligence Platform*")
        
        return "\n".join(description_parts)
    
    async def _create_consolidated_task_email(
        self,
        actions: List[Dict],
        meeting: Dict,
        project: Optional[Dict],
        drive_docs: List[Dict],
        attendees: List[Dict],
        user_id: str
    ) -> Optional[Dict]:
        """
        Create ONE Gmail draft to ALL assignees with ALL their tasks.
        
        Email includes:
        - Summary of meeting
        - Each person's tasks listed
        - Links to Linear project
        - Links to all Google Drive documents
        - Professional formatting
        """
        
        integration = await self._get_user_integration(user_id, 'google')
        if not integration:
            return None
        
        try:
            from app.integrations.google_client import get_google_client
            
            client = get_google_client(
                access_token=integration['access_token'],
                refresh_token=integration.get('refresh_token')
            )
            
            # Get all unique assignee emails
            assignee_emails = list(set([
                action['owner_email']
                for action in actions
                if action.get('owner_email')
            ]))
            
            if not assignee_emails:
                print("   ⚠ No assignees with emails found")
                return None
            
            # Build email subject
            subject = f"📋 Action Items from {meeting['title']} ({meeting.get('meeting_date', 'Today')})"
            
            # Build consolidated email body
            body_html = self._build_consolidated_email_body(
                actions, meeting, project, drive_docs, attendees
            )
            
            # Create draft to all assignees
            draft = await client.create_email_draft(
                to=assignee_emails,
                subject=subject,
                body_html=body_html
            )
            
            return {
                'draft_id': draft['id'],
                'recipients': [action.get('owner_name') for action in actions if action.get('owner_name')],
                'recipient_emails': assignee_emails,
                'subject': subject,
                'task_count': len(actions)
            }
            
        except Exception as e:
            print(f"   ⚠ Gmail consolidated draft creation failed: {str(e)}")
            return None
    
    def _build_consolidated_email_body(
        self,
        actions: List[Dict],
        meeting: Dict,
        project: Optional[Dict],
        drive_docs: List[Dict],
        attendees: List[Dict]
    ) -> str:
        """
        Build consolidated email body with ALL tasks for ALL assignees.
        
        Format:
        - Meeting summary
        - Marcus's tasks (3 tasks)
        - Fanny's tasks (2 tasks)
        - Henrik's tasks (1 task)
        - Links to Linear project
        - Links to all Drive documents
        """
        
        # Group actions by assignee
        tasks_by_assignee = {}
        for action in actions:
            owner = action.get('owner_name', 'Unassigned')
            if owner not in tasks_by_assignee:
                tasks_by_assignee[owner] = []
            tasks_by_assignee[owner].append(action)
        
        # Build task sections for each person
        task_sections = []
        for assignee, tasks in sorted(tasks_by_assignee.items()):
            if assignee == 'Unassigned':
                continue
            
            task_list_html = self._build_task_list_for_assignee(tasks)
            task_sections.append(f"""
        <div style="background: #f8f9fa; padding: 20px; border-radius: 12px; margin: 16px 0;">
            <h3 style="margin-top: 0; color: #0066cc;">👤 {assignee}'s Tasks ({len(tasks)})</h3>
            {task_list_html}
        </div>
            """)
        
        # Get Drive folder URL
        drive_folder_url = None
        if drive_docs:
            # Assume all docs in same folder, extract folder ID from first doc URL
            first_doc_url = drive_docs[0].get('url', '')
            if 'folders/' in first_doc_url:
                folder_id = first_doc_url.split('folders/')[-1].split('/')[0]
                drive_folder_url = f"https://drive.google.com/drive/folders/{folder_id}"
        
        # Get meeting notes
        meeting_notes_url = next(
            (d['url'] for d in drive_docs if d.get('type') == 'meeting_notes' and d.get('language') == 'sv'),
            None
        )
        
        html = f"""
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 700px; margin: 0 auto; padding: 20px;">
        <h1 style="color: #0066cc; border-bottom: 3px solid #0066cc; padding-bottom: 12px;">
            📋 Action Items: {meeting['title']}
        </h1>
        
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%); padding: 20px; border-radius: 12px; margin: 20px 0; border-left: 4px solid #0066cc;">
            <p style="margin: 8px 0;"><strong>📅 Date:</strong> {meeting.get('meeting_date', 'Today')}</p>
            <p style="margin: 8px 0;"><strong>👥 Attendees:</strong> {', '.join([a.get('name', 'Unknown') for a in attendees])}</p>
            <p style="margin: 8px 0;"><strong>✅ Action Items:</strong> {len(actions)} tasks created</p>
            {f'<p style="margin: 8px 0;"><strong>📊 Linear Project:</strong> <a href="{project["url"]}" style="color: #0066cc;">{project["name"]}</a></p>' if project and project.get('url') else ''}
        </div>
        
        <h2 style="color: #1a1a1a; margin-top: 32px;">🎯 Your Tasks</h2>
        <p style="color: #666;">Below are all action items from this meeting. Your specific tasks are assigned to you in Linear.</p>
        
        {''.join(task_sections)}
        
        <div style="background: #e3f2fd; padding: 20px; border-radius: 12px; margin: 30px 0;">
            <h3 style="margin-top: 0; color: #1976d2;">📁 Meeting Resources</h3>
            <ul style="list-style: none; padding: 0; margin: 0;">
                {f'<li style="margin: 12px 0;"><a href="{drive_folder_url}" style="color: #1976d2; text-decoration: none; font-weight: 600; font-size: 16px;">📂 Google Drive Folder (All Documents)</a></li>' if drive_folder_url else ''}
                {f'<li style="margin: 12px 0;"><a href="{meeting_notes_url}" style="color: #1976d2; text-decoration: none; font-weight: 600; font-size: 16px;">📄 Meeting Notes (Swedish)</a></li>' if meeting_notes_url else ''}
                {f'<li style="margin: 12px 0;"><a href="{project["url"]}" style="color: #1976d2; text-decoration: none; font-weight: 600; font-size: 16px;">📊 Linear Project</a></li>' if project and project.get('url') else ''}
            </ul>
            
            <div style="margin-top: 20px; padding-top: 16px; border-top: 1px solid #90caf9;">
                <strong>All Meeting Documents:</strong>
                <ul style="margin: 8px 0; padding-left: 20px;">
                    {self._build_drive_docs_list_html(drive_docs)}
                </ul>
            </div>
        </div>
        
        <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 30px 0;">
        
        <p style="color: #999; font-size: 13px;">
            ℹ️ This is a draft email. Review, edit if needed, and send when ready.<br>
            Each task is also assigned to you in Linear with full details and links.<br><br>
            <em>Auto-generated by Meeting Intelligence Platform</em>
        </p>
    </div>
</body>
</html>
        """
        
        return html
    
    def _build_task_list_for_assignee(self, tasks: List[Dict]) -> str:
        """Build HTML list of tasks for one assignee."""
        
        task_items = []
        for task in tasks:
            priority_color = {
                'urgent': '#d32f2f',
                'high': '#f57c00',
                'medium': '#fbc02d',
                'low': '#666'
            }.get(task.get('priority', 'medium').lower(), '#666')
            
            # Get Linear task identifier if available
            linear_id = task.get('metadata', {}).get('linear_identifier', '')
            linear_url = task.get('metadata', {}).get('linear_issue_url', '#')
            
            task_html = f"""
            <div style="padding: 16px; background: white; border-radius: 8px; margin: 12px 0; border-left: 4px solid {priority_color};">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                    <strong style="font-size: 16px; color: #1a1a1a;">{task['title']}</strong>
                    <span style="background: {priority_color}; color: white; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: 600;">
                        {task.get('priority', 'medium').upper()}
                    </span>
                </div>
                {f'<p style="color: #666; margin: 8px 0;">{task["description"][:200]}...</p>' if task.get('description') else ''}
                <div style="margin-top: 12px; color: #666; font-size: 14px;">
                    {f'📅 Due: <strong>{task["due_date"]}</strong>' if task.get('due_date') else ''}
                    {f' | <a href="{linear_url}" style="color: #0066cc; text-decoration: none;">📊 {linear_id}</a>' if linear_id else ''}
                </div>
            </div>
            """
            task_items.append(task_html)
        
        return '\n'.join(task_items)
    
    def _build_drive_docs_list_html(self, drive_docs: List[Dict]) -> str:
        """Build HTML list of Drive documents."""
        items = []
        for doc in drive_docs:
            if doc.get('url'):
                lang = f" ({doc['language'].upper()})" if doc.get('language') else ""
                items.append(f'<li style="margin: 4px 0;"><a href="{doc["url"]}" style="color: #1976d2;">{doc["name"]}{lang}</a></li>')
        return '\n'.join(items)
    
    def _build_drive_docs_section(self, drive_docs: List[Dict]) -> str:
        """Build HTML section for Drive documents."""
        
        if not drive_docs:
            return ""
        
        html_parts = ['<h3>📁 All Meeting Documents</h3>', '<ul>']
        
        for doc in drive_docs:
            if doc.get('url'):
                lang = f" ({doc['language'].upper()})" if doc.get('language') else ""
                html_parts.append(
                    f'<li><a href="{doc["url"]}" style="color: #0066cc;">{doc["name"]}{lang}</a></li>'
                )
        
        html_parts.append('</ul>')
        
        return '\n'.join(html_parts)
    
    async def _create_meeting_notes_drafts(
        self,
        meeting: Dict,
        attendees: List[Dict],
        drive_docs: List[Dict],
        user_id: str
    ) -> int:
        """
        Create email drafts with meeting notes for all attendees.
        
        Returns:
            Number of drafts created
        """
        
        integration = await self._get_user_integration(user_id, 'google')
        if not integration:
            return 0
        
        drafts_created = 0
        
        for attendee in attendees:
            if not attendee.get('email'):
                continue
            
            try:
                from app.integrations.google_client import get_google_client
                
                client = get_google_client(
                    access_token=integration['access_token'],
                    refresh_token=integration.get('refresh_token')
                )
                
                subject = f"📝 Meeting Notes: {meeting['title']}"
                
                # Build email with links to docs
                body_html = self._build_meeting_notes_email(
                    meeting, attendee, drive_docs
                )
                
                draft = await client.create_email_draft(
                    to=[attendee['email']],
                    subject=subject,
                    body_html=body_html
                )
                
                drafts_created += 1
                print(f"   ✓ Draft for {attendee['name']}")
                
            except Exception as e:
                print(f"   ⚠ Draft failed for {attendee.get('name')}: {e}")
        
        return drafts_created
    
    def _build_meeting_notes_email(
        self,
        meeting: Dict,
        attendee: Dict,
        drive_docs: List[Dict]
    ) -> str:
        """Build meeting notes email HTML."""
        
        meeting_notes_url = next(
            (d['url'] for d in drive_docs if d.get('type') == 'meeting_notes' and d.get('language') == 'sv'),
            None
        )
        
        html = f"""
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #0066cc;">📝 {meeting['title']}</h2>
        <p>Hej {attendee['name']},</p>
        <p>Meeting notes from {meeting.get('meeting_date', 'today')} are ready.</p>
        
        {f'<a href="{meeting_notes_url}" style="display: inline-block; background: #0066cc; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: 600; margin: 20px 0;">📄 View Meeting Notes</a>' if meeting_notes_url else ''}
        
        <h3>📁 All Documents</h3>
        <ul>
            {self._build_drive_docs_list(drive_docs)}
        </ul>
        
        <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 30px 0;">
        <p style="color: #999; font-size: 13px;">
            This is a draft email. Review and send when ready.
        </p>
    </div>
</body>
</html>
        """
        
        return html
    
    def _build_drive_docs_list(self, drive_docs: List[Dict]) -> str:
        """Build HTML list of Drive documents."""
        items = []
        for doc in drive_docs:
            if doc.get('url'):
                lang = f" ({doc['language'].upper()})" if doc.get('language') else ""
                items.append(f'<li><a href="{doc["url"]}" style="color: #0066cc;">{doc["name"]}{lang}</a></li>')
        return '\n'.join(items)
    
    async def _generate_all_documents(
        self,
        meeting: Dict,
        attendees: List[Dict],
        decisions: List[Dict],
        actions: List[Dict]
    ) -> List[Dict]:
        """Generate all document types in both languages."""
        
        from app.api.documents import (
            generate_meeting_notes,
            generate_decision_email,
            generate_action_reminder,
            generate_summary_email
        )
        
        current_date = datetime.now().strftime('%Y-%m-%d')
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M')
        meeting_date = meeting.get('meeting_date') or current_date
        metadata = meeting.get('meeting_metadata', {}) if isinstance(meeting.get('meeting_metadata'), dict) else {}
        
        docs = []
        
        for lang in ['sv', 'en']:
            docs.append({
                'type': 'meeting_notes',
                'language': lang,
                'title': f"Meeting Notes",
                'content': generate_meeting_notes(meeting, attendees, decisions, actions, metadata, meeting_date, current_datetime, lang),
            })
            
            docs.append({
                'type': 'email_decision_update',
                'language': lang,
                'title': f"Decision Update",
                'content': generate_decision_email(meeting, decisions, lang),
            })
            
            docs.append({
                'type': 'email_action_reminder',
                'language': lang,
                'title': f"Action Items",
                'content': generate_action_reminder(meeting, actions, lang),
            })
        
        return docs
    
    async def _get_user_integration(self, user_id: str, integration_type: str) -> Optional[Dict]:
        """Get user's integration credentials."""
        result = self.supabase.table('user_integrations').select('*').match({
            'user_id': user_id,
            'integration_type': integration_type,
            'is_active': True
        }).execute()
        
        return result.data[0] if result.data else None
    
    async def _get_linear_token(self, user_id: str) -> Optional[str]:
        """Get Linear API token (user-level or fall back to global)."""
        
        # Try user-level first
        integration = await self._get_user_integration(user_id, 'linear')
        if integration:
            return integration['access_token']
        
        # Fall back to global API key
        if settings.linear_api_key:
            return settings.linear_api_key
        
        return None
    
    async def _get_linear_assignee_id(
        self,
        owner_name: Optional[str],
        owner_email: Optional[str],
        user_id: str
    ) -> Optional[str]:
        """
        Get Linear user ID for assignee.
        Uses name → Linear ID mapping.
        """
        
        if not owner_name and not owner_email:
            return None
        
        # TODO: Implement user mapping lookup
        # For now, return None (tasks created unassigned)
        return None
    
    async def _get_org_id_for_user(self, user_id: str) -> Optional[str]:
        """Get user's org ID."""
        result = self.supabase.table('org_memberships').select('org_id').eq('user_id', user_id).limit(1).execute()
        return result.data[0]['org_id'] if result.data else None


# Export singleton
enhanced_distribution = EnhancedDistributionPipeline()

