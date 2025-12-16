-- Migration 003: Fix Junction Tables and Policies
-- Adds org_id to junction tables and updates RLS policies

-- ============================================================================
-- ADD MISSING COLUMNS TO JUNCTION TABLES
-- ============================================================================

DO $$ 
BEGIN
    -- Add org_id to meeting_participants if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='meeting_participants' AND column_name='org_id'
    ) THEN
        RAISE NOTICE 'Adding org_id to meeting_participants';
        
        -- Add column as nullable first
        ALTER TABLE meeting_participants ADD COLUMN org_id UUID;
        
        -- Populate from meetings table
        UPDATE meeting_participants mp
        SET org_id = m.org_id
        FROM meetings m
        WHERE mp.meeting_id = m.id;
        
        -- Now make it NOT NULL
        ALTER TABLE meeting_participants ALTER COLUMN org_id SET NOT NULL;
        
        -- Add foreign key constraint
        ALTER TABLE meeting_participants 
            ADD CONSTRAINT fk_meeting_participants_org 
            FOREIGN KEY (org_id) REFERENCES orgs(id) ON DELETE CASCADE;
        
        -- Add index
        CREATE INDEX IF NOT EXISTS ix_meeting_participants_org_id 
            ON meeting_participants(org_id);
    END IF;
    
    -- Add created_at to meeting_participants if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='meeting_participants' AND column_name='created_at'
    ) THEN
        ALTER TABLE meeting_participants 
            ADD COLUMN created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
    END IF;
    
    -- Add org_id to meeting_tags if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='meeting_tags' AND column_name='org_id'
    ) THEN
        RAISE NOTICE 'Adding org_id to meeting_tags';
        
        ALTER TABLE meeting_tags ADD COLUMN org_id UUID;
        
        UPDATE meeting_tags mt
        SET org_id = m.org_id
        FROM meetings m
        WHERE mt.meeting_id = m.id;
        
        ALTER TABLE meeting_tags ALTER COLUMN org_id SET NOT NULL;
        
        ALTER TABLE meeting_tags 
            ADD CONSTRAINT fk_meeting_tags_org 
            FOREIGN KEY (org_id) REFERENCES orgs(id) ON DELETE CASCADE;
        
        CREATE INDEX IF NOT EXISTS ix_meeting_tags_org_id 
            ON meeting_tags(org_id);
    END IF;
    
    -- Add created_at to meeting_tags if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='meeting_tags' AND column_name='created_at'
    ) THEN
        ALTER TABLE meeting_tags 
            ADD COLUMN created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
    END IF;
    
    -- Add org_id to meeting_entities if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='meeting_entities' AND column_name='org_id'
    ) THEN
        RAISE NOTICE 'Adding org_id to meeting_entities';
        
        ALTER TABLE meeting_entities ADD COLUMN org_id UUID;
        
        UPDATE meeting_entities me
        SET org_id = m.org_id
        FROM meetings m
        WHERE me.meeting_id = m.id;
        
        ALTER TABLE meeting_entities ALTER COLUMN org_id SET NOT NULL;
        
        ALTER TABLE meeting_entities 
            ADD CONSTRAINT fk_meeting_entities_org 
            FOREIGN KEY (org_id) REFERENCES orgs(id) ON DELETE CASCADE;
        
        CREATE INDEX IF NOT EXISTS ix_meeting_entities_org_id 
            ON meeting_entities(org_id);
    END IF;
    
    -- Add created_at to meeting_entities if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='meeting_entities' AND column_name='created_at'
    ) THEN
        ALTER TABLE meeting_entities 
            ADD COLUMN created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
    END IF;
    
END $$;

-- ============================================================================
-- DROP OLD CONFLICTING POLICIES
-- ============================================================================

DO $$ 
DECLARE
    r RECORD;
BEGIN
    -- Drop all existing policies on key tables to avoid conflicts
    FOR r IN (
        SELECT tablename, policyname
        FROM pg_policies
        WHERE schemaname = 'public'
        AND tablename IN (
            'meetings', 'meeting_groups', 'people', 'meeting_participants',
            'artifacts', 'transcript_chunks', 'summaries', 'action_items',
            'decisions', 'tags', 'meeting_tags', 'entities', 'meeting_entities',
            'links', 'processing_runs', 'external_refs', 'integrations'
        )
    ) LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON %I', r.policyname, r.tablename);
        RAISE NOTICE 'Dropped policy % on %', r.policyname, r.tablename;
    END LOOP;
END $$;

-- ============================================================================
-- RECREATE HELPER FUNCTIONS (ensure they exist)
-- ============================================================================

CREATE OR REPLACE FUNCTION user_is_org_member(check_org_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM org_memberships
    WHERE org_id = check_org_id
    AND user_id = auth.uid()
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION user_can_write_org(check_org_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM org_memberships
    WHERE org_id = check_org_id
    AND user_id = auth.uid()
    AND role IN ('owner', 'admin', 'member')
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION user_is_org_admin(check_org_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM org_memberships
    WHERE org_id = check_org_id
    AND user_id = auth.uid()
    AND role IN ('owner', 'admin')
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- CREATE NEW POLICIES
-- ============================================================================

-- Meeting Groups
DROP POLICY IF EXISTS meeting_groups_all ON meeting_groups;
CREATE POLICY meeting_groups_all ON meeting_groups FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

-- Meetings
DROP POLICY IF EXISTS meetings_all ON meetings;
CREATE POLICY meetings_all ON meetings FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

-- People
DROP POLICY IF EXISTS people_all ON people;
CREATE POLICY people_all ON people FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

-- Meeting Participants
DROP POLICY IF EXISTS meeting_participants_all ON meeting_participants;
CREATE POLICY meeting_participants_all ON meeting_participants FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

-- Artifacts
DROP POLICY IF EXISTS artifacts_all ON artifacts;
CREATE POLICY artifacts_all ON artifacts FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

-- Transcript Chunks
DROP POLICY IF EXISTS transcript_chunks_all ON transcript_chunks;
CREATE POLICY transcript_chunks_all ON transcript_chunks FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

-- Summaries
DROP POLICY IF EXISTS summaries_all ON summaries;
CREATE POLICY summaries_all ON summaries FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

-- Action Items
DROP POLICY IF EXISTS action_items_all ON action_items;
CREATE POLICY action_items_all ON action_items FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

-- Decisions
DROP POLICY IF EXISTS decisions_all ON decisions;
CREATE POLICY decisions_all ON decisions FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

-- Tags
DROP POLICY IF EXISTS tags_all ON tags;
CREATE POLICY tags_all ON tags FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

-- Meeting Tags
DROP POLICY IF EXISTS meeting_tags_all ON meeting_tags;
CREATE POLICY meeting_tags_all ON meeting_tags FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

-- Entities
DROP POLICY IF EXISTS entities_all ON entities;
CREATE POLICY entities_all ON entities FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

-- Meeting Entities
DROP POLICY IF EXISTS meeting_entities_all ON meeting_entities;
CREATE POLICY meeting_entities_all ON meeting_entities FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

-- Links
DROP POLICY IF EXISTS links_all ON links;
CREATE POLICY links_all ON links FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

-- Processing Runs
DROP POLICY IF EXISTS processing_runs_all ON processing_runs;
CREATE POLICY processing_runs_all ON processing_runs FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

-- External Refs
DROP POLICY IF EXISTS external_refs_all ON external_refs;
CREATE POLICY external_refs_all ON external_refs FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

-- Integrations (admin only for write)
DROP POLICY IF EXISTS integrations_select ON integrations;
CREATE POLICY integrations_select ON integrations FOR SELECT
  USING (user_is_org_member(org_id));

DROP POLICY IF EXISTS integrations_insert ON integrations;
CREATE POLICY integrations_insert ON integrations FOR INSERT
  WITH CHECK (user_is_org_admin(org_id));

DROP POLICY IF EXISTS integrations_update ON integrations;
CREATE POLICY integrations_update ON integrations FOR UPDATE
  USING (user_is_org_admin(org_id))
  WITH CHECK (user_is_org_admin(org_id));

DROP POLICY IF EXISTS integrations_delete ON integrations;
CREATE POLICY integrations_delete ON integrations FOR DELETE
  USING (user_is_org_admin(org_id));

-- ============================================================================
-- VERIFICATION
-- ============================================================================

DO $$ 
BEGIN
    RAISE NOTICE '✓ Migration 003 complete: Junction tables fixed and policies updated';
END $$;




