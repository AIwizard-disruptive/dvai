-- Initial multi-tenant schema with Row Level Security (RLS)
-- SAFE VERSION: Adds missing columns to existing tables

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- ADD MISSING COLUMNS TO EXISTING TABLES (if tables already exist)
-- ============================================================================

-- Add org_id to tables that might be missing it
DO $$ 
BEGIN
    -- Add org_id to meetings if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='meetings' AND column_name='org_id'
    ) THEN
        ALTER TABLE meetings ADD COLUMN org_id UUID;
        -- Can't add NOT NULL to existing table with data, so we'll leave it nullable
    END IF;
    
    -- Add org_id to artifacts if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='artifacts' AND column_name='org_id'
    ) THEN
        ALTER TABLE artifacts ADD COLUMN org_id UUID;
    END IF;
    
    -- Add org_id to transcript_chunks if missing  
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='transcript_chunks' AND column_name='org_id'
    ) THEN
        ALTER TABLE transcript_chunks ADD COLUMN org_id UUID;
    END IF;
    
    -- Add org_id to summaries if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='summaries' AND column_name='org_id'
    ) THEN
        ALTER TABLE summaries ADD COLUMN org_id UUID;
    END IF;
    
    -- Add org_id to action_items if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='action_items' AND column_name='org_id'
    ) THEN
        ALTER TABLE action_items ADD COLUMN org_id UUID;
    END IF;
    
    -- Add org_id to decisions if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='decisions' AND column_name='org_id'
    ) THEN
        ALTER TABLE decisions ADD COLUMN org_id UUID;
    END IF;
    
    -- Add org_id to tags if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='tags' AND column_name='org_id'
    ) THEN
        ALTER TABLE tags ADD COLUMN org_id UUID;
    END IF;
    
    -- Add org_id to entities if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='entities' AND column_name='org_id'
    ) THEN
        ALTER TABLE entities ADD COLUMN org_id UUID;
    END IF;
    
    -- Add org_id to links if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='links' AND column_name='org_id'
    ) THEN
        ALTER TABLE links ADD COLUMN org_id UUID;
    END IF;
    
    -- Add org_id to processing_runs if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='processing_runs' AND column_name='org_id'
    ) THEN
        ALTER TABLE processing_runs ADD COLUMN org_id UUID;
    END IF;
    
    -- Add org_id to external_refs if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='external_refs' AND column_name='org_id'
    ) THEN
        ALTER TABLE external_refs ADD COLUMN org_id UUID;
    END IF;
    
    -- Add org_id to integrations if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='integrations' AND column_name='org_id'
    ) THEN
        ALTER TABLE integrations ADD COLUMN org_id UUID;
    END IF;
    
    -- Add org_id to people if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='people' AND column_name='org_id'
    ) THEN
        ALTER TABLE people ADD COLUMN org_id UUID;
    END IF;
    
    -- Add org_id to meeting_groups if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='meeting_groups' AND column_name='org_id'
    ) THEN
        ALTER TABLE meeting_groups ADD COLUMN org_id UUID;
    END IF;
END $$;

-- ============================================================================
-- Success message
-- ============================================================================
DO $$ 
BEGIN
    RAISE NOTICE 'Schema update complete - org_id columns added where missing';
END $$;




