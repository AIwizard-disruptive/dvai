# Execute 4-Wheel VC Operating System - NOW

## 🎯 Single File to Run

**File:** `backend/migrations/FINAL_4_WHEELS_COMPLETE.sql`

This ONE file contains everything (1184 lines):
- ✅ All 4 wheels (PEOPLE, DEALFLOW, BUILDING COMPANIES, ADMIN)
- ✅ LinkedIn integration
- ✅ Google Workspace Directory sync
- ✅ Google Contacts CRM
- ✅ Employment contract management
- ✅ Full RLS policies
- ✅ Helper functions for automation
- ✅ ZERO conflicts with existing migrations

## 🚀 How to Execute (2 minutes)

### Step 1: Open Supabase SQL Editor
Go to: https://supabase.com/dashboard/project/gqpupmuzriqarmrsuwev/editor

### Step 2: Run the Migration
1. Click "**New Query**"
2. Open file: `backend/migrations/FINAL_4_WHEELS_COMPLETE.sql`
3. Copy **entire contents** (all 1184 lines)
4. Paste into SQL editor
5. Click "**Run**"

### Step 3: Verify Success
Run this verification query:

```sql
-- Copy from: backend/migrations/VERIFY_4_WHEELS.sql
```

**Expected Results:**
- PEOPLE WHEEL: 8 tables ✅
- DEALFLOW WHEEL: 4 tables ✅
- BUILDING COMPANIES WHEEL: 6 tables ✅
- ADMIN WHEEL: 2 tables ✅
- Materialized views: 2 ✅
- Helper functions: 5 ✅
- Total: 20 tables + 2 views + 5 functions

---

## 📊 What Gets Created

### PEOPLE Wheel (8 tables)
- `contracts` - Employment, NDA, investment contracts with AI generation
- `role_descriptions` - Job roles for recruitment
- `recruitment_candidates` - Candidate pipeline with AI screening
- `recruitment_notes` - Interview feedback extraction
- `person_competencies` - Skills for Google Directory search
- `person_cvs` - CV storage + **LinkedIn auto-generation**
- `google_profile_syncs` - Google Workspace Directory sync tracking
- `google_contacts_syncs` - Google Contacts CRM sync tracking

**Plus:** Enhanced `people` table with work_email, employee_number, contract links

### DEALFLOW Wheel (4 tables)
- `dealflow_leads` - Inbound leads with AI qualification (0-100 score)
- `dealflow_research` - AI-generated market research reports
- `market_analyses` - Reusable market analysis cache
- `dealflow_outreach` - Automated outreach campaigns with tracking

### BUILDING COMPANIES Wheel (6 tables)
- `portfolio_companies` - Portfolio company tracking
- `portfolio_targets` - Next-round qualification targets
- `target_updates` - Target progress history
- `qualification_criteria` - Rules for next-round readiness
- `ceo_dashboard_configs` - CEO dashboard settings
- `portfolio_support_requests` - Support requests to DV team

### ADMIN Wheel (2 tables + 2 views)
- `dv_dashboard_configs` - Partner dashboard preferences
- `dv_alerts` - Alerts across all 4 wheels
- `dv_portfolio_health` - Portfolio metrics view (Green/Yellow/Red)
- `dv_dealflow_metrics` - Dealflow pipeline metrics

### Helper Functions (5 functions)
- `populate_email_domain()` - Auto-extract domain from email
- `update_person_from_linkedin()` - Import LinkedIn profile data
- `sync_person_to_google_directory()` - Generate Google Directory payload
- `link_person_to_contract()` - Link employee to contract
- `generate_cv_from_linkedin()` - Auto-create CV from LinkedIn

---

## 🎨 Key Features

### 1. LinkedIn Integration
```sql
-- Generate CV from LinkedIn profile
SELECT generate_cv_from_linkedin(
    person_id,
    '{"headline": "...", "summary": "...", "skills": [...], ...}'::jsonb
);
```

### 2. Google Workspace Directory
```sql
-- Generate Google Directory sync payload
SELECT sync_person_to_google_directory(person_id);
```

### 3. Auto Email Domain
```sql
-- Automatically extracts domain when work_email is set
INSERT INTO people (name, work_email) 
VALUES ('Marcus', 'marcus@disruptiveventures.se');
-- email_domain automatically becomes 'disruptiveventures.se'
```

### 4. Contract Linking
```sql
-- Link employee to their employment contract
SELECT link_person_to_contract(person_id, contract_id);
-- Auto-updates contract_start_date and contract_end_date
```

---

## 🔒 Security

All tables have:
- ✅ Row Level Security (RLS) enabled
- ✅ Org-based isolation (multi-tenant safe)
- ✅ Service role access (for automation)
- ✅ User-level permissions (view own data)
- ✅ Admin permissions (manage org data)

CEO Dashboard access:
- ✅ Portfolio company CEOs can view their own targets
- ✅ CEOs can update target progress
- ✅ CEOs can request DV support
- ✅ DV team can manage everything

---

## ✅ After Migration

### 1. Update Environment Variables

Add to `backend/.env`:

```env
# Slack
SLACK_BOT_TOKEN=xoxb-your-token

# Whisperflow
WHISPERFLOW_API_KEY=your-key

# Google Service Account
GOOGLE_SERVICE_ACCOUNT_FILE=/path/to/service-account.json
GOOGLE_WORKSPACE_ADMIN_EMAIL=admin@disruptiveventures.se
```

### 2. Set Up Google Workspace (One-time)

**Create contact groups in Google Contacts:**
- DV_Team
- Leads
- High_Priority_Leads
- Portfolio_CEOs
- Portfolio_Green/Yellow/Red

**Create custom schemas in Google Directory:**
- Skills (technical_skills, domain_expertise, languages)
- DV_Data (cv_link, linkedin, portfolio_companies)

### 3. Test the System

```sql
-- Test 1: Create a test lead
INSERT INTO dealflow_leads (
    org_id,
    company_name,
    founder_name,
    founder_email,
    one_liner,
    company_stage
) VALUES (
    (SELECT id FROM orgs LIMIT 1),
    'Test Corp',
    'Test Founder',
    'founder@testcorp.com',
    'AI-powered testing solution',
    'mvp'
);

-- Test 2: Check it was created
SELECT * FROM dealflow_leads ORDER BY created_at DESC LIMIT 1;

-- Test 3: Create a portfolio company
INSERT INTO portfolio_companies (
    organization_id,
    dv_org_id,
    investment_stage,
    qualification_status
) VALUES (
    (SELECT id FROM organizations LIMIT 1),
    (SELECT id FROM orgs LIMIT 1),
    'seed',
    'green'
);

-- Test 4: Check materialized views work
SELECT * FROM dv_portfolio_health;
SELECT * FROM dv_dealflow_metrics;
```

---

## 🎉 You're Done!

After running `FINAL_4_WHEELS_COMPLETE.sql`, you have:

✅ Complete database for all 4 wheels
✅ LinkedIn → CV auto-generation
✅ Google Workspace integration ready
✅ Google Contacts CRM ready
✅ CEO dashboards ready
✅ Next-round qualification system ready
✅ All helper functions for automation

**Next:** Set up the Python services (AI engine, sync services, agents)

See `IMPLEMENTATION_STATUS.md` for next steps!
