---
id: ho_0028_2026_05_21_windows_alpha_polish
title: Handoff - Windows Alpha Polish and Telemetry Alignment
type: handoff
status: completed
project: APMultitool
created_at: 2026-05-21
---

# Developer Handoff: Windows Alpha Polish & Telemetry Alignment

## Summary

This handoff details the polish updates applied to the **v1.0.0-alpha1 Windows build** to ready it for alpha tester rollout. We aligned all versioning constants, integrated build ID telemetry payload parameters, wired up UI dashboard reporting, simplified feedback documents, created operator guides, and successfully ran the staging playbook checks.

---

## 🛠️ Code and UI Changes

1.  **Version String Updates**:
    *   Updated `config.py` `__version__` variable to `v1.0.0-alpha1`.
2.  **Telemetry Payload and UI Wiring**:
    *   Modified `apmultitool_qt/telemetry.py` to store and refresh `build_id` (derived from version & channel constants).
    *   Added `lbl_tel_build` label in `apmultitool_qt/views/about.py` layout.
    *   Wired `update_telemetry_display()` in `about.py` to refresh the label text dynamically using `stats['build_id']`.
3.  **Installer Build Recompilation**:
    *   Ran `packaging/windows/build_installer.ps1` to rebuild the PyInstaller bundles and compile the Inno Setup setup file.
    *   Verified output at `dist\APMultitool_Setup_v1.0.0-alpha1.exe`.
    *   Extracted the new build SHA256 checksum: `F0706FC434E4753219008EC13096A21DD34EA36B92470A3E3F178CA7DA97344C`.

---

## 📄 Documentation Adjustments

1.  **`docs/ops/windows_smartscreen_alpha_notes.md`**: Updated expected SHA256 hash.
2.  **`docs/ops/release_notes_v1.0.0-alpha1.md`**: Updated checksum and appended a "Known Packaging & System Integration Issues" section describing unsigned installers, PATH shell refresh latency, and Office COM engine requirements.
3.  **`docs/ops/feedback_intake_v1.0.0.md`**: Rewrote the document for non-technical paralegals, streamlining OS details, install results, SmartScreen, and friction points.
4.  **`docs/ops/alpha_operator_brief_v1.0.0-alpha1.md`**: [NEW] Created instructions for secure distribution, tester guides, log directories, and feedback file conventions.
5.  **`docs/README.md`**: Registered all new files in the documentation index directory.

---

## 🔬 Staging and Verification Results

*   **Pytest Suite**: All 59 core unit and integration tests passed cleanly in 10.93 seconds.
*   **Staging Playbook Checks**: Ran `scratch/run_staging_tests.py` verifying all 4 playbook scenarios:
    *   **ST-01 (Overwrite Trap)**: Intercepted existing files successfully.
    *   **ST-02 (Stress Test)**: Compiled 55 mock documents.
    *   **ST-03 (Cancellation)**: Halted Bates stamping, closed file handles, and deleted partial outputs.
    *   **ST-04 (File Room Setup)**: Built Case blueprints successfully.
    *   Results logged in `docs/ops/staging_test_results.md`.
*   **UI Dashboard Verification**: Ran `scratch/verify_about_view.py` programmatically loading the Qt `AboutView` layout. Confirmed that the version label and build ID telemetry text match perfectly:
    *   `lbl_ver`: `Version: v1.0.0-alpha1 (Qt/PySide6 Edition)`
    *   `lbl_tel_build`: `Build ID: v1.0.0-alpha1`
    *   `lbl_tel_total`: `Total runs: 2`
