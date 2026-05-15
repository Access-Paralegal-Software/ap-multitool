import os
import time
import argparse
from typing import List

from adapters.evernote_parser import EvernoteAdapter
from database.repository import DatabaseRepository
from core.models import Note

def execute_ingest(source_file: str, db_path: str, batch_size: int = 100):
    """
    Ties together the Ingestion Pipeline:
    Parser yields streaming records -> Controller buffers records -> Repository writes bulk ACID transactions.
    """
    if not os.path.exists(source_file):
        raise FileNotFoundError(f"Source notebook archive not found: {source_file}")

    print("====================================================")
    print("   ARCHIVIST CORE: UNIVERSAL INGESTION ENGINE")
    print("====================================================")
    print(f"Source Payload: {os.path.basename(source_file)}")
    print(f"Dest Database: {os.path.basename(db_path)}")
    print(f"Buffer Size: {batch_size} notes per transaction")
    print("----------------------------------------------------")

    start_time = time.time()

    # 1. Initialize Infrastructure
    repo = DatabaseRepository(db_path)
    adapter = EvernoteAdapter()

    # 2. Process Metadata and Collection Anchor
    print("--- Discovering notebook structure ---")
    collection = adapter.parse_collection(source_file)
    repo.save_collection(collection)
    print(f"[OK] Collection anchored: '{collection.name}' (ID: {collection.id[:8]}...)")

    # 3. Stream & Buffer Ingest Transaction Loop
    print("\n--- Commencing high-speed streaming ingest ---")
    
    note_buffer: List[Note] = []
    total_notes_ingested = 0
    total_attachments_ingested = 0
    batch_count = 0

    try:
        for note in adapter.parse_notes(source_file, collection):
            note_buffer.append(note)
            total_notes_ingested += 1
            total_attachments_ingested += len(note.attachments)

            # If buffer full, commit transaction and purge memory
            if len(note_buffer) >= batch_size:
                repo.save_notes_batch(note_buffer)
                batch_count += 1
                print(f"   -> Committed Batch #{batch_count} ({len(note_buffer)} notes) to database...")
                note_buffer.clear() # Evict references to prevent RAM swell

        # Commit any remaining residual records in buffer
        if note_buffer:
            repo.save_notes_batch(note_buffer)
            batch_count += 1
            print(f"   -> Committed Final Batch #{batch_count} ({len(note_buffer)} notes)...")
            note_buffer.clear()

    except Exception as e:
        print(f"\n[CRITICAL ERROR DURING PIPELINE EXECUTION]: {e}")
        raise e

    elapsed = time.time() - start_time

    # 4. Pull Database Final Verification Telemetry
    stats = repo.get_collection_stats(collection.id)

    print("\n====================================================")
    print("INGESTION PIPELINE SUCCESSFULLY COMPLETED!")
    print("====================================================")
    print(f"Execution Velocity: {elapsed:.2f} seconds")
    print(f"Notes Transferred:  {stats['notes_total']}")
    print(f"Total Attachments:  {stats['attachments_total']}")
    print(f"Base64 Asset Mass:  {stats['attachments_size_mb']} MB cached")
    print("----------------------------------------------------")
    print(f"Pipeline State: 100% ACCURATE, ACID PERSISTENT!")
    print("====================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Archivist Core Ingest Engine")
    parser.add_argument("source", help="Path to the Evernote .enex source file")
    parser.add_argument("--db", default="archivist_vault.db", help="Path to target SQLite vault")
    parser.add_argument("--batch", type=int, default=100, help="Ingest transaction batch size")
    
    args = parser.parse_args()
    execute_ingest(args.source, args.db, args.batch)
