---
id: qt_engine_boundary_notes
title: Engine Boundary Notes
type: ops-audit
---

# Engine / UI Boundary Notes

## Review Goals
Confirm that business logic, document transformations, and strict validation remain inside the `core/` package and have not bled into the `apmultitool_qt/` views.

## Component Boundaries
### 1. PDF Compiler (`compiler.py`)
- **UI Responsibility:** Grabs drag-and-drop paths, builds visual list, verifies user order, creates `MergeParams`.
- **Engine Responsibility:** The `core/operations/merge_pdfs.py` does all raw PyPDF2 stream concatenation, bookmark resolution, scale formatting, and compression.
- **Status:** Clean boundary. The UI does not manipulate raw bytes.

### 2. Bates Stamping (`bates.py`)
- **UI Responsibility:** Reads user font dropdowns, start numbers, outputs an Advanced Options spec dictionary. Auto-increments ledger based on UI state.
- **Engine Responsibility:** The `core/operations/bates_stamp.py` uses `reportlab` canvas layers and merges them onto existing PDF dimensions, handling collision shrinkage dynamically.
- **Status:** Minor drift identified. The UI maintains a `bates_registry` dictionary memory mapping Matter IDs to current start indexes. If this moves to the web, this ledger must migrate to a persistent database (SQLite). For the desktop context, it is acceptable transient state.

### 3. File Room (`fileroom.py`)
- **UI Responsibility:** Manages string manipulation to replace `{Date}` tokens in blueprint lists and visualizes it in `QTreeWidget`.
- **Engine Responsibility:** Safely calls `os.makedirs` over the parsed tree array and handles OS-level permissions errors.
- **Status:** Clean boundary. The engine just receives an array of absolute paths to build.

## Overall Verdict
The "Engine-First" STAX Guardrail is strictly honored. UI controllers only manage widgets, parameter collection, and thread orchestration.

## Browser-Readiness Data Contracts (Task 9 Check)
The core engine interacts exclusively via standard dataclasses located in `core/job.py`. To facilitate a seamless transition to a web API, these data models are conceptually JSON-ready.

**Core Data Models:**
- `Job`: `operation` (string), `inputs` (list), `params` (dict), `output` (dict).
- `InputSpec`: Currently initialized via `from_path(Path)`. For the browser surface, this will simply accept a UUID referencing a cloud storage bucket object instead of a local path.
- `MergeParams`: Flat dictionary of settings (e.g., `preserve_bookmarks=True`). Trivially serializable.
- `OutputSpec`: Currently `directory` (Path) and `overwrite` (bool). For the web API, this will just require an expected filename, and the server will return a download URL.

**Adjustment Needed:** The only minor adjustment needed for the web backend will be abstracting `Path` objects in `InputSpec` and `OutputSpec` into generic `uri` strings so the engine can resolve AWS S3/GCP objects identically to local `C:\` drives. No core logic refactoring is required.
