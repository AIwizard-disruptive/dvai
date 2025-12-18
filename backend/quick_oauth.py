#!/usr/bin/env python3
"""Quick OAuth setup with new credentials."""

import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file'
]

def main():
    print("\n🔐 Starting Google OAuth...")
    print("   A browser will open - sign in with wizard@disruptiveventures.se")
    
    with open('/tmp/google_client_config.json') as f:
        client_config = json.load(f)
    
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=0)  # Use random available port
    
    # Save credentials
    creds_data = {
        'access_token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': 'https://oauth2.googleapis.com/token',
        'client_id': client_config['installed']['client_id'],
        'client_secret': client_config['installed']['client_secret'],
        'scopes': SCOPES
    }
    
    with open('/tmp/google_credentials.json', 'w') as f:
        json.dump(creds_data, f, indent=2)
    
    print("\n✅ Authentication successful!")
    print("   Credentials saved to /tmp/google_credentials.json")
    print("\n🚀 Ready to generate documents!")

if __name__ == "__main__":
    main()

