---
id: qt_release_readiness_checklist
title: Qt Release Readiness Checklist
type: ops-checklist
---

# Qt Release Readiness Checklist

This checklist must be cleared before transitioning the APMultitool Qt build from Staging to Production release.

## 1. Application Launch & UI Smoke Tests
- [ ] **Launch Cold Start:** App boots within 3 seconds under normal load without phantom terminal windows appearing (Noconsole mode verified).
- [ ] **License Prompts:** Fernet Vault intercepts unactivated users successfully and accepts valid AES configurations.
- [ ] **Compiler View:** Drag-and-drop natively accepts PDF/DOCX inputs. Queue manipulation (move up/down, remove) behaves accurately without signaling lag.
- [ ] **Bates View:** Stamp application correctly avoids edge-collision and creates independent output files.
- [ ] **File Room View:** Matter blueprint previews reflect nested hierarchies accurately.
- [ ] **About/Help Routing:** Built-in help content maps correctly.

## 2. Shutdown & Thread Safety
- [ ] **Idle Shutdown:** App closes cleanly without lingering background processes.
- [ ] **Active Job Cancellation:** Hitting "Cancel" mid-compile safely terminates the background worker and updates the status to "Cancelled".
- [ ] **Hard Close with Active Job:** Clicking the window 'X' while a job is running correctly fires `closeEvent` and halts the engine cleanly without thread segmentation faults.

## 3. Packaging Artifact Validation
- [ ] **Artifact Hash Check:** Generated `.exe` checksums match expected output signatures.
- [ ] **Inno Setup:** Uninstallation cleanly removes registry entries and `AppData` footprint (excluding Vault licensing if explicitly retained).
- [ ] **Shortcuts:** Start menu and Desktop shortcuts launch the executable with correct working directories.

## 4. Documentation & Platform Caveats
- [ ] **Windows Required Utilities:** Verified `wmic` dependency is noted in the deployment prerequisites for machine ID bounding.
- [ ] **Antivirus False Positives:** Verified PyInstaller bootloader does not flag Windows Defender heuristics (or notarization steps are applied).
