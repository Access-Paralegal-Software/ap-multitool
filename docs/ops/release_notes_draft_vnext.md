# APMultitool Release Notes — v1.0.0 (Production Release)

We are excited to announce the production release of **APMultitool v1.0.0**, introducing a unified Windows Setup Installer, complete GUI layout modernization, thread-safe background execution with real-time cancel/progress controls, and local CLI PATH environment integration.

---

## 🚀 Key Highlights

1. **Windows Installer Integration**: High-performance, single-executable setup installer compiled using Inno Setup 6.
2. **Local Environment PATH Registration**: Optionally adds APMultitool to the user's registry `PATH` environment variable during installation. Active console environments are notified dynamically via system broadcast (`WM_SETTINGCHANGE`) without requiring a reboot.
3. **Non-Elevated Installations**: The installer runs under user privileges by default (`PrivilegesRequired=lowest`), installing files to the user's Local AppData directory. This eliminates the need for administrator privileges (UAC prompts) during deployment.
4. **Consolidated & Modernized GUI Layouts**:
   - **Unified Document Compiler**: Left panel controls (bookmarks, viewer fit, stream compression) are grouped into cohesive styled boxes with standard styling, clear padding, and helpful inline instructions.
   - **Modernized Bates Stamping**: Left-panel config parameters are grouped logically, paired with real-time output console logging, and persist inputs between program loads.
   - **Cohesive File Room & Case Trees**: Grouped dynamic case context input variables and tree blueprints into unified panels for frictionless data intake.
5. **Thread-Safe Cancellation & Execution Guardrails**:
   - In-progress compile processes (both Document Merger and Bates Stamping) can now be cancelled mid-run with cooperative thread polling and automatic safety copy cleanups.
   - All input widgets (entries, menus, checkboxes, browse buttons) are fully disabled during processing to prevent concurrent thread spawn and memory corruptions.
6. **Interaction & Keyboard Accessibility**:
   - All modal popup windows (About, EULA, Settings, Case Blueprint Architect) automatically bind the **Escape** key to dismiss/destroy.
   - Standardized tab navigation through modal input fields.
7. **Silent Deployments Support**: System administrators can run headless installations using standard Inno Setup command-line switches (e.g. `/SILENT` and `/VERYSILENT`).

---

## 🛠️ Detailed Changelog

### User Interface (GUI)
- **`gui_apmultitool.py`**:
  - Refactored settings panels into visually separate group containers with borders and clear padding.
  - Implemented `toggle_compiler_inputs()` and `toggle_bates_inputs()` to handle state transitions.
  - Wired `cancel_requested` cooperative thread checks into Document Compiler and Bates Stamping loops.
  - Bound `<Escape>` to all modals via `setup_modal_window()`.
  - Added CLI companion tips inside the Help/About window to bridge GUI and command line workflows.

### Core & Packaging
- **`packaging/windows/apmultitool_installer.iss`**: Created Inno Setup script with modern UI style, license acceptance page, desktop and start menu shortcuts, and custom Pascal uninstallers to cleanly purge registry entries.
- **`packaging/windows/build_installer.ps1`**: Added build orchestrator to build Python binaries, verify outputs, locate the Inno compiler, compile the installer, and generate checksum files.
- **`scripts/build_windows.ps1`**: Added support for running PyInstaller as a Python module fallback if the global executable is not on system path.

---

## 📥 Installation Instructions

### 1. Standard Interactive GUI Installation
- Download `APMultitool_Setup_v1.0.0.exe` and double-click to run it.
- Choose whether you want to add a desktop shortcut and/or register `apmultitool` on your CLI path.
- Follow the wizard prompts to complete installation.

### 2. Silent/Command Line Deployments
For automated deployments (e.g. via scripting tools), run:
```cmd
APMultitool_Setup_v1.0.0.exe /VERYSILENT /SUPPRESSMSGBOXES /TASKS="desktopicon,addtopath"
```
