---
id: release-notes-v1.0.0-alpha1
title: Release Notes - v1.0.0-alpha1 (Windows Alpha)
type: operations
status: active
project: APMultitool
created_at: 2026-05-21T03:30:00Z
tags:
  - release
  - alpha
  - windows
---

# 🚀 APMultitool Release Notes — v1.0.0-alpha1 (Windows Alpha Build)

We are pleased to announce the release of **APMultitool v1.0.0-alpha1**, the first packaged Windows installer build for the Access Paralegal Multitool test cohort. This release includes the modernized Qt UI, diagnostic systems, local telemetry pipeline, and Inno Setup 6 packaging structure.

---

## 📦 Build Specifications
*   **Version:** `1.0.0-alpha1`
*   **Release Date:** 2026-05-21
*   **Platform:** Windows 10 / 11 (x64)
*   **Installer Filename:** `APMultitool_Setup_v1.0.0-alpha1.exe`
*   **SHA256 Checksum:** `F0706FC434E4753219008EC13096A21DD34EA36B92470A3E3F178CA7DA97344C`
*   **Signature status:** Unsigned (subject to Windows SmartScreen warning)

---

## ✨ Features and Enhancements Included

### 1. Modernized Qt GUI Shell
*   **Sidebar Navigation**: Dynamic fade-in/fade-out animations (200ms `QPropertyAnimation` transitions) when switching tabs.
*   **Custom Scrollbars**: Premium, custom QSS styling applied to all application scrollbars.
*   **Document Compiler**: Integrated "The Overwrite Trap" confirmation to prevent users from accidentally overwriting existing files, and automatic fallback reset of empty Output PDF Names to `compiled.pdf`.
*   **Bates Stamping**: Replaced the text gear emoji on the Options button with a custom, high-resolution vector gear icon drawn via QPainter.
*   **File Room Trees**: Legal case structure blueprint configuration, directory previewing, and creation.
*   **Escape to Dismiss**: All popups and modals automatically bind the `<Escape>` key to exit.

### 2. Local Telemetry Pipeline
*   All engine operations executed via the GUI thread worker register telemetry events.
*   Aggregates statistics on total runs, successful runs, failures, cancellations, and individual tool usage counts.
*   Stores data locally in JSON format at `~/.access_paralegal_telemetry.json`.
*   Synchronizes and displays real-time statistics in the **Help/About** dashboard view.

### 3. Integrated Setup Installer
*   Bundled using PyInstaller with customized profile rules to strip WebEngine and QML weight.
*   Compiled using Inno Setup 6 into a non-elevated user-space setup wizard (`PrivilegesRequired=lowest`).
*   Installs desktop and start menu shortcuts.
*   Provides an optional **"Add to PATH"** setting for CLI command execution, complete with registry updates and system environment broadcasts (`WM_SETTINGCHANGE`) to avoid rebooting.

---

## 🛠️ Verification Logs
All 4 playbook staging scenarios have been validated:
1.  **ST-01 (Overwrite Trap)**: Intercepted and blocked merge when target file was pre-existing.
2.  **ST-02 (Stress Test)**: Successfully merged 55 separate mock documents in a single click.
3.  **ST-03 (Cancellation)**: Halted Bates stamp execution mid-run, wiped partial output file handles, and logged cancellation status.
4.  **ST-04 (File Room Setup)**: Correctly built legal case directories matching configured blueprints.

---

## ⚠️ Known Packaging & System Integration Issues
*   **Unsigned Installer Warnings:** Because the alpha installer is unsigned, Windows SmartScreen will display an "Unknown Publisher" warning block. Testers must click "More info" and then "Run anyway" to proceed.
*   **PATH Environment Updates:** While the installer broadcasts environment changes (`WM_SETTINGCHANGE`) to active shells, command prompt instances already open *prior* to installation will not see the updated PATH. Testers must open a new terminal window to run `apmultitool` CLI commands.
*   **Multi-user PATH Cleanup:** If the application is installed on a multi-user machine, environment PATH adjustments apply only to the current Windows user profile under HKCU.
*   **Word/Excel to PDF Fallback:** Headless office document conversion is dependent on a local MS Word or Excel installation. Fallbacks for non-Office environments (LibreOffice CLI interface) are not enabled in this alpha release.
