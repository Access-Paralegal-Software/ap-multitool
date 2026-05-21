---
id: windows_alpha_hero_flows
title: Windows Alpha Hero Flows
type: ops
status: active
project: APMultitool
created_at: 2026-05-21
tags:
  - alpha
  - ux
  - windows
---

# Windows Alpha Hero Flows

Documented as part of the ho_0045 flow-polish lane. These are the three most
important user-facing workflows in the v1.0.0-alpha1 build. Each was walked
through at least twice during dogfooding, with friction points noted.

---

## Flow 1 — Compile a Document Packet (Document Compiler tab)

**Entry point:** Application opens on the Document Compiler tab by default.

**Typical steps:**

1. Add files to the queue via "Add Files" (file picker) or drag-and-drop.
   - Alternatively, use "Add Folder" to pull all supported documents from a directory.
2. Reorder documents using "Move Up ⬆" / "Move Down ⬇" if needed.
3. Optionally adjust compiler settings in the left panel:
   - Table of Contents bookmarks (on by default)
   - Enforce standard page fit / Letter size (on by default)
   - Compress output streams
   - Grayscale output
4. Set the output PDF filename in "Output PDF Name:".
5. Set or confirm the output folder via "Output Folder: / Browse".
6. Click **Compile Documents**.
   - If a file by that name already exists, a single confirmation dialog asks to overwrite.
   - The run button changes to "Cancel" during execution.
7. Each queue row updates its Status column to "Processing…" then "✅ Combined".
8. On success: "Documents compiled successfully!" dialog. Queue rows all show ✅.

**Expected success state:** A single merged PDF appears in the output folder.

**Friction points identified (pre-polish):**
- A "Confirm Merge Order" dialog fired on every run, even without a conflict.
  This was purely friction — removed in ho_0045.
- Button label "Combine & Merge Files" was verbose and inconsistent with the
  "Compilation" language used everywhere else. Changed to "Compile Documents".

---

## Flow 2 — Apply Bates Numbers (Bates Stamping tab)

**Entry point:** Click "🔢 Bates Stamping" in the sidebar.

**Typical steps:**

1. Click "..." (Browse) next to "Target PDF:" and select the source PDF.
2. Enter the Bates prefix (e.g., "AP" or the matter identifier).
3. Confirm the starting index (defaults to 1, or the last-used value for that
   prefix/matter pair if the Bates registry has a prior run).
4. Select the separator style from the "Separator:" dropdown.
5. Optionally click **Stamp Options...** to configure font, size, placement,
   page margin collision, naming style, and output folder policy.
6. Click **Apply Bates Numbers**.
   - The Bates Stamp Log panel on the right shows live progress messages.
   - A progress bar appears in the status bar.
   - The run button changes to "Cancel" during execution.
7. On success:
   - The log shows the output filename and page count.
   - The "Start Index:" field auto-advances to the next available number.
   - A success dialog shows file name and page count.
   - Windows Explorer opens to the output folder automatically.

**Expected success state:** A Bates-numbered copy of the PDF is in the output
folder (default: a dated subfolder named `AP-Bates-YYYY-MM-DD` next to the source).

**Friction points identified (pre-polish):**
- "⚡ FLATTEN & APPLY BATES STAMPS" — "FLATTEN" is a PDF technical term
  unfamiliar to non-technical users; all-caps is aggressive. Changed to
  "Apply Bates Numbers".
- "SYSTEM TERMINAL READY. WAITING FOR OPERATION PARAMETERS…" — the console
  initial text read like a 1980s terminal. Changed to plain-English guidance.
- " ADVANCED STAMP OPTIONS" (all-caps) changed to "Stamp Options..." (sentence
  case, clearer affordance).
- "BATES OUTPUT TERMINAL" header changed to "BATES STAMP LOG".
- "✅ SAVE PROTOCOL" in the options dialog changed to "Save Settings".
- "Naming Protocol:" label changed to "Output Naming Style:".
- Clearing the console log required a "Are you sure?" confirmation dialog —
  unnecessary friction for a non-destructive action. Removed.
- Stability: `on_bates_finished` accessed `result.outputs[0]` without guarding
  against None or empty outputs. Fixed with explicit guard + fallback warning.

---

## Flow 3 — Create a Matter Folder Structure (File Room tab)

**Entry point:** Click "🏛️ File Room & Trees" in the sidebar.

**Typical steps:**

1. Enter the Matter ID in "Matter ID Reference:" (e.g., "2026-AP-9908").
   - The folder structure preview on the right updates live.
2. Select a blueprint from the "Structure Blueprint:" dropdown.
   - "⭐ Custom User Blueprint" (default) enables the Blueprint Architect section.
   - Pre-built blueprints ("Standard Civil Litigation", "Trial Notebook Model",
     "Solo / Freelance Core") disable editing.
3. For Custom User Blueprint: optionally add/remove folders using the Architect
   tools in the left panel. The preview tree reflects changes instantly.
4. Click **Create Folder Structure**.
5. A folder picker opens to select the parent destination directory.
6. If the destination contains existing files, a confirmation dialog warns before
   proceeding.
7. On success: a dialog shows the count of folders created, and Windows Explorer
   opens to the parent folder.

**Expected success state:** The chosen destination contains a full nested folder
structure matching the blueprint, with the Matter ID as the root folder name.

**Friction points identified (pre-polish):**
- "Spin Up Folder Tree" — developer jargon ("spin up") with no user-facing
  meaning. Changed to "Create Folder Structure".
- "FOLDER TREE ARCHITECTURE PREVIEW" header verbose. Changed to
  "FOLDER STRUCTURE PREVIEW".
- Success message "Instantiated {n} customized subfolders" used technical
  language. Changed to "Folder structure created successfully! {n} folders created."
- Error message "Could not build directory architectures" changed to
  "Could not create folder structure".
- Stability: `result.outputs[0]` in `on_fileroom_finished` was unguarded.
  Fixed with a None/empty guard before access.
