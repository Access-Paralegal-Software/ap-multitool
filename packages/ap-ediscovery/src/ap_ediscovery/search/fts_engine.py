"""FTS5 search utilities and query helpers."""

from __future__ import annotations

import sqlite3
from typing import Any


def build_near_query(terms: list[str], max_distance: int = 8) -> str:
    """Build an FTS5 NEAR query clause.

    Example:
        build_near_query(['"constructive notice"', '"landlord"'], 8)
        -> 'NEAR("constructive notice" "landlord", 8)'
    """
    joined_terms = " ".join(terms)
    return f"NEAR({joined_terms}, {max_distance})"


def search_documents(conn: sqlite3.Connection, match_query: str) -> list[sqlite3.Row]:
    """Execute FTS5 MATCH search on documents_fts and return matching rows."""
    cursor = conn.cursor()
    cursor.row_factory = sqlite3.Row
    return cursor.execute(
        """
        SELECT d.*
        FROM documents d
        JOIN documents_fts fts ON d.id = fts.rowid
        WHERE documents_fts MATCH ?
        ORDER BY rank
        """,
        (match_query,),
    ).fetchall()
