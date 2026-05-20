---
id: ho_0025_2026_05_19_windows_codesigning_and_staging_rollout
title: Project Manager Report - Windows Codesigning & Staging Rollout
type: pm-report
status: complete
project: Access Paralegal
---

# Project Manager Report: Windows Codesigning & Staging Rollout

## Executive Summary
This sprint transformed the APMultitool Windows build pipeline from an unverified compilation script into a parameterized, staging-ready release pipeline. Codesigning hooks (Authenticode via `signtool.exe`) were injected into both the core binaries and the final Inno Setup installer. The PyInstaller footprint was aggressively pruned, dropping the main GUI executable weight by nearly 30% down to a lean 87.1 MB. STAX staging channels (`-alpha1`, `-rc1`) are now standardized and dynamically injected into the UI frame at build time. Furthermore, the engine boundaries were successfully validated and documented against future browser REST API requirements.

---

## Task Outcomes

| Task | Description | Status | Output File |
| :--- | :--- | :--- | :--- |
| **Task 1** | Define Windows signing and staging plan | Completed ✅ | `docs/ops/windows_signing_and_staging_plan.md` |
| **Task 2** | Add signing hooks to Windows build scripts | Completed ✅ | Modified `build_installer.ps1` |
| **Task 3** | Document signing prereqs and verification | Completed ✅ | `docs/ops/windows_codesigning_prereqs_and_verification.md` |
| **Task 4** | Prune PyInstaller config | Completed ✅ | Modified `ap_multitool.spec`, added `docs/ops/qt_pyinstaller_profile.md` |
| **Task 5** | Validate packaging output size | Completed ✅ | Appended actual metrics to `qt_package_size_and_efficiency_notes.md` |
| **Task 6** | Add release artifact naming convention | Completed ✅ | `docs/ops/release_artifact_naming_windows.md` |
| **Task 7** | Define "Paralegal Alpha" staging playbook | Completed ✅ | `docs/ops/windows_alpha_staging_playbook.md` |
| **Task 8** | Wire version/channel strings into UI | Completed ✅ | Wired `core/__init__.py` to `apmultitool_qt/shell.py` |
| **Task 9** | Cross-check engine contracts for JSON readiness | Completed ✅ | Appended to `qt_engine_boundary_notes.md` |
| **Task 10** | Minimal API surface sketch for browser | Completed ✅ | `docs/ops/browser_surface_api_sketch.md` |
| **Task 11** | Expand tests for version wiring | Completed ✅ | `tests/test_versioning.py` |
| **Task 12** | Update roadmap and index docs | Completed ✅ | `docs/README.md`, `roadmaps/qt_migration_program_apmultitool.md` |
| **Task 13** | Mandatory Project Manager Report & Handoff | Completed ✅ | This document. |

---

## Files & Structures Touched
- `packaging/windows/build_installer.ps1` (Injected params: `$AppVersion`, `$ReleaseChannel`, `$SignCertThumbprint`, plus `signtool` loops).
- `packaging/windows/apmultitool_installer.iss` (Switched to `/D` dynamic variables).
- `ap_multitool.spec` (Switched root to `gui_apmultitool_qt.py`, added massive PySide6 `excludes`).
- `core/__init__.py` (Added `__version__`, `__channel__`).
- `apmultitool_qt/shell.py` (Injected dynamic version into Window Title and Footer).
- `tests/test_versioning.py` (Created unit tests for version injection).
- `docs/ops/` (Added 5 new QA/blueprint files).
- `docs/README.md` (Indexed all artifacts).
- `docs/roadmaps/qt_migration_program_apmultitool.md` (Closed Phase 7).

---

## Release Staging Assessment

### Windows Pipeline Readiness
- **Status:** **Ready for Production Signing.** 
- **Distance to Ship:** The pipeline is 100% ready. It simply awaits the STAX operator passing `-SignCertThumbprint "YOUR_THUMBPRINT"` to `build_installer.ps1`.
- **Packaging Gaps:** None. The size is optimized (87 MB), the installer works cleanly, and the versioning convention is strict. SmartScreen trust-building is the only remaining physical hurdle.

### Universality Posture
- **macOS/Linux Scaling:** The parameterized naming convention (`vX.X.X-channel`) is globally agnostic and will map directly to `.dmg` and `.AppImage` outputs.
- **Browser Scaling:** `browser_surface_api_sketch.md` confirmed that our strict `Job` dataclass models map beautifully to JSON REST payloads without requiring engine refactors.

---

## Recommended Next Sprint
**Sprint Title:** "macOS Notarization PoC and Paralegal Alpha Deployment"
- Execute the playbook to deploy `APMultitool_Setup_v1.0.0-alpha1.exe` to a localized Windows user.
- Build the initial `build_macos.sh` script to confirm App Sandbox rules don't block the STAX Vault.
