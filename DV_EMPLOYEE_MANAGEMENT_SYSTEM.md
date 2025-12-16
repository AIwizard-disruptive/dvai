# DV Employee Management System
**Complete Profile, Contract, LinkedIn & Google Workspace Integration**

---

## 🎯 Overview

Your enhanced **People Wheel (Migration 009)** now provides a complete employee management system for Disruptive Ventures with:

✅ **Domain Management** - All employees tracked as `@disruptiveventures.se`  
✅ **LinkedIn Integration** - Generate CVs from LinkedIn profiles  
✅ **Google Workspace Sync** - Update Google Directory profile cards  
✅ **Employment Contracts** - Link profiles to contracts with full terms  
✅ **Competency Tracking** - Skills extracted from LinkedIn and CVs  

---

## 📋 Database Schema Enhancements

### 1. **People Table Extensions**

New fields added to track DV employees:

```sql
-- Domain & Email
work_email TEXT                    -- name@disruptiveventures.se
email_domain TEXT                  -- Auto-populated: disruptiveventures.se
employee_number TEXT               -- Internal employee ID

-- Contract Linkage
employment_contract_id UUID        -- Links to contracts table
contract_start_date DATE          
contract_end_date DATE            

-- Google Workspace
google_workspace_id TEXT          -- Google Directory user ID
google_directory_synced_at TIMESTAMPTZ
```

**Automatic Domain Extraction**: The `email_domain` field is **auto-populated** via trigger whenever `work_email` is set.

---

### 2. **Enhanced Contracts Table**

Employment contracts now support:

```sql
contract_type TEXT                 -- 'employment', 'nda', 'investment', etc.
value DECIMAL                      -- Annual salary (in SEK)
currency TEXT DEFAULT 'SEK'
terms JSONB                        -- {salary_breakdown, benefits, vacation_days, notice_period}

-- Employment-specific
employment_type TEXT               -- 'full-time', 'part-time', 'contractor'
probation_end_date DATE
notice_period_days INTEGER

-- Signing & Status
status TEXT                        -- 'draft', 'sent', 'signed', 'active', 'expired'
google_doc_id TEXT                 -- Link to Google Docs version
signed_pdf_url TEXT                -- Signed PDF in storage
signed_at TIMESTAMPTZ
signed_by UUID
```

**Example Contract Terms JSON:**
```json
{
  "salary_breakdown": {
    "base_salary": 600000,
    "bonus_potential": 100000,
    "equity_options": 5000
  },
  "benefits": [
    "Health insurance",
    "Pension 4.5%",
    "Wellness allowance 5000 SEK/year"
  ],
  "vacation_days": 30,
  "notice_period": 90,
  "remote_work": "hybrid"
}
```

---

### 3. **Enhanced CV Storage (person_cvs)**

Supports **LinkedIn-generated CVs**:

```sql
-- LinkedIn Integration
generated_from_linkedin BOOLEAN
linkedin_profile_url TEXT
linkedin_data_snapshot JSONB       -- Raw LinkedIn data
linkedin_scraped_at TIMESTAMPTZ

-- CV Metadata
cv_language TEXT DEFAULT 'en'
cv_format TEXT                     -- 'standard', 'executive', 'technical'
is_primary BOOLEAN
is_public BOOLEAN                  -- Can be shared publicly?

-- Content
structured_data JSONB              -- {experience, education, skills, certifications}
extracted_competencies TEXT[]
ai_generated_summary TEXT
```

---

### 4. **Enhanced Google Profile Syncs**

Tracks sync to Google Workspace Directory:

```sql
-- Google IDs
google_user_id TEXT                -- Google Workspace user ID
google_email TEXT                  -- @disruptiveventures.se

-- Sync Config
auto_sync_enabled BOOLEAN
sync_frequency TEXT                -- 'realtime', 'hourly', 'daily', 'manual'
fields_to_sync TEXT[]              -- ['name', 'title', 'department', 'phone', 'bio', 'photo']

-- Sync Tracking
sync_status TEXT                   -- 'pending', 'syncing', 'completed', 'failed'
sync_direction TEXT                -- 'to_google', 'from_google', 'both'
synced_fields JSONB                -- What was synced
current_profile_data JSONB         -- Current Google Directory data
previous_profile_data JSONB        -- For change tracking
```

---

## 🔧 Helper Functions

### 1. **Generate CV from LinkedIn**

Automatically creates a CV from LinkedIn profile data:

```sql
SELECT generate_cv_from_linkedin(
    p_person_id := '123e4567-e89b-12d3-a456-426614174000',
    p_linkedin_data := '{
        "headline": "Senior Product Manager at Disruptive Ventures",
        "summary": "Experienced PM with 10 years in tech...",
        "positions": [...],
        "education": [...],
        "skills": ["Product Management", "Strategy", "Leadership"]
    }'::jsonb,
    p_cv_format := 'executive'
);
```

**What it does:**
- ✅ Creates `person_cvs` record
- ✅ Stores LinkedIn data snapshot
- ✅ Extracts structured data (experience, education, skills)
- ✅ Updates person profile (bio, job title, photo)
- ✅ Adds competencies to `person_competencies` table

---

### 2. **Update Person from LinkedIn**

Updates person profile with LinkedIn data:

```sql
SELECT update_person_from_linkedin(
    p_person_id := '123e4567-e89b-12d3-a456-426614174000',
    p_linkedin_data := '{...}'::jsonb
);
```

Updates: `bio`, `job_title`, `photo_url`, `location`, and extracts `skills` to competencies.

---

### 3. **Sync to Google Workspace Directory**

Generates Google Directory API payload:

```sql
SELECT sync_person_to_google_directory(
    p_person_id := '123e4567-e89b-12d3-a456-426614174000'
);
```

**Returns JSON payload** ready for Google Directory API:
```json
{
  "name": {
    "fullName": "Marcus Andersson",
    "givenName": "Marcus",
    "familyName": "Andersson"
  },
  "primaryEmail": "marcus@disruptiveventures.se",
  "organizations": [{
    "title": "Partner",
    "department": "Ventures",
    "primary": true
  }],
  "phones": [{
    "value": "+46701234567",
    "type": "work"
  }],
  "locations": [{
    "area": "Stockholm",
    "type": "desk"
  }]
}
```

---

### 4. **Link Person to Employment Contract**

Links a person to their employment contract:

```sql
SELECT link_person_to_contract(
    p_person_id := '123e4567-e89b-12d3-a456-426614174000',
    p_contract_id := '987e6543-e21b-12d3-a456-426614174000'
);
```

**Updates person record** with:
- `employment_contract_id`
- `contract_start_date`
- `contract_end_date`

---

## 📊 Complete Employee Workflow

### **Step 1: Create Employee**

```sql
INSERT INTO people (
    org_id,
    name,
    work_email,
    person_type,
    job_title,
    department,
    phone,
    linkedin_url
)
VALUES (
    '00000000-0000-0000-0000-000000000001', -- Your DV org_id
    'Anna Svensson',
    'anna@disruptiveventures.se',
    'internal',
    'Investment Manager',
    'Ventures',
    '+46701234567',
    'https://linkedin.com/in/annasvensson'
);
```

✅ `email_domain` is **auto-populated** to `disruptiveventures.se`

---

### **Step 2: Generate CV from LinkedIn**

```sql
-- After scraping LinkedIn profile
SELECT generate_cv_from_linkedin(
    p_person_id := (SELECT id FROM people WHERE work_email = 'anna@disruptiveventures.se'),
    p_linkedin_data := '{
        "headline": "Investment Manager | Early-stage Ventures",
        "summary": "Investment professional with 8 years experience...",
        "positions": [
            {
                "title": "Investment Manager",
                "company": "Disruptive Ventures",
                "startDate": "2022-01",
                "current": true
            }
        ],
        "education": [
            {
                "school": "Stockholm School of Economics",
                "degree": "MSc Finance"
            }
        ],
        "skills": ["Venture Capital", "Due Diligence", "Portfolio Management"]
    }'::jsonb
);
```

---

### **Step 3: Create Employment Contract**

```sql
INSERT INTO contracts (
    org_id,
    contract_type,
    contract_name,
    party_person_id,
    start_date,
    value,
    currency,
    employment_type,
    probation_end_date,
    notice_period_days,
    terms,
    status
)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'employment',
    'Employment Agreement - Anna Svensson',
    (SELECT id FROM people WHERE work_email = 'anna@disruptiveventures.se'),
    '2022-01-15',
    720000,  -- 720k SEK annual
    'SEK',
    'full-time',
    '2022-07-15',  -- 6 months probation
    90,  -- 3 months notice
    '{
        "salary_breakdown": {
            "base_salary": 600000,
            "bonus_potential": 120000
        },
        "benefits": ["Health insurance", "Pension 4.5%", "Wellness 5000 SEK/year"],
        "vacation_days": 30,
        "remote_work": "hybrid",
        "equipment": ["MacBook Pro", "iPhone"]
    }'::jsonb,
    'draft'
);
```

---

### **Step 4: Link Contract to Employee**

```sql
SELECT link_person_to_contract(
    p_person_id := (SELECT id FROM people WHERE work_email = 'anna@disruptiveventures.se'),
    p_contract_id := (SELECT id FROM contracts WHERE party_person_id = 
                      (SELECT id FROM people WHERE work_email = 'anna@disruptiveventures.se'))
);
```

---

### **Step 5: Sync to Google Workspace**

```sql
-- Generate sync payload
SELECT sync_person_to_google_directory(
    p_person_id := (SELECT id FROM people WHERE work_email = 'anna@disruptiveventures.se')
);

-- This returns JSON payload to send to Google Directory API
-- Your backend integration should POST this to:
-- POST https://admin.googleapis.com/admin/directory/v1/users
```

---

### **Step 6: Track Sync Status**

```sql
INSERT INTO google_profile_syncs (
    person_id,
    google_user_id,
    google_email,
    sync_status,
    fields_to_sync,
    auto_sync_enabled
)
VALUES (
    (SELECT id FROM people WHERE work_email = 'anna@disruptiveventures.se'),
    '116830299264123456789',  -- From Google API response
    'anna@disruptiveventures.se',
    'completed',
    ARRAY['name', 'title', 'department', 'phone', 'bio', 'photo'],
    true
);
```

---

## 🔍 Useful Queries

### **View All DV Employees with Contracts**

```sql
SELECT 
    p.name,
    p.work_email,
    p.job_title,
    p.department,
    p.employee_number,
    c.status as contract_status,
    c.start_date as employment_start,
    c.value as annual_salary,
    c.employment_type,
    p.google_directory_synced_at
FROM people p
LEFT JOIN contracts c ON c.id = p.employment_contract_id
WHERE p.email_domain = 'disruptiveventures.se'
AND p.person_type = 'internal'
ORDER BY p.name;
```

---

### **View Employees with LinkedIn CVs**

```sql
SELECT 
    p.name,
    p.work_email,
    cv.cv_format,
    cv.linkedin_scraped_at,
    cv.extracted_competencies,
    cv.is_primary
FROM people p
JOIN person_cvs cv ON cv.person_id = p.id
WHERE cv.generated_from_linkedin = true
AND p.email_domain = 'disruptiveventures.se';
```

---

### **View Google Sync Status**

```sql
SELECT 
    p.name,
    p.work_email,
    gs.sync_status,
    gs.last_sync_at,
    gs.auto_sync_enabled,
    gs.fields_to_sync
FROM people p
LEFT JOIN google_profile_syncs gs ON gs.person_id = p.id
WHERE p.email_domain = 'disruptiveventures.se'
ORDER BY gs.last_sync_at DESC NULLS LAST;
```

---

### **View Employee Competencies**

```sql
SELECT 
    p.name,
    p.job_title,
    pc.skill_name,
    pc.skill_category,
    pc.proficiency_level,
    pc.source
FROM people p
JOIN person_competencies pc ON pc.person_id = p.id
WHERE p.email_domain = 'disruptiveventures.se'
ORDER BY p.name, pc.skill_category;
```

---

## 🚀 Next Steps

### **Backend Integration Tasks**

1. **LinkedIn Scraper**
   - Build API integration or scraper to fetch LinkedIn profiles
   - Call `generate_cv_from_linkedin()` with scraped data
   - Store CV PDF in Google Drive or cloud storage

2. **Google Workspace Sync Service**
   - Set up Google Directory API credentials
   - Create cron job to sync profiles (daily/weekly)
   - Use `sync_person_to_google_directory()` to generate payloads
   - POST to Google Directory API
   - Update `google_profile_syncs` with results

3. **Contract Management UI**
   - Create contract templates in Google Docs
   - UI to generate contracts from templates
   - E-signature integration (DocuSign, HelloSign)
   - Store signed PDFs in `signed_pdf_url`

4. **Employee Onboarding Flow**
   - Create person record
   - Scrape LinkedIn → Generate CV
   - Generate employment contract
   - Send for signature
   - Sync to Google Workspace
   - Grant access to systems

---

## 📝 Migration Status

✅ **Migration 009 (People Wheel)** updated with:
- Domain tracking (`email_domain`, `work_email`)
- Employment contract linkage
- Enhanced CV storage with LinkedIn support
- Google Workspace sync tracking
- Helper functions for automation

**To apply:**
```bash
# Run the updated migration
psql $DATABASE_URL -f backend/migrations/009_people_wheel_clean.sql
```

---

## 🔒 Security & GDPR Notes

✅ **Data Minimization**: Only store necessary employee data  
✅ **Consent**: LinkedIn data requires consent for scraping/processing  
✅ **Access Control**: RLS policies ensure org-level isolation  
✅ **Right to be Forgotten**: DELETE CASCADE on person records  
✅ **Audit Trail**: All tables have `created_at`, `updated_at`  

**GDPR Compliance for LinkedIn Data:**
- Get explicit consent before scraping LinkedIn profiles
- Document legal basis (legitimate interest for employment)
- Provide data export capability
- Support deletion requests

---

## 📞 Support

**Questions?**
- Check the migration file: `backend/migrations/009_people_wheel_clean.sql`
- Review function definitions for parameters
- Test with sample data before production

**Marcus** - Your complete DV employee management system is ready! 🎉
