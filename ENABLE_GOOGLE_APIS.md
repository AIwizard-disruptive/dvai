# Enable Google Tasks & Contacts APIs

## ✅ What You Already Have

From your `.env` file:
```
GOOGLE_CLIENT_ID=***REMOVED***
GOOGLE_CLIENT_SECRET=***REMOVED***
```

✅ OAuth is configured!  
⚠️ Just need to enable APIs + add scopes

---

## 🚀 Quick Setup (5 minutes)

### **Step 1: Enable Google Tasks API**

1. **Go to Google Cloud Console:**
   ```
   https://console.cloud.google.com/apis/library/tasks.googleapis.com
   ```

2. **Make sure correct project is selected** (top dropdown)
   - Should be the project with your client ID ending in `...llqi8`

3. **Click "ENABLE"**
   - Wait 10 seconds for it to activate

4. **Verify:**
   ```
   https://console.cloud.google.com/apis/dashboard
   ```
   - Should see "Google Tasks API" in the list

---

### **Step 2: Enable Google People API (for Contacts)**

1. **Go to Google Cloud Console:**
   ```
   https://console.cloud.google.com/apis/library/people.googleapis.com
   ```

2. **Click "ENABLE"**

3. **Also enable Contacts API:**
   ```
   https://console.cloud.google.com/apis/library/contacts.googleapis.com
   ```
   - Click "ENABLE"

---

### **Step 3: Add Scopes to OAuth Consent Screen**

1. **Go to OAuth consent screen:**
   ```
   https://console.cloud.google.com/apis/credentials/consent
   ```

2. **Click "EDIT APP"** (or configure if first time)

3. **Click "ADD OR REMOVE SCOPES"**

4. **Add these scopes** (paste into "Manually add scopes" field):

   ```
   https://www.googleapis.com/auth/tasks
   https://www.googleapis.com/auth/tasks.readonly
   https://www.googleapis.com/auth/contacts
   https://www.googleapis.com/auth/contacts.readonly
   https://www.googleapis.com/auth/directory.readonly
   ```

5. **Click "UPDATE"** at bottom

6. **Click "SAVE AND CONTINUE"**

7. **Review summary and click "BACK TO DASHBOARD"**

---

## ✅ Verify Setup

### **Test Google Tasks API**

```bash
# In your backend directory
python3 -c "
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# You'll need to get an access token first via OAuth flow
# This is just to test the API is enabled
print('Google Tasks API is enabled!')
"
```

### **Test in Your App**

1. Start your backend:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. Open browser:
   ```
   http://localhost:8000/integration-test
   ```

3. Click **"Connect Google"**

4. Authorize the app

5. Try fetching tasks:
   ```
   GET http://localhost:8000/google/tasks
   ```

---

## 📋 Complete Scope List

Here are ALL the scopes you should have in OAuth consent screen:

```
# Email & Profile (basic)
https://www.googleapis.com/auth/userinfo.email
https://www.googleapis.com/auth/userinfo.profile

# Google Drive
https://www.googleapis.com/auth/drive.file
https://www.googleapis.com/auth/drive.readonly

# Gmail
https://www.googleapis.com/auth/gmail.send
https://www.googleapis.com/auth/gmail.readonly

# Google Calendar
https://www.googleapis.com/auth/calendar
https://www.googleapis.com/auth/calendar.events

# Google Tasks (NEW)
https://www.googleapis.com/auth/tasks
https://www.googleapis.com/auth/tasks.readonly

# Google Contacts (NEW)
https://www.googleapis.com/auth/contacts
https://www.googleapis.com/auth/contacts.readonly

# Google Workspace Directory (for employee profiles)
https://www.googleapis.com/auth/admin.directory.user
https://www.googleapis.com/auth/admin.directory.user.readonly
```

---

## 🔧 Quick Test Script

Create `backend/test_google_apis.py`:

```python
#!/usr/bin/env python3
"""Test Google Tasks and Contacts APIs"""

import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def test_tasks_api(access_token: str):
    """Test Google Tasks API"""
    try:
        creds = Credentials(token=access_token)
        service = build('tasks', 'v1', credentials=creds)
        
        # List task lists
        results = service.tasklists().list().execute()
        items = results.get('items', [])
        
        print("✅ Google Tasks API working!")
        print(f"Found {len(items)} task lists:")
        for item in items:
            print(f"  - {item['title']} (ID: {item['id']})")
        
        return True
    except HttpError as error:
        print(f"❌ Google Tasks API error: {error}")
        return False

def test_contacts_api(access_token: str):
    """Test Google People/Contacts API"""
    try:
        creds = Credentials(token=access_token)
        service = build('people', 'v1', credentials=creds)
        
        # List connections (contacts)
        results = service.people().connections().list(
            resourceName='people/me',
            pageSize=10,
            personFields='names,emailAddresses'
        ).execute()
        
        connections = results.get('connections', [])
        
        print("✅ Google Contacts API working!")
        print(f"Found {len(connections)} contacts (showing first 10)")
        for person in connections:
            names = person.get('names', [])
            if names:
                name = names[0].get('displayName')
                print(f"  - {name}")
        
        return True
    except HttpError as error:
        print(f"❌ Google Contacts API error: {error}")
        return False

if __name__ == "__main__":
    print("Google APIs Test")
    print("=" * 50)
    print()
    
    # You need to get access_token from OAuth flow first
    print("⚠️  First, authenticate via OAuth flow:")
    print("   1. Go to http://localhost:8000/integration-test")
    print("   2. Click 'Connect Google'")
    print("   3. Copy the access_token from the response")
    print()
    
    access_token = input("Paste access_token here: ").strip()
    
    if not access_token:
        print("❌ No token provided")
        exit(1)
    
    print()
    print("Testing APIs...")
    print()
    
    tasks_ok = test_tasks_api(access_token)
    print()
    contacts_ok = test_contacts_api(access_token)
    
    print()
    print("=" * 50)
    if tasks_ok and contacts_ok:
        print("✅ All APIs working!")
    else:
        print("⚠️  Some APIs not working - check errors above")
```

**Run it:**
```bash
cd backend
python test_google_apis.py
```

---

## 🐛 Troubleshooting

### **"API not enabled" error**

Go back to:
```
https://console.cloud.google.com/apis/dashboard
```

Make sure you see:
- ✅ Google Tasks API
- ✅ Google People API
- ✅ Contacts API (Legacy)

### **"Insufficient permissions" error**

1. Check OAuth consent screen has the scopes
2. **Important:** Re-authorize the app (revoke and reconnect)
   - Go to: https://myaccount.google.com/permissions
   - Find your app, click "Remove access"
   - Re-connect via OAuth flow

### **"Access blocked" error**

If app is not verified:
1. OAuth consent screen → "PUBLISH APP"
2. Or add test users: OAuth consent screen → "ADD USERS"
3. Add: wizard@disruptiveventures.se, serge@disruptiveventures.se

---

## 📝 Summary

**What you need to do:**

1. ✅ Enable Google Tasks API (1 click)
2. ✅ Enable Google People API (1 click)  
3. ✅ Enable Contacts API (1 click)
4. ✅ Add scopes to OAuth consent screen (copy-paste)
5. ✅ Re-authorize your app (revoke + reconnect)

**Total time:** 5 minutes

---

## ✅ After Setup

Once APIs are enabled, you can:

1. **Fetch Google Tasks:**
   ```python
   from googleapiclient.discovery import build
   
   service = build('tasks', 'v1', credentials=creds)
   tasklists = service.tasklists().list().execute()
   ```

2. **Create Google Task:**
   ```python
   task = {
       'title': 'Review Q4 deck',
       'notes': 'Provide feedback on investor presentation'
   }
   service.tasks().insert(tasklist='@default', body=task).execute()
   ```

3. **Fetch Contacts:**
   ```python
   service = build('people', 'v1', credentials=creds)
   results = service.people().connections().list(
       resourceName='people/me',
       personFields='names,emailAddresses'
   ).execute()
   ```

4. **Create Contact:**
   ```python
   contact = {
       'names': [{'givenName': 'John', 'familyName': 'Doe'}],
       'emailAddresses': [{'value': 'john@example.com'}]
   }
   service.people().createContact(body=contact).execute()
   ```

---

**Your OAuth is ready - just enable the APIs and you're good to go!** 🚀
