---
id: qt_windows_packaging_validation
title: Qt Windows Packaging Validation Notes
type: ops-audit
---

# Windows Packaging Validation Notes

## Existing Build Path
The repository currently utilizes a standard PyInstaller to Inno Setup pipeline defined in `packaging/windows/build_installer.ps1`.
- **PyInstaller Phase:** Compiles `gui_apmultitool_qt.py` into a monolithic directory (`--onedir` structure), embedding `hook-cryptography` and PySide6 dependencies.
- **Inno Setup Phase:** `apmultitool_installer.iss` wraps the `dist/` directory into a final `APMultitool_Setup_v0.5.x.exe`.

## Observations & Validation
- **Metadata Consistency:** The installer accurately registers the Access Paralegal branding and sets shortcuts correctly.
- **Environment Isolation:** The packaged application behaves entirely isolated from the user's local Python installation.
- **CLI Behavior:** Currently, the executable runs in `noconsole` windowed mode. However, CLI arguments passed to the bundled executable are ignored. If STAX strategy requires exposing the CLI via the packaged binary, the PyInstaller spec will need an entrypoint modification or a secondary binary built.

## Remaining Trust Issues (Action Required)
- **Code Signing:** The generated `APMultitool_Setup.exe` is currently **UNSIGNED**. Windows SmartScreen will flag this payload maliciously upon user download. An EV Code Signing Certificate or standard Authenticode certificate MUST be applied via `signtool.exe` in the `build_installer.ps1` before actual production release.
