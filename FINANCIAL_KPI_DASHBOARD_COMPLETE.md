# ✅ Financial KPI Dashboard - COMPLETE!

## What Was Built

Replaced the Financial Kanban with a **proper startup KPI dashboard** showing key financial metrics with mock data from Fortnox.

---

## Dashboard Features

### 📊 Key Metrics (Top Row)

**1. Monthly Recurring Revenue (MRR)**
- Current: 2.4M kr
- Growth: +12.5% vs last month
- Trend: 📈 Positive

**2. Annual Recurring Revenue (ARR)**
- Current: 28.8M kr  
- Growth: +18% YoY
- Trend: 📈 Strong growth

**3. Monthly Burn Rate**
- Current: -850k kr
- Runway: 8.5 months
- Status: ⚠️ Monitor closely

**4. Cash Balance**
- Current: 7.2M kr
- Change: +5.2% this month
- Trend: 📈 Healthy

---

### 💰 Revenue Breakdown

Visual breakdown with progress bars:
- **Subscription Revenue:** 1.8M kr (75%)
- **Professional Services:** 480k kr (20%)
- **One-time Sales:** 120k kr (5%)

---

### 📈 Key Ratios

**Gross Margin:** 72%  
**EBITDA Margin:** -15% (normal for growth stage)  
**LTV/CAC:** 3.2x (healthy unit economics)

---

### 👥 Top 5 Customers (Last 30 Days)

1. **Volvo Group** - 485k kr (3 invoices)
2. **Ericsson AB** - 320k kr (2 invoices)
3. **Atlas Copco** - 285k kr (4 invoices)
4. **IKEA Components** - 240k kr (2 invoices)
5. **Scania AB** - 195k kr (1 invoice)

---

### 🧾 Recent Large Invoices

Shows 5 most recent large invoices with:
- Invoice number
- Customer name
- Due date
- Amount
- Status (Paid/Sent/Overdue/Draft)

---

## What Will Come from Fortnox API

When connected, the dashboard will fetch:

### From `/api/v1/invoices` endpoint:
- ✅ Total invoice amounts
- ✅ Payment status
- ✅ Due dates
- ✅ Customer names
- ✅ Overdue tracking

### From `/api/v1/accounts` endpoint:
- ✅ Revenue by category
- ✅ Expenses breakdown
- ✅ Cash position

### Calculated Metrics:
- ✅ MRR/ARR from subscription invoices
- ✅ Burn rate from monthly expenses
- ✅ Runway from cash balance
- ✅ Gross margin from revenue vs COGS

---

## Mock Data vs Real Data

### Current (Mock Data)
```python
# Hardcoded in HTML for demonstration
MRR: 2.4M kr
Top Customer: Volvo Group (485k kr)
```

### Future (From Fortnox API)
```python
# Fetched from Fortnox
fortnox_data = await fetch_fortnox_financial_data()

MRR = calculate_mrr(fortnox_data['invoices'])
Top Customers = aggregate_by_customer(fortnox_data['invoices'])
```

---

## Fortnox API Integration Plan

### Phase 1: Authentication

```python
# Add to .env
FORTNOX_ACCESS_TOKEN=your-access-token
FORTNOX_CLIENT_SECRET=your-client-secret
```

### Phase 2: Fetch Financial Data

```python
async def fetch_fortnox_financial_data():
    headers = {
        'Authorization': f'Bearer {settings.fortnox_access_token}',
        'Client-Secret': settings.fortnox_client_secret
    }
    
    # Get invoices
    invoices = await httpx.get(
        'https://api.fortnox.se/3/invoices',
        headers=headers,
        params={'filter': 'unbooked,unpaid,unpaidoverdue,fullypaid'}
    )
    
    # Get accounts for revenue/expense data
    accounts = await httpx.get(
        'https://api.fortnox.se/3/accounts',
        headers=headers
    )
    
    return {
        'invoices': invoices.json(),
        'accounts': accounts.json()
    }
```

### Phase 3: Calculate KPIs

```python
def calculate_startup_kpis(fortnox_data):
    invoices = fortnox_data['invoices']
    
    # MRR calculation
    subscription_invoices = [i for i in invoices 
                            if 'subscription' in i.get('Comments', '').lower()]
    mrr = sum(i['Total'] for i in subscription_invoices) / len(subscription_invoices)
    
    # ARR = MRR * 12
    arr = mrr * 12
    
    # Burn rate from expenses
    # ... etc
    
    return {
        'mrr': mrr,
        'arr': arr,
        'burn_rate': burn_rate,
        'runway': runway
    }
```

---

## Dashboard Layout

```
┌─────────────────────────────────────────────┐
│  MRR    │  ARR    │  Burn   │  Cash        │
│ 2.4M kr │ 28.8M kr│ -850k kr│  7.2M kr     │
├─────────────────────────────────────────────┤
│ Revenue Breakdown    │  Key Ratios          │
│ ▓▓▓▓▓▓▓▓ 75%       │  Gross:   72%        │
│ ▓▓ 20%              │  EBITDA: -15%        │
│ ▓ 5%                │  LTV/CAC: 3.2x       │
├─────────────────────────────────────────────┤
│ Top Customers        │  Recent Invoices     │
│ Volvo Group  485k kr │  #1247   285k kr Paid│
│ Ericsson AB  320k kr │  #1246   240k kr Sent│
│ ...                  │  ...                 │
└─────────────────────────────────────────────┘
```

---

## Startup KPIs Included

### Growth Metrics
- ✅ MRR (Monthly Recurring Revenue)
- ✅ ARR (Annual Recurring Revenue)
- ✅ Revenue growth rate

### Financial Health
- ✅ Cash balance
- ✅ Burn rate
- ✅ Runway (months)

### Unit Economics
- ✅ Gross margin
- ✅ EBITDA margin
- ✅ LTV/CAC ratio

### Operational
- ✅ Top customers
- ✅ Invoice status
- ✅ Payment tracking

---

## Design Principles

### ✅ Clean & Minimal
- Large, readable numbers
- Clear labels
- Color-coded status

### ✅ Actionable Insights
- Show trends (↑ ↓)
- Highlight problems (overdue)
- Focus on what matters

### ✅ Executive-Friendly
- At-a-glance understanding
- No clutter
- Key metrics only

---

## Benefits vs Kanban

### Why KPI Dashboard is Better for Financial

**Kanban (Old):**
- ❌ Invoice workflow not useful for overview
- ❌ Too granular for executive view
- ❌ Doesn't show financial health

**KPI Dashboard (New):**
- ✅ Shows company financial health
- ✅ Tracks key growth metrics
- ✅ Identifies issues (overdue, burn rate)
- ✅ Better for board meetings

---

## Three Tab System Overview

### Activities Tab
**Type:** Kanban  
**Purpose:** Task management  
**Source:** Linear API  
**Actions:** Edit, drag, sync

### Dealflow Tab
**Type:** Kanban  
**Purpose:** CRM pipeline  
**Source:** Pipedrive API  
**Actions:** View deals (edit in Pipedrive)

### Financial Tab  
**Type:** KPI Dashboard  
**Purpose:** Financial overview  
**Source:** Fortnox API  
**Actions:** View metrics (edit in Fortnox)

---

## Test It Now!

```
http://localhost:8000/wheels/building
```

**Refresh and click:**
1. ✅ **Activities** → Task Kanban
2. ✅ **Dealflow** → Deal Pipeline
3. ✅ **Financial** → KPI Dashboard (with mock data)

---

## Next Steps

### When Ready to Connect Fortnox:

1. **Get API credentials** from Fortnox
2. **Add to `.env`:**
   ```
   FORTNOX_ACCESS_TOKEN=...
   FORTNOX_CLIENT_SECRET=...
   ```
3. **Implement data fetching**
4. **Replace mock data** with real metrics

### Additional Features to Add:

- [ ] Month-over-month comparison charts
- [ ] Revenue forecast
- [ ] Expense breakdown
- [ ] Customer churn tracking
- [ ] Payment collection metrics
- [ ] Export to PDF report

---

## Status

- ✅ KPI dashboard design: **Complete**
- ✅ Mock data visualization: **Complete**
- ✅ Responsive layout: **Complete**
- ✅ Dark mode support: **Complete**
- 🔄 Fortnox API integration: **Ready for credentials**

---

**The Financial KPI dashboard is live with mock data!**  
Refresh and click the Financial tab to see your startup metrics! 📊

**File modified:** `backend/app/api/wheel_building.py`  
**Server status:** ✅ Running and ready!

