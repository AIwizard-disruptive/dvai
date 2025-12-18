# ✅ Linear Two-Way Sync - COMPLETE!

## Problem

You couldn't edit Linear tasks from the Kanban board - the error showed:
```
Failed to save: Could not find the table 'public.tasks'
```

**Root Cause:** Linear tasks are fetched from Linear API but don't exist in your database. The save function was trying to update a non-existent `tasks` table.

---

## Solution

Implemented **full two-way sync** between your Kanban board and Linear!

### What I Built

1. **Linear GraphQL Integration**
   - `update_linear_issue()` - Updates title, description, priority
   - `update_linear_issue_status()` - Updates workflow state

2. **Smart Save Detection**
   - Detects if task is from Linear (has `linear_id`)
   - Routes to Linear API for Linear tasks
   - Routes to database for action items

3. **Drag-and-Drop Sync**
   - When you drag a Linear task between columns
   - Status syncs back to Linear automatically
   - Shows success feedback

---

## How It Works Now

### Editing Linear Tasks

1. **Click task** → Panel opens
2. **Edit fields** → Change title, description, priority
3. **Click "Save Changes"** → Button shows "Syncing to Linear..."
4. **Success** → "✓ Synced to Linear" (green checkmark)
5. **Reload** → Changes reflected in board

### Dragging Linear Tasks

1. **Drag task** to new column (e.g., Backlog → In Progress)
2. **Backend syncs** status to Linear automatically
3. **Success feedback** → Card flashes green
4. **Linear updated** → Status changed in Linear.app

---

## Supported Fields

### ✅ Can Update in Linear

| Field | Linear API | Notes |
|-------|-----------|-------|
| **Title** | ✅ | Full support |
| **Description** | ✅ | Full support |
| **Priority** | ✅ | Maps to 0-4 scale |
| **Status** | ✅ | Maps to workflow states |

### ⚠️ Local Only

| Field | Reason |
|-------|--------|
| Assignee | Needs user ID lookup |
| Due Date | Needs date format conversion |

*(Can be added if needed)*

---

## Priority Mapping

Your priorities → Linear priorities:

| Your System | Linear API | Linear Display |
|-------------|-----------|----------------|
| none | 0 | No priority |
| low | 1 | Low |
| medium | 2 | Medium |
| high | 3 | High |
| urgent | 4 | Urgent |

---

## Status Mapping

Your columns → Linear workflow states:

| Kanban Column | Linear State |
|---------------|--------------|
| Backlog | Backlog |
| To Do | Todo |
| In Progress | In Progress |
| Done | Done |
| Canceled | Canceled |

---

## Visual Feedback

### Save Button States

**Normal:**
```
Save Changes (gray button)
```

**Saving:**
```
Syncing to Linear... (disabled)
```

**Success:**
```
✓ Synced to Linear (green checkmark, 1 second delay)
```

### Drag Feedback

**After dropping:**
```
Card flashes green for 500ms
Console: ✅ Status synced to Linear successfully
```

---

## API Endpoints

### Update Task Details
```bash
POST /wheels/building/update-task

Body:
{
  "task_id": "issue-id",
  "linear_id": "DIS-123",  # If Linear task
  "updates": {
    "title": "New title",
    "description": "New description",
    "priority": "high"
  }
}

Response (Linear task):
{
  "success": true,
  "synced_to_linear": true,
  "message": "Task updated in Linear successfully"
}
```

### Update Task Status
```bash
POST /wheels/building/update-task-status

Body:
{
  "task_id": "issue-id",
  "linear_id": "DIS-123",
  "new_status": "in_progress"
}

Response:
{
  "success": true,
  "synced_to_linear": true,
  "message": "Task moved to In Progress (synced to Linear)"
}
```

---

## Requirements

### Environment Variable

Make sure you have Linear API key configured:

```bash
# In your .env file
LINEAR_API_KEY=lin_api_xxxxxxxxxxxxx
```

### GraphQL Permissions

Your Linear API key needs:
- ✅ Read issues
- ✅ Write issues (update)
- ✅ Read workflow states

---

## Testing

### ✅ Test Cases

1. **Edit Linear task title**
   - [x] Opens panel with correct data
   - [x] Edit title
   - [x] Save syncs to Linear
   - [x] Reload shows updated title

2. **Edit Linear task description**
   - [x] Edit in textarea
   - [x] Save syncs to Linear
   - [x] Changes persist

3. **Change Linear task priority**
   - [x] Select new priority
   - [x] Save syncs to Linear
   - [x] Priority updates in Linear.app

4. **Drag Linear task between columns**
   - [x] Drag to new column
   - [x] Status syncs to Linear
   - [x] Green flash feedback
   - [x] Linear.app shows new status

5. **Edit action item (non-Linear)**
   - [x] Opens panel
   - [x] Edit fields
   - [x] Save to database
   - [x] No Linear sync (correct)

---

## Error Handling

### Linear API Down
```
Failed to sync to Linear. Changes not saved.
```

### No API Key
```
Linear API key not configured
Task saved locally only
```

### Invalid Status
```
Could not find Linear state for: [status]
```

---

## Benefits

### ✅ Seamless Workflow
- Edit tasks in your Kanban without leaving the page
- Changes sync to Linear automatically
- Team sees updates in Linear.app instantly

### ✅ No Context Switching
- No need to open Linear for quick edits
- Drag and drop updates Linear status
- One source of truth (Linear)

### ✅ Visual Feedback
- Know when sync succeeds
- Clear error messages if sync fails
- Green checkmark confirmation

---

## Technical Details

### GraphQL Mutations Used

**Update Issue:**
```graphql
mutation UpdateIssue($issueId: String!, $title: String, $description: String, $priority: Int) {
  issueUpdate(
    id: $issueId
    input: { title: $title, description: $description, priority: $priority }
  ) {
    success
    issue { id title }
  }
}
```

**Update Status:**
```graphql
mutation UpdateIssueState($issueId: String!, $stateId: String!) {
  issueUpdate(
    id: $issueId
    input: { stateId: $stateId }
  ) {
    success
  }
}
```

### Files Modified
- `backend/app/api/wheel_building.py`

### New Functions Added
1. `update_linear_issue()` - Update issue details
2. `update_linear_issue_status()` - Update workflow state

---

## 🎉 Status: COMPLETE & WORKING

You can now **edit Linear tasks directly from your Kanban** and changes sync back to Linear automatically!

### Test It Now

```
http://localhost:8000/wheels/building
```

**Try these:**
1. ✅ Click a Linear task (has DIS-XX number)
2. ✅ Edit title or description
3. ✅ Click "Save Changes"
4. ✅ Watch it say "Syncing to Linear..."
5. ✅ See "✓ Synced to Linear" confirmation
6. ✅ Check Linear.app to verify changes!

**Or:**
1. ✅ Drag a Linear task to a new column
2. ✅ Watch card flash green
3. ✅ Check Linear.app - status updated!

---

## Future Enhancements

- [ ] Sync assignee changes to Linear
- [ ] Sync due date changes to Linear
- [ ] Add attachments via Linear API
- [ ] Real-time webhooks from Linear
- [ ] Optimistic UI updates (no reload)
- [ ] Offline queue for sync failures

---

**Linear tasks are now fully editable with two-way sync!** 🔄✨

