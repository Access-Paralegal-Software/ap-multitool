---
id: windows-alpha-issue-deck-v1.0.0-alpha1
title: Windows Alpha Issue Deck (v1.0.0-alpha1)
type: operations
status: active
project: APMultitool
created_at: 2026-05-21T08:30:00Z
tags:
  - testing
  - triage
  - issue-deck
  - alpha-release
---

# 📋 APMultitool Windows Alpha Issue Deck (v1.0.0-alpha1)

This issue deck compiles, categorizes, and prioritizes feedback collected during guided alpha sessions on **2026-05-21** for Windows Alpha build `v1.0.0-alpha1`.

---

## 🔍 Executive Summary

A cohort of 3 testers (Brenda M., Ryan K., Sarah T.) executed core paralegal workflows (motion packet compilation, Bates stamping, and File Room structure creation) using the GUI and CLI.
* **Total Issues Identified:** 7
* **Severe Blockers:** 0 (core application remains stable and functional)
* **Major Issues:** 2 (requires correction before wider distribution)
* **Minor Issues:** 3 (polish to CLI and inputs)
* **Polish Items:** 2 (aesthetic or cosmetic improvements)

---

## 🎯 Prioritized Triage List

### A. Must-Fix-Before-Wider-Alpha (Blocker/Major)

#### 1. Encrypted/Protected PDF Crash in Document Compiler
* **Severity:** Major
* **Area:** Document Compiler (Backend Engine)
* **Tester & Bundle Link:** [tester_sarah_t Notes](file:///C:/Users/aewoo/Desktop/Repos/ap-multitool/alpha_feedback/2026-05-21/tester_sarah_t/notes.md) (Bundle: `apmultitool_support_bundle_20260521_082840.zip`)
* **Observed Behavior:** Merging a password-encrypted PDF throws `PyPDF2.errors.FileNotDecryptedException` in the background worker thread. The UI is frozen for a moment, then pops up a long technical thread crash traceback dialog.
* **Reproduction Steps:**
  1. Add an encrypted PDF to the compiler queue.
  2. Add any other normal PDF.
  3. Click "Merge documents".
* **Proposed Hypothesis:** The merge loop in `core/compiler.py` does not check `reader.is_encrypted` before attempting to access document pages.
* **Action Item:** Add a check for `.is_encrypted` on all loaded PDFs. Catch `FileNotDecryptedException` and surface a friendly warning dialog: *"The file '[filename]' is password-encrypted or restricted. Please remove protection before merging."*

#### 2. KeyError on Empty Case ID in Bates Registry Lookup
* **Severity:** Major
* **Area:** Bates Stamping (UI & Autoincrement Registry)
* **Tester & Bundle Link:** [tester_brenda_m Notes](file:///C:/Users/aewoo/Desktop/Repos/ap-multitool/alpha_feedback/2026-05-21/tester_brenda_m/notes.md) (Bundle: `apmultitool_support_bundle_20260521_082555.zip`)
* **Observed Behavior:** Tabbing out of the Bates "Prefix" input field while the "Case ID" field (in File Room tab) is blank causes a silent `KeyError` traceback in logs and prevents registry autoincrement from populating.
* **Reproduction Steps:**
  1. Open the app, do NOT enter a Case ID on the File Room tab.
  2. Navigate to the Bates Stamping tab.
  3. Change the Prefix value and tab out (triggering `editingFinished`).
* **Proposed Hypothesis:** In `apmultitool_qt/views/bates.py` line 351, `on_prefix_editing_finished` retrieves `matter_name` from `view_fileroom.txt_case_id.text()`. If this string is empty, it uses `Default_Matter` or tries to search keys but gets an unhandled key reference.
* **Action Item:** Add a guard clause. If the Case ID is empty, default safely without querying the dictionary or return early:
  ```python
  if not matter_name:
      return
  ```

---

### B. Nice-to-Have During Alpha (Minor)

#### 3. CLI support-bundle Directory Auto-creation
* **Severity:** Minor
* **Area:** CLI (Support Module)
* **Tester & Bundle Link:** [tester_ryan_k Notes](file:///C:/Users/aewoo/Desktop/Repos/ap-multitool/alpha_feedback/2026-05-21/tester_ryan_k/notes.md) (Bundle: `apmultitool_support_bundle_20260521_082812.zip`)
* **Observed Behavior:** Running the support bundle command with a non-existent output directory (e.g. `apmultitool support-bundle -o C:\nonexistent`) fails with a `FileNotFoundError` instead of creating the folder path.
* **Proposed Hypothesis:** `core/support.py` writes the ZIP archive directly using `open(..., 'wb')` without checking if the parent directory tree exists.
* **Action Item:** Update `create_support_bundle` to call `target_dir.mkdir(parents=True, exist_ok=True)` before creating the ZIP.

#### 4. File Room Illegal Windows Characters Silent Failures
* **Severity:** Minor
* **Area:** File Room (UI & Engine)
* **Tester & Bundle Link:** [tester_ryan_k Notes](file:///C:/Users/aewoo/Desktop/Repos/ap-multitool/alpha_feedback/2026-05-21/tester_ryan_k/notes.md) (Bundle: `apmultitool_support_bundle_20260521_082812.zip`)
* **Observed Behavior:** Adding folder names with characters like colons (`:`) or slashes causes the build to fail with a `WinError 123` OSError in logs, but the UI terminal console doesn't explain the cause to the user.
* **Proposed Hypothesis:** Folder tree generator raises an OS level exception when creating directories. The GUI catches it and halts, but log forwarding to the GUI console does not cleanly write the error message.
* **Action Item:** Add name validation before calling tree builder or handle `OSError` to print: *"Error: Cannot create directory '[name]'. It contains characters that are illegal on Windows filesystems."*

#### 5. Drag-and-Drop Queue Ordering Friction
* **Severity:** Minor
* **Area:** Document Compiler (UI UX)
* **Tester & Bundle Link:** [tester_brenda_m Notes](file:///C:/Users/aewoo/Desktop/Repos/ap-multitool/alpha_feedback/2026-05-21/tester_brenda_m/notes.md) (Bundle: `apmultitool_support_bundle_20260521_082555.zip`)
* **Observed Behavior:** Users struggle to drag and drop rows in the merge queue table, finding the dropping target area very narrow.
* **Action Item:** In `apmultitool_qt/views/compiler.py`, add explicit "Move Up" and "Move Down" buttons on the side of the table queue to provide a bulletproof keyboard-friendly and click-friendly fallback.

---

### C. Later / Beta-Level Improvements (Polish)

#### 6. Monospaced Font (Courier) Bates Layout Offset
* **Severity:** Polish
* **Area:** Bates Stamping (Graphics Layout)
* **Tester & Bundle Link:** [tester_sarah_t Notes](file:///C:/Users/aewoo/Desktop/Repos/ap-multitool/alpha_feedback/2026-05-21/tester_sarah_t/notes.md) (Bundle: `apmultitool_support_bundle_20260521_082840.zip`)
* **Observed Behavior:** Stamps made with monospaced "Courier" are slightly offset from page edges compared to variable-width fonts.
* **Action Item:** Adjust padding offsets in `core/bates.py` layout engine dynamically when font family is detected as monospaced.

#### 7. Telemetry Count Increments on Job Cancellation
* **Severity:** Polish
* **Area:** Telemetry (UI & Engine)
* **Tester & Bundle Link:** [tester_sarah_t Notes](file:///C:/Users/aewoo/Desktop/Repos/ap-multitool/alpha_feedback/2026-05-21/tester_sarah_t/notes.md) (Bundle: `apmultitool_support_bundle_20260521_082840.zip`)
* **Observed Behavior:** If a user stamps 50 pages of a 100-page document and cancels the process, the "Pages Stamped" telemetry registers 0 because the job transaction did not complete successfully.
* **Action Item:** Track progress increments dynamically rather than updating telemetry only at the terminal success block of a job worker.
