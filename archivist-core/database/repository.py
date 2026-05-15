import sqlite3
import json
import os
from typing import List, Optional
from datetime import datetime

from core.models import Collection, Note, NoteAttachment

class DatabaseRepository:
    """
    Handles all persistent storage transactions for Archivist Core.
    Optimized for bulk streaming SQLite ingest operations.
    """

    def __init__(self, db_path: str, schema_path: Optional[str] = None):
        self.db_path = db_path
        # Resolve default schema path relative to database directory
        if not schema_path:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            schema_path = os.path.join(base_dir, "schema.sql")
            
        self._init_db(schema_path)

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        # Enable WAL mode for faster write throughput
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        # Enable Foreign Key constraints
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_db(self, schema_path: str):
        """Executes standard schema definitions if the tables don't exist."""
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found at: {schema_path}")
            
        with open(schema_path, 'r', encoding='utf-8') as f:
            ddl = f.read()

        conn = self._get_connection()
        try:
            conn.executescript(ddl)
            conn.commit()
        finally:
            conn.close()

    def _format_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        if dt is None:
            return None
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def save_collection(self, collection: Collection):
        """Inserts or updates a parent Notebook/Collection record."""
        query = """
        INSERT INTO universal_collections (id, name, provider_group, provider, created_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            provider_group=excluded.provider_group
        """
        
        created_at = self._format_datetime(collection.created_at) or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        conn = self._get_connection()
        try:
            conn.execute(query, (
                collection.id,
                collection.name,
                collection.provider_group,
                collection.provider,
                created_at
            ))
            conn.commit()
        finally:
            conn.close()

    def save_notes_batch(self, notes: List[Note]):
        """
        Executes high-speed ACID transaction saving multiple notes and attachments.
        Prevents memory sprawl by committing groups of records sequentially.
        """
        if not notes:
            return

        note_query = """
        INSERT INTO universal_notes (
            id, source_id, collection_id, provider, title, content_raw, 
            content_markdown, source_url, author, original_created_at, 
            original_updated_at, tags, triage_status, is_distilled
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            title=excluded.title,
            content_raw=excluded.content_raw,
            original_updated_at=excluded.original_updated_at
        """

        attach_query = """
        INSERT INTO universal_attachments (
            id, note_id, source_resource_id, filename, mime_type, 
            file_size_bytes, width_px, height_px, system_file_path, 
            ai_classification, ai_confidence, user_approval_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            note_tuples = []
            attachment_tuples = []

            for n in notes:
                note_tuples.append((
                    n.id,
                    n.source_id,
                    n.collection_id,
                    n.provider,
                    n.title,
                    n.content_raw,
                    n.content_markdown,
                    n.source_url,
                    n.author,
                    self._format_datetime(n.original_created_at),
                    self._format_datetime(n.original_updated_at),
                    json.dumps(n.tags),
                    n.triage_status,
                    1 if n.is_distilled else 0
                ))

                # Collect attachments belonging to this note
                for a in n.attachments:
                    attachment_tuples.append((
                        a.id,
                        n.id, # Direct foreign key
                        a.source_resource_id,
                        a.filename,
                        a.mime_type,
                        a.file_size_bytes,
                        a.width_px,
                        a.height_px,
                        a.system_file_path,
                        a.ai_classification,
                        a.ai_confidence,
                        a.user_approval_status
                    ))

            # Bulk Write Notes
            cursor.executemany(note_query, note_tuples)
            
            # Bulk Write Attachments
            if attachment_tuples:
                cursor.executemany(attach_query, attachment_tuples)

            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_collection_stats(self, collection_id: str) -> dict:
        """Returns performance diagnostic telemetry for a processed collection."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            # 1. Count Notes
            cursor.execute("SELECT COUNT(*) FROM universal_notes WHERE collection_id=?", (collection_id,))
            note_count = cursor.fetchone()[0]

            # 2. Count Attachments
            cursor.execute("""
                SELECT COUNT(*), SUM(file_size_bytes) 
                FROM universal_attachments a 
                JOIN universal_notes n ON a.note_id = n.id
                WHERE n.collection_id=?
            """, (collection_id,))
            attach_data = cursor.fetchone()
            attach_count = attach_data[0] or 0
            total_size_bytes = attach_data[1] or 0

            return {
                "notes_total": note_count,
                "attachments_total": attach_count,
                "attachments_size_mb": round(total_size_bytes / (1024 * 1024), 2)
            }
        finally:
            conn.close()
