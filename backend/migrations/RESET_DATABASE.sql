-- ============================================================================
-- COMPLETE DATABASE RESET
-- ⚠️  WARNING: This will DELETE ALL DATA and rebuild from scratch
-- ============================================================================

-- Step 1: Drop everything
-- ============================================================================

DO $$ 
DECLARE
    r RECORD;
BEGIN
    RAISE NOTICE '🗑️  Dropping all policies...';
    FOR r IN (
        SELECT schemaname, tablename, policyname
        FROM pg_policies
        WHERE schemaname = 'public'
    ) LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON %I.%I CASCADE', 
            r.policyname, r.schemaname, r.tablename);
    END LOOP;
END $$;

DROP FUNCTION IF EXISTS user_is_org_member(UUID) CASCADE;
DROP FUNCTION IF EXISTS user_can_write_org(UUID) CASCADE;
DROP FUNCTION IF EXISTS user_is_org_admin(UUID) CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

-- Drop all tables
DROP TABLE IF EXISTS intelligence_evidence CASCADE;
DROP TABLE IF EXISTS intelligence_action_items CASCADE;
DROP TABLE IF EXISTS intelligence_decisions CASCADE;
DROP TABLE IF EXISTS intelligence_summaries CASCADE;
DROP TABLE IF EXISTS pii_detected CASCADE;
DROP TABLE IF EXISTS speakers_normalized CASCADE;
DROP TABLE IF EXISTS transcripts_normalized CASCADE;
DROP TABLE IF EXISTS transcripts_raw CASCADE;
DROP TABLE IF EXISTS meeting_entities CASCADE;
DROP TABLE IF EXISTS meeting_tags CASCADE;
DROP TABLE IF EXISTS meeting_participants CASCADE;
DROP TABLE IF EXISTS links CASCADE;
DROP TABLE IF EXISTS entities CASCADE;
DROP TABLE IF EXISTS tags CASCADE;
DROP TABLE IF EXISTS decisions CASCADE;
DROP TABLE IF EXISTS action_items CASCADE;
DROP TABLE IF EXISTS summaries CASCADE;
DROP TABLE IF EXISTS transcript_chunks CASCADE;
DROP TABLE IF EXISTS artifacts CASCADE;
DROP TABLE IF EXISTS people CASCADE;
DROP TABLE IF EXISTS external_refs CASCADE;
DROP TABLE IF EXISTS processing_runs CASCADE;
DROP TABLE IF EXISTS integrations CASCADE;
DROP TABLE IF EXISTS meetings CASCADE;
DROP TABLE IF EXISTS meeting_groups CASCADE;
DROP TABLE IF EXISTS org_memberships CASCADE;
DROP TABLE IF EXISTS orgs CASCADE;

DO $$ 
BEGIN
    RAISE NOTICE '✓ All tables dropped';
    RAISE NOTICE '';
    RAISE NOTICE '🏗️  Creating fresh schema...';
END $$;

-- Step 2: Create fresh schema from 001_initial_schema.sql
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- ORGANIZATIONS & MEMBERSHIPS
-- ============================================================================

CREATE TABLE IF NOT EXISTS orgs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    settings JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS org_memberships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    user_id UUID NOT NULL, -- References auth.users.id
    role VARCHAR(50) NOT NULL DEFAULT 'member', -- owner, admin, member, viewer
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(org_id, user_id)
);

CREATE INDEX IF NOT EXISTS ix_org_memberships_org_user ON org_memberships(org_id, user_id);
CREATE INDEX IF NOT EXISTS ix_org_memberships_user_id ON org_memberships(user_id);

-- ============================================================================
-- MEETING INTELLIGENCE TABLES
-- ============================================================================

CREATE TABLE IF NOT EXISTS meeting_groups (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_meeting_groups_org_id ON meeting_groups(org_id);

CREATE TABLE IF NOT EXISTS meetings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    meeting_group_id UUID REFERENCES meeting_groups(id) ON DELETE SET NULL,
    title VARCHAR(500) NOT NULL,
    meeting_date DATE,
    meeting_type VARCHAR(100),
    company VARCHAR(255),
    location VARCHAR(255),
    duration_minutes INTEGER,
    processing_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    meeting_metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_meetings_org_id ON meetings(org_id);
CREATE INDEX IF NOT EXISTS ix_meetings_date ON meetings(meeting_date);
CREATE INDEX IF NOT EXISTS ix_meetings_status ON meetings(processing_status);

CREATE TABLE IF NOT EXISTS people (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    role VARCHAR(255),
    company VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_people_org_id ON people(org_id);
CREATE INDEX IF NOT EXISTS ix_people_email ON people(email);

CREATE TABLE IF NOT EXISTS meeting_participants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    meeting_id UUID NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    person_id UUID NOT NULL REFERENCES people(id) ON DELETE CASCADE,
    attended BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_meeting_participants_org_id ON meeting_participants(org_id);
CREATE INDEX IF NOT EXISTS ix_meeting_participants_meeting ON meeting_participants(meeting_id);
CREATE INDEX IF NOT EXISTS ix_meeting_participants_person ON meeting_participants(person_id);

CREATE TABLE IF NOT EXISTS artifacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    meeting_id UUID REFERENCES meetings(id) ON DELETE CASCADE,
    filename VARCHAR(500) NOT NULL,
    file_type VARCHAR(50) NOT NULL, -- audio, docx, pdf
    mime_type VARCHAR(100),
    file_size INTEGER,
    storage_path TEXT NOT NULL,
    sha256 VARCHAR(64),
    content_text TEXT,
    duration_seconds FLOAT,
    language VARCHAR(10),
    transcription_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    transcription_provider VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_artifacts_org_id ON artifacts(org_id);
CREATE INDEX IF NOT EXISTS ix_artifacts_meeting_id ON artifacts(meeting_id);
CREATE INDEX IF NOT EXISTS ix_artifacts_sha256 ON artifacts(sha256);

CREATE TABLE IF NOT EXISTS transcript_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    meeting_id UUID NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    artifact_id UUID REFERENCES artifacts(id) ON DELETE CASCADE,
    sequence INTEGER NOT NULL,
    speaker VARCHAR(255),
    text TEXT NOT NULL,
    start_time FLOAT,
    end_time FLOAT,
    confidence FLOAT,
    language VARCHAR(10),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_transcript_chunks_org_id ON transcript_chunks(org_id);
CREATE INDEX IF NOT EXISTS ix_transcript_chunks_meeting ON transcript_chunks(meeting_id);
CREATE INDEX IF NOT EXISTS ix_transcript_chunks_sequence ON transcript_chunks(meeting_id, sequence);

CREATE TABLE IF NOT EXISTS summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    meeting_id UUID NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    summary_type VARCHAR(50) NOT NULL DEFAULT 'full',
    content_md TEXT NOT NULL,
    model VARCHAR(100),
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_summaries_org_id ON summaries(org_id);
CREATE INDEX IF NOT EXISTS ix_summaries_meeting ON summaries(meeting_id);

CREATE TABLE IF NOT EXISTS action_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    meeting_id UUID NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    owner_name VARCHAR(255),
    owner_email VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'open',
    due_date DATE,
    priority VARCHAR(20),
    source_chunk_id UUID REFERENCES transcript_chunks(id) ON DELETE SET NULL,
    source_quote TEXT,
    confidence FLOAT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_action_items_org_id ON action_items(org_id);
CREATE INDEX IF NOT EXISTS ix_action_items_meeting ON action_items(meeting_id);
CREATE INDEX IF NOT EXISTS ix_action_items_status ON action_items(status);
CREATE INDEX IF NOT EXISTS ix_action_items_owner ON action_items(owner_email);

CREATE TABLE IF NOT EXISTS decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    meeting_id UUID NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    decision TEXT NOT NULL,
    rationale TEXT,
    source_chunk_id UUID REFERENCES transcript_chunks(id) ON DELETE SET NULL,
    source_quote TEXT,
    confidence FLOAT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_decisions_org_id ON decisions(org_id);
CREATE INDEX IF NOT EXISTS ix_decisions_meeting ON decisions(meeting_id);

CREATE TABLE IF NOT EXISTS tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(20),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(org_id, name)
);

CREATE INDEX IF NOT EXISTS ix_tags_org_name ON tags(org_id, name);

CREATE TABLE IF NOT EXISTS meeting_tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    meeting_id UUID NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(meeting_id, tag_id)
);

CREATE INDEX IF NOT EXISTS ix_meeting_tags_org_id ON meeting_tags(org_id);
CREATE INDEX IF NOT EXISTS ix_meeting_tags_meeting ON meeting_tags(meeting_id);
CREATE INDEX IF NOT EXISTS ix_meeting_tags_tag ON meeting_tags(tag_id);

CREATE TABLE IF NOT EXISTS entities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    kind VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    canonical_name VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_entities_org_kind_name ON entities(org_id, kind, name);

CREATE TABLE IF NOT EXISTS meeting_entities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    meeting_id UUID NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    mention_count INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(meeting_id, entity_id)
);

CREATE INDEX IF NOT EXISTS ix_meeting_entities_org_id ON meeting_entities(org_id);
CREATE INDEX IF NOT EXISTS ix_meeting_entities_meeting ON meeting_entities(meeting_id);
CREATE INDEX IF NOT EXISTS ix_meeting_entities_entity ON meeting_entities(entity_id);

CREATE TABLE IF NOT EXISTS links (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    meeting_id UUID NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    title VARCHAR(500),
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_links_org_id ON links(org_id);
CREATE INDEX IF NOT EXISTS ix_links_meeting ON links(meeting_id);

-- ============================================================================
-- OPERATIONAL TABLES
-- ============================================================================

CREATE TABLE IF NOT EXISTS processing_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    meeting_id UUID REFERENCES meetings(id) ON DELETE CASCADE,
    artifact_id UUID REFERENCES artifacts(id) ON DELETE CASCADE,
    stage VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'queued',
    error TEXT,
    run_metadata JSONB,
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_processing_runs_org_id ON processing_runs(org_id);
CREATE INDEX IF NOT EXISTS ix_processing_runs_meeting ON processing_runs(meeting_id);
CREATE INDEX IF NOT EXISTS ix_processing_runs_status ON processing_runs(status);
CREATE INDEX IF NOT EXISTS ix_processing_runs_stage ON processing_runs(stage);

CREATE TABLE IF NOT EXISTS external_refs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    local_table VARCHAR(100) NOT NULL,
    local_id UUID NOT NULL,
    provider VARCHAR(50) NOT NULL,
    kind VARCHAR(50) NOT NULL,
    external_id VARCHAR(500) NOT NULL,
    external_url TEXT,
    sync_metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_external_refs_org_id ON external_refs(org_id);
CREATE INDEX IF NOT EXISTS ix_external_refs_local ON external_refs(local_table, local_id);
CREATE INDEX IF NOT EXISTS ix_external_refs_provider_kind ON external_refs(provider, kind);
CREATE INDEX IF NOT EXISTS ix_external_refs_external_id ON external_refs(external_id);

CREATE TABLE IF NOT EXISTS integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT true,
    config JSONB,
    secrets_encrypted TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(org_id, provider)
);

CREATE INDEX IF NOT EXISTS ix_integrations_org_provider ON integrations(org_id, provider);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all org-scoped tables
ALTER TABLE orgs ENABLE ROW LEVEL SECURITY;
ALTER TABLE org_memberships ENABLE ROW LEVEL SECURITY;
ALTER TABLE meeting_groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE meetings ENABLE ROW LEVEL SECURITY;
ALTER TABLE people ENABLE ROW LEVEL SECURITY;
ALTER TABLE meeting_participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE artifacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE transcript_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE summaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE action_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE meeting_tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE meeting_entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE links ENABLE ROW LEVEL SECURITY;
ALTER TABLE processing_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE external_refs ENABLE ROW LEVEL SECURITY;
ALTER TABLE integrations ENABLE ROW LEVEL SECURITY;

-- Helper function to check org membership
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

-- Helper function to check if user can write (not viewer)
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

-- Helper function to check if user is admin or owner
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

-- Orgs policies
CREATE POLICY orgs_select ON orgs FOR SELECT
  USING (user_is_org_member(id));

CREATE POLICY orgs_insert ON orgs FOR INSERT
  WITH CHECK (true); -- Anyone can create an org

CREATE POLICY orgs_update ON orgs FOR UPDATE
  USING (user_is_org_admin(id))
  WITH CHECK (user_is_org_admin(id));

CREATE POLICY orgs_delete ON orgs FOR DELETE
  USING (EXISTS (
    SELECT 1 FROM org_memberships
    WHERE org_id = orgs.id
    AND user_id = auth.uid()
    AND role = 'owner'
  ));

-- Org memberships policies
CREATE POLICY org_memberships_select ON org_memberships FOR SELECT
  USING (user_is_org_member(org_id));

CREATE POLICY org_memberships_insert ON org_memberships FOR INSERT
  WITH CHECK (user_is_org_admin(org_id));

CREATE POLICY org_memberships_update ON org_memberships FOR UPDATE
  USING (user_is_org_admin(org_id))
  WITH CHECK (user_is_org_admin(org_id));

CREATE POLICY org_memberships_delete ON org_memberships FOR DELETE
  USING (user_is_org_admin(org_id));

-- Generic policies for org-scoped tables
CREATE POLICY meeting_groups_all ON meeting_groups FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

CREATE POLICY meetings_all ON meetings FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

CREATE POLICY people_all ON people FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

CREATE POLICY meeting_participants_all ON meeting_participants FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

CREATE POLICY artifacts_all ON artifacts FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

CREATE POLICY transcript_chunks_all ON transcript_chunks FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

CREATE POLICY summaries_all ON summaries FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

CREATE POLICY action_items_all ON action_items FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

CREATE POLICY decisions_all ON decisions FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

CREATE POLICY tags_all ON tags FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

CREATE POLICY meeting_tags_all ON meeting_tags FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

CREATE POLICY entities_all ON entities FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

CREATE POLICY meeting_entities_all ON meeting_entities FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

CREATE POLICY links_all ON links FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

CREATE POLICY processing_runs_all ON processing_runs FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

CREATE POLICY external_refs_all ON external_refs FOR ALL
  USING (user_is_org_member(org_id))
  WITH CHECK (user_can_write_org(org_id));

-- Integrations require admin access
CREATE POLICY integrations_select ON integrations FOR SELECT
  USING (user_is_org_member(org_id));

CREATE POLICY integrations_insert ON integrations FOR INSERT
  WITH CHECK (user_is_org_admin(org_id));

CREATE POLICY integrations_update ON integrations FOR UPDATE
  USING (user_is_org_admin(org_id))
  WITH CHECK (user_is_org_admin(org_id));

CREATE POLICY integrations_delete ON integrations FOR DELETE
  USING (user_is_org_admin(org_id));

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_orgs_updated_at BEFORE UPDATE ON orgs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_org_memberships_updated_at BEFORE UPDATE ON org_memberships
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_meeting_groups_updated_at BEFORE UPDATE ON meeting_groups
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_meetings_updated_at BEFORE UPDATE ON meetings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_people_updated_at BEFORE UPDATE ON people
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_artifacts_updated_at BEFORE UPDATE ON artifacts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transcript_chunks_updated_at BEFORE UPDATE ON transcript_chunks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_summaries_updated_at BEFORE UPDATE ON summaries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_action_items_updated_at BEFORE UPDATE ON action_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_decisions_updated_at BEFORE UPDATE ON decisions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tags_updated_at BEFORE UPDATE ON tags
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_entities_updated_at BEFORE UPDATE ON entities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_links_updated_at BEFORE UPDATE ON links
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_processing_runs_updated_at BEFORE UPDATE ON processing_runs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_external_refs_updated_at BEFORE UPDATE ON external_refs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_integrations_updated_at BEFORE UPDATE ON integrations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- COMPLETE
-- ============================================================================

DO $$ 
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '✅ DATABASE RESET COMPLETE';
    RAISE NOTICE '✓ All old data deleted';
    RAISE NOTICE '✓ Fresh schema created';
    RAISE NOTICE '✓ %s tables created', (
        SELECT COUNT(*) FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    );
    RAISE NOTICE '✓ RLS policies enabled';
    RAISE NOTICE '';
    RAISE NOTICE '→ Ready for data import';
END $$;




