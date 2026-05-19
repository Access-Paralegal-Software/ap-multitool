-- ==========================================
-- ARCHIVIST CORE: UNIVERSAL SCHEMA DDL
-- ==========================================
-- Designed for high-performance normalization of multiple note providers.
-- Supports both SQLite (local dev) and PostgreSQL (production SaaS).

-- ------------------------------------------
-- 1. COLLECTIONS TABLE
-- Tracks Stacks, Notebooks, Notion Databases, and Email Inboxes.
-- ------------------------------------------
CREATE TABLE IF NOT EXISTS universal_collections (
    id TEXT PRIMARY KEY,                         -- UUID
    name TEXT NOT NULL,                          -- 'Access Paralegal', 'Inbox', etc.
    provider_group TEXT,                         -- Evernote 'Stack' or Notion 'Workspace'
    provider TEXT NOT NULL,                      -- 'evernote', 'notion', 'email'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------
-- 2. NOTES LEDGER
-- The primary document indexing storage.
-- ------------------------------------------
CREATE TABLE IF NOT EXISTS universal_notes (
    id TEXT PRIMARY KEY,                         -- Internal Unique UUID
    source_id TEXT,                              -- Original Guid from Provider
    collection_id TEXT,                          -- Link to universal_collections
    provider TEXT NOT NULL,                      -- 'evernote', 'notion', 'email'
    
    title TEXT NOT NULL,                         -- Subject or Note Title
    content_raw TEXT,                            -- Raw ENML / HTML Source
    content_markdown TEXT,                       -- Cleaned markdown version
    
    source_url TEXT,                             -- Webclipper URL source
    author TEXT,                                 -- Note author or Email Sender
    
    original_created_at DATETIME,                -- Date Note was created in Provider
    original_updated_at DATETIME,                -- Last edit time in Provider
    system_indexed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    tags TEXT,                                   -- JSON serialized list of tag strings
    
    triage_status TEXT DEFAULT 'pending',        -- 'pending', 'approved', 'distilled', 'trashed'
    is_distilled INTEGER DEFAULT 0,             -- Boolean: 0=False, 1=True
    
    FOREIGN KEY (collection_id) REFERENCES universal_collections (id)
);

-- ------------------------------------------
-- 3. ATTACHMENTS / ASSET REGISTRY
-- Tracks images, PDFs, and embeds, with hooks for the AI Pre-Filter.
-- ------------------------------------------
CREATE TABLE IF NOT EXISTS universal_attachments (
    id TEXT PRIMARY KEY,                         -- Unique Asset UUID
    note_id TEXT NOT NULL,                       -- Links back to universal_notes
    source_resource_id TEXT,                     -- Evernote MD5 hash or Resource ID
    
    filename TEXT NOT NULL,                      -- e.g., 'photo_1.png'
    mime_type TEXT,                              -- 'image/png', 'application/pdf'
    file_size_bytes INTEGER,                     -- File size for optimization triage
    
    width_px INTEGER,                            -- Resolution tracking
    height_px INTEGER,                           -- (Helps heuristically flag tiny spacer GIFs)
    
    system_file_path TEXT,                       -- Path to raw binary in storage
    
    ai_classification TEXT DEFAULT 'untested',   -- 'junk', 'valuable', 'untested'
    ai_confidence REAL,                          -- Confidence score of classifier
    user_approval_status TEXT DEFAULT 'pending', -- 'keep', 'discard', 'pending'
    
    FOREIGN KEY (note_id) REFERENCES universal_notes (id)
);

CREATE INDEX IF NOT EXISTS idx_notes_collection ON universal_notes (collection_id);
CREATE INDEX IF NOT EXISTS idx_notes_triage ON universal_notes (triage_status);
CREATE INDEX IF NOT EXISTS idx_attachments_note ON universal_attachments (note_id);
CREATE INDEX IF NOT EXISTS idx_attachments_ai ON universal_attachments (ai_classification);
