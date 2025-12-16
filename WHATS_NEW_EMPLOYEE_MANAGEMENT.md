# What's New: DV Employee Management System

## ✅ Summary

Your **People Wheel (migration 009)** has been enhanced with complete employee management for **@disruptiveventures.se**:

1. ✅ **Domain tracking** - Auto-populate `email_domain` from work email
2. ✅ **LinkedIn → CV generation** - Scrape LinkedIn profiles and generate CVs
3. ✅ **Google Workspace sync** - Update Google Directory profile cards
4. ✅ **Employment contracts** - Full contract management with terms, signatures
5. ✅ **Profile completeness** - CVs, competencies, contracts all linked

---

## 🗂️ Files Modified

### **1. `backend/migrations/009_people_wheel_clean.sql`**
Enhanced with complete employee management system.

---

## 📋 New Database Fields

### **People Table**
```sql
work_email TEXT                    -- name@disruptiveventures.se
email_domain TEXT                  -- Auto-populated: disruptiveventures.se
employee_number TEXT               -- DV-001, DV-002, etc.
employment_contract_id UUID        -- Link to contracts
contract_start_date DATE
contract_end_date DATE
google_workspace_id TEXT
google_directory_synced_at TIMESTAMPTZ
```

### **Contracts Table** (Enhanced)
```sql
employment_type TEXT               -- 'full-time', 'part-time', etc.
probation_end_date DATE
notice_period_days INTEGER
terms JSONB                        -- Complete contract terms
```

### **Person CVs** (Enhanced)
```sql
generated_from_linkedin BOOLEAN
linkedin_profile_url TEXT
linkedin_data_snapshot JSONB
linkedin_scraped_at TIMESTAMPTZ
cv_format TEXT
is_public BOOLEAN
```

### **Google Profile Syncs** (Enhanced)
```sql
google_user_id TEXT
auto_sync_enabled BOOLEAN
sync_frequency TEXT
fields_to_sync TEXT[]
sync_direction TEXT
```

---

## 🔧 New Helper Functions

### 1. **`generate_cv_from_linkedin(person_id, linkedin_data, cv_format)`**
Generates CV from LinkedIn profile data.

### 2. **`update_person_from_linkedin(person_id, linkedin_data)`**
Updates person profile with LinkedIn info.

### 3. **`sync_person_to_google_directory(person_id)`**
Returns Google Directory API payload for syncing.

### 4. **`link_person_to_contract(person_id, contract_id)`**
Links employee to employment contract.

### 5. **`populate_email_domain()` (trigger)**
Auto-populates `email_domain` from `work_email`.

---

## 🚀 Quick Start

### **Step 1: Run Migration**
```bash
psql $DATABASE_URL -f backend/migrations/009_people_wheel_clean.sql
```

### **Step 2: Test with Example**
```bash
# Edit EXAMPLE_DV_EMPLOYEE_SETUP.sql first:
# - Replace 'YOUR_ORG_ID' with your actual org_id
# - Run it:
psql $DATABASE_URL -f backend/migrations/EXAMPLE_DV_EMPLOYEE_SETUP.sql
```

### **Step 3: Verify**
```sql
SELECT name, work_email, email_domain, job_title
FROM people
WHERE email_domain = 'disruptiveventures.se';
```

---

## 📖 Documentation

**Complete guide:** `DV_EMPLOYEE_MANAGEMENT_SYSTEM.md`
- Full schema reference
- Function documentation
- Example workflows
- Useful queries

**Example script:** `EXAMPLE_DV_EMPLOYEE_SETUP.sql`
- Complete employee onboarding workflow
- Test data generation
- Verification queries

---

## 🔄 Next Integration Steps

### **1. LinkedIn Scraper**
Build service to:
- Fetch LinkedIn profile data
- Call `generate_cv_from_linkedin()`
- Store CV PDFs

### **2. Google Workspace Sync**
Build service to:
- Call `sync_person_to_google_directory()`
- POST to Google Directory API
- Update `google_profile_syncs` status

### **3. Contract Management**
Build UI to:
- Generate contracts from templates
- Send for e-signature (DocuSign)
- Store signed PDFs

---

## 💡 Key Features

### **Automatic Domain Extraction**
```sql
INSERT INTO people (work_email) VALUES ('anna@disruptiveventures.se');
-- email_domain is automatically set to 'disruptiveventures.se'
```

### **LinkedIn → CV**
```sql
SELECT generate_cv_from_linkedin(person_id, linkedin_json);
-- Creates CV, extracts skills, updates profile
```

### **Contract Linkage**
```sql
SELECT link_person_to_contract(person_id, contract_id);
-- Links contract and copies start/end dates
```

### **Google Sync Payload**
```sql
SELECT sync_person_to_google_directory(person_id);
-- Returns JSON ready for Google API
```

---

## 🔒 GDPR Notes

✅ Get consent before scraping LinkedIn  
✅ Document legal basis for processing  
✅ Support data export and deletion  
✅ RLS policies enforce org-level access  

---

## ✨ What This Enables

✅ **Complete employee profiles** in your database  
✅ **Automated CV generation** from LinkedIn  
✅ **Google Workspace sync** for directory  
✅ **Contract management** with full terms  
✅ **Competency tracking** for skills  
✅ **Single source of truth** for DV employees  

---

**Ready to go!** 🎉

Marcus, your DV employee management system is complete. All employees can now have:
- Complete profiles with domain tracking
- CVs generated from LinkedIn
- Employment contracts with terms
- Google Workspace sync
- Skills and competencies tracking

Start by running the migration, then test with the example script!
