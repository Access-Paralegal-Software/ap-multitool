# APMultitool Windows Installer Smoke-Test & Verification Spec

Last verified on 2026-05-21 for the `v1.0.0-beta1` packaging lane.

This document defines the manual validation sequence to run after generating a Windows installer.

## Smoke Validation Checklist

### 1. Interactive installation

1. Double-click `dist\APMultitool_Setup_v1.0.0-beta1.exe`.
2. Verify the welcome page shows:
   - product name: `APMultitool`
   - publisher: `Access Paralegal Systems`
   - version: `v1.0.0-beta1`
3. Verify the default install directory is:
   - `%LOCALAPPDATA%\Programs\APMultitool`
4. Verify the optional tasks page exposes:
   - desktop shortcut
   - local PATH integration
5. Complete the install and launch the app.

### 2. Post-install file checks

Verify `%LOCALAPPDATA%\Programs\APMultitool` contains:

- `Access_Paralegal_Multitool.exe`
- `apmultitool.exe`
- `LICENSE`
- `logo_small.png`
- `water_texture.png`
- `README_BUNDLE.txt`
- `unins000.exe`

Verify shortcuts:

- desktop shortcut if selected
- Start Menu group entries for:
  - `APMultitool`
  - `APMultitool CLI Help`
  - `Uninstall APMultitool`

### 3. CLI path integration

Open a fresh shell and run:

```powershell
apmultitool --version
apmultitool merge --help
```

Expected version output:

```text
APMultitool CLI v1.0.0-beta1
```

### 4. Hero flow check

After install, launch the GUI and verify at least one of:

- Document Compiler startup
- Bates view startup
- File Room startup

Also export a support bundle from the About view or CLI when that flow is part of the release smoke pass.

### 5. Uninstall and reinstall

1. Uninstall from Start Menu or Apps & Features.
2. Confirm:
   - install directory is removed
   - shortcuts are removed
   - uninstall entry disappears from Apps & Features
   - PATH entry is removed from `HKCU\Environment`
3. Reinstall the same beta1 installer.
4. Confirm the app launches cleanly again and the reinstall does not collide with stale install state.

### 6. Silent install checks

```powershell
dist\APMultitool_Setup_v1.0.0-beta1.exe /SILENT /TASKS="desktopicon,addtopath"
dist\APMultitool_Setup_v1.0.0-beta1.exe /VERYSILENT /SUPPRESSMSGBOXES
```

Use these only after the interactive flow has passed.

## Leftover Artifact Review

When validating uninstall, classify leftovers as one of:

- acceptable retained user data
- acceptable retained local logs or diagnostics
- problematic leftover installer garbage

User vaults, user-created document outputs, and support bundles must not be silently deleted by uninstall.
