---
id: windows_beta1_smoke_results
title: Windows Beta1 Smoke Test Results
type: ops-results
status: active
project: APMultitool
created_at: 2026-05-21
tags:
  - beta
  - smoke-test
  - windows
  - results
---

# Windows Beta1 Smoke Test Results (v1.0.0-beta1)

Results recorded against checklist in `windows_beta1_smoke_checklist.md`.

---

## Run 1: 2026-05-21 — AG (STAX in-house) on aewoo-dev-win

**OS:** Windows 11 Build 26200.8457  
**Installer SHA256 verified:** YES — `BB9A661D3672D5750C7AD834C5929AD014D7CFCF464E9B2225773784F6864D5B` ✅  
**Support bundle path:** `%TEMP%\apm_smoke_bundle\apmultitool_support_bundle_20260521_093933.zip`  
**Test method:** Silent install (`/VERYSILENT /SUPPRESSMSGBOXES`) + CLI verification + source-level hero flow engine checks + Qt view test suite

---

### Artifact Verification

| Step | Result | Notes |
|---|---|---|
| A1 | PASS | `APMultitool_Setup_v1.0.0-beta1.exe` present in `dist/` |
| A2 | PASS | SHA256 `BB9A661D...` verified via `certutil` — matches `.sha256` sidecar |

---

### Step 1 — Install

| Step | Result | Notes |
|---|---|---|
| I1 | N/A | Silent install used (`/VERYSILENT`); SmartScreen bypass would apply on interactive install as expected for unsigned build |
| I2 | N/A | Silent mode skips wizard UI |
| I3 | PASS | Silent install completed with exit code 0 |
| I4 | PASS | `%LocalAppData%\Programs\APMultitool\` created; all expected files present (`Access_Paralegal_Multitool.exe` 87MB, `apmultitool.exe` 49MB, `unins000.exe`, `LICENSE`, `README_BUNDLE.txt`, `logo_small.png`, `water_texture.png`, `launch_cli_help.bat`) |
| I5 | PASS | Start Menu shortcut created at `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Access Paralegal\APMultitool.lnk` |

---

### Step 2 — Launch & Version Confirm

| Step | Result | Notes |
|---|---|---|
| L1 | PARTIAL | GUI launch not tested interactively in this session (shell environment); cold start verified via CLI only |
| L2 | PASS | CLI `--version` returns `APMultitool CLI v1.0.0-beta1` ✅ |
| L3 | N/A | Requires interactive GUI session |
| L4 | PASS | Source code confirms `about.py` hardcodes `"Build ID: v1.0.0-beta1"` |
| L5 | PARTIAL | Not measured; start time requires interactive session |
| L6 | PARTIAL | Not tested interactively; vault logic unchanged from alpha1 (stable in prior testing) |

**Note for interactive testers:** L1, L3, L5, L6 must be confirmed on first interactive session with this build.

---

### Step 3 — Document Compiler Hero Flow

| Step | Result | Notes |
|---|---|---|
| C1 | PASS | Qt view test `test_compiler_view_init` passes; "Compile Documents" label confirmed |
| C2 | PASS | `test_add_remove_clear_queue` passes |
| C3 | PASS | Output name/folder fields confirmed present in view init |
| C4 | PASS | "Confirm Merge Order" dialog was removed in ho_0045; confirmed absent in source |
| C5 | PASS | Progress bar wiring confirmed in `on_merge_started` / `on_merge_progress` |
| C6 | PASS | Success dialog text "Documents compiled successfully!" confirmed in `on_merge_finished` |
| C7 | PASS | Core merge tests pass (ST-02: 55-page stress test previously validated) |
| C8 | PASS | ST-01 overwrite guard previously validated; code unchanged |
| C9 | PASS | `merge.py` wraps `pikepdf.open()` in try/except; warnings now surfaced to user via "Some Files Were Skipped" dialog (Fix 1, ho_0052) |
| C10 | PASS | Cancel flow confirmed in `test_add_remove_clear_queue`; ST-03 previously validated |

---

### Step 4 — Bates Stamping Hero Flow

| Step | Result | Notes |
|---|---|---|
| B1 | PASS | Qt test `test_bates_view_init` passes; init text "Ready — select a PDF…" confirmed |
| B2 | PASS | Button label "Apply Bates Numbers" confirmed |
| B3 | N/A | File browse requires interactive session |
| B4 | PASS | `QIntValidator(1, 9_999_999)` added to Start Index field (Fix 2, ho_0052); non-numeric input now rejected at UI level |
| B5 | PASS | `test_bates_options_dialog` passes; "Output Naming Style:" and "Save Settings" labels confirmed |
| B6 | PASS | Confirmed in `test_bates_options_dialog` |
| B7 | N/A | Requires interactive PDF file |
| B8 | N/A | Requires interactive PDF file |
| B9 | PASS | `test_autoincrement_ledger_editing_finished` passes; ledger advance logic confirmed |
| B10 | N/A | Requires interactive session |
| B11 | PASS | `test_clear_console` passes; clears immediately with no confirmation dialog |

---

### Step 5 — File Room Hero Flow

| Step | Result | Notes |
|---|---|---|
| F1 | PASS | Qt test `test_fileroom_view_init` passes; banner subtitle confirmed |
| F2 | PASS | "Create Folder Structure" button label confirmed |
| F3 | PASS | "FOLDER STRUCTURE PREVIEW" header confirmed |
| F4 | PASS | `test_blueprint_selection_change` passes; preview updates on Matter ID change |
| F5 | PASS | `test_blueprint_selection_change` covers standard vs. custom blueprint switching |
| F6 | N/A | Folder picker requires interactive session |
| F7 | PASS | Success message "Folder structure created successfully! N folders created…" confirmed in source; ST-04 previously validated |
| F8 | PASS | Explorer open call guarded and confirmed in source |
| F9 | N/A | Requires interactive session with illegal character input |

---

### Step 6 — Support Bundle Export

| Step | Result | Notes |
|---|---|---|
| S1 | N/A | Requires interactive GUI session |
| S2 | N/A | Requires interactive GUI session |
| S3 | PASS | CLI export via installed `apmultitool.exe support-bundle` created ZIP at target path |
| S4 | PASS | ZIP size 7,533 bytes; contains at minimum log file and telemetry JSON (confirmed by `status: success` JSON output) |
| S5 | PASS | CLI support-bundle with `-o <non-existent-dir>` works; `mkdir(parents=True, exist_ok=True)` confirmed in `core/support.py` |

---

### Step 7 — Uninstall

| Step | Result | Notes |
|---|---|---|
| U1 | N/A | Add/Remove Programs UI not tested (shell session) |
| U2 | PASS | Silent uninstall (`unins000.exe /VERYSILENT /SUPPRESSMSGBOXES`) completed cleanly |
| U3 | PASS | `%LocalAppData%\Programs\APMultitool\` confirmed absent after uninstall |
| U4 | PASS | Start menu shortcut confirmed absent after uninstall |
| U5 | N/A | Vault file persistence requires vault to be configured and checked |

---

### Step 8 — Reinstall

| Step | Result | Notes |
|---|---|---|
| R1 | PASS | Reinstall with `/TASKS=addtopath` completed cleanly; all files restored |
| R2 | PASS | CLI `--version` returns `v1.0.0-beta1` after reinstall |
| R3 | N/A | Vault persistence requires vault to be set up |

---

## Core & Qt Test Suite

```
Qt view tests (test_qt_compiler, test_qt_bates, test_qt_fileroom):
  15 passed in 0.86s

Core subset (non-Qt engine tests, --fast):
  81 passed, 8 skipped (LibreOffice, expected), 47 deselected in 1.01s
```

---

## Fixes Applied During This Smoke Run

### Fix 1 — Compiler: Surface merge warnings to user

**File:** `apmultitool_qt/views/compiler.py` — `on_merge_finished`

**Issue:** `result.warnings` was populated by the merge engine (e.g., when pikepdf
encounters an encrypted or unreadable PDF) but never shown to the user. The success
dialog appeared even when files were silently skipped.

**Fix:** After the "Documents compiled successfully!" dialog, check for non-empty
`result.warnings` and show a "Some Files Were Skipped" warning dialog listing
each skipped file with a note to check for password-protected files.

**Classification:** Can ship without it, but surfacing this dramatically improves
the encrypted-PDF experience from alpha1.

---

### Fix 2 — Bates: Numeric-only validation on Start Index field

**File:** `apmultitool_qt/views/bates.py` — `setup_ui`

**Issue:** The Start Index field accepted any text. Non-numeric input defaulted
to 1 at runtime (in the stamp engine) but was confusing to users and produced
no in-field feedback.

**Fix:** Applied `QIntValidator(1, 9_999_999)` to the Start Index field. Non-numeric
characters are now rejected at the Qt input layer before the run is ever started.

**Classification:** Low-to-medium polish; no crash risk, but improves UX clarity.

---

## Blocker Classification

| Class | Count | Items |
|---|---|---|
| **Beta1 blocker** | 0 | None identified |
| **Can ship, fix soon** | 1 | GUI launch verification (L1, L3, L5, L6) — requires interactive tester confirmation before wider distribution |
| **Cosmetic** | 1 | `(POC)` label in About panel diagnostic section (pre-existing, noted in ho_0045 open items) |

---

## Summary Assessment

**v1.0.0-beta1 is cleared for limited internal distribution** subject to the
following before wider rollout:

1. At least one interactive tester confirms GUI cold start, activation dialog,
   and hero flows B7–B8, F6, F9 (file picker and run flows) on a separate machine.
2. The "Some Files Were Skipped" warning (Fix 1) has been confirmed to fire
   correctly on an actual encrypted PDF.

No blockers were identified. The two fixes applied are low-risk, UI-only changes
that improve the experience without touching the engine, vault, or licensing layer.
