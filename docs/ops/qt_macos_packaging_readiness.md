---
id: qt_macos_packaging_readiness
title: macOS Packaging Readiness
type: ops-audit
---

# macOS Packaging & Notarization Readiness

## Current Status
macOS packaging is **NOT YET VERIFIED** and remains a theoretical path in this repository. No build scripts exist in `packaging/macos/`.

## Deployment Assumptions
- **Framework Compatibility:** PySide6 natively supports macOS (Intel and Apple Silicon). The core `EngineJobWorker` and `QThread` paradigms will operate identically.
- **Path Restrictions:** macOS enforces strict App Sandbox constraints. If APMultitool attempts to write Vault licensing data to system directories rather than `~/Library/Application Support/`, it will fail.
- **Packaging Format:** The target artifact must be an `.app` bundle nested within a `.dmg`.

## Required Implementation Steps
1. Create `packaging/macos/build_app.sh` using PyInstaller's `--windowed` mode.
2. Ensure the PyInstaller `Info.plist` accurately maps necessary permissions (e.g., file access).
3. **Codesigning:** Execute `codesign` using an Apple Developer ID Application certificate.
4. **Notarization:** Run `xcrun altool` (or `notarytool`) to submit the DMG to Apple's notary service. Unnotarized apps will be completely blocked by Gatekeeper on modern macOS.

## Verdict
Do not advertise macOS support until the exact notarization pipeline is constructed and verified on bare metal macOS hardware.
