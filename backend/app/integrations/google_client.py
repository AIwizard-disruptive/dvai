"""Google Workspace integration (Gmail + Calendar)."""
import base64
from typing import Optional
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.config import settings


class GoogleClient:
    """Client for Google Workspace APIs."""
    
    def __init__(
        self,
        access_token: str,
        refresh_token: Optional[str] = None,
        token_expiry: Optional[datetime] = None,
    ):
        """
        Initialize Google client with OAuth credentials.
        
        Args:
            access_token: OAuth access token
            refresh_token: OAuth refresh token
            token_expiry: Token expiry datetime
        """
        self.credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
        )
        
        if token_expiry:
            self.credentials.expiry = token_expiry
    
    def get_gmail_service(self):
        """Get Gmail API service."""
        return build("gmail", "v1", credentials=self.credentials)
    
    def get_calendar_service(self):
        """Get Calendar API service."""
        return build("calendar", "v3", credentials=self.credentials)
    
    async def create_email_draft(
        self,
        to: list[str],
        subject: str,
        body_html: str,
        cc: Optional[list[str]] = None,
        bcc: Optional[list[str]] = None,
    ) -> dict:
        """
        Create a Gmail draft.
        
        Args:
            to: Recipient email addresses
            subject: Email subject
            body_html: HTML body content
            cc: CC recipients
            bcc: BCC recipients
        
        Returns:
            Draft data with ID
        """
        service = self.get_gmail_service()
        
        # Create message
        message = MIMEText(body_html, "html")
        message["To"] = ", ".join(to)
        message["Subject"] = subject
        
        if cc:
            message["Cc"] = ", ".join(cc)
        if bcc:
            message["Bcc"] = ", ".join(bcc)
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        
        # Create draft
        try:
            draft = service.users().drafts().create(
                userId="me",
                body={"message": {"raw": raw_message}},
            ).execute()
            
            return {
                "id": draft["id"],
                "message_id": draft["message"]["id"],
            }
        
        except HttpError as e:
            raise ValueError(f"Failed to create draft: {e}") from e
    
    async def send_email(
        self,
        to: list[str],
        subject: str,
        body_html: str,
        cc: Optional[list[str]] = None,
        bcc: Optional[list[str]] = None,
    ) -> dict:
        """
        Send an email via Gmail.
        
        Args:
            to: Recipient email addresses
            subject: Email subject
            body_html: HTML body content
            cc: CC recipients
            bcc: BCC recipients
        
        Returns:
            Sent message data
        """
        service = self.get_gmail_service()
        
        # Create message
        message = MIMEText(body_html, "html")
        message["To"] = ", ".join(to)
        message["Subject"] = subject
        
        if cc:
            message["Cc"] = ", ".join(cc)
        if bcc:
            message["Bcc"] = ", ".join(bcc)
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        
        # Send
        try:
            sent = service.users().messages().send(
                userId="me",
                body={"raw": raw_message},
            ).execute()
            
            return {
                "id": sent["id"],
                "thread_id": sent["threadId"],
            }
        
        except HttpError as e:
            raise ValueError(f"Failed to send email: {e}") from e
    
    async def create_calendar_event(
        self,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[list[str]] = None,
        send_updates: bool = False,
    ) -> dict:
        """
        Create a Google Calendar event.
        
        Args:
            summary: Event title
            start_time: Start datetime
            end_time: End datetime
            description: Event description
            location: Event location
            attendees: List of attendee emails
            send_updates: Whether to send invites
        
        Returns:
            Created event data
        """
        service = self.get_calendar_service()
        
        event = {
            "summary": summary,
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "UTC",
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": "UTC",
            },
        }
        
        if description:
            event["description"] = description
        if location:
            event["location"] = location
        if attendees:
            event["attendees"] = [{"email": email} for email in attendees]
        
        try:
            created_event = service.events().insert(
                calendarId="primary",
                body=event,
                sendUpdates="all" if send_updates else "none",
            ).execute()
            
            return {
                "id": created_event["id"],
                "html_link": created_event.get("htmlLink"),
                "status": created_event.get("status"),
            }
        
        except HttpError as e:
            raise ValueError(f"Failed to create calendar event: {e}") from e
    
    async def get_calendar_events(
        self,
        time_min: datetime,
        time_max: datetime,
        max_results: int = 10,
    ) -> list[dict]:
        """
        Get calendar events in time range.
        
        Args:
            time_min: Start of time range
            time_max: End of time range
            max_results: Maximum number of results
        
        Returns:
            List of events
        """
        service = self.get_calendar_service()
        
        try:
            events_result = service.events().list(
                calendarId="primary",
                timeMin=time_min.isoformat() + "Z",
                timeMax=time_max.isoformat() + "Z",
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            ).execute()
            
            return events_result.get("items", [])
        
        except HttpError as e:
            raise ValueError(f"Failed to fetch calendar events: {e}") from e


def get_google_client(
    access_token: str,
    refresh_token: Optional[str] = None,
    token_expiry: Optional[datetime] = None,
) -> GoogleClient:
    """Get Google client instance."""
    return GoogleClient(
        access_token=access_token,
        refresh_token=refresh_token,
        token_expiry=token_expiry,
    )



