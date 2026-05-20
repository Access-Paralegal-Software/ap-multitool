# Windows Installer Specification

This document defines the branding, architecture, deployment layout, registry config, and user experience requirements for the APMultitool Windows Installer.

## 1. Product Intent & Installer Goals
The installation engine must provide a premium, native Windows distribution bundle ("fancy installer") to shield non-technical legal professionals from CLI configuration, python runtimes, or COM registration overhead, while enabling power users and IT admins to script silent deployments.

### Goals:
- **No Python Prerequisite**: Distribute fully compiled native binaries bundled with all interpreter libraries.
- **Unified Package**: Bundle both the Desktop GUI and the Command Line Interface (CLI) in a single installer.
- **PATH Registration**: Optionally add the install directory to the system PATH environment variable to allow calling `apmultitool` headlessly from any command prompt.
- **Branded Presentation**: Use professional logo layouts and clear license confirmation sheets.

## 2. Target Installation Layout

The default install path varies based on authorization elevation:
- **Per-User (Recommended / Default)**: `%LocalAppData%\Programs\APMultitool` (does not require administrator rights).
- **Per-Machine (System-wide)**: `%ProgramFiles%\APMultitool` (requires UAC elevation).

### File Structure:
```
APMultitool/
├── Access_Paralegal_Multitool.exe (GUI Application)
├── apmultitool.exe               (CLI Application)
├── logo_small.png                 (Branding Asset)
├── water_texture.png              (GUI Texture Asset)
├── LICENSE                        (License Agreement)
└── unins000.exe                   (Uninstaller Binary)
```

## 3. Desktop and Start Menu Shortcuts
- **Start Menu**: Create a program group named `Access Paralegal` containing:
  - `APMultitool` (Shortcut to `Access_Paralegal_Multitool.exe`)
  - `APMultitool CLI Help` (Shortcut launching `cmd.exe /k apmultitool --help`)
  - `Uninstall APMultitool`
- **Desktop Shortcut**: Optional checkbox (checked by default) to create `APMultitool` on the user's Desktop.

## 4. Registry and Environment Integrations

### Uninstallation Registry Keys:
- Write configuration keys to `HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\APMultitool` to register under Windows Add/Remove Programs.

### Path Registration:
- Append the installation folder to the user's registry `PATH` key (`HKCU\Environment`) so that users can instantly type `apmultitool` in any Command Prompt or PowerShell shell without specifying full paths.

## 5. Chosen Technology: Inno Setup 6

Inno Setup 6 has been locked as the compiler pipeline for APMultitool's Windows installer.

### Rationale:
1. **Zero Cash Cost**: It is free, open-source, and does not require active subscription licenses (e.g. InstallShield).
2. **Robust User-Level Deployment**: Supports non-admin local programs directory installations, meaning users do not need standard enterprise IT elevation to run it.
3. **Pascal Scripting Support**: Provides custom procedural handlers to dynamically edit/append User environment variables (like the system `PATH`) without third-party extension DLLs.
4. **Command-Line Integration**: Compiles headlessly via `ISCC.exe` which integrates easily with local script pipelines.

### Expected Invocation Flow:
1. Orchestrator script runs PyInstaller to build standalone executable outputs.
2. Script runs `prepare_bundle.ps1` to assemble binaries and assets under `dist/APMultitool_Bundle`.
3. Orchestrator invokes Inno Setup's command-line compiler:
   ```cmd
   ISCC.exe packaging/windows/apmultitool_installer.iss
   ```
4. Output file `APMultitool_Setup_v<Version>.exe` is saved in the `dist/` release directory.

### Known Tradeoffs:
- **No Native MSI Output**: Inno Setup produces `.exe` setup binaries. For Active Directory group policy object (GPO) deployments, IT administrators must wrap the `.exe` or deploy it using silent arguments instead of distributing a native `.msi`.
- **System-Wide vs Per-User Registry Scope**: Per-user PATH modifications are restricted to `HKCU\Environment`. System-wide modifications are ignored during local non-elevated installations.

## 6. Silent Deployment (IT/Admin usage)

The installer supports command-line switches for automated enterprise distribution:
- `/SILENT`: Shows progress window but performs actions automatically.
- `/VERYSILENT`: Completely headless installation. No UI shown.
- `/SUPPRESSMSGBOXES`: Suppresses installer message prompts (e.g. overwrite warnings), using default answers.
- `/NORESTART`: Inhibits system reboots if any file was locked.
- `/MERGETASKS="addtopath,desktopicon"`: Merges the selected optional setup tasks.

Example:
```cmd
APMultitool_Setup_v0.5.0.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /MERGETASKS="addtopath,desktopicon"
```
