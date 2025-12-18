# How to Connect Fortnox - Step-by-Step Guide 💰

**For:** Financial data, invoices, and accounting  
**Difficulty:** ⭐⭐⭐ Complex (2-3 days including approval)  
**Required Access:** Fortnox account + Developer account

---

## What You'll Get

Once connected, you'll see:
- ✅ Real-time revenue (MRR, ARR)
- ✅ Invoice tracking (paid, unpaid, overdue)
- ✅ Expense data (burn rate, runway)
- ✅ Customer list (who's buying)
- ✅ Financial statements (P&L)
- ✅ Cash flow tracking

**Example:** Crystal Alarm's 5.8M tkr Q3 revenue automatically tracked!

---

## Important Note

Fortnox integration is **more complex** than Pipedrive because:
1. Requires developer account registration
2. App must be approved by Fortnox (1-2 business days)
3. Uses OAuth 2.0 (not just an API token)
4. Requires user authorization flow

**Allow 2-3 days** for complete setup.

---

## Step 1: Register as Fortnox Developer

### 1A: Go to Fortnox Developer Portal
Open: https://developer.fortnox.se

### 1B: Create Developer Account
1. Click **"Bli utvecklare"** (Become developer) or **"Logga in"** (Log in)
2. Use your Fortnox account to log in
3. If you don't have a developer account, sign up
4. Fill in your information:
   - Name
   - Email
   - Company
   - Purpose: "Portfolio company financial tracking"

---

## Step 2: Create Application

### 2A: Go to "My Applications"
1. Once logged in, go to **"Mina applikationer"** (My Applications)
2. Click **"Skapa ny applikation"** (Create new application)

### 2B: Fill in Application Details

**App Name:**
```
DV Portfolio Platform
```

**Description:**
```
Portfolio company financial tracking and reporting system for Disruptive Ventures
```

**Redirect URI:**
```
http://localhost:8000/integrations/fortnox/callback
```

**For production, also add:**
```
https://yourdomain.com/integrations/fortnox/callback
```

**Scopes (välj omfattningar):**
Select these permissions:

Required:
- ✅ `invoice` - Read and write invoices
- ✅ `customer` - Read and write customers  
- ✅ `account` - Read chart of accounts
- ✅ `voucher` - Read financial transactions

Recommended:
- ✅ `supplierinvoice` - Read supplier invoices
- ✅ `article` - Read products/services
- ✅ `settings` - Read company information

### 2C: Submit for Approval
1. Review your information
2. Click **"Skicka in"** (Submit)
3. **Wait for Fortnox to approve** (usually 1-2 business days)
4. You'll get an email when approved

### 2D: Save Your Credentials
Once approved, you'll see:
- **Client ID**: Your application identifier
- **Client Secret**: Keep this secure!

**Write these down or save securely**

---

## Step 3: Get Authorization from User

### 3A: Authorization URL
Once your app is approved, you need the Fortnox account user to authorize it.

The authorization URL looks like:
```
https://apps.fortnox.se/oauth-v1/auth
  ?client_id=YOUR_CLIENT_ID
  &redirect_uri=http://localhost:8000/integrations/fortnox/callback
  &scope=invoice customer account voucher supplierinvoice
  &state=random_string_12345
  &response_type=code
  &account_type=service
```

**Replace:**
- `YOUR_CLIENT_ID` with your actual Client ID
- `random_string_12345` with any random string (for security)

### 3B: User Authorizes
1. Send this URL to the Fortnox account holder
2. They log into Fortnox
3. They see permission request
4. They click **"Godkänn"** (Approve)
5. Browser redirects to your callback URL
6. You get an **authorization code** in the URL

### 3C: Exchange Code for Access Token
The redirect will look like:
```
http://localhost:8000/integrations/fortnox/callback?code=AUTHORIZATION_CODE&state=...
```

**Save the `code` parameter!**

---

## Step 4: Get Access Token

### 4A: Exchange Authorization Code
Make a POST request to:
```
https://apps.fortnox.se/oauth-v1/token
```

**Body (form-encoded):**
```
grant_type=authorization_code
code=AUTHORIZATION_CODE_FROM_STEP_3
redirect_uri=http://localhost:8000/integrations/fortnox/callback
```

**Headers:**
```
Authorization: Basic base64(client_id:client_secret)
Content-Type: application/x-www-form-urlencoded
```

**Response:**
```json
{
  "access_token": "abc123...",
  "refresh_token": "xyz789...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

**Save both tokens!**

---

## Step 5: Add to DV Platform

### 5A: Go to Settings Page
```
http://localhost:8000/settings
```

### 5B: Portfolio Companies Tab
Click the third tab

### 5C: Find Your Company
- Scroll to the company
- Example: "Crystal Alarm" or "Coeo"

### 5D: Click "Connect" on Fortnox
- Find the **"Fortnox"** integration box
- Click **"Connect"**

### 5E: Fill in the Form

**Access Token:**
```
Paste the access_token from Step 4
(looks like: abc123def456...)
```

**Client Secret:**
```
Paste your Client Secret from Step 2D
(looks like: xyz789ghi012...)
```

### 5F: Click "Save Integration"
- The token gets encrypted
- Stored securely in database
- Status changes to **"✅ Connected"**

---

## Step 6: Verify It's Working

### 6A: Go to Building Companies
```
http://localhost:8000/wheels/building
```

### 6B: Select Company
Choose the company you connected

### 6C: Click "Financial" Tab
You should now see:
- Real MRR and ARR from invoices
- Cash balance
- Burn rate calculations
- Accurate financial metrics

---

## What Data Gets Pulled & Mapped

### Invoices → Revenue Metrics:
```
GET /invoices?status=fully_paid&fromdate=2025-01-01

Maps to:
- Monthly Recurring Revenue (MRR)
- Annual Recurring Revenue (ARR)
- Revenue growth %
- Top customers
```

### Accounts → Financial Statements:
```
GET /accounts

Maps to:
- Revenue accounts (3000-3999)
- Expense accounts (6000-7999)
- Assets (1000-1999)
- Liabilities (2000-2999)

Calculates:
- Gross margin
- Operating margin
- EBITDA
```

### Supplier Invoices → Expenses:
```
GET /supplierinvoices

Maps to:
- Monthly burn rate
- Operating expenses
- Vendor spending
- Cash runway (months)
```

### Customers → Client Database:
```
GET /customers

Maps to:
- Top customers by revenue
- Customer concentration risk
- Payment terms
- Geographic distribution
```

### Vouchers → Transactions:
```
GET /vouchers

Maps to:
- Detailed expense breakdown
- Cost categories
- Transaction history
- Audit trail
```

---

## OAuth Token Refresh

### Access tokens expire after 1 hour!

**The platform will automatically:**
1. Detect expired token (401 error)
2. Use refresh_token to get new access_token
3. Update database with new token
4. Retry the API call
5. Continue working seamlessly

**Refresh tokens last 30 days**  
**After 30 days:** User needs to re-authorize

---

## Fortnox API Rate Limits

**4 requests per second** per access token

**Our strategy:**
- Cache financial data for 1 hour
- Batch requests where possible
- Implement exponential backoff for 429 errors
- Show cached data while fetching fresh

---

## Data Refresh Schedule

### Initial Load:
- Pulls last 12 months of data
- Processes all invoices and expenses
- Calculates baseline metrics

### Ongoing Updates:
- **Every page load**: Checks for cache expiry
- **Every hour**: Refreshes if cache expired
- **Manual**: "Sync Now" button triggers immediate fetch
- **Scheduled**: Nightly sync at 2am for all companies

---

## Common Issues

### ❌ Application Not Approved Yet
**Status:** Pending Fortnox review  
**Time:** 1-2 business days  
**Solution:** Wait for approval email, then continue setup

### ❌ "Invalid grant" Error
**Cause:** Authorization code already used or expired  
**Solution:** User needs to re-authorize (Step 3)

### ❌ "Invalid client" Error
**Cause:** Client ID or Secret incorrect  
**Solution:** Double-check credentials from developer portal

### ❌ "Insufficient permissions"
**Cause:** Missing required scopes  
**Solution:** Add scopes in developer portal, user re-authorizes

### ❌ Token Expired
**Cause:** Access token older than 1 hour  
**Solution:** Platform auto-refreshes (or re-authorize if refresh fails)

---

## Security Best Practices

### ✅ DO:
- Store access tokens encrypted
- Use refresh tokens to maintain access
- Implement token rotation
- Log API requests (without tokens!)
- Use HTTPS in production
- Rotate client secrets annually

### ❌ DON'T:
- Hardcode credentials
- Share client secrets
- Log access tokens
- Use same credentials for dev and prod
- Store tokens in plain text

---

## Testing Without Real Account

### Mock Data Mode:
If Fortnox not connected, the platform shows:
- Estimated MRR based on valuation
- Placeholder financial metrics
- "Connect Fortnox for real data" message

### Real Data Mode:
Once connected:
- Live invoice data
- Actual MRR/ARR calculations
- Real-time financial health

---

## For Each Portfolio Company

Repeat this process for:
- ✅ Crystal Alarm (5.8M tkr Q3 revenue)
- ✅ Alent Dynamic (2.9M tkr)
- ✅ Basic Safety (753 tkr)
- ✅ Coeo (614 tkr)
- ✅ Others as they sign up for Fortnox

Each company will need to:
1. Give you their Fortnox login (or access to developer portal)
2. Create OAuth app in their account
3. Authorize the integration
4. Provide access token

---

## Summary Checklist

**Part 1: Setup (One-time)**
- [ ] Register as Fortnox developer
- [ ] Create application
- [ ] Request scopes (invoice, customer, account, etc.)
- [ ] Submit for approval
- [ ] Wait 1-2 days
- [ ] Get Client ID and Client Secret

**Part 2: Per Company**
- [ ] Get user to authorize app
- [ ] Receive authorization code
- [ ] Exchange code for access token
- [ ] Go to Settings page
- [ ] Portfolio Companies tab
- [ ] Find company
- [ ] Connect Fortnox
- [ ] Paste tokens
- [ ] Save
- [ ] Verify "✅ Connected"

**Part 3: Verify**
- [ ] Go to Building page
- [ ] Select company
- [ ] Financial tab
- [ ] See real financial data!

---

## Timeline

- **Day 1**: Register developer account, submit app (30 min)
- **Day 2-3**: Wait for Fortnox approval
- **Day 4**: Get authorization, add to platform (15 min per company)
- **Done!** Real-time financial data flowing

---

## Support Resources

**Fortnox Developer:**
- Portal: https://developer.fortnox.se
- API Docs: https://api.fortnox.se/apidocs
- Support: Via developer portal

**DV Platform:**
- Guide: `FORTNOX_API_DATA.md`
- Setup: `PIPEDRIVE_FORTNOX_SETUP.md`

---

**Time Required:** 2-3 days (including approval wait)  
**Technical Knowledge:** Moderate (OAuth concepts helpful)  
**Result:** Real-time financial metrics for portfolio companies! 💰

---

**Pro Tip:** Start the application approval process NOW, then continue setup once approved!

