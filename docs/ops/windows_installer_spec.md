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

## 5. Tooling Selection

For compile-time construction, **Inno Setup** is selected as the primary installer engine due to:
1. Zero cost (eliminating licensing overhead).
2. Human-readable Pascal scripting for custom PATH modifications.
3. Native support for silent command-line installations (`/SILENT` and `/VERYSILENT` switches).

### Alternative Reviewed:
- **WiX Toolset**: XML-based, produces `.msi` packages. More complex but better suited for enterprise Active Directory GPO group policies if requested in the future.

## 6. Silent Deployment (IT/Admin usage)
The installer must support execution flags for quiet system provisioning:
```cmd
APMultitool_Installer.exe /SILENT /NORESTART /MERGETASKS="addtopath,desktopicon"
```
