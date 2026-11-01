"""Tests validating SQLite schema, FTS5 sync triggers, and O(1) tag counting."""

import sqlite3
import pytest
from ap_ediscovery.db import get_schema_sql


@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(get_schema_sql())
    yield conn
    conn.close()


def test_schema_tables_exist(db_conn: sqlite3.Connection):
    tables = [
        row[0]
        for row in db_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    ]
    assert "custodians" in tables
    assert "documents" in tables
    assert "documents_fts" in tables
    assert "tags" in tables
    assert "document_tags" in tables
    assert "tag_counts" in tables


def test_documents_and_fts_sync_triggers(db_conn: sqlite3.Connection):
    # Insert custodian
    db_conn.execute("INSERT INTO custodians (name, email) VALUES (?, ?)", ("Alice Smith", "alice@example.com"))
    custodian_id = db_conn.execute("SELECT id FROM custodians WHERE name = ?", ("Alice Smith",)).fetchone()["id"]

    # Insert document
    body_text = "The tenant provided constructive notice of plumbing defects directly to the landlord."
    db_conn.execute(
        """
        INSERT INTO documents (doc_hash, family_hash, custodian_id, file_name, title, body)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("blake3_doc_hash_1", "blake3_fam_hash_1", custodian_id, "notice.pdf", "Notice of Breach", body_text),
    )

    # Verify FTS5 MATCH using NEAR
    near_query = 'NEAR("constructive notice" "landlord", 8)'
    matches = db_conn.execute(
        "SELECT rowid, title, body FROM documents_fts WHERE documents_fts MATCH ?",
        (near_query,),
    ).fetchall()
    assert len(matches) == 1
    assert matches[0]["title"] == "Notice of Breach"

    # Test UPDATE trigger (trg_documents_au)
    doc_id = matches[0]["rowid"]
    updated_body = "The revised settlement agreement was executed by all parties without constructive notice to the prior landlord."
    db_conn.execute(
        "UPDATE documents SET body = ? WHERE id = ?",
        (updated_body, doc_id),
    )

    updated_matches = db_conn.execute(
        "SELECT rowid, title FROM documents_fts WHERE documents_fts MATCH ?",
        ('NEAR("constructive notice" "landlord", 8)',),
    ).fetchall()
    assert len(updated_matches) == 1

    settlement_matches = db_conn.execute(
        "SELECT rowid FROM documents_fts WHERE documents_fts MATCH ?",
        ('"settlement agreement"',),
    ).fetchall()
    assert len(settlement_matches) == 1

    # Test DELETE trigger (trg_documents_ad)
    db_conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    deleted_matches = db_conn.execute(
        "SELECT rowid FROM documents_fts WHERE documents_fts MATCH ?",
        ('NEAR("constructive notice" "landlord", 8)',),
    ).fetchall()
    assert len(deleted_matches) == 0


def test_o1_trigger_updated_tag_counts(db_conn: sqlite3.Connection):
    # Insert tag
    db_conn.execute("INSERT INTO tags (name, description) VALUES (?, ?)", ("Responsive", "Responsive discovery documents"))
    tag_id = db_conn.execute("SELECT id FROM tags WHERE name = ?", ("Responsive",)).fetchone()["id"]

    # Verify initial O(1) tag count
    initial_count = db_conn.execute("SELECT doc_count FROM tag_counts WHERE tag_id = ?", (tag_id,)).fetchone()["doc_count"]
    assert initial_count == 0

    # Insert document
    db_conn.execute(
        """
        INSERT INTO documents (doc_hash, family_hash, title, body)
        VALUES (?, ?, ?, ?)
        """,
        ("doc_101", "fam_101", "Lease Contract", "Standard lease term covenants."),
    )
    doc_id = db_conn.execute("SELECT id FROM documents WHERE doc_hash = ?", ("doc_101",)).fetchone()["id"]

    # Assign tag to document (triggers trg_document_tags_ai)
    db_conn.execute("INSERT INTO document_tags (document_id, tag_id) VALUES (?, ?)", (doc_id, tag_id))
    cnt = db_conn.execute("SELECT doc_count, count, document_count FROM tag_counts WHERE tag_id = ?", (tag_id,)).fetchone()
    assert cnt["doc_count"] == 1
    assert cnt["count"] == 1
    assert cnt["document_count"] == 1

    # Unassign tag (triggers trg_document_tags_ad)
    db_conn.execute("DELETE FROM document_tags WHERE document_id = ? AND tag_id = ?", (doc_id, tag_id))
    cnt_after = db_conn.execute("SELECT doc_count FROM tag_counts WHERE tag_id = ?", (tag_id,)).fetchone()["doc_count"]
    assert cnt_after == 0
