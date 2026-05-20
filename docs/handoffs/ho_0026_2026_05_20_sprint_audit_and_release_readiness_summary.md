---
id: ho_0026_2026_05_20_sprint_audit_and_release_readiness_summary
title: Handoff - APMultitool Qt Migration Audits, Hardening, and Windows Release Packaging
type: handoff
status: completed
project: Access Paralegal
---

# APMultitool Qt Migration Audits, Hardening, and Windows Release Packaging: Master Handoff

## 1. Context & Orientation
This document serves as the master hand-off for the APMultitool graphical user interface migration, audit, and release readiness hardening. The legacy CustomTkinter GUI has been successfully migrated to a robust, responsive, cross-platform PySide6 (Qt Widgets) shell, fully audited for safety/performance, pruned of unnecessary dependencies, and integrated with release-packaging pipelines and Windows Codesigning hooks.

---

## 2. Core Work Accomplished (This Session)

### A. Security, Parity, & Hardening Audits
- **Parity Review:** Verified complete parity of the **Document Compiler**, **Bates Stamping**, and **File Room Architect** screens with the legacy CustomTkinter GUI.
- **Security Audit:** Conducted a comprehensive audit of the Case Vault and Pro Activation subsystems. Created mock-hardware lock configurations for local sandbox execution while maintaining strict cryptography.
- **Lifecycle & Cleanup:** Hardened thread teardowns. Implemented standard termination overrides in `closeEvent` inside `shell.py` to prevent zombie QThreads or resource locks on application exit. Tested and verified with pytest.

### B. Size Optimization & PyInstaller Customization
- **aggressive Pruning:** Customized `ap_multitool.spec` to explicitly exclude heavyweight, unused PySide6 components (WebEngine, QML, Quick, Network, Test, SpatialAudio, 3D).
- **Audit Results:**
  - **GUI Executable (`Access_Paralegal_Multitool.exe`):** Reduced from an estimated ~150 MB down to **87.1 MB**.
  - **CLI Executable (`apmultitool.exe`):** Reduced to **48.8 MB**.
  - Verified bundle creation and assets layout (license, launchers, watermarks).

### C. Release Channels & Version Wiring
- Wired `core/__init__.py` constants (`__version__ = "1.0.0"`, `__channel__ = "-alpha1"`) dynamically into `apmultitool_qt/shell.py`.
- Automated window title branding and sidebar footers to render the active release channel.
- Implemented `tests/test_versioning.py` to verify this wiring.

### D. Windows Codesigning & Staging Pipeline
- Paramaterized the powershell build orchestrator (`packaging/windows/build_installer.ps1`) to accept `$AppVersion`, `$ReleaseChannel`, and `$SignCertThumbprint`.
- Integrated dual-phase Authenticode signatures via `signtool.exe`:
  1. Signs individual inner binaries (`Access_Paralegal_Multitool.exe` and `apmultitool.exe`) post-PyInstaller.
  2. Signs the final unified setup installer (`APMultitool_Setup_v1.0.0-alpha1.exe`) post-Inno Setup.
- Standardized staging conventions and created the **Paralegal Alpha Staging Playbook** (`docs/ops/windows_alpha_staging_playbook.md`).

### E. Future-Proofing & Browser Surface Readying
- **Engine-UI Separation:** Verified that the core engine and PySide6 UI controllers communicate exclusively via serializable `Job` dataclasses (`core/job.py`).
- **Browser API Sketch:** Authored `docs/ops/browser_surface_api_sketch.md` defining REST/JSON payloads for a web-based client wrapper.

---

## 3. Reference Documentation Created
All operational files are organized in the git-tracked `/docs` directory:
- **`docs/ops/windows_signing_and_staging_plan.md`**: Cryptographic certificates, staging tiers, and release gates.
- **`docs/ops/windows_codesigning_prereqs_and_verification.md`**: Command-line verification for Authenticode signatures.
- **`docs/ops/release_artifact_naming_windows.md`**: Target installer filename conventions.
- **`docs/ops/windows_alpha_staging_playbook.md`**: Test group recruitment, telemetry, and rollout schedules.
- **`docs/ops/qt_pyinstaller_profile.md`**: Complete listing of excluded libraries and compression configs.
- **`docs/ops/browser_surface_api_sketch.md`**: JSON endpoint mockups for compiling, stamping, and blueprint operations.
- **`docs/handoffs/ho_0025_2026_05_19_windows_codesigning_and_staging_rollout.md`**: PM execution summary.

---

## 4. Current Repository Status & Next Steps
- **Branch:** `master` (All work committed and pushed to `woodyardae/Access_Paralegal_PDF_Merger`).
- **Tests:** `pytest` passes 100% (covering workers, dialogs, versioning, and teardown).
- **Next Actions:**
  1. **Execute Alpha Playbook:** Provide the installer (`dist/APMultitool_Setup_v1.0.0-alpha1.exe`) to the initial test cohort.
  2. **Notarization PoC:** Begin scaffolding the macOS codesigning and notarization script.
  3. **Telemetry Scaffold:** Wire telemetry triggers into the UI worker feedback channels.
