-- AP-eDiscovery Local Search Appliance Database Schema
-- SQLite 3 schema with BLAKE3 deduplication, FTS5 external content, and O(1) tag counting

PRAGMA foreign_keys = ON;

-- Custodians table: Source individuals or entities responsible for evidentiary documents
CREATE TABLE IF NOT EXISTS custodians (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    email TEXT,
    title TEXT,
    department TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- Documents table: Stored legal documents with cryptographic hashes and custodian relations
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_hash TEXT NOT NULL UNIQUE, -- BLAKE3 hex-encoded hash of the document content
    family_hash TEXT,              -- BLAKE3 hex hash grouping parent email/attachment families
    custodian_id INTEGER REFERENCES custodians(id) ON DELETE SET NULL,
    file_path TEXT,
    file_name TEXT,
    file_size INTEGER,
    mime_type TEXT,
    title TEXT,
    body TEXT NOT NULL,
    metadata_json TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_documents_doc_hash ON documents(doc_hash);
CREATE INDEX IF NOT EXISTS idx_documents_family_hash ON documents(family_hash);
CREATE INDEX IF NOT EXISTS idx_documents_custodian_id ON documents(custodian_id);

-- External-content documents_fts virtual table using FTS5 (unicode61 tokenizer with diacritics removed)
CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
    title,
    body,
    content='documents',
    content_rowid='id',
    tokenize='unicode61 remove_diacritics 2'
);

-- Sync Trigger: After Insert on documents -> sync into documents_fts
CREATE TRIGGER IF NOT EXISTS trg_documents_ai AFTER INSERT ON documents
BEGIN
    INSERT INTO documents_fts(rowid, title, body) VALUES (new.id, new.title, new.body);
END;

-- Sync Trigger: After Delete on documents -> delete from documents_fts
CREATE TRIGGER IF NOT EXISTS trg_documents_ad AFTER DELETE ON documents
BEGIN
    INSERT INTO documents_fts(documents_fts, rowid, title, body) VALUES('delete', old.id, old.title, old.body);
END;

-- Sync Trigger: After Update on documents -> update documents_fts
CREATE TRIGGER IF NOT EXISTS trg_documents_au AFTER UPDATE ON documents
BEGIN
    INSERT INTO documents_fts(documents_fts, rowid, title, body) VALUES('delete', old.id, old.title, old.body);
    INSERT INTO documents_fts(rowid, title, body) VALUES (new.id, new.title, new.body);
END;

-- Tags table: Classification and responsive tags (e.g. Privileged, Responsive, Hot, Work Product)
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    color TEXT,
    description TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- Document tags join table
CREATE TABLE IF NOT EXISTS document_tags (
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    PRIMARY KEY (document_id, tag_id)
);

CREATE INDEX IF NOT EXISTS idx_document_tags_tag_id ON document_tags(tag_id);

-- O(1) Precomputed Tag Counts table
CREATE TABLE IF NOT EXISTS tag_counts (
    tag_id INTEGER PRIMARY KEY REFERENCES tags(id) ON DELETE CASCADE,
    doc_count INTEGER NOT NULL DEFAULT 0,
    count INTEGER GENERATED ALWAYS AS (doc_count) VIRTUAL,
    document_count INTEGER GENERATED ALWAYS AS (doc_count) VIRTUAL
);

-- Initialize count when tag is created
CREATE TRIGGER IF NOT EXISTS trg_tags_ai AFTER INSERT ON tags
BEGIN
    INSERT INTO tag_counts (tag_id, doc_count) VALUES (new.id, 0);
END;

-- Clean up tag_counts when tag is removed
CREATE TRIGGER IF NOT EXISTS trg_tags_ad AFTER DELETE ON tags
BEGIN
    DELETE FROM tag_counts WHERE tag_id = old.id;
END;

-- O(1) Increment on tag assignment
CREATE TRIGGER IF NOT EXISTS trg_document_tags_ai AFTER INSERT ON document_tags
BEGIN
    INSERT INTO tag_counts (tag_id, doc_count)
    VALUES (new.tag_id, 1)
    ON CONFLICT(tag_id) DO UPDATE SET doc_count = tag_counts.doc_count + 1;
END;

-- O(1) Decrement on tag unassignment
CREATE TRIGGER IF NOT EXISTS trg_document_tags_ad AFTER DELETE ON document_tags
BEGIN
    UPDATE tag_counts
    SET doc_count = MAX(0, doc_count - 1)
    WHERE tag_id = old.tag_id;
END;

-- O(1) Update on tag reassignment
CREATE TRIGGER IF NOT EXISTS trg_document_tags_au AFTER UPDATE OF tag_id ON document_tags
BEGIN
    UPDATE tag_counts
    SET doc_count = MAX(0, doc_count - 1)
    WHERE tag_id = old.tag_id;

    INSERT INTO tag_counts (tag_id, doc_count)
    VALUES (new.tag_id, 1)
    ON CONFLICT(tag_id) DO UPDATE SET doc_count = tag_counts.doc_count + 1;
END;
