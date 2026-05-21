---
id: windows_beta1_smoke_checklist
title: Windows Beta1 Smoke Test Checklist
type: ops-checklist
status: active
project: APMultitool
created_at: 2026-05-21
tags:
  - beta
  - smoke-test
  - windows
  - checklist
---

# Windows Beta1 Smoke Test Checklist (v1.0.0-beta1)

This is the must-pass checklist for the **v1.0.0-beta1** Windows installer before
distributing to the internal beta cohort. Run it on every target machine. Record
results in `windows_beta1_smoke_results.md`.

---

## Artifact Verification

| # | Check | Expected |
|---|---|---|
| A1 | Installer filename | `APMultitool_Setup_v1.0.0-beta1.exe` |
| A2 | SHA256 matches | `BB9A661D3672D5750C7AD834C5929AD014D7CFCF464E9B2225773784F6864D5B` |

Verify with:
```
certutil -hashfile APMultitool_Setup_v1.0.0-beta1.exe SHA256
```

---

## Step 1 — Install

| # | Step | Pass Criteria |
|---|---|---|
| I1 | Double-click installer | SmartScreen warning appears (expected for unsigned build) |
| I2 | Click "More info" → "Run anyway" | Wizard opens, shows `APMultitool v1.0.0-beta1` in title |
| I3 | Complete wizard (accept defaults; enable "Add to PATH" if testing CLI) | Wizard closes with no error |
| I4 | Install directory exists | `%LocalAppData%\Programs\APMultitool\` contains `Access_Paralegal_Multitool.exe`, `apmultitool.exe`, `unins000.exe` |
| I5 | Start menu shortcut exists | `Start > Access Paralegal > APMultitool` launches the app |

---

## Step 2 — Launch & Version Confirm

| # | Step | Pass Criteria |
|---|---|---|
| L1 | Launch via Start Menu shortcut | App opens, no ghost console window behind it |
| L2 | Window title shows version | Title bar reads `Access Paralegal Multitool v1.0.0-beta1 (Qt Edition)` |
| L3 | Navigate to Help & About tab | Banner shows "Help & About" |
| L4 | Check Build ID label | Shows `Build ID: v1.0.0-beta1` |
| L5 | Cold start time | App is interactive within 5 seconds |
| L6 | License activation dialog | On first launch with no vault, activation dialog appears; entering a valid key accepts and loads the app |

---

## Step 3 — Document Compiler Hero Flow

| # | Step | Pass Criteria |
|---|---|---|
| C1 | Click "Document Compiler" in sidebar | View loads; button reads "Compile Documents" |
| C2 | Add 2–3 test PDFs via "Add Files" | Files appear in queue with file names and sizes |
| C3 | Set output PDF name and output folder | Fields populate correctly |
| C4 | Click "Compile Documents" | No spurious "Confirm Merge Order" dialog appears |
| C5 | Compilation runs | Progress bar appears in status bar; rows update to "Processing…" |
| C6 | Compilation succeeds | "Documents compiled successfully!" dialog; all rows show "✅ Combined" |
| C7 | Output file exists | Output PDF present in chosen folder, file is non-empty and openable |
| C8 | Overwrite guard | Re-run with same output filename → overwrite confirmation dialog appears; cancelling aborts; confirming overwrites |
| C9 | Encrypted PDF handling | Add an encrypted PDF to queue → compilation completes but shows a "Some Files Were Skipped" warning naming the encrypted file |
| C10 | Cancel mid-run | Click "Cancel" during a large compilation → job halts, button restores to "Compile Documents" |

---

## Step 4 — Bates Stamping Hero Flow

| # | Step | Pass Criteria |
|---|---|---|
| B1 | Click "Bates Stamping" in sidebar | View loads; console reads "Ready — select a PDF and configure parameters above to begin." |
| B2 | Run button label | Button reads "Apply Bates Numbers" (not FLATTEN/all-caps) |
| B3 | Browse for a target PDF | File path populates in "Target PDF:" field |
| B4 | Set Bates prefix and start index | Fields accept input; start index field rejects non-numeric characters |
| B5 | Click "Stamp Options..." | Options dialog opens; shows "Output Naming Style:" label and "Save Settings" button |
| B6 | Save options and close dialog | Dialog closes; settings persist |
| B7 | Click "Apply Bates Numbers" | Log panel shows live messages; progress bar appears |
| B8 | Run completes | Success dialog shows filename and page count; Explorer opens to output folder |
| B9 | Start index auto-advances | "Start Index:" field updated to next available number after successful run |
| B10 | Cancel mid-run | "Cancel" button halts stamping; button restores to "Apply Bates Numbers"; partial output file removed |
| B11 | Clear log | Click the clear button in the log panel → clears immediately with no "Are you sure?" dialog |

---

## Step 5 — File Room Hero Flow

| # | Step | Pass Criteria |
|---|---|---|
| F1 | Click "File Room & Trees" in sidebar | View loads; banner reads "File Room & Matter Structure" |
| F2 | Run button label | Button reads "Create Folder Structure" |
| F3 | Preview panel label | Header reads "FOLDER STRUCTURE PREVIEW" |
| F4 | Enter a Matter ID | Preview tree updates to reflect the Matter ID as root |
| F5 | Select a blueprint | Standard blueprints disable editing; Custom blueprint enables Architect tools |
| F6 | Click "Create Folder Structure" | Folder picker opens |
| F7 | Select destination folder | Folders created; success message reads "Folder structure created successfully! N folders created in the selected location." |
| F8 | Explorer opens | Windows Explorer opens to the parent folder automatically |
| F9 | Illegal characters in folder name | Entering `:` or `/` in a custom folder name → app does not crash; error message is human-readable |

---

## Step 6 — Support Bundle Export

| # | Step | Pass Criteria |
|---|---|---|
| S1 | Navigate to Help & About | Telemetry card visible |
| S2 | Click "Export Support Bundle…" | Save dialog opens; defaults to Desktop |
| S3 | Save ZIP | ZIP file is created at chosen path; "Open folder" prompt appears |
| S4 | ZIP is non-empty | ZIP contains at minimum one log file and a metadata JSON |
| S5 | CLI export | From a new terminal: `apmultitool support-bundle` → ZIP created in current directory with success message |

---

## Step 7 — Uninstall

| # | Step | Pass Criteria |
|---|---|---|
| U1 | Open Settings > Apps | APMultitool v1.0.0-beta1 appears in installed apps list |
| U2 | Uninstall | Uninstaller runs cleanly with no errors |
| U3 | Install directory removed | `%LocalAppData%\Programs\APMultitool\` no longer exists |
| U4 | Start menu shortcut removed | Shortcut gone from Start menu |
| U5 | Vault data preserved (if configured) | Vault/license file at `%APPDATA%\AccessParalegal\` survives uninstall (by design) |

---

## Step 8 — Reinstall

| # | Step | Pass Criteria |
|---|---|---|
| R1 | Run installer again | Installs cleanly over prior uninstall with no conflicts |
| R2 | Launch after reinstall | App launches; shows v1.0.0-beta1 |
| R3 | Prior vault recognized | If vault file was preserved, activation is not re-prompted |

---

## Result Logging Format

Record results in `docs/ops/windows_beta1_smoke_results.md` using the following format per machine/run:

```markdown
## Run: [YYYY-MM-DD] — [Tester Initials] on [Machine Alias]

**OS:** Windows 10/11 xxxx (Build xxxxxxx)
**Installer SHA256 verified:** YES / NO
**Support bundle path:** [path or N/A]

| Step | Result | Notes |
|---|---|---|
| A1–A2 | PASS / FAIL | |
| I1–I5 | PASS / FAIL | |
| L1–L6 | PASS / FAIL | |
| C1–C10 | PASS / FAIL | |
| B1–B11 | PASS / FAIL | |
| F1–F9 | PASS / FAIL | |
| S1–S5 | PASS / FAIL | |
| U1–U5 | PASS / FAIL | |
| R1–R3 | PASS / FAIL | |

**Blocker classification:**
- [ ] Beta1 blocker (must fix before any further distribution)
- [ ] Can ship, fix soon (must fix before beta2 or wider release)
- [ ] Cosmetic / low priority

**Issues found:**
[Describe any failures or unexpected behavior here]
```

---

## Blocker Classification Guide

| Class | Meaning | Examples |
|---|---|---|
| **Beta1 blocker** | Prevents safe distribution to even a small internal cohort | App crashes on launch, installer leaves orphan processes, vault broken |
| **Can ship, fix soon** | Workaround exists or impact is narrow | Warning dialog missing, minor text incorrect, minor UX friction |
| **Cosmetic** | No functional impact | Pixel misalignment, non-critical label wording |
