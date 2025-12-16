#!/usr/bin/env python3
"""
Create calendar event for today at 15:00 with Serge invited.
"""
import asyncio
import json
from datetime import datetime, timedelta
from app.integrations.google_client import get_google_client


async def create_demo_event():
    """Create calendar event for 9 AM demo prep."""
    
    print("\n📅 Creating Calendar Event...\n")
    
    # Load credentials
    with open('/tmp/google_credentials.json', 'r') as f:
        creds = json.load(f)
    
    client = get_google_client(
        access_token=creds['access_token'],
        refresh_token=creds.get('refresh_token')
    )
    
    # Today at 15:00
    today = datetime.now().replace(hour=15, minute=0, second=0, microsecond=0)
    end_time = today + timedelta(hours=1)
    
    print(f"Event Details:")
    print(f"  Title: Meeting Intelligence Demo Prep")
    print(f"  When: {today.strftime('%Y-%m-%d at %H:%M')}")
    print(f"  Duration: 1 hour")
    print(f"  Organizer: wizard@disruptiveventures.se")
    print(f"  Attendee: serge@disruptiveventures.se")
    
    try:
        event = await client.create_calendar_event(
            summary="Meeting Intelligence Demo Prep",
            start_time=today,
            end_time=end_time,
            description="""Prepare for tomorrow's 9 AM demo of Meeting Intelligence Platform.

What we'll show:
✅ All 6 meetings processed automatically
✅ Google Drive folders with 36 documents
✅ Linear projects with 21 tasks
✅ Kanban boards and progress tracking
✅ Live upload demonstration

System Status: 100% Ready
Dashboard: http://localhost:8000/dashboard-ui
Linear: https://linear.app/disruptiveventures/projects

See you at 15:00!
""",
            location="Office / Zoom",
            attendees=["wizard@disruptiveventures.se", "serge@disruptiveventures.se"],
            send_updates=True  # Send calendar invites
        )
        
        print(f"\n✅ Calendar event created!")
        print(f"   Event ID: {event['id']}")
        print(f"   URL: {event.get('html_link', 'N/A')[:60]}")
        print(f"   Status: {event.get('status')}")
        print(f"\n📧 Calendar invite sent to Serge!")
        print(f"\n🎯 Check your Google Calendar at 15:00 today")
    
    except Exception as e:
        error_msg = str(e)
        if 'calendar-json.googleapis.com' in error_msg or 'Calendar API has not been used' in error_msg:
            print(f"\n⚠️ Calendar API not enabled yet!")
            print(f"\n📋 Quick fix:")
            print(f"   1. Open: https://console.developers.google.com/apis/api/calendar-json.googleapis.com/overview?project=16579505104")
            print(f"   2. Click the blue 'ENABLE' button")
            print(f"   3. Wait 30 seconds")
            print(f"   4. Run this script again: python3 create_calendar_event_now.py")
        else:
            print(f"\n❌ Error: {error_msg[:200]}")


if __name__ == "__main__":
    asyncio.run(create_demo_event())


