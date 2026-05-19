import os
import sys
import time
import argparse
import xml.etree.ElementTree as ET
import sqlite3
from typing import Set

from core.exporter import MarkdownExporter

def get_database_junk_ids(db_path: str) -> Set[str]:
    """Fetches list of attachment hashes/ids identified as junk from relational ledger."""
    if not os.path.exists(db_path):
        return set()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT source_resource_id FROM universal_attachments WHERE ai_classification = 'junk'")
        rows = cursor.fetchall()
        conn.close()
        # Return set of raw hashes
        return {r[0].lower() for r in rows if r[0]}
    except Exception:
        return set()

def execute_export(source_file: str, db_path: str, output_dir: str, sample_limit: int = None):
    """
    Main control loop for the Render & Export pipeline phase.
    """
    if not os.path.exists(source_file):
        raise FileNotFoundError(f"Source file not found: {source_file}")

    filename = os.path.basename(source_file)
    notebook_name, _ = os.path.splitext(filename)

    print("====================================================")
    print("   ARCHIVIST CORE: MARKDOWN RENDER & EXPORT")
    print("====================================================")
    print(f"Source File: {filename}")
    print(f"Output Root: {output_dir}")
    if sample_limit:
        print(f"Sample Mode: Limiting export to {sample_limit} notes")
    print("----------------------------------------------------")

    start_time = time.time()

    # 1. Query Relational Triage Data
    print("-> Fetching smart triage records from database...")
    junk_hashes = get_database_junk_ids(db_path)
    print(f"[OK] Loaded triage registry ({len(junk_hashes)} junk assets blacklisted).")

    # 2. Instantiate Exporter engine
    exporter = MarkdownExporter(output_dir, junk_ids=junk_hashes)

    # 3. Stream XML and Generate Bundles
    print("\n--- Commencing extraction and file compilation ---")
    
    context = ET.iterparse(source_file, events=('end',))
    notes_exported = 0

    try:
        for event, elem in context:
            if elem.tag == 'note':
                notes_exported += 1
                
                title = elem.findtext('title', 'Untitled Note')
                print(f"   -> Bundling Note #{notes_exported}: '{title[:40]}...'")
                
                exporter.export_note_bundle(elem, notebook_name)

                # Crucial for memory clearing
                elem.clear()

                # Check user sample limit threshold
                if sample_limit and notes_exported >= sample_limit:
                    print(f"\n[NOTICE] Hit requested sample limit of {sample_limit} notes.")
                    break
    except Exception as e:
        print(f"\n[CRITICAL EXPORT ERROR]: {e}")
        raise e

    elapsed = time.time() - start_time

    print("\n====================================================")
    print("RENDER & EXPORT COMPLETED!")
    print("====================================================")
    print(f"Execution Duration: {elapsed:.2f} seconds")
    print(f"Physical Bundles:   {notes_exported} directories created")
    print(f"Vault Structure:    {os.path.join(output_dir, notebook_name)}")
    print("[OK] Bundled outputs are now 100% Obsidian Native!")
    print("====================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Archivist Core Exporter Engine")
    parser.add_argument("source", help="Path to target Evernote .enex file")
    parser.add_argument("--db", default="", help="Path to SQLite vault containing triage data")
    parser.add_argument("--out", required=True, help="Root output folder for Obsidian bundle files")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of notes to extract")

    args = parser.parse_args()
    execute_export(args.source, args.db, args.out, args.limit)
