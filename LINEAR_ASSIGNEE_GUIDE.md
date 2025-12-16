# 👥 Linear Assignee Matching Guide

**How tasks get assigned to the right people**

---

## 🎯 How It Works

### **Matching Strategy:**

The system matches meeting attendees to Linear users in this order:

1. **Email match** (most reliable)
   - If person has `@disruptiveventures.se` email
   - Matches exactly with their Linear email
   - Example: `fanny@disruptiveventures.se` → Fanny's Linear account

2. **Full name match**
   - "Fanny Lundin" → "Fanny Lundin" in Linear
   - Case-insensitive

3. **First name match**
   - "Fanny" → Matches Linear user "Fanny Lundin"
   - Useful for Swedish meeting data where only first names used

---

## 📋 What You Need

### **For Assignee Matching to Work:**

Your team members need to:
1. **Have Linear accounts** (invite them!)
2. **Use work emails** in Linear (`@disruptiveventures.se`)
3. **Match names** in meetings with names in Linear

---

## 👥 Multiple Assignees

### **Linear Limitation:**
Linear only allows **ONE assignee per task**.

### **Our Solution:**
```
Action: "Niklas Jansson och Fanny - Kontakta headhuntingbyråer"

Creates task:
- Assigned to: Niklas Jansson (primary)
- Description mentions: "Also: Fanny"
- Both can see it
- Both get notified
```

### **Parsing Multiple Assignees:**

The system recognizes these formats:
- `"Niklas och Fanny"` → Assigns to Niklas, mentions Fanny
- `"Fanny/Mikaela med Serge"` → Assigns to Fanny, mentions Mikaela and Serge
- `"Team (Niklas, Henrik, Serge)"` → Assigns to Niklas, mentions others
- `"Niklas Jansson, Fanny Lundin"` → Assigns to Niklas, mentions Fanny

---

## 🔧 Updated Script

The `sync_swedish_meeting.py` script now:

1. **Fetches all Linear users** from your workspace
2. **Maps names** → Linear user IDs
3. **Assigns tasks** to correct person
4. **Mentions collaborators** in description

---

## 📊 Example Output

When you run the script:

```
👥 Fetching Linear users...
✓ Found 6 Linear users
  - Henrik (henrik@disruptiveventures.se)
  - Hugo Carlsten (hugo@disruptiveventures.se)
  - Niklas Jansson (niklas@disruptiveventures.se)
  - Mikaela Jansson (mikaela@disruptiveventures.se)
  - Fanny Lundin (fanny@disruptiveventures.se)
  - Serge Lachapelle (serge@disruptiveventures.se)

Mapping attendees to Linear users:
  ✓ Mapped (email): Fanny Lundin → fanny@disruptiveventures.se
  ✓ Mapped (email): Henrik → henrik@disruptiveventures.se
  ✓ Mapped (name): Niklas Jansson → niklas@disruptiveventures.se
  ...

📋 Creating 14 Linear tasks...
   ✓ [1/14] DIS-22: Gemensam intro... → Fanny Lundin ✅
   ✓ [2/14] DIS-23: Fixa dator... → Serge Lachapelle ✅
   ✓ [3/14] DIS-24: Skicka uppsägning... → Niklas Jansson ✅
   ✓ [4/14] DIS-25: Kontakta headhuntingbyråer → Niklas Jansson (+ 1 more) ✅
   ...
```

---

## ✅ Task Assignment Examples

### **Single Assignee:**
```
Action: "Fanny Lundin - Update spreadsheet"

Linear Task:
- Assigned to: Fanny Lundin ✅
- Description: Standard description
```

### **Multiple Assignees:**
```
Action: "Niklas Jansson och Fanny - Kontakta headhuntingbyråer"

Linear Task:
- Assigned to: Niklas Jansson ✅ (primary)
- Description:
  "👥 Collaboration task: Primary: Niklas Jansson | Also: Fanny
  
  From Meeting: Veckomöte...
  
  Additional team members:
  - Fanny"
```

### **Team Task:**
```
Action: "Team (Niklas, Henrik, Serge, Marcus) - Definiera arbetsströmmar"

Linear Task:
- Assigned to: Niklas ✅ (first in list)
- Description:
  "👥 Collaboration task: Primary: Niklas | Also: Henrik, Serge, Marcus
  
  From Meeting: Veckomöte...
  
  Additional team members:
  - Henrik
  - Serge  
  - Marcus"
```

---

## 🚀 Run Updated Script

```bash
cd backend
source venv/bin/activate
python3 sync_swedish_meeting.py
```

**Will create:**
- 1 Linear project
- 14 tasks with CORRECT assignees ✅
- Proper @mentions for collaborators
- All based on matching Linear users

---

## 🎯 What Each Person Sees in Linear

### **Fanny's View (My Issues):**
```
DIS-8:  Gemensam intro för Marcus...        High    Today
DIS-11: Kontakta headhuntingbyråer         Medium  (collab with Niklas)
DIS-16: Uppföljning Linksense              Medium  (collab with Mikaela)
DIS-17: Möte med Anders från Biodiv        Low     
DIS-18: Strukturering av dealflow          Medium  
```

**Only HER tasks!** She doesn't see Henrik's or Niklas's tasks unless she looks at "All Issues".

### **Niklas's View (My Issues):**
```
DIS-10: Skicka uppsägning till Minding      High    
DIS-11: Kontakta headhuntingbyråer         Medium  (collab with Fanny)
DIS-20: Snacka processer med Marcus        Low     
DIS-21: Definiera arbetsströmmar           Medium  (collab with team)
```

**Only HIS tasks!**

---

## 🔧 If Someone Isn't in Linear Yet

### **They need to:**
1. Get invited to Linear workspace
2. Accept invitation
3. Set up their account with `@disruptiveventures.se` email

### **Then:**
- Re-run the sync script
- Tasks will be re-created with correct assignees
- Or manually assign in Linear

---

## ✅ Benefits

**Proper Assignment:**
- ✅ Each person sees only THEIR tasks in "My Issues"
- ✅ Automatic assignment based on names
- ✅ Email matching for reliability
- ✅ Collaboration tasks handled properly

**Team Collaboration:**
- ✅ Multiple assignees mentioned in description
- ✅ Everyone involved can find the task
- ✅ Clear who's primary vs collaborator
- ✅ No confusion

---

## 🎯 Next Run

Delete the old test tasks and run the updated script:

```bash
# In Linear, archive old tasks if you want
# Or keep them for comparison

# Run updated script with assignee matching
cd backend
source venv/bin/activate
python3 sync_swedish_meeting.py
```

**New tasks will have correct assignees!** ✅

---

**Ready to run it?** The script now properly matches and assigns! 🚀


