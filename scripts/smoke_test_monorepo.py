#!/usr/bin/env python3
"""Smoke test script for AP-Suite monorepo core & engine foundations.

Validates:
1. CRC 2.111 baseline positioning:
   calculate_baseline_y(1) == 720.0 and calculate_baseline_y(28) == 72.0
2. SQLite in-memory execution of schema.sql and validation of:
   NEAR("constructive notice" "landlord", 8)
3. Synchronized FTS5 triggers and O(1) tag counting.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

# Ensure package src directories are in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "packages" / "doc-chameleon" / "src"))
sys.path.insert(0, str(REPO_ROOT / "packages" / "ap-ediscovery" / "src"))


def test_baseline_y() -> None:
    print("--- [1/3] Testing CRC 2.111 Baseline Positioning ---")
    from doc_chameleon.rules.ca.transformer_2111 import calculate_baseline_y

    y_line1 = calculate_baseline_y(1)
    y_line28 = calculate_baseline_y(28)

    print(f"calculate_baseline_y(1)  = {y_line1} pt (Expected: 720.0 pt)")
    print(f"calculate_baseline_y(28) = {y_line28} pt (Expected: 72.0 pt)")

    assert y_line1 == 720.0, f"Expected 720.0, got {y_line1}"
    assert y_line28 == 72.0, f"Expected 72.0, got {y_line28}"

    # Also test intermediate lines and step pitch
    y_line2 = calculate_baseline_y(2)
    assert y_line2 == 696.0, f"Expected 696.0, got {y_line2}"
    assert y_line1 - y_line2 == 24.0, "Line pitch must be exactly 24.0 pt"
    print("[PASS] CRC 2.111 baseline positioning assertions PASSED.")


def test_sqlite_schema_and_fts_near() -> None:
    print("\n--- [2/3] Testing SQLite schema.sql and FTS5 NEAR search ---")
    schema_path = REPO_ROOT / "packages" / "ap-ediscovery" / "src" / "ap_ediscovery" / "db" / "schema.sql"
    assert schema_path.exists(), f"schema.sql not found at {schema_path}"
    schema_sql = schema_path.read_text(encoding="utf-8")

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(schema_sql)

    # Insert Custodian
    conn.execute(
        "INSERT INTO custodians (name, email) VALUES (?, ?)",
        ("Custodian John Doe", "jdoe@example-litigation.com"),
    )
    custodian = conn.execute("SELECT id FROM custodians WHERE name = ?", ("Custodian John Doe",)).fetchone()
    custodian_id = custodian["id"]

    # Insert Document containing "constructive notice" and "landlord" within 8 words
    body_content = (
        "In this matter, plaintiff contends that the tenant gave constructive notice "
        "of the hazardous premise defect directly to the landlord prior to the incident."
    )
    conn.execute(
        """
        INSERT INTO documents (doc_hash, family_hash, custodian_id, file_name, title, body)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            "b3_a87f9b8c001",
            "b3_fam_001",
            custodian_id,
            "demand_letter.txt",
            "Demand Letter re Hazardous Condition",
            body_content,
        ),
    )

    # Validate FTS5 NEAR query
    near_query = 'NEAR("constructive notice" "landlord", 8)'
    print(f"Executing FTS5 MATCH with: {near_query}")
    results = conn.execute(
        """
        SELECT fts.rowid, d.title, d.doc_hash, d.body
        FROM documents_fts fts
        JOIN documents d ON d.id = fts.rowid
        WHERE documents_fts MATCH ?
        """,
        (near_query,),
    ).fetchall()

    print(f"FTS5 Query returned {len(results)} matches.")
    assert len(results) == 1, f"Expected exactly 1 match for NEAR query, found {len(results)}"
    matched_doc = results[0]
    print(f"Matched Doc ID: {matched_doc['rowid']}, Title: '{matched_doc['title']}', Hash: '{matched_doc['doc_hash']}'")
    assert matched_doc["title"] == "Demand Letter re Hazardous Condition"
    assert "constructive notice" in matched_doc["body"]
    assert "landlord" in matched_doc["body"]
    print("[PASS] SQLite schema and FTS5 NEAR query PASSED.")

    print("\n--- [3/3] Testing O(1) Trigger-Updated Tag Counts ---")
    conn.execute("INSERT INTO tags (name, description) VALUES (?, ?)", ("Trial Exhibit", "Exhibits admitted at trial"))
    tag = conn.execute("SELECT id FROM tags WHERE name = ?", ("Trial Exhibit",)).fetchone()
    tag_id = tag["id"]

    initial_count = conn.execute("SELECT doc_count FROM tag_counts WHERE tag_id = ?", (tag_id,)).fetchone()["doc_count"]
    print(f"Initial tag count for tag_id={tag_id}: {initial_count}")
    assert initial_count == 0, f"Expected 0, got {initial_count}"

    # Tag the document
    conn.execute("INSERT INTO document_tags (document_id, tag_id) VALUES (?, ?)", (matched_doc["rowid"], tag_id))
    tagged_count = conn.execute("SELECT doc_count, count FROM tag_counts WHERE tag_id = ?", (tag_id,)).fetchone()
    print(f"Tag count after tagging document: {tagged_count['doc_count']} (alias count: {tagged_count['count']})")
    assert tagged_count["doc_count"] == 1
    assert tagged_count["count"] == 1

    # Untag the document
    conn.execute("DELETE FROM document_tags WHERE document_id = ? AND tag_id = ?", (matched_doc["rowid"], tag_id))
    untagged_count = conn.execute("SELECT doc_count FROM tag_counts WHERE tag_id = ?", (tag_id,)).fetchone()["doc_count"]
    print(f"Tag count after untagging document: {untagged_count}")
    assert untagged_count == 0

    conn.close()
    print("[PASS] O(1) trigger-updated tag counts PASSED.")


def main() -> int:
    print("================================================================")
    print("AP-Suite Monorepo Core & Engine Foundations Smoke Test")
    print("================================================================")
    try:
        test_baseline_y()
        test_sqlite_schema_and_fts_near()
        print("\n================================================================")
        print("ALL MONOREPO SMOKE TESTS PASSED SUCCESSFULLY!")
        print("================================================================")
        return 0
    except AssertionError as e:
        print(f"\n[FAIL] Assertion failed: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
