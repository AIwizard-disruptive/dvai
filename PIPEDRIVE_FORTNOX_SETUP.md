# Pipedrive & Fortnox API Setup Guide 🔑

**Date:** December 17, 2025

---

## Overview

Configuration has been added for both Pipedrive CRM and Fortnox Accounting APIs. This guide explains how to obtain API credentials and configure the integrations.

---

## 1. Pipedrive CRM Setup 📊

### What You'll Get Access To:
- Deals pipeline (leads, opportunities, proposals)
- Organizations (companies in CRM)
- Persons (contacts)
- Activities (calls, meetings, tasks)
- Notes and custom fields

### Getting Your API Token:

#### Step 1: Log into Pipedrive
```
https://yourcompany.pipedrive.com
```

#### Step 2: Go to Settings
1. Click your profile icon (top right)
2. Select "Personal preferences"
3. Click "API" tab

#### Step 3: Generate API Token
1. Click "Generate new token"
2. Give it a name: "DV Platform Integration"
3. Copy the token (looks like: `abc123def456...`)
4. **Save it securely** - You can't see it again!

### Add to Environment:

Add these to your `.env` file:

```bash
# Pipedrive CRM
PIPEDRIVE_API_TOKEN=your-api-token-here
PIPEDRIVE_API_URL=https://api.pipedrive.com/v1
PIPEDRIVE_COMPANY_DOMAIN=disruptiveventures.pipedrive.com
```

### Test Connection:

```bash
curl "https://api.pipedrive.com/v1/deals?api_token=YOUR_TOKEN&limit=5"
```

Should return your recent deals.

---

## 2. Fortnox Accounting Setup 💰

### What You'll Get Access To:
- Invoices (sales invoices)
- Customers (client database)
- Supplier Invoices (expenses)
- Accounts (chart of accounts)
- Vouchers (transactions)
- Articles (products/services)

### Getting Your API Credentials:

#### Step 1: Register as Fortnox Developer
1. Go to: https://developer.fortnox.se
2. Create developer account
3. Click "My Applications"

#### Step 2: Create Application
1. Click "Create Application"
2. Fill in:
   - **Name**: "DV Portfolio Platform"
   - **Description**: "Portfolio company financial tracking"
   - **Redirect URI**: `http://localhost:8000/integrations/fortnox/callback`
3. Submit for approval

#### Step 3: Get Credentials
Once approved, you'll get:
- **Client ID**: Your application ID
- **Client Secret**: Keep this secure!

#### Step 4: OAuth Flow (One-time Setup)
1. User authorization URL:
```
https://apps.fortnox.se/oauth-v1/auth
  ?client_id=YOUR_CLIENT_ID
  &redirect_uri=YOUR_REDIRECT_URI
  &scope=invoice customer account voucher
  &state=random_string
  &response_type=code
```

2. User approves access
3. Exchange authorization code for access token
4. Store access token securely (encrypted in database)

### Add to Environment:

```bash
# Fortnox Accounting
FORTNOX_CLIENT_ID=your-client-id
FORTNOX_CLIENT_SECRET=your-client-secret
FORTNOX_API_URL=https://api.fortnox.se/3
FORTNOX_REDIRECT_URI=http://localhost:8000/integrations/fortnox/callback
```

### Required Scopes:
- `invoice` - Read/write invoices
- `customer` - Read/write customers
- `account` - Read chart of accounts
- `voucher` - Read financial transactions
- `supplierinvoice` - Read supplier invoices
- `article` - Read products/services

### Test Connection:

```bash
curl -X GET "https://api.fortnox.se/3/invoices" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Client-Secret: YOUR_CLIENT_SECRET"
```

---

## Updated Configuration Files

### 1. `backend/app/config.py`

Added settings:
```python
# Pipedrive CRM
pipedrive_api_token: str = ""
pipedrive_api_url: str = "https://api.pipedrive.com/v1"
pipedrive_company_domain: str = ""

# Fortnox Accounting
fortnox_api_token: str = ""
fortnox_client_secret: str = ""
fortnox_api_url: str = "https://api.fortnox.se/3"
```

### 2. `backend/env.example`

Added placeholders for both services.

---

## Quick Start Guide

### For Pipedrive (Easier - Just API Token):

1. **Get Token** (5 minutes)
   - Log into Pipedrive
   - Settings → Personal → API
   - Generate token

2. **Add to .env**
   ```bash
   PIPEDRIVE_API_TOKEN=abc123...
   PIPEDRIVE_COMPANY_DOMAIN=disruptiveventures.pipedrive.com
   ```

3. **Test**
   ```python
   from app.config import settings
   import httpx
   
   response = httpx.get(
       f"{settings.pipedrive_api_url}/deals",
       params={"api_token": settings.pipedrive_api_token}
   )
   print(response.json())
   ```

### For Fortnox (OAuth - More Complex):

1. **Register App** (1-2 days for approval)
   - Create developer account
   - Submit application
   - Wait for approval

2. **Implement OAuth**
   - Create authorization endpoint
   - Handle callback
   - Exchange code for token
   - Store token encrypted

3. **Use Token**
   ```python
   headers = {
       "Authorization": f"Bearer {access_token}",
       "Client-Secret": settings.fortnox_client_secret,
       "Content-Type": "application/json"
   }
   ```

---

## API Rate Limits

### Pipedrive:
- **100 requests per 2 seconds** per API token
- Burst-friendly for quick operations

### Fortnox:
- **4 requests per second** per access token
- Implement exponential backoff for 429 errors
- Cache data to reduce API calls

---

## Security Best Practices

### DO:
✅ Store API tokens encrypted in database  
✅ Use environment variables for secrets  
✅ Rotate tokens regularly  
✅ Use separate tokens for dev/staging/prod  
✅ Log API requests (without tokens)  
✅ Implement token refresh logic  

### DON'T:
❌ Commit tokens to git  
❌ Share tokens in Slack/email  
❌ Use production tokens in development  
❌ Log API tokens  
❌ Hardcode credentials  

---

## Integration Modules to Create

### `backend/app/integrations/pipedrive_client.py`
```python
import httpx
from app.config import settings

class PipedriveClient:
    def __init__(self):
        self.base_url = settings.pipedrive_api_url
        self.api_token = settings.pipedrive_api_token
    
    async def get_deals(self, status=None, stage_id=None):
        params = {"api_token": self.api_token}
        if status:
            params['status'] = status
        if stage_id:
            params['stage_id'] = stage_id
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/deals",
                params=params
            )
            return response.json()
```

### `backend/app/integrations/fortnox_client.py`
```python
import httpx
from app.config import settings

class FortnoxClient:
    def __init__(self, access_token: str):
        self.base_url = settings.fortnox_api_url
        self.access_token = access_token
        self.client_secret = settings.fortnox_client_secret
    
    async def get_invoices(self, from_date=None):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Client-Secret": self.client_secret,
            "Content-Type": "application/json"
        }
        
        params = {}
        if from_date:
            params['fromdate'] = from_date
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/invoices",
                headers=headers,
                params=params
            )
            return response.json()
```

---

## Testing Without Real Credentials

### Mock Data (for Development):

```python
# In fetch_pipedrive_deals() function
async def fetch_pipedrive_deals():
    if not settings.pipedrive_api_token:
        # Return mock data for testing
        return [
            {
                'id': 1,
                'title': 'Series A - Crystal Alarm',
                'stage': 'due_diligence',
                'value': 5000000,
                'currency': 'SEK',
                'organization_name': 'Crystal Alarm',
            }
        ]
    
    # Real API call here...
```

---

## Documentation Links

### Pipedrive:
- **API Docs**: https://developers.pipedrive.com/docs/api/v1
- **Getting Started**: https://pipedrive.readme.io/docs/getting-started
- **Deals**: https://developers.pipedrive.com/docs/api/v1/Deals
- **Rate Limits**: https://pipedrive.readme.io/docs/core-api-concepts-rate-limiting

### Fortnox:
- **API Docs**: https://api.fortnox.se/apidocs
- **Developer Portal**: https://developer.fortnox.se
- **OAuth Guide**: https://developer.fortnox.se/general/authentication
- **Scopes**: https://www.fortnox.se/en/developer/guides-and-good-to-know/scopes

---

## Environment Variables Added

### To `config.py`:
```python
pipedrive_api_token: str = ""
pipedrive_api_url: str = "https://api.pipedrive.com/v1"
pipedrive_company_domain: str = ""

fortnox_api_token: str = ""
fortnox_client_secret: str = ""
fortnox_api_url: str = "https://api.fortnox.se/3"
```

### To `env.example`:
```bash
PIPEDRIVE_API_TOKEN=your-pipedrive-api-token
PIPEDRIVE_API_URL=https://api.pipedrive.com/v1
PIPEDRIVE_COMPANY_DOMAIN=yourcompany.pipedrive.com

FORTNOX_API_TOKEN=your-fortnox-access-token
FORTNOX_CLIENT_SECRET=your-fortnox-client-secret
FORTNOX_API_URL=https://api.fortnox.se/3
```

---

## Next Steps

### Immediate (for Testing):
1. Get Pipedrive API token (easiest - just copy from settings)
2. Add to your `.env` file
3. Test dealflow integration

### Later (for Production):
1. Register Fortnox developer app
2. Wait for approval (1-2 days)
3. Implement OAuth flow
4. Test financial integration

---

## Summary

✅ **Pipedrive configuration added** - Ready for API token  
✅ **Fortnox configuration added** - Ready for OAuth setup  
✅ **Environment examples updated** - Copy to your `.env`  
✅ **Config.py updated** - New settings available  
✅ **Integration clients ready** - Just add implementation  

**To use:** Add your Pipedrive API token to `.env` and restart the server!

---

**Documentation References:**
- FORTNOX_API_DATA.md - Complete Fortnox endpoint guide
- This file (PIPEDRIVE_FORTNOX_SETUP.md) - Setup instructions

