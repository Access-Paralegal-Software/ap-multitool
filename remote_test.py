
import sys
import os
sys.path.append(os.path.abspath("/home/aewoodyard/archivist-core"))

from core.models import Note, Collection
from adapters.evernote_parser import EvernoteAdapter

adapter = EvernoteAdapter()
source_file = "/home/aewoodyard/DataWarehouse/EvernoteRaw/Sewing.enex"
collection = adapter.parse_collection(source_file)

print("====================================================")
print("⚡ SUCCESS! EXECUTING LIVE XML PARSER ON SPARKY")
print("====================================================")
print(f"📦 Notebook: {collection.name} (Provider: {collection.provider})")

notes_count = 0
attachments_count = 0
samples = []

for note in adapter.parse_notes(source_file, collection):
    notes_count += 1
    attachments_count += len(note.attachments)
    if len(samples) < 3:
        samples.append(note)

print(f"🏆 Telemetry Results:")
print(f"   - Total Notes Processed: {notes_count}")
print(f"   - Total Attachments: {attachments_count}")
print("----------------------------------------------------")
for i, note in enumerate(samples, 1):
    print(f"👉 [SAMPLE #{i}]: {note.title}")
    print(f"   - Created: {note.original_created_at}")
    print(f"   - Tags: {', '.join(note.tags) if note.tags else 'None'}")
    print(f"   - Attachments: {len(note.attachments)}")
print("====================================================")
