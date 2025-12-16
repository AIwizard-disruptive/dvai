-- Generated Documents Table
-- Stores all auto-generated documents (meeting notes, emails, etc.)

CREATE TABLE IF NOT EXISTS generated_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    meeting_id UUID NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    doc_type VARCHAR(100) NOT NULL,  -- meeting_notes, email_decision_update, etc.
    language VARCHAR(10) NOT NULL DEFAULT 'sv',  -- sv, en
    format VARCHAR(50) NOT NULL,  -- markdown, email, pdf, etc.
    content TEXT NOT NULL,
    storage_path VARCHAR(1000),  -- Path in Google Drive when uploaded
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_generated_documents_org_id ON generated_documents(org_id);
CREATE INDEX IF NOT EXISTS ix_generated_documents_meeting ON generated_documents(meeting_id);
CREATE INDEX IF NOT EXISTS ix_generated_documents_type ON generated_documents(doc_type);
CREATE INDEX IF NOT EXISTS ix_generated_documents_language ON generated_documents(language);

COMMENT ON TABLE generated_documents IS 'Auto-generated documents from meetings (notes, emails, reports)';
COMMENT ON COLUMN generated_documents.doc_type IS 'Type of document: meeting_notes, email_decision_update, email_action_reminder, etc.';
COMMENT ON COLUMN generated_documents.language IS 'Language code: sv (Swedish), en (English)';
COMMENT ON COLUMN generated_documents.content IS 'Full document content in markdown or text format';




