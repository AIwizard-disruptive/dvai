-- ============================================================================
-- MIGRATION 021: PIPELINE STAGES / KANBAN COLUMNS
-- Store pipeline stages (Kanban columns) synced from Pipedrive or other CRMs
-- ============================================================================

-- Pipeline stages (Kanban columns) for each portfolio company
CREATE TABLE IF NOT EXISTS pipeline_stages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_company_id UUID NOT NULL REFERENCES portfolio_companies(id) ON DELETE CASCADE,
    
    -- Stage Information
    external_stage_id TEXT, -- ID from external system (Pipedrive stage ID, Linear state ID, etc.)
    stage_name TEXT NOT NULL,
    stage_order INTEGER NOT NULL DEFAULT 0, -- Order in Kanban board (0 = leftmost)
    stage_type TEXT, -- 'backlog', 'todo', 'in_progress', 'review', 'done', 'won', 'lost', etc.
    
    -- Visual Configuration
    color TEXT, -- Hex color for the column
    icon TEXT, -- Icon name for the column
    
    -- Metadata
    source_system TEXT DEFAULT 'pipedrive', -- 'pipedrive', 'linear', 'manual', etc.
    is_active BOOLEAN DEFAULT true,
    is_closed_status BOOLEAN DEFAULT false, -- True for "won" or "done" stages
    
    -- Sync tracking
    synced_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(portfolio_company_id, external_stage_id, source_system)
);

CREATE INDEX IF NOT EXISTS idx_pipeline_stages_company ON pipeline_stages(portfolio_company_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_stages_order ON pipeline_stages(portfolio_company_id, stage_order);
CREATE INDEX IF NOT EXISTS idx_pipeline_stages_active ON pipeline_stages(is_active);
CREATE INDEX IF NOT EXISTS idx_pipeline_stages_source ON pipeline_stages(source_system);

-- Comments
COMMENT ON TABLE pipeline_stages IS 'Pipeline stages (Kanban columns) synced from CRMs for each portfolio company';
COMMENT ON COLUMN pipeline_stages.external_stage_id IS 'Stage ID from external system (Pipedrive, Linear, etc.)';
COMMENT ON COLUMN pipeline_stages.stage_order IS 'Display order in Kanban board (0 = leftmost)';
COMMENT ON COLUMN pipeline_stages.stage_type IS 'Standardized stage type for filtering and logic';
COMMENT ON COLUMN pipeline_stages.is_closed_status IS 'True for final stages like won/lost/done';

-- Default stages for companies without external system
-- These will be used as fallback if Pipedrive sync hasn't run yet
INSERT INTO pipeline_stages (portfolio_company_id, stage_name, stage_order, stage_type, source_system)
SELECT 
    pc.id,
    stages.stage_name,
    stages.stage_order,
    stages.stage_type,
    'default'
FROM portfolio_companies pc
CROSS JOIN (
    VALUES 
        ('Backlog', 0, 'backlog'),
        ('To Do', 1, 'todo'),
        ('In Progress', 2, 'in_progress'),
        ('Done', 3, 'done')
) AS stages(stage_name, stage_order, stage_type)
WHERE NOT EXISTS (
    SELECT 1 FROM pipeline_stages ps 
    WHERE ps.portfolio_company_id = pc.id
)
ON CONFLICT DO NOTHING;
