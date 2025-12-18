# 🏗️ Dealflow & Financial Boards - Architecture Plan

## Your Question: Store in Database or Not?

### ✅ My Recommendation: NO DATABASE STORAGE

For **view-only** Pipedrive and Fortnox data, fetch directly from APIs without database storage.

---

## Why Not Store in Database?

### Advantages of Direct API

✅ **Always Fresh Data**
- See real-time updates
- No stale data issues
- Matches Pipedrive/Fortnox exactly

✅ **Simpler Architecture**
- No sync jobs to maintain
- No database schema for deals/invoices
- Less code to maintain

✅ **Easier Integration**
- Just connect to API
- Transform and display
- No CRUD operations

✅ **No Sync Issues**
- No conflicts between systems
- No "last synced" tracking
- Single source of truth (Pipedrive/Fortnox)

### When Database Storage Makes Sense

❌ If you need to **edit** deals (but Pipedrive is the editor)
❌ If Pipedrive API is **slow** (can cache if needed)
❌ If you need **offline access** (probably not critical)
❌ If you want **custom fields** Pipedrive doesn't have

---

## Proposed Architecture

### Activities Board (Linear)
```
Linear API ⟷ Database ⟷ Your Kanban
   ↑                         ↑
   └─────── Two-way sync ────┘
```
- **Storage:** Database (`tasks` table)
- **Why:** Need to edit tasks
- **Sync:** Two-way with Linear

### Dealflow Board (Pipedrive)
```
Pipedrive API → Transform → Your Kanban (view-only)
   ↑                            ↓
   └───── Edit in Pipedrive ────┘
```
- **Storage:** None (direct from API)
- **Why:** View-only, Pipedrive is source of truth
- **Sync:** One-way (fetch only)

### Financial Board (Fortnox)
```
Fortnox API → Transform → Your Kanban (view-only)
   ↑                          ↓
   └───── Edit in Fortnox ────┘
```
- **Storage:** None (direct from API)
- **Why:** View-only, Fortnox is accounting system
- **Sync:** One-way (fetch only)

---

## Implementation Plan

### Phase 1: Pipedrive Integration (Dealflow)

**1. Add API Credentials**
```python
# In .env
PIPEDRIVE_API_TOKEN=your-token-here
PIPEDRIVE_COMPANY_DOMAIN=yourcompany  # yourcompany.pipedrive.com
```

**2. Fetch Deals**
```python
async def fetch_pipedrive_deals():
    response = await httpx.get(
        f'https://{settings.pipedrive_company_domain}.pipedrive.com/api/v1/deals',
        params={
            'api_token': settings.pipedrive_api_token,
            'status': 'open'
        }
    )
    deals = response.json()['data']
    
    # Transform to our format
    return [{
        'id': deal['id'],
        'title': deal['title'],
        'value': deal['value'],
        'stage': map_pipedrive_stage(deal['stage_id']),
        'person_name': deal['person_name'],
        'org_name': deal['org_name'],
        'expected_close_date': deal['expected_close_date']
    } for deal in deals]
```

**3. Display as Cards**
```python
def generate_deal_cards(deals):
    # Similar to task cards but with deal-specific fields
    # Show: company name, deal value, person, expected close date
```

---

### Phase 2: Fortnox Integration (Financial)

**1. Add API Credentials**
```python
# In .env
FORTNOX_ACCESS_TOKEN=your-token
FORTNOX_CLIENT_SECRET=your-secret
```

**2. Fetch Invoices**
```python
async def fetch_fortnox_invoices():
    response = await httpx.get(
        'https://api.fortnox.se/3/invoices',
        headers={
            'Authorization': f'Bearer {settings.fortnox_access_token}',
            'Client-Secret': settings.fortnox_client_secret
        }
    )
    invoices = response.json()['Invoices']
    
    # Transform to our format
    return [{
        'id': invoice['DocumentNumber'],
        'customer': invoice['CustomerName'],
        'amount': invoice['Total'],
        'due_date': invoice['DueDate'],
        'status': map_fortnox_status(invoice)
    } for invoice in invoices]
```

**3. Display as Cards**
```python
def generate_invoice_cards(invoices):
    # Show: invoice number, customer, amount, due date, status
```

---

## Current Status

### ✅ What's Done

1. **Three-tab system** - Activities | Dealflow | Financial
2. **Activities board** - Fully functional with Linear
3. **Dealflow structure** - 6 columns ready
4. **Financial structure** - 5 columns ready
5. **Fetch functions** - Stubbed and ready

### 🔄 What's Next

1. **Add Pipedrive API credentials** to `.env`
2. **Implement `fetch_pipedrive_deals()`**
3. **Create `generate_deal_cards()`**
4. **Add Fortnox API credentials**
5. **Implement `fetch_fortnox_invoices()`**
6. **Create `generate_invoice_cards()`**

---

## Benefits of This Approach

### For Dealflow
- ✅ See latest pipeline in real-time
- ✅ No data duplication
- ✅ Pipedrive remains source of truth
- ✅ Simple "view" dashboard
- ✅ Click deal → Opens in Pipedrive

### For Financial
- ✅ See invoice status at a glance
- ✅ Track overdue payments
- ✅ Fortnox handles accounting rules
- ✅ No financial data duplication
- ✅ Click invoice → Opens in Fortnox

---

## Future: If You Need Editing

If you later want to **edit deals** from your Kanban:

**Option A: Minimal Database**
- Store only `pipedrive_deal_id` mappings
- Store any custom fields Pipedrive doesn't have
- Sync edits back to Pipedrive immediately

**Option B: Full Database**
- Store entire deal data
- Sync both ways like Linear
- More complex but fully independent

**For now: Direct API is simplest!** ✅

---

## Code Structure

```python
# activities_columns - From Linear API + Database
# dealflow_columns - From Pipedrive API only
# financial_columns - From Fortnox API only

html = f"""
    <div id="activities-tab">
        {generate_task_cards(activities_columns['backlog'])}
    </div>
    
    <div id="dealflow-tab">
        {generate_deal_cards(dealflow_columns['lead'])}
    </div>
    
    <div id="financial-tab">
        {generate_invoice_cards(financial_columns['draft'])}
    </div>
"""
```

---

## Next Step

Ready to add Pipedrive integration? I'll need:
1. Your Pipedrive API token
2. Your Pipedrive company domain
3. Then I'll connect it and populate the Dealflow board!

Same for Fortnox when you're ready. 🚀

---

## Summary

**Decision:** ✅ **No database storage for view-only Pipedrive/Fortnox data**

**Why:** Simpler, fresher, less maintenance

**When to reconsider:** If you need editing or offline access

**Current code:** Already structured to support direct API approach!

