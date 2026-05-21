---
handoff_id: pm_report_ho_0046_2026_05_21
date: 2026-05-21
title: PM Report — macOS Host & Dry-Run Packaging Lane
project: APMultitool
status: completed
type: pm_report
lane: macos-host-and-dry-run-packaging
tags:
  - macos
  - packaging
  - dmg
  - dry-run
  - tooling
---

# PM Report — macOS Host & Dry-Run Packaging Lane (ho_0046)

## Executive Summary

This lane was tasked with validating the macOS packaging pipeline on a real macOS host by running an unsigned DMG build. No macOS host was available in the development environment (Windows 11), so the local dry-run portion remains deferred — consistent with the same deferral in lane ho_0041.

In lieu of a live run, a static review of the full macOS pipeline was performed. The review uncovered two blocking correctness issues and one stale documentation claim. All three were corrected. The pipeline now points at the active Qt entry point (`gui_apmultitool_qt.py`) with correct CI dependencies, and a host profile template has been created so the first operator to run a bare-metal build has a clear record-keeping framework.

macOS remains a probe/preparation platform. No macOS support is claimed.

---

## macOS Host Profile

**Host used for this lane:** None — development environment is Windows 11 Home (x64), build 10.0.26200.

A host profile template and first-run observation checklist have been created at `docs/ops/macos_host_profile_apmultitool.md`. The operator who performs the first bare-metal run should fill in:

- macOS version and architecture (Intel / Apple Silicon)
- Xcode / CLT version
- Python source and version (Homebrew / pyenv / system)
- Installed toolchain versions (PyInstaller, PySide6)
- First-run build and launch observations

---

## Task Status

| # | Task | Status | Notes |
|---|---|---|---|
| 1 | Establish macOS host context | ⏭️ Deferred | No macOS host available; template created in `docs/ops/macos_host_profile_apmultitool.md` |
| 2 | Clone and set up repo on macOS | ⏭️ Deferred | No macOS host available |
| 3 | Run unsigned DMG build locally | ⏭️ Deferred | No macOS host available |
| 4 | Inspect generated .app and DMG | ⏭️ Deferred | No macOS host available |
| 5 | Capture and fix minimal host-specific issues | ✅ Completed (static) | Two blocking issues found and fixed via code review; see §Files Changed |
| 6 | Update macOS packaging docs with real observations | ✅ Completed | `macos_packaging_overview.md` updated; stale `qt_macos_packaging_readiness.md` corrected |
| 7 | Align CI expectations with local behavior | ✅ Completed (static) | CI pip install aligned to active Qt framework |
| 8 | Non-support disclaimer check | ✅ Completed | All macOS docs reviewed; no over-claims found; probe/preparation language confirmed |

---

## Files Changed

### Created

| File | Description |
|---|---|
| `docs/ops/macos_host_profile_apmultitool.md` | Host profile placeholder: template for OS/toolchain recording, setup steps, first-run observation checklist, and pre-run issue log |
| `handoffs/pm_report_ho_0046_2026_05_21_macos_host_and_dry_run_packaging.md` | This report |

### Modified

| File | Change |
|---|---|
| `packaging/macos/build_app.sh` | **Line 109:** Entry point corrected from `gui_apmultitool.py` (legacy CustomTkinter) to `gui_apmultitool_qt.py` (active PySide6 Qt edition). Without this fix, the macOS build would have compiled the abandoned CustomTkinter GUI rather than the live application. |
| `.github/workflows/macos_packaging_probe.yml` | **pip install step:** `customtkinter` replaced with `PySide6`. Without PySide6 installed in CI, `gui_apmultitool_qt.py` would fail to import during PyInstaller compilation. |
| `docs/ops/qt_macos_packaging_readiness.md` | Removed stale claim "No build scripts exist in `packaging/macos/`" (false since ho_0030). Updated pipeline status table and required steps to reflect current probe state. |
| `docs/ops/macos_packaging_overview.md` | (1) Corrected "Known gap" line about Qt entry point — gap is now resolved. (2) Added `§1a Verified on Host` section documenting static-review-only status and linking to host profile doc. (3) Updated Status table: Qt entrypoint row changed from ⚠️ Pending to ✅ Fixed. |

---

## Static Review Findings

### Issue 1 — Wrong entry point in `build_app.sh` (Blocking)

**File:** `packaging/macos/build_app.sh`, line 109
**Problem:** PyInstaller was called with `gui_apmultitool.py` (the legacy CustomTkinter GUI, which imports `customtkinter`, `tkinter`, `PIL`, and `extract_msg` via the old architecture). This entry point is functionally abandoned.
**Fix:** Changed to `gui_apmultitool_qt.py` — the PySide6 bootstrap that wires `apmultitool_qt.main.main()`. This is what the Windows build already uses and what `ap_multitool.spec` already referenced correctly.

### Issue 2 — Wrong framework dependency in CI (`macos_packaging_probe.yml`) (Blocking)

**File:** `.github/workflows/macos_packaging_probe.yml`, pip install step
**Problem:** CI installed `customtkinter` but not `PySide6`. Running `pyinstaller gui_apmultitool_qt.py` without PySide6 present would fail at the import analysis stage with `ModuleNotFoundError: No module named 'PySide6'`.
**Fix:** Replaced `customtkinter` with `PySide6` in the pip install list. All other dependencies (`pypdf`, `reportlab`, `pikepdf`, `pymupdf`, `extract-msg`, `cryptography`, `pillow`) remain and are correct for the core engine operations.

### Issue 3 — Stale documentation claim (Documentation)

**File:** `docs/ops/qt_macos_packaging_readiness.md`
**Problem:** Document stated "No build scripts exist in `packaging/macos/`" — this was accurate before ho_0030 but has been false since `build_app.sh` was created in that lane.
**Fix:** Rewrote the document to reflect current state: scripts exist, CI probe is wired, signing/notarization is guarded pending credentials, bare-metal run is still pending.

### Non-support Disclaimer Check (Task 8)

All four macOS ops documents reviewed:
- `docs/ops/macos_packaging_overview.md` — probe/preparation language confirmed.
- `docs/ops/macos_signing_requirements.md` — no support claim; all credentials marked not configured.
- `docs/ops/macos_secrets_activation_checklist.md` — states "macOS remains a packaging/notarization probe."
- `docs/ops/qt_macos_packaging_readiness.md` — updated to include "Do not advertise macOS support until notarized build is validated on bare metal."

No over-claims found or introduced.

---

## Remaining Manual Steps for Operators

1. **Obtain a macOS host** — any Intel or Apple Silicon Mac running macOS 13+ with Xcode CLT installed.
2. **Clone, set up, and run the unsigned build** following the setup steps in `docs/ops/macos_host_profile_apmultitool.md`.
3. **Record the host profile** — fill in the template fields in that document.
4. **Test first launch** — open the `.app`, confirm the UI surfaces, note any crashes or vault/path issues.
5. **Update `macos_packaging_overview.md` §1a** with actual observations.
6. **When ready to activate signing** — follow `docs/ops/macos_secrets_activation_checklist.md`.

---

## Confirmations

- ✅ No secrets, private keys, certificates, or `.p12` files were committed to the repository.
- ✅ macOS remains a probe/preparation platform. No macOS support is claimed.
- ✅ Windows alpha behavior was not modified.
- ✅ Vault, encryption, and hardware identity logic were not touched.
- ✅ Engine/UI boundary maintained throughout.
