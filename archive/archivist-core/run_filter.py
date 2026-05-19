import os
import sys
import time
import argparse
import sqlite3

from core.filters import AttachmentFilterEngine
from core.models import NoteAttachment
from database.repository import DatabaseRepository

def execute_filter_triage(db_path: str):
    """
    Loads all attachments from the target database, runs them through the 
    Filter Heuristics, and commits the classification tags back to SQLite.
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Target vault database not found: {db_path}")

    print("====================================================")
    print("   ARCHIVIST CORE: AI & HEURISTIC TRIAGE ENGINE")
    print("====================================================")
    print(f"Target Database: {os.path.basename(db_path)}")
    print("----------------------------------------------------")

    start_time = time.time()

    engine = AttachmentFilterEngine()

    # Connect directly to SQLite for fast triage querying
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    cursor = conn.cursor()

    # 1. Fetch all attachments currently waiting for triage
    print("-> Pulling attachment inventory from relational registry...")
    cursor.execute("""
        SELECT id, filename, mime_type, file_size_bytes, width_px, height_px, ai_classification 
        FROM universal_attachments
    """)
    rows = cursor.fetchall()
    total_found = len(rows)
    print(f"[OK] Discovered {total_found} attachments stored in database.")

    # 2. Process heuristics and compile updates
    print("\n--- Commencing deterministic filtration ruleset ---")
    
    update_tuples = []
    stats = {
        "junk": {"count": 0, "bytes": 0},
        "valuable": {"count": 0, "bytes": 0},
        "untested": {"count": 0, "bytes": 0}
    }

    for r in rows:
        att_id, filename, mime_type, size_bytes, w, h, current_class = r
        
        # Construct temporary entity for the engine to process
        temp_entity = NoteAttachment(
            id=att_id,
            filename=filename or "unnamed",
            mime_type=mime_type or "application/octet-stream",
            file_size_bytes=size_bytes or 0,
            width_px=w,
            height_px=h
        )
        
        # Classify!
        classification, confidence = engine.classify(temp_entity)
        
        # Aggregate Stats
        stats[classification]["count"] += 1
        stats[classification]["bytes"] += (size_bytes or 0)
        
        # Queue up for bulk SQL update (only if classification changed/set)
        update_tuples.append((classification, confidence, att_id))

    # 3. Bulk Commit Classifications back to Database
    print("-> Writing transactional classification updates back to SQLite...")
    update_query = """
        UPDATE universal_attachments 
        SET ai_classification = ?, ai_confidence = ?
        WHERE id = ?
    """
    try:
        cursor.executemany(update_query, update_tuples)
        conn.commit()
        print("[SUCCESS] Relational ledger updated securely!")
    except Exception as e:
        conn.rollback()
        print(f"[CRITICAL ERROR] Database update failed: {e}")
        raise e
    finally:
        conn.close()

    elapsed = time.time() - start_time

    # Calculate Storage Recovery (Base64 length to approximate binary size recovery)
    junk_mb = round(stats["junk"]["bytes"] / (1024 * 1024), 2)
    valuable_mb = round(stats["valuable"]["bytes"] / (1024 * 1024), 2)

    print("\n====================================================")
    print("TRIAGE FILTRATION COMPLETED!")
    print("====================================================")
    print(f"Execution Velocity: {elapsed:.2f} seconds")
    print("----------------------------------------------------")
    print("AUTO-CLASSIFICATION REPORT:")
    print(f"   - JUNK FLAG (Logos/Spacers): {stats['junk']['count']} files")
    print(f"   - VALUABLE (Photos/Docs):   {stats['valuable']['count']} files")
    print(f"   - UNTESTED (Borderline):    {stats['untested']['count']} files")
    print("----------------------------------------------------")
    print("POTENTIAL RESOURCE OPTIMIZATION:")
    print(f"   -> Garbage Asset Load: {junk_mb} MB base64 footprint")
    print(f"   -> Valuable Asset Load: {valuable_mb} MB preserved")
    print(f"[OK] Pre-Filter successfully pruned {round((stats['junk']['count'] / total_found) * 100, 1)}% of total attachments!")
    print("====================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Archivist Core Filtration Engine")
    parser.add_argument("db", help="Path to the SQLite database vault")
    
    args = parser.parse_args()
    execute_filter_triage(args.db)
