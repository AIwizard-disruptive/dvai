# Tasks Created for Serge & Wizard

## ✅ What Was Created

**23 total tasks:**
- 11 tasks for **Serge** (investment & strategy focused)
- 11 tasks for **Wizard** (admin & support focused)
- 1 shared task assigned to both

---

## 📋 Serge's Tasks (Investment Focus)

### **High Priority / Urgent**
1. ⏰ **Review Q4 portfolio company metrics** (Due: 3 days)
   - Analyze Q4 performance across portfolio
   - Focus on revenue growth, burn rate, runway

2. 🔥 **Due diligence: TechStartup AB** (Due: 5 days, IN PROGRESS)
   - Complete technical and financial DD for Series A
   - Review cap table, financials, architecture

3. 📊 **Prepare board meeting agenda - PortfolioCo** (Due: 7 days)
   - Include Q4 results, 2025 strategy, funding needs

4. 📝 **Update LP quarterly report** (Due: 10 days)
   - Compile Q4 portfolio performance
   - Include valuations and exits

### **Medium Priority**
5. ☎️ **Follow up: AI startup pitch from last week** (Due: 2 days)
   - Schedule follow-up call
   - Review financials and customer traction

6. ☕ **Coffee meeting with enterprise SaaS founder** (Due: 4 days)
   - Discuss market trends
   - Explore investment opportunities

7. 🤝 **Introduce PortfolioCo to potential customer** (Due: 3 days)
   - Connect CEO with enterprise contact at TechCorp

8. 👥 **Review and approve portfolio company hiring plan** (Due: 5 days)
   - Review hiring plans
   - Approve budget allocations

### **Strategic**
9. 🎯 **Define 2025 investment thesis** (Due: 14 days, IN PROGRESS)
   - Workshop with team
   - Refine focus: AI/ML, Climate Tech, Enterprise SaaS

### **Completed** ✅
10. ✅ **Send term sheet to Nordic SaaS startup**
    - Term sheet sent and accepted

11. ✅ **Attend Nordic Startup Conference**
    - Networked with 15+ founders

---

## 🤖 Wizard's Tasks (Admin & Support Focus)

### **High Priority**
1. 📋 **Process meeting notes from investor call** (Due: 1 day)
   - Extract action items and key decisions
   - Create follow-up tasks

2. 📅 **Schedule Q1 board meetings** (Due: 7 days, IN PROGRESS)
   - Coordinate with 8 portfolio companies
   - Send calendar invites

3. 🧪 **Test Google Tasks sync integration** (Due: 1 day)
   - Verify bidirectional sync working

### **Medium Priority**
4. 📇 **Update CRM with new dealflow contacts** (Due: 2 days)
   - Add 12 new startup contacts from meetings

5. 📊 **Generate LP report distribution list** (Due: 8 days)
   - Compile email list for Q4 LP report
   - Verify all contacts current

6. ⚙️ **Set up automated weekly portfolio metrics report** (Due: 10 days, IN PROGRESS)
   - Configure automation to pull key metrics

7. 🔍 **Research AI trends for investment thesis** (Due: 14 days)
   - Compile report on emerging AI trends
   - LLMs, AI agents, enterprise AI adoption

### **Low Priority**
8. 📁 **Organize Q4 portfolio documents in Drive** (Due: 5 days)
   - Create folder structure
   - Organize board decks, financial reports

9. 🔬 **Analyze competitor fund strategies** (Due: 20 days)
   - Review investment focus of 5 competing VC funds

### **Completed** ✅
10. ✅ **Send meeting invites for team sync**
    - All invites sent, meeting Friday 10am

11. ✅ **Update portfolio company contact list**
    - Contact list updated with new CEOs/CFOs

---

## 🔄 Shared Task (Both Assigned)

12. 🎤 **Prepare annual investor meeting presentation** (Due: 21 days, IN PROGRESS, URGENT)
    - Collaborate on annual meeting deck
    - Portfolio highlights, performance, 2025 outlook

---

## 📊 Task Statistics

### **By Status:**
- 🟡 To Do: 15 tasks
- 🔵 In Progress: 4 tasks
- ✅ Done: 4 tasks

### **By Priority:**
- 🔥 Urgent: 2 tasks
- ⬆️ High: 8 tasks
- ➡️ Medium: 10 tasks
- ⬇️ Low: 3 tasks

### **By Category (Tags):**
- 💼 Portfolio: 7 tasks
- 📈 Dealflow: 4 tasks
- 🤝 Networking: 3 tasks
- 📊 Reporting: 3 tasks
- 🗂️ Admin: 5 tasks
- 🔬 Research: 2 tasks
- 🎯 Strategy: 2 tasks

---

## 🚀 How to Create These Tasks

### **Method 1: Run the Script**
```bash
./create_tasks.sh
```

### **Method 2: Run SQL Directly**
```bash
psql $DATABASE_URL -f backend/migrations/CREATE_TASKS_SERGE_WIZARD.sql
```

### **Method 3: Via Supabase Dashboard**
1. Go to SQL Editor
2. Copy contents of `CREATE_TASKS_SERGE_WIZARD.sql`
3. Click "Run"

---

## 🔄 Sync to Google Tasks

After creating tasks in database:

```bash
cd backend
python sync_google_tasks.py
```

This will:
1. 📤 Push all 23 tasks to Google Tasks
2. ✅ Link them with `google_task_id`
3. 🔄 Enable bidirectional sync

---

## ✨ Test the Sync

### **1. Create tasks in DB** ✅ (Done)

### **2. Sync to Google Tasks**
```bash
python sync_google_tasks.py
```

### **3. Check Google Tasks**
Open https://tasks.google.com
- Should see all 23 tasks!
- Organized by due date
- With full descriptions

### **4. Update a task in Google Tasks**
- Mark "Test Google Tasks sync integration" as complete
- Or change due date on any task

### **5. Sync back to DB**
```bash
python sync_google_tasks.py
```

### **6. Verify in database**
```sql
SELECT title, status, google_task_id, last_synced_to_google_at
FROM tasks
WHERE assigned_to_person_id IN (
    SELECT id FROM people 
    WHERE email IN ('serge@disruptiveventures.se', 'wizard@disruptiveventures.se')
)
ORDER BY updated_at DESC;
```

Should see your changes reflected! ✨

---

## 📝 View Tasks Queries

### **Serge's tasks:**
```sql
SELECT title, status, priority, due_date, tags
FROM tasks t
JOIN people p ON p.id = t.assigned_to_person_id
WHERE p.email LIKE '%serge%'
ORDER BY due_date;
```

### **Wizard's tasks:**
```sql
SELECT title, status, priority, due_date, tags
FROM tasks t
JOIN people p ON p.id = t.assigned_to_person_id
WHERE p.email = 'wizard@disruptiveventures.se'
ORDER BY due_date;
```

### **All tasks summary:**
```sql
SELECT 
    p.name,
    COUNT(*) as total_tasks,
    SUM(CASE WHEN t.status = 'todo' THEN 1 ELSE 0 END) as todo,
    SUM(CASE WHEN t.status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
    SUM(CASE WHEN t.status = 'done' THEN 1 ELSE 0 END) as done
FROM tasks t
JOIN people p ON p.id = t.assigned_to_person_id
WHERE p.email IN ('serge@disruptiveventures.se', 'wizard@disruptiveventures.se')
GROUP BY p.name;
```

---

## 🎯 What This Demonstrates

✅ **Task Management** - Full task lifecycle  
✅ **Priorities** - Urgent, High, Medium, Low  
✅ **Due Dates** - Range from tomorrow to 3 weeks  
✅ **Status Tracking** - Todo, In Progress, Done  
✅ **Tags** - Categorization and filtering  
✅ **Descriptions** - Full context for each task  
✅ **Assignments** - Multiple people, shared tasks  
✅ **Google Sync** - Bidirectional sync ready  

---

## 🚀 Ready to Sync!

Your tasks are ready to be created and synced to Google Tasks. Just run:

```bash
./create_tasks.sh
```

Then sync with:

```bash
cd backend
python sync_google_tasks.py
```

🎉 **All tasks will appear in Google Tasks instantly!**
