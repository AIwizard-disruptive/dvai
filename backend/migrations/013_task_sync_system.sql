-- ============================================================================
-- MIGRATION 013: TASK SYNC SYSTEM
-- Linear ↔ Google Tasks ↔ Database Bidirectional Sync
-- ============================================================================

-- ============================================================================
-- TASKS TABLE - Central source of truth
-- ============================================================================
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    
    -- Assignment
    assigned_to_person_id UUID REFERENCES people(id),
    assigned_to_email TEXT,
    created_by_person_id UUID REFERENCES people(id),
    
    -- Task details
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'todo',  -- 'todo', 'in_progress', 'done', 'cancelled'
    priority TEXT,  -- 'low', 'medium', 'high', 'urgent'
    
    -- Dates
    due_date DATE,
    completed_at TIMESTAMPTZ,
    
    -- Source
    source TEXT,  -- 'meeting', 'linear', 'google_tasks', 'manual'
    source_meeting_id UUID REFERENCES meetings(id),
    
    -- External IDs for sync
    linear_issue_id TEXT,
    google_task_id TEXT,
    
    -- Sync tracking
    last_synced_to_linear_at TIMESTAMPTZ,
    last_synced_to_google_at TIMESTAMPTZ,
    sync_enabled BOOLEAN DEFAULT true,
    
    -- Tags/labels
    tags TEXT[],
    labels JSONB,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Unique constraints for external IDs
    UNIQUE(linear_issue_id),
    UNIQUE(google_task_id)
);

CREATE INDEX IF NOT EXISTS idx_tasks_org ON tasks(org_id);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned_to ON tasks(assigned_to_person_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_linear_id ON tasks(linear_issue_id);
CREATE INDEX IF NOT EXISTS idx_tasks_google_id ON tasks(google_task_id);
CREATE INDEX IF NOT EXISTS idx_tasks_email ON tasks(assigned_to_email);

-- ============================================================================
-- TASK SYNC LOG - Track all sync events
-- ============================================================================
CREATE TABLE IF NOT EXISTS task_sync_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    
    -- Sync details
    sync_direction TEXT NOT NULL,  -- 'to_linear', 'from_linear', 'to_google', 'from_google'
    sync_type TEXT NOT NULL,  -- 'create', 'update', 'delete', 'status_change'
    
    -- What changed
    field_changes JSONB,  -- {field: {old: 'value', new: 'value'}}
    
    -- External IDs
    linear_issue_id TEXT,
    google_task_id TEXT,
    
    -- Status
    sync_status TEXT DEFAULT 'pending',  -- 'pending', 'success', 'failed', 'skipped'
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Timestamps
    synced_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sync_log_task ON task_sync_log(task_id);
CREATE INDEX IF NOT EXISTS idx_sync_log_status ON task_sync_log(sync_status);
CREATE INDEX IF NOT EXISTS idx_sync_log_direction ON task_sync_log(sync_direction);

-- ============================================================================
-- GOOGLE TASKS MAPPING - Track Google Task Lists
-- ============================================================================
CREATE TABLE IF NOT EXISTS google_task_lists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    person_id UUID REFERENCES people(id),
    
    -- Google Task List details
    google_task_list_id TEXT NOT NULL,
    google_task_list_name TEXT,
    
    -- Sync config
    auto_sync_enabled BOOLEAN DEFAULT true,
    sync_to_linear BOOLEAN DEFAULT true,
    sync_from_linear BOOLEAN DEFAULT true,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_synced_at TIMESTAMPTZ,
    
    UNIQUE(person_id, google_task_list_id)
);

CREATE INDEX IF NOT EXISTS idx_google_task_lists_person ON google_task_lists(person_id);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_tasks_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_tasks_updated_at ON tasks;
CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_tasks_updated_at();

-- Log changes trigger
CREATE OR REPLACE FUNCTION log_task_changes()
RETURNS TRIGGER AS $$
DECLARE
    v_changes JSONB := '{}'::jsonb;
    v_sync_direction TEXT;
BEGIN
    -- Build change log
    IF TG_OP = 'UPDATE' THEN
        IF OLD.title IS DISTINCT FROM NEW.title THEN
            v_changes := v_changes || jsonb_build_object('title', jsonb_build_object('old', OLD.title, 'new', NEW.title));
        END IF;
        IF OLD.status IS DISTINCT FROM NEW.status THEN
            v_changes := v_changes || jsonb_build_object('status', jsonb_build_object('old', OLD.status, 'new', NEW.status));
        END IF;
        IF OLD.description IS DISTINCT FROM NEW.description THEN
            v_changes := v_changes || jsonb_build_object('description', jsonb_build_object('old', OLD.description, 'new', NEW.description));
        END IF;
        IF OLD.due_date IS DISTINCT FROM NEW.due_date THEN
            v_changes := v_changes || jsonb_build_object('due_date', jsonb_build_object('old', OLD.due_date, 'new', NEW.due_date));
        END IF;
        
        -- Only log if there are actual changes
        IF v_changes != '{}'::jsonb THEN
            -- Determine sync direction based on which external ID changed
            v_sync_direction := 'internal_update';
            
            INSERT INTO task_sync_log (
                task_id,
                sync_direction,
                sync_type,
                field_changes,
                linear_issue_id,
                google_task_id,
                sync_status
            ) VALUES (
                NEW.id,
                v_sync_direction,
                'update',
                v_changes,
                NEW.linear_issue_id,
                NEW.google_task_id,
                'pending'
            );
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS log_task_changes ON tasks;
CREATE TRIGGER log_task_changes
    AFTER UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION log_task_changes();

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to sync task to Linear
CREATE OR REPLACE FUNCTION sync_task_to_linear(
    p_task_id UUID
)
RETURNS JSONB AS $$
DECLARE
    task_record RECORD;
    person_record RECORD;
    linear_mapping RECORD;
    sync_payload JSONB;
BEGIN
    -- Get task
    SELECT * INTO task_record FROM tasks WHERE id = p_task_id;
    IF NOT FOUND THEN
        RETURN jsonb_build_object('error', 'Task not found');
    END IF;
    
    -- Get person and Linear mapping
    IF task_record.assigned_to_person_id IS NOT NULL THEN
        SELECT p.*, lm.linear_user_id
        INTO person_record
        FROM people p
        LEFT JOIN linear_user_mappings lm ON lm.person_email = p.email
        WHERE p.id = task_record.assigned_to_person_id;
    ELSIF task_record.assigned_to_email IS NOT NULL THEN
        SELECT lm.linear_user_id
        INTO linear_mapping
        FROM linear_user_mappings lm
        WHERE lm.person_email = task_record.assigned_to_email;
    END IF;
    
    -- Build Linear API payload
    sync_payload := jsonb_build_object(
        'title', task_record.title,
        'description', COALESCE(task_record.description, ''),
        'priority', CASE 
            WHEN task_record.priority = 'urgent' THEN 1
            WHEN task_record.priority = 'high' THEN 2
            WHEN task_record.priority = 'medium' THEN 3
            ELSE 4
        END,
        'state', CASE
            WHEN task_record.status = 'done' THEN 'completed'
            WHEN task_record.status = 'in_progress' THEN 'started'
            WHEN task_record.status = 'cancelled' THEN 'cancelled'
            ELSE 'backlog'
        END
    );
    
    IF person_record.linear_user_id IS NOT NULL THEN
        sync_payload := sync_payload || jsonb_build_object('assigneeId', person_record.linear_user_id);
    ELSIF linear_mapping.linear_user_id IS NOT NULL THEN
        sync_payload := sync_payload || jsonb_build_object('assigneeId', linear_mapping.linear_user_id);
    END IF;
    
    IF task_record.due_date IS NOT NULL THEN
        sync_payload := sync_payload || jsonb_build_object('dueDate', task_record.due_date);
    END IF;
    
    -- Update sync timestamp
    UPDATE tasks
    SET last_synced_to_linear_at = NOW()
    WHERE id = p_task_id;
    
    RETURN sync_payload;
END;
$$ LANGUAGE plpgsql;

-- Function to sync task to Google Tasks
CREATE OR REPLACE FUNCTION sync_task_to_google(
    p_task_id UUID
)
RETURNS JSONB AS $$
DECLARE
    task_record RECORD;
    sync_payload JSONB;
BEGIN
    SELECT * INTO task_record FROM tasks WHERE id = p_task_id;
    IF NOT FOUND THEN
        RETURN jsonb_build_object('error', 'Task not found');
    END IF;
    
    -- Build Google Tasks API payload
    sync_payload := jsonb_build_object(
        'title', task_record.title,
        'notes', COALESCE(task_record.description, ''),
        'status', CASE
            WHEN task_record.status = 'done' THEN 'completed'
            ELSE 'needsAction'
        END
    );
    
    IF task_record.due_date IS NOT NULL THEN
        sync_payload := sync_payload || jsonb_build_object('due', task_record.due_date::text || 'T00:00:00Z');
    END IF;
    
    IF task_record.completed_at IS NOT NULL THEN
        sync_payload := sync_payload || jsonb_build_object('completed', task_record.completed_at);
    END IF;
    
    -- Update sync timestamp
    UPDATE tasks
    SET last_synced_to_google_at = NOW()
    WHERE id = p_task_id;
    
    RETURN sync_payload;
END;
$$ LANGUAGE plpgsql;

-- Function to create task from Linear issue
CREATE OR REPLACE FUNCTION create_task_from_linear(
    p_org_id UUID,
    p_linear_issue_id TEXT,
    p_linear_data JSONB
)
RETURNS UUID AS $$
DECLARE
    v_task_id UUID;
    v_person_id UUID;
    v_assignee_linear_id TEXT;
BEGIN
    -- Extract assignee Linear ID
    v_assignee_linear_id := p_linear_data->>'assigneeId';
    
    -- Find person by Linear ID
    IF v_assignee_linear_id IS NOT NULL THEN
        SELECT p.id INTO v_person_id
        FROM people p
        JOIN linear_user_mappings lm ON lm.person_email = p.email
        WHERE lm.linear_user_id = v_assignee_linear_id
        AND p.org_id = p_org_id;
    END IF;
    
    -- Create task
    INSERT INTO tasks (
        org_id,
        assigned_to_person_id,
        title,
        description,
        status,
        priority,
        due_date,
        source,
        linear_issue_id,
        last_synced_to_linear_at
    ) VALUES (
        p_org_id,
        v_person_id,
        p_linear_data->>'title',
        p_linear_data->>'description',
        CASE p_linear_data->>'state'
            WHEN 'completed' THEN 'done'
            WHEN 'started' THEN 'in_progress'
            WHEN 'cancelled' THEN 'cancelled'
            ELSE 'todo'
        END,
        CASE (p_linear_data->>'priority')::integer
            WHEN 1 THEN 'urgent'
            WHEN 2 THEN 'high'
            WHEN 3 THEN 'medium'
            ELSE 'low'
        END,
        (p_linear_data->>'dueDate')::date,
        'linear',
        p_linear_issue_id,
        NOW()
    )
    RETURNING id INTO v_task_id;
    
    RETURN v_task_id;
END;
$$ LANGUAGE plpgsql;

-- Function to create task from Google Task
CREATE OR REPLACE FUNCTION create_task_from_google(
    p_org_id UUID,
    p_person_id UUID,
    p_google_task_id TEXT,
    p_google_data JSONB
)
RETURNS UUID AS $$
DECLARE
    v_task_id UUID;
BEGIN
    INSERT INTO tasks (
        org_id,
        assigned_to_person_id,
        title,
        description,
        status,
        due_date,
        source,
        google_task_id,
        last_synced_to_google_at,
        completed_at
    ) VALUES (
        p_org_id,
        p_person_id,
        p_google_data->>'title',
        p_google_data->>'notes',
        CASE p_google_data->>'status'
            WHEN 'completed' THEN 'done'
            ELSE 'todo'
        END,
        (p_google_data->>'due')::date,
        'google_tasks',
        p_google_task_id,
        NOW(),
        (p_google_data->>'completed')::timestamptz
    )
    RETURNING id INTO v_task_id;
    
    RETURN v_task_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- RLS POLICIES
-- ============================================================================

ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE task_sync_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE google_task_lists ENABLE ROW LEVEL SECURITY;

-- Tasks: Users can view tasks in their org
CREATE POLICY "Users can view org tasks" ON tasks FOR SELECT
    USING (org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid()));

-- Tasks: Users can view their assigned tasks
CREATE POLICY "Users can view assigned tasks" ON tasks FOR SELECT
    USING (assigned_to_person_id IN (
        SELECT p.id FROM people p 
        JOIN org_memberships om ON om.org_id = p.org_id 
        WHERE om.user_id = auth.uid()
    ));

-- Tasks: Org admins can manage all tasks
CREATE POLICY "Org admins manage tasks" ON tasks FOR ALL
    USING (org_id IN (SELECT om.org_id FROM org_memberships om WHERE om.user_id = auth.uid() AND om.role IN ('owner', 'admin')));

-- Service role access
CREATE POLICY "Service role tasks" ON tasks FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role sync_log" ON task_sync_log FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role google_lists" ON google_task_lists FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE tasks IS 'Central tasks table - syncs with Linear and Google Tasks';
COMMENT ON TABLE task_sync_log IS 'Audit log of all task sync operations';
COMMENT ON TABLE google_task_lists IS 'Tracks Google Task Lists for sync configuration';

COMMENT ON COLUMN tasks.linear_issue_id IS 'Linear issue ID for bidirectional sync';
COMMENT ON COLUMN tasks.google_task_id IS 'Google Task ID for bidirectional sync';
COMMENT ON COLUMN tasks.sync_enabled IS 'Enable/disable sync for this task';
COMMENT ON COLUMN tasks.source IS 'Where task originated: meeting, linear, google_tasks, manual';

COMMENT ON FUNCTION sync_task_to_linear IS 'Generates Linear API payload for syncing task';
COMMENT ON FUNCTION sync_task_to_google IS 'Generates Google Tasks API payload for syncing task';
COMMENT ON FUNCTION create_task_from_linear IS 'Creates task from Linear webhook/API data';
COMMENT ON FUNCTION create_task_from_google IS 'Creates task from Google Tasks API data';
