"""Database schema and connection management for AP-eDiscovery."""

from pathlib import Path

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_schema_sql() -> str:
    """Return the raw SQL schema string."""
    return SCHEMA_PATH.read_text(encoding="utf-8")
