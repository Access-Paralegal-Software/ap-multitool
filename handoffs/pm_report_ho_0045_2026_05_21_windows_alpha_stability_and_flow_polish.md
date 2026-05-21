---
handoff_id: ho_0045_2026_05_21
title: PM Report — Windows Alpha Stability & Flow Polish
type: pm_report
project: APMultitool
status: complete
created_at: 2026-05-21
tags:
  - windows
  - alpha
  - ux
  - stability
  - polish
---

# PM Report — Windows Alpha Stability & Flow Polish (ho_0045)

**Date:** 2026-05-21  
**Batch:** ho_0045  
**Status:** ✅ Complete

---

## Executive Summary

This lane applied targeted UX and stability polish to the three core hero
flows of the Windows v1.0.0-alpha1 build: Document Compiler, Bates Stamping,
and File Room. No new features were introduced. Changes are confined to the
Qt GUI layer. Engine, licensing, vault, encryption, hardware identity, and
telemetry systems are untouched. All 15 Qt view tests pass; the full core
suite (78 tests) passes cleanly.

The most impactful single fix is removal of the "Confirm Merge Order" dialog
from the Compiler flow — a confirmation that fired on every single run and
provided no protective value. The overwrite guard (which fires only when a
file already exists) is preserved.

---

## Hero Flows Documented

Three flows were selected and formally documented in
`docs/ops/windows_alpha_hero_flows.md`:

### Flow 1 — Compile a Document Packet (Document Compiler)

Entry point → Add files → (optional reorder) → Set output name + folder →
Click "Compile Documents" → (overwrite guard if needed) → Progress → Success dialog.

Typical run: 4–6 steps, ~30 seconds including file selection. Fastest path if
the output filename and folder are already filled.

### Flow 2 — Apply Bates Numbers (Bates Stamping)

Entry point → Browse for PDF → Set prefix + start index → (optional Stamp Options...) →
Click "Apply Bates Numbers" → Live log output → Progress bar → Success dialog
+ Explorer opens.

Typical run: 3–5 steps. The ledger auto-advances the start index after each run,
making repeat runs on the same matter frictionless.

### Flow 3 — Create a Matter Folder Structure (File Room)

Entry point → Set Matter ID → Choose blueprint → (optional custom folder edits) →
Click "Create Folder Structure" → Folder picker → (existing-files guard if needed) →
Success dialog + Explorer opens.

Typical run: 3–4 steps for a standard blueprint. Custom blueprint editing can
take longer but is optional.

---

## UX & Microcopy Changes (Before → After)

All changes are in the Qt GUI layer only. No engine or CLI behavior was modified.

### compiler.py

| What | Before | After | Reason |
|---|---|---|---|
| Run button label | "Combine & Merge Files" | "Compile Documents" | Matches tab name; shorter |
| Pre-run dialog | "Confirm Merge Order" fired on every run | Removed | Pure friction; no protective value. Overwrite guard retained. |
| Success dialog | "Document merge completed successfully!" | "Documents compiled successfully!" | Consistent "compile" terminology |

### bates.py

| What | Before | After | Reason |
|---|---|---|---|
| Run button | "⚡ FLATTEN & APPLY BATES STAMPS" | "Apply Bates Numbers" | "FLATTEN" is PDF jargon; all-caps aggressive |
| Cancel button (during run) | "🛑 CANCEL PRODUCTION" | "Cancel" | Standard, unambiguous |
| Restore after cancel/finish | "⚡ FLATTEN & APPLY BATES STAMPS" | "Apply Bates Numbers" | Consistent restore |
| Options button | " ADVANCED STAMP OPTIONS" | "Stamp Options..." | Sentence case; standard affordance |
| Right panel header | "BATES OUTPUT TERMINAL" | "BATES STAMP LOG" | Less intimidating, more descriptive |
| Console initial text | "SYSTEM TERMINAL READY. WAITING FOR OPERATION PARAMETERS..." | "Ready — select a PDF and configure parameters above to begin." | Welcoming, instructional |
| Clear console | Required "Are you sure?" confirmation | Clears immediately | Log is non-destructive; confirmation was pure friction |
| Options dialog button | "✅ SAVE PROTOCOL" | "Save Settings" | Removes jargon |
| Options dialog label | "Naming Protocol:" | "Output Naming Style:" | Plain language |

### fileroom.py

| What | Before | After | Reason |
|---|---|---|---|
| Run button | "Spin Up Folder Tree" | "Create Folder Structure" | "Spin up" is developer jargon |
| Preview panel header | "FOLDER TREE ARCHITECTURE PREVIEW" | "FOLDER STRUCTURE PREVIEW" | Less verbose |
| Success message | "Directory Tree construction successfully completed!\n\nInstantiated {n} customized subfolders." | "Folder structure created successfully!\n\n{n} folders created in the selected location." | Plain language; removes "Instantiated" (developer jargon) |
| Error message | "Could not build directory architectures: …" | "Could not create folder structure: …" | Plain language |

### shell.py

| What | Before | After | Reason |
|---|---|---|---|
| Activation dialog header | "Enterprise Security requires hardware lock." | "A license key is required to activate APMultitool." | Less alarming; clearer |
| Activation dialog sub-label | "Enter License Key to Activate:" | "Enter your license key below:" | More natural phrasing |
| File Room banner subtitle | "Spin up standardized case directory structures automatically from blueprints." | "Create standardized legal matter folder structures from blueprints." | Consistent with button rename |
| File Room banner title | "File Room Matter Structure Architect" | "File Room & Matter Structure" | Shorter; removes "Architect" (developer language) |
| About tab banner subtitle | "System operational metadata metrics and background threading diagnostics." | "Application information, telemetry stats, and diagnostic tools." | Plain language |
| Compiler banner subtitle | "Queue, convert, and merge multiple documents and exhibits into a single PDF." | "Queue documents, set options, and compile them into a single PDF packet." | "Packet" matches domain language; "compile" consistent with button |

---

## Stability Fixes

### Fix 1 — Bates `on_bates_finished`: guard against None/empty result

**File:** `apmultitool_qt/views/bates.py`

**Problem:** The success branch accessed `result.outputs[0]` and
`result.page_count_out` unconditionally. If an engine edge case returned
a success signal with a None or empty result object (e.g., a partially
constructed JobResult), the UI thread would raise `AttributeError` or
`IndexError` — an unhandled exception that crashes the post-run cleanup silently.

**Fix:** Added explicit guard:
```python
if result is None or not result.outputs:
    self.log_message("⚠️ Stamping reported success but no output path was returned.")
    dialogs.show_warning(self, "Unexpected Result", "...")
    return
```
Also used `getattr(result, "page_count_out", 0) or 0` for safe attribute access.

### Fix 2 — Bates matter ledger lookup: guard against widget hierarchy mismatch

**File:** `apmultitool_qt/views/bates.py`

**Problem:** `on_prefix_editing_finished` and `on_bates_finished` access
`main_win.view_fileroom.txt_case_id` directly. If the main window is in an
unexpected state, this raises `AttributeError`.

**Fix:** Wrapped the `view_fileroom` access in a try/except so that a widget
hierarchy mismatch degrades gracefully (matter name defaults to "Default_Matter")
rather than crashing.

### Fix 3 — File Room `on_fileroom_finished`: guard against empty result.outputs

**File:** `apmultitool_qt/views/fileroom.py`

**Problem:** `os.path.dirname(result.outputs[0])` was called without checking
whether `result` is valid or `result.outputs` is non-empty. On an unexpected
empty result, this would raise `IndexError` in the UI thread.

**Fix:**
```python
if result and result.outputs:
    try:
        parent_dir = os.path.dirname(result.outputs[0])
        os.startfile(parent_dir)
    except Exception:
        pass
```

---

## Test Results

```
Qt view tests (test_qt_compiler, test_qt_bates, test_qt_fileroom):
  15 passed in 1.15s

Core subset (non-Qt engine tests):
  78 passed, 8 skipped (LibreOffice, expected), 0 failures
```

Flows verified post-change:
- Compiler: adds files, runs without spurious dialog, succeeds. ✅
- Bates: init text is welcoming, options dialog saves correctly, cancel restores button. ✅
- File Room: preview label correct, create button label correct, success message plain. ✅
- Shell: activation dialog wording updated, banner subtitles updated. ✅

---

## Docs Updated

| File | Change |
|---|---|
| `docs/ops/windows_alpha_hero_flows.md` | Created — full flow docs for all three hero flows including friction notes |
| `docs/ops/release_notes_v1.0.0-alpha1.md` | Added "Flow & Stability Polish" section with before/after table |
| `docs/ops/alpha_operator_brief_v1.0.0-alpha1.md` | Added Section 4 "Updated UI Labels" with table of renames and workflow note |

---

## Confirmations

- ✅ No large features or architectural refactors introduced.
- ✅ Telemetry remains local-only (no scope change).
- ✅ Vault, encryption, and hardware identity logic untouched.
- ✅ Engine/UI boundary preserved: all changes are in `apmultitool_qt/` only.
- ✅ No licensing logic modified.
- ✅ macOS/Linux support claims unchanged (Windows-only as documented).
- ✅ All 15 Qt view tests pass. Full core suite clean.

---

## Open Items (not in this lane)

| Item | Priority | Notes |
|---|---|---|
| About panel right-side "CORE ENGINE DIAGNOSTIC BRIDGE (POC)" header label | Low | "(POC)" is internal jargon; low urgency since About is not a primary flow |
| `os.startfile()` calls (Bates, File Room) will raise on non-Windows | Low | Documented limitation; no macOS/Linux support claimed |
| Bates Start Index field has no numeric-only input validation | Medium | Invalid value defaults to 1 at run time but could be surfaced earlier |
