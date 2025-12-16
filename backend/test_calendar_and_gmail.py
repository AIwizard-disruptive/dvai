#!/usr/bin/env python3
"""
Test Calendar and Gmail APIs
1. Create calendar event today at 15:00
2. Create email draft to Serge about the system
"""
import asyncio
import json
from datetime import datetime, timedelta
from app.integrations.google_client import get_google_client


async def test_calendar_and_gmail():
    """Test both Calendar and Gmail APIs."""
    
    print("\n" + "="*80)
    print("TESTING CALENDAR & GMAIL APIS")
    print("="*80)
    
    # Load Google credentials
    with open('/tmp/google_credentials.json', 'r') as f:
        creds = json.load(f)
    
    print("\n✓ Loaded Google credentials")
    
    # Create Google client
    client = get_google_client(
        access_token=creds['access_token'],
        refresh_token=creds.get('refresh_token')
    )
    
    print("✓ Google client created")
    
    # TEST 1: Create Calendar Event
    print("\n" + "-"*80)
    print("TEST 1: CREATE CALENDAR EVENT")
    print("-"*80)
    
    # Today at 15:00
    today = datetime.now().replace(hour=15, minute=0, second=0, microsecond=0)
    end_time = today + timedelta(hours=1)
    
    print(f"\nCreating event:")
    print(f"  Title: Demo - Meeting Intelligence System")
    print(f"  Start: {today.strftime('%Y-%m-%d %H:%M')}")
    print(f"  End: {end_time.strftime('%Y-%m-%d %H:%M')}")
    print(f"  Attendee: wizard@disruptiveventures.se")
    
    try:
        event = await client.create_calendar_event(
            summary="Demo - Meeting Intelligence System",
            start_time=today,
            end_time=end_time,
            description="""Demo of the automated meeting intelligence platform.

What we'll show:
- Upload meeting files
- Auto-parse action items
- Auto-generate Google Drive folders
- Auto-create Linear tasks
- Full organization integration

Prepared by: Meeting Intelligence Platform
""",
            attendees=["wizard@disruptiveventures.se"],
            send_updates=False  # Don't send invites, just create event
        )
        
        print(f"\n✅ Calendar event created!")
        print(f"   Event ID: {event['id']}")
        print(f"   URL: {event.get('html_link', 'N/A')}")
        print(f"   Status: {event.get('status', 'unknown')}")
    
    except Exception as e:
        print(f"\n❌ Calendar event failed: {str(e)}")
    
    # TEST 2: Create Gmail Draft
    print("\n" + "-"*80)
    print("TEST 2: CREATE GMAIL DRAFT TO SERGE")
    print("-"*80)
    
    subject = "Meeting Intelligence System - Ready to Use!"
    
    body_html = """<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 700px; margin: 0 auto; padding: 20px;">
    
    <h1 style="color: #0A2540; border-bottom: 3px solid #635BFF; padding-bottom: 12px;">
        🎉 Meeting Intelligence System - Ready!
    </h1>
    
    <p>Hej Serge,</p>
    
    <p>I wanted to share what we've built today – our automated meeting intelligence platform is now live and ready for the team!</p>
    
    <h2 style="color: #0A2540; margin-top: 30px;">✨ What It Does</h2>
    
    <div style="background: #F7FAFC; padding: 20px; border-radius: 12px; border-left: 4px solid #635BFF; margin: 20px 0;">
        <p><strong>Upload a meeting file</strong> → The system automatically:</p>
        <ul style="line-height: 1.8;">
            <li>📝 <strong>Parses the transcript</strong> (extracts attendees, action items, decisions)</li>
            <li>📁 <strong>Creates Google Drive folder</strong> with organized documents</li>
            <li>📄 <strong>Generates 6 documents</strong> (Meeting Notes, Decisions, Actions in Swedish & English)</li>
            <li>📊 <strong>Creates Linear project</strong> for the meeting</li>
            <li>✅ <strong>Creates tasks in Linear</strong> with links to all Drive documents</li>
            <li>👥 <strong>Assigns to correct people</strong> automatically</li>
            <li>📅 <strong>Sets deadlines</strong> (2 weeks default or from transcript)</li>
        </ul>
        <p style="margin-top: 16px; color: #635BFF; font-weight: 600;">Everything happens in 1-2 minutes. Zero manual work!</p>
    </div>
    
    <h2 style="color: #0A2540; margin-top: 30px;">🎯 Live Examples</h2>
    
    <p>We already processed 6 meetings with full automation:</p>
    
    <div style="background: white; padding: 16px; border-radius: 8px; margin: 12px 0; border: 1px solid #EDF2F7;">
        <strong>Veckomöte - Team Meeting</strong><br>
        <a href="https://linear.app/disruptiveventures/project/veckomote-team-meeting-marcus-intro-ai-projekt-uppfoljningar-none-3b5b9bf805b7" style="color: #635BFF; text-decoration: none;">📊 Linear Project (14 tasks)</a> | 
        <a href="https://drive.google.com/drive/folders/1T79qOhcV-PO7NZ0k9gKK03XGk9MRcIJN" style="color: #635BFF; text-decoration: none;">📁 Drive Folder</a>
    </div>
    
    <div style="background: white; padding: 16px; border-radius: 8px; margin: 12px 0; border: 1px solid #EDF2F7;">
        <strong>IK Disruptive Ventures Möte</strong><br>
        <a href="https://linear.app/disruptiveventures/project/ik-disruptive-ventures-mote-20231005-2023-10-05-ik-disrup-2023-10-05-1c05345f96d9" style="color: #635BFF; text-decoration: none;">📊 Linear Project (2 tasks)</a> | 
        <a href="https://drive.google.com/drive/folders/1H6eR8QfnsZmVcIQA4-Wq9SzpTLfEQHsm" style="color: #635BFF; text-decoration: none;">📁 Drive Folder</a>
    </div>
    
    <p style="color: #666; font-size: 14px;">...and 4 more meetings, all fully automated</p>
    
    <h2 style="color: #0A2540; margin-top: 30px;">👥 How Team Members Use It</h2>
    
    <div style="background: #F7FAFC; padding: 20px; border-radius: 12px; margin: 20px 0;">
        <h3 style="margin-top: 0; color: #635BFF;">Option 1: Linear (Recommended)</h3>
        <p>Go to <a href="https://linear.app/disruptiveventures/projects" style="color: #635BFF;">Linear Projects</a></p>
        <ul style="line-height: 1.8;">
            <li>See all meeting projects</li>
            <li>Click any meeting → View Kanban board</li>
            <li>Use "My Issues" to see only YOUR tasks</li>
            <li>Each task has links to all meeting documents</li>
            <li>Drag & drop to update status</li>
            <li>Progress tracked automatically</li>
        </ul>
        
        <h3 style="margin-top: 20px; color: #635BFF;">Option 2: Google Drive</h3>
        <p>All meeting folders organized by date at:<br>
        <a href="https://drive.google.com/drive/folders/1T79qOhcV-PO7NZ0k9gKK03XGk9MRcIJN" style="color: #635BFF;">/Meetings/YYYY/Month/</a></p>
        <ul style="line-height: 1.8;">
            <li>Meeting Notes (SV & EN)</li>
            <li>Decision Updates</li>
            <li>Action Items Summary</li>
            <li>All editable Google Docs</li>
        </ul>
        
        <h3 style="margin-top: 20px; color: #635BFF;">Option 3: Dashboard</h3>
        <p><a href="http://localhost:8000/dashboard-ui" style="color: #635BFF;">Meeting Intelligence Dashboard</a></p>
        <ul style="line-height: 1.8;">
            <li>See all meetings in one place</li>
            <li>Quick links to Drive & Linear</li>
            <li>Progress tracking</li>
            <li>Upload new meetings</li>
        </ul>
    </div>
    
    <h2 style="color: #0A2540; margin-top: 30px;">📊 Current Stats</h2>
    
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin: 20px 0;">
        <div style="background: white; padding: 20px; border-radius: 8px; text-align: center; border: 2px solid #00C48C;">
            <div style="font-size: 36px; font-weight: bold; color: #00C48C;">6</div>
            <div style="color: #425466;">Meetings Processed</div>
        </div>
        <div style="background: white; padding: 20px; border-radius: 8px; text-align: center; border: 2px solid #635BFF;">
            <div style="font-size: 36px; font-weight: bold; color: #635BFF;">21</div>
            <div style="color: #425466;">Tasks in Linear</div>
        </div>
        <div style="background: white; padding: 20px; border-radius: 8px; text-align: center; border: 2px solid #00D4FF;">
            <div style="font-size: 36px; font-weight: bold; color: #00D4FF;">36</div>
            <div style="color: #425466;">Documents Generated</div>
        </div>
        <div style="background: white; padding: 20px; border-radius: 8px; text-align: center; border: 2px solid #FFA726;">
            <div style="font-size: 36px; font-weight: bold; color: #FFA726;">~10h</div>
            <div style="color: #425466;">Time Saved</div>
        </div>
    </div>
    
    <h2 style="color: #0A2540; margin-top: 30px;">🚀 Next Steps</h2>
    
    <ol style="line-height: 1.8;">
        <li>Team members join Linear workspace</li>
        <li>Start uploading meeting files</li>
        <li>Review generated tasks in Linear</li>
        <li>Track progress on Kanban boards</li>
        <li>Enjoy automated workflow!</li>
    </ol>
    
    <hr style="border: none; border-top: 1px solid #EDF2F7; margin: 30px 0;">
    
    <p style="color: #666;">
        Questions? The system is ready to demo tomorrow at 9 AM.<br>
        <strong>Dashboard:</strong> <a href="http://localhost:8000/dashboard-ui" style="color: #635BFF;">http://localhost:8000/dashboard-ui</a>
    </p>
    
    <p style="color: #999; font-size: 13px; margin-top: 30px;">
        <em>Auto-generated by Meeting Intelligence Platform</em>
    </p>

</body>
</html>"""
    
    print(f"\nCreating draft email:")
    print(f"  To: serge@disruptiveventures.se")
    print(f"  Subject: {subject}")
    
    try:
        draft = await client.create_email_draft(
            to=["serge@disruptiveventures.se"],
            subject=subject,
            body_html=body_html
        )
        
        print(f"\n✅ Gmail draft created!")
        print(f"   Draft ID: {draft['id']}")
        print(f"   Message ID: {draft.get('message_id', 'N/A')}")
        print(f"\n📧 Check Gmail Drafts: https://mail.google.com/mail/#drafts")
    
    except Exception as e:
        print(f"\n❌ Gmail draft failed: {str(e)}")
    
    print("\n" + "="*80)
    print("✅ API TESTS COMPLETE")
    print("="*80)
    print("\nCheck:")
    print("  📅 Google Calendar for today at 15:00")
    print("  📧 Gmail Drafts folder")


if __name__ == "__main__":
    asyncio.run(test_calendar_and_gmail())


