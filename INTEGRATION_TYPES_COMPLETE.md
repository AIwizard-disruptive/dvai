# All Integration Types - Complete ✅

**Date:** December 17, 2025  
**Status:** 6 Integration Types Available

---

## Overview

The settings page now supports 6 different integration types for both Disruptive Ventures and all portfolio companies:

1. **Pipedrive CRM** - Deal pipeline and customer tracking
2. **Fortnox** - Financial data and accounting
3. **Google Sheets** - KPI reporting and data import
4. **Google Workspace** - Gmail, Drive, Calendar (NEW!)
5. **Office 365** - Outlook, OneDrive, Teams (NEW!)
6. **Custom Integration** - Any API endpoint (NEW!)

Each company can have all 6 integrations configured with their own credentials.

---

## Integration Types Details

### 1. Pipedrive CRM 📊
**For:** Sales pipeline and deal tracking  
**Fields:**
- API Token
- Company Domain (e.g., coeo.pipedrive.com)

**Use Cases:**
- Track deals and opportunities
- Customer relationship management
- Sales forecasting
- **Example:** Coeo with 200 deals ✅

---

### 2. Fortnox 💰
**For:** Financial data and accounting  
**Fields:**
- Access Token (OAuth)
- Client Secret

**Use Cases:**
- Invoice tracking (MRR, ARR)
- Expense management
- P&L statements
- Cash flow monitoring

---

### 3. Google Sheets 📈
**For:** KPI reports and data import  
**Fields:**
- Spreadsheet URL
- Service Account JSON

**Use Cases:**
- Auto-import Q3 2025 KPI data
- Financial reporting
- Custom dashboards
- **Example:** Your Q3 report ready to connect

---

### 4. Google Workspace ☁️ NEW!
**For:** Full Google Suite integration  
**Fields:**
- Client ID (OAuth)
- Client Secret
- Service Account Email (optional)

**APIs Available:**
- **Gmail API** - Email management
- **Google Drive API** - Document storage
- **Google Calendar API** - Meeting scheduling
- **Google Contacts API** - Contact sync
- **Google Tasks API** - Task management

**Use Cases:**
- Send automated emails to founders
- Store company documents in Drive
- Schedule board meetings
- Sync contacts
- Track action items

---

### 5. Office 365 🏢 NEW!
**For:** Microsoft ecosystem integration  
**Fields:**
- Tenant ID (Azure AD)
- Client ID (Application ID)
- Client Secret

**APIs Available:**
- **Outlook Mail API** - Email management
- **OneDrive API** - File storage
- **Microsoft Teams API** - Collaboration
- **Calendar API** - Meeting scheduling
- **People API** - Contact management

**Use Cases:**
- Email communication with portfolio companies
- Document sharing via OneDrive
- Teams channels per company
- Meeting coordination
- Contact synchronization

---

### 6. Custom Integration 🔧 NEW!
**For:** Any custom or proprietary API  
**Fields:**
- Integration Name (custom label)
- API Endpoint URL
- API Token/Key
- Additional Headers (JSON)

**Use Cases:**
- Internal CRM systems
- Custom ERP platforms
- Proprietary accounting software
- Legacy systems
- Third-party tools not listed above

**Examples:**
- HubSpot CRM
- Salesforce
- QuickBooks
- Xero
- Stripe
- Intercom
- Slack webhooks
- Custom data warehouse

---

## Per-Company Configuration

### Each Portfolio Company Can Have:
- ✅ Their own Pipedrive (sales pipeline)
- ✅ Their own Fortnox (financials)
- ✅ Their own Google Sheets (KPI reports)
- ✅ Their own Google Workspace (email, docs)
- ✅ Their own Office 365 (if they use Microsoft)
- ✅ Custom integrations (company-specific tools)

### Disruptive Ventures Can Have:
- ✅ DV Pipedrive (investor pipeline)
- ✅ DV Fortnox (fund accounting)
- ✅ DV Google Sheets (portfolio KPIs)
- ✅ DV Google Workspace (DV team email/drive)
- ✅ DV Office 365 (if DV uses Microsoft)
- ✅ Custom integrations (internal tools)

---

## Setup Guides

### Google Workspace Setup:

#### Step 1: Enable APIs
1. Go to: https://console.cloud.google.com
2. Create or select project
3. Enable APIs:
   - Gmail API
   - Google Drive API
   - Google Calendar API
   - Google Contacts API

#### Step 2: Create OAuth Credentials
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Application type: "Web application"
4. Authorized redirect URIs: `http://localhost:8000/integrations/google/callback`
5. Copy Client ID and Client Secret

#### Step 3: Service Account (for server-to-server)
1. Create Credentials → Service Account
2. Download JSON key file
3. Share necessary resources with service account email
4. Enable domain-wide delegation if needed

### Office 365 Setup:

#### Step 1: Register App in Azure
1. Go to: https://portal.azure.com
2. Navigate to "Azure Active Directory"
3. Click "App registrations" → "New registration"
4. Name: "DV Portfolio Platform"
5. Redirect URI: `http://localhost:8000/integrations/microsoft/callback`

#### Step 2: Configure API Permissions
Request permissions for:
- Mail.Read, Mail.Send
- Calendars.Read, Calendars.ReadWrite
- Files.Read.All
- User.Read
- Contacts.Read

#### Step 3: Create Client Secret
1. Go to "Certificates & secrets"
2. Click "New client secret"
3. Copy the value (only shown once!)
4. Note your Tenant ID and Application ID

### Custom Integration Setup:

#### Configuration:
1. Get API documentation from service
2. Obtain API key/token
3. Note base URL (e.g., https://api.service.com/v1)
4. Document any custom headers needed
5. Test endpoint before saving

---

## Database Schema Update

### Migration 020 Updated:
```sql
CREATE TABLE portfolio_company_integrations (
    ...
    integration_type TEXT NOT NULL,
    integration_name TEXT, -- NEW: For custom integrations
    ...
);
```

Supports all 6 integration types:
- 'pipedrive'
- 'fortnox'
- 'google_sheets'
- 'google_workspace' ← NEW
- 'office365' ← NEW
- 'custom' ← NEW

---

## Integration Grid Layout

### Desktop View (3 per row):
```
┌─────────────┬─────────────┬─────────────┐
│ Pipedrive   │ Fortnox     │ Google      │
│             │             │ Sheets      │
├─────────────┼─────────────┼─────────────┤
│ Google      │ Office 365  │ Custom      │
│ Workspace   │             │             │
└─────────────┴─────────────┴─────────────┘
```

### Mobile View (1 per row):
Stacks vertically for easy access

---

## Use Case Examples

### Scenario 1: Coeo (Event Company)
**Integrations:**
- ✅ **Pipedrive**: 200 deals, 2.77M SEK pipeline
- ⏳ **Google Workspace**: Gmail for customer communication
- ⏳ **Google Sheets**: Event KPI dashboard
- ⏳ **Custom**: Their proprietary event booking system

### Scenario 2: Crystal Alarm (Security Tech)
**Integrations:**
- ⏳ **Fortnox**: 5.8M tkr Q3 revenue tracking
- ⏳ **Pipedrive**: B2B sales pipeline
- ⏳ **Office 365**: Using Microsoft Teams internally
- ⏳ **Custom**: Security system API integration

### Scenario 3: Disruptive Ventures (Fund)
**Integrations:**
- ⏳ **Pipedrive**: Track investment opportunities
- ⏳ **Fortnox**: Fund expenses and LP distributions
- ⏳ **Google Sheets**: Q3 KPI report auto-import
- ⏳ **Google Workspace**: DV team email and Drive
- ⏳ **Custom**: Internal dealflow tracking tools

---

## Modal Forms

### Each Integration Type Has Custom Fields:

#### Pipedrive:
- API Token (password)
- Company Domain (text)

#### Fortnox:
- Access Token (password)
- Client Secret (password)

#### Google Sheets:
- Spreadsheet URL (text)
- Service Account JSON (textarea)

#### Google Workspace: ✨ NEW
- Client ID (text)
- Client Secret (password)
- Service Account Email (text, optional)

#### Office 365: ✨ NEW
- Tenant ID (text)
- Client ID (text)
- Client Secret (password)

#### Custom: ✨ NEW
- Integration Name (text)
- API Endpoint URL (text)
- API Token (password)
- Additional Headers (JSON textarea)

---

## Security

### All Credentials Encrypted:
- ✅ Fernet encryption
- ✅ Stored encrypted at rest
- ✅ Decrypted only when making API calls
- ✅ Never logged or exposed

### Per-Company Isolation:
- Each company has own credentials
- No cross-contamination
- Audit trail of who configured what

---

## Current Status

### Integrations Available:
- 6 types × 9 companies (DV + 8 portfolio) = **54 possible integrations**

### Currently Connected:
- **Coeo Pipedrive**: ✅ 200 deals live
- **Linear**: ✅ 45 tasks synced
- **OpenAI**: ✅ Configured

### Ready to Connect:
- 53 more integration slots available!

---

## Next Steps

### Phase 1: Core Integrations
1. **DV Google Sheets** - Connect Q3 KPI spreadsheet
2. **DV Google Workspace** - Team email and drive
3. **Add more Pipedrive accounts** - Other portfolio companies

### Phase 2: Financial Integrations
1. **Fortnox for top companies** - Crystal Alarm, Alent Dynamic
2. **Real-time financial dashboards**
3. **Automated MRR/ARR calculations**

### Phase 3: Communication Integrations
1. **Google Workspace per company** - Automated founder emails
2. **Office 365 if needed** - For Microsoft-based companies
3. **Slack webhooks** - Notifications

### Phase 4: Custom Integrations
1. **Company-specific tools** - Integrate proprietary systems
2. **Data warehouses** - Push data to analytics platforms
3. **Zapier/Make webhooks** - No-code automation

---

## Files Modified

1. **`app/api/settings.py`**
   - Added 3 new integration types
   - Added modal forms for each
   - Updated JavaScript handlers
   - 6 integration options per company

2. **`migrations/020_portfolio_company_integrations.sql`**
   - Added `integration_name` column
   - Supports all 6 types

3. **`app/config.py`**
   - Already has Pipedrive/Fortnox
   - Ready for Workspace/Office365

---

## Total Integration Capacity

| Entity | Integrations | Total Slots |
|--------|--------------|-------------|
| Disruptive Ventures | 6 | 6 |
| Crystal Alarm | 6 | 6 |
| LumberScan | 6 | 6 |
| Alent Dynamic | 6 | 6 |
| LunaLEC | 6 | 6 |
| Vaylo | 6 | 6 |
| Coeo | 6 | 6 |
| Basic Safety | 6 | 6 |
| Service Node | 6 | 6 |
| **TOTAL** | **54** | **54** |

---

## Testing

### Verify All Integration Types:
1. Go to: http://localhost:8000/settings
2. Click "Portfolio Companies (8)" tab
3. Find any company
4. Should see 6 integration options:
   - Pipedrive CRM
   - Fortnox
   - Google Sheets
   - Google Workspace ✨
   - Office 365 ✨
   - Custom Integration ✨

5. Click "Connect" on each to see appropriate fields

---

## Success Metrics

| Metric | Result |
|--------|--------|
| Integration Types | 6 |
| Companies | 9 (DV + 8) |
| Total Capacity | 54 integrations |
| Currently Connected | 1 (Coeo Pipedrive) |
| Ready for Configuration | 53 |

---

## Conclusion

✅ **Complete integration framework ready!**

Your portfolio platform now supports:
- ✅ 6 different integration types
- ✅ Per-company credential storage
- ✅ Secure encryption
- ✅ Flexible custom integrations
- ✅ Easy configuration UI

**Next:** Start connecting real integrations for DV and your portfolio companies!

---

**Access:** http://localhost:8000/settings → Portfolio Companies tab

Click any "Connect" button to see the new integration options! 🚀

