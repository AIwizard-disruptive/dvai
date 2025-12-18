"""
Slack integration client for DV VC Operating System.
Handles notifications, alerts, and team collaboration across all 4 wheels.
"""
from typing import List, Dict, Optional, Any
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
import logging

logger = logging.getLogger(__name__)


class SlackClient:
    """
    Slack client for sending notifications and managing channels.
    
    Use cases:
    - PEOPLE: Notify team about candidates, interviews, new hires
    - DEALFLOW: Alert partners about high-score leads, research completion
    - BUILDING: Notify about at-risk targets, support requests, qualification changes
    - ADMIN: Send critical alerts to partners
    """
    
    def __init__(self, bot_token: str, app_token: Optional[str] = None):
        """
        Initialize Slack client.
        
        Args:
            bot_token: Slack bot token (xoxb-...)
            app_token: Optional app-level token for Socket Mode
        """
        self.client = AsyncWebClient(token=bot_token)
        self.app_token = app_token
    
    async def post_message(
        self,
        channel: str,
        text: str,
        blocks: Optional[List[Dict]] = None,
        thread_ts: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post message to a channel.
        
        Args:
            channel: Channel ID or name (e.g., "#general" or "C1234567890")
            text: Plain text message (fallback for notifications)
            blocks: Optional Block Kit blocks for rich formatting
            thread_ts: Optional thread timestamp to reply in thread
            **kwargs: Additional arguments for chat.postMessage
        
        Returns:
            Response from Slack API with ts, channel, etc.
        
        Example:
            await slack.post_message(
                "#dealflow",
                "New high-score lead!",
                blocks=[{
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "*Acme Corp* scored 85/100"}
                }]
            )
        """
        try:
            response = await self.client.chat_postMessage(
                channel=channel,
                text=text,
                blocks=blocks,
                thread_ts=thread_ts,
                **kwargs
            )
            return response.data
        except SlackApiError as e:
            logger.error(f"Error posting message to Slack: {e.response['error']}")
            raise
    
    async def send_dm(
        self,
        user_id: str,
        text: str,
        blocks: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Send direct message to a user.
        
        Args:
            user_id: Slack user ID (U1234567890)
            text: Plain text message
            blocks: Optional Block Kit blocks
        
        Returns:
            Response from Slack API
        
        Example:
            await slack.send_dm(
                "U1234567890",
                "You have a new interview scheduled",
                blocks=[...]
            )
        """
        try:
            # Open DM channel
            dm_response = await self.client.conversations_open(users=[user_id])
            channel_id = dm_response['channel']['id']
            
            # Send message
            return await self.post_message(channel_id, text, blocks)
        except SlackApiError as e:
            logger.error(f"Error sending DM to user {user_id}: {e.response['error']}")
            raise
    
    async def create_channel(
        self,
        name: str,
        is_private: bool = False,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new Slack channel.
        
        Args:
            name: Channel name (without #, lowercase, no spaces)
            is_private: Whether to create private channel
            description: Optional channel description
        
        Returns:
            Channel data with id, name, etc.
        
        Example:
            # Create channel per portfolio company
            channel = await slack.create_channel(
                "portfolio-acme-corp",
                is_private=True,
                description="Acme Corp - Series A portfolio company"
            )
        """
        try:
            response = await self.client.conversations_create(
                name=name,
                is_private=is_private
            )
            
            channel_id = response['channel']['id']
            
            # Set description if provided
            if description:
                await self.client.conversations_setTopic(
                    channel=channel_id,
                    topic=description
                )
            
            return response['channel']
        except SlackApiError as e:
            logger.error(f"Error creating channel {name}: {e.response['error']}")
            raise
    
    async def upload_file(
        self,
        channels: List[str],
        file_path: str = None,
        file_content: bytes = None,
        filename: str = None,
        title: Optional[str] = None,
        initial_comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload file to one or more channels.
        
        Args:
            channels: List of channel IDs
            file_path: Path to file on disk
            file_content: File content as bytes (alternative to file_path)
            filename: Filename to display
            title: Optional file title
            initial_comment: Optional comment with the file
        
        Returns:
            Response with file data
        
        Example:
            # Upload research report
            await slack.upload_file(
                ["C1234567890"],
                file_path="/tmp/research_report.pdf",
                title="Acme Corp Research Report",
                initial_comment="Research completed for high-priority lead"
            )
        """
        try:
            kwargs = {
                'channels': ','.join(channels),
                'title': title,
                'initial_comment': initial_comment,
                'filename': filename
            }
            
            if file_path:
                kwargs['file'] = file_path
            elif file_content:
                kwargs['content'] = file_content
            else:
                raise ValueError("Either file_path or file_content must be provided")
            
            response = await self.client.files_upload(**kwargs)
            return response.data
        except SlackApiError as e:
            logger.error(f"Error uploading file to Slack: {e.response['error']}")
            raise
    
    async def add_reaction(
        self,
        channel: str,
        timestamp: str,
        emoji: str
    ) -> Dict[str, Any]:
        """
        Add emoji reaction to a message.
        
        Args:
            channel: Channel ID
            timestamp: Message timestamp
            emoji: Emoji name (without colons, e.g., "thumbsup")
        
        Returns:
            Response from Slack API
        
        Example:
            await slack.add_reaction("C1234567890", "1234567890.123456", "white_check_mark")
        """
        try:
            response = await self.client.reactions_add(
                channel=channel,
                timestamp=timestamp,
                name=emoji
            )
            return response.data
        except SlackApiError as e:
            logger.error(f"Error adding reaction: {e.response['error']}")
            raise
    
    async def update_message(
        self,
        channel: str,
        ts: str,
        text: str,
        blocks: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing message.
        
        Args:
            channel: Channel ID
            ts: Message timestamp to update
            text: New text
            blocks: New blocks
        
        Returns:
            Response from Slack API
        
        Example:
            # Update qualification status message
            await slack.update_message(
                "C1234567890",
                "1234567890.123456",
                "Lead qualification updated: 85 → 90",
                blocks=[...]
            )
        """
        try:
            response = await self.client.chat_update(
                channel=channel,
                ts=ts,
                text=text,
                blocks=blocks
            )
            return response.data
        except SlackApiError as e:
            logger.error(f"Error updating message: {e.response['error']}")
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Find Slack user by email address.
        
        Args:
            email: User's email address
        
        Returns:
            User data or None if not found
        
        Example:
            user = await slack.get_user_by_email("marcus@disruptiveventures.se")
            if user:
                await slack.send_dm(user['id'], "New task assigned")
        """
        try:
            response = await self.client.users_lookupByEmail(email=email)
            return response['user']
        except SlackApiError as e:
            if e.response['error'] == 'users_not_found':
                return None
            logger.error(f"Error looking up user by email: {e.response['error']}")
            raise
    
    async def schedule_message(
        self,
        channel: str,
        text: str,
        post_at: int,
        blocks: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Schedule a message to be sent later.
        
        Args:
            channel: Channel ID
            text: Message text
            post_at: Unix timestamp when to post
            blocks: Optional blocks
        
        Returns:
            Scheduled message data with scheduled_message_id
        
        Example:
            # Schedule reminder about target deadline
            import time
            tomorrow = int(time.time()) + 86400
            await slack.schedule_message(
                "#portfolio",
                "Reminder: Target deadline is tomorrow",
                tomorrow
            )
        """
        try:
            response = await self.client.chat_scheduleMessage(
                channel=channel,
                text=text,
                post_at=post_at,
                blocks=blocks
            )
            return response.data
        except SlackApiError as e:
            logger.error(f"Error scheduling message: {e.response['error']}")
            raise


# Pre-built message templates for common notifications

class SlackMessageTemplates:
    """Pre-built message templates for common DV notifications."""
    
    @staticmethod
    def high_score_lead(lead_data: Dict) -> Dict:
        """Template for high-score lead notification (DEALFLOW wheel)."""
        return {
            "text": f"🎯 High-score lead: {lead_data['company_name']} ({lead_data['score']}/100)",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🎯 High-Score Lead: {lead_data['company_name']}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Score:*\n{lead_data['score']}/100"},
                        {"type": "mrkdwn", "text": f"*Stage:*\n{lead_data.get('stage', 'N/A')}"},
                        {"type": "mrkdwn", "text": f"*Founder:*\n{lead_data.get('founder_name', 'N/A')}"},
                        {"type": "mrkdwn", "text": f"*Source:*\n{lead_data.get('source', 'N/A')}"}
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*One-liner:*\n{lead_data.get('one_liner', 'No description')}"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "View in System"},
                            "url": f"{lead_data.get('url', '#')}",
                            "style": "primary"
                        }
                    ]
                }
            ]
        }
    
    @staticmethod
    def target_at_risk(target_data: Dict) -> Dict:
        """Template for at-risk target alert (BUILDING wheel)."""
        return {
            "text": f"⚠️ Target at risk: {target_data['target_name']} - {target_data['company_name']}",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"⚠️ Target At Risk"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Company:*\n{target_data['company_name']}"},
                        {"type": "mrkdwn", "text": f"*Target:*\n{target_data['target_name']}"},
                        {"type": "mrkdwn", "text": f"*Progress:*\n{target_data['progress']}%"},
                        {"type": "mrkdwn", "text": f"*Deadline:*\n{target_data.get('deadline', 'N/A')}"}
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*AI Recommendation:*\n{target_data.get('recommendation', 'No recommendation yet')}"
                    }
                }
            ]
        }
    
    @staticmethod
    def candidate_ready(candidate_data: Dict) -> Dict:
        """Template for candidate ready for review (PEOPLE wheel)."""
        return {
            "text": f"👤 Candidate ready: {candidate_data['name']} ({candidate_data['score']}/100)",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"👤 Candidate Ready for Review"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Name:*\n{candidate_data['name']}"},
                        {"type": "mrkdwn", "text": f"*Role:*\n{candidate_data['role']}"},
                        {"type": "mrkdwn", "text": f"*AI Score:*\n{candidate_data['score']}/100"},
                        {"type": "mrkdwn", "text": f"*Stage:*\n{candidate_data.get('stage', 'Applied')}"}
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Summary:*\n{candidate_data.get('summary', 'No summary')}"
                    }
                }
            ]
        }


