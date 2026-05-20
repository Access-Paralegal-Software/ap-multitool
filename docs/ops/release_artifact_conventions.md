# APMultitool Release Artifact Structure & Naming Conventions

This document specifies the standard locations, file names, structure, and git tagging conventions for release builds of APMultitool.

---

## 📦 Directory Structure of Release Artifacts

All release builds are compiled into the `dist/` directory at the repository root.

```
dist/
├── APMultitool_Bundle/                     # Staging directory for the raw executables
│   ├── Access_Paralegal_Multitool.exe      # GUI executable (compiled from main_gui.py)
│   ├── apmultitool.exe                     # CLI executable (compiled from cli.py)
│   ├── logo_small.png                      # App UI logo image
│   ├── water_texture.png                   # App UI background image
│   ├── LICENSE                             # License agreement
│   ├── README_BUNDLE.txt                   # Quick start manual for raw files
│   └── launch_cli_help.bat                 # Helper script to launch CLI help
│
├── APMultitool_Setup_v0.5.0.exe            # Consolidated Windows Setup Installer
└── APMultitool_Setup_v0.5.0.exe.sha256     # SHA-256 Checksum hash file for setup verification
```

---

## 🏷️ Artifact Naming Conventions

To maintain consistency across releases, all compiled setup installers must adhere to the following naming pattern:

- **Installer executable**: `APMultitool_Setup_v<Version>.exe`
  - Example: `APMultitool_Setup_v0.5.0.exe`
- **Hash file**: `APMultitool_Setup_v<Version>.exe.sha256`
  - Example: `APMultitool_Setup_v0.5.0.exe.sha256`

The `<Version>` token must follow standard **Semantic Versioning** (`MAJOR.MINOR.PATCH`).

---

## 🛡️ Hash Code Generation

The SHA-256 checksum is generated using the PowerShell command `Get-FileHash`. It produces a uppercase hex string of the file's hash, which is stored in a corresponding `.sha256` file:

- Command used:
  ```powershell
  $sha256 = (Get-FileHash -Path "dist\APMultitool_Setup_v0.5.0.exe" -Algorithm SHA256).Hash
  $sha256 | Out-File -FilePath "dist\APMultitool_Setup_v0.5.0.exe.sha256" -Encoding ascii
  ```
- Verification: Users can verify the downloaded installer integrity in PowerShell:
  ```powershell
  Get-FileHash -Path "dist\APMultitool_Setup_v0.5.0.exe" -Algorithm SHA256
  ```

---

## 🏷️ Git Tagging & Release Conventions

Releases are tracked using git tags linked directly to build commits.

- **Tag format**: `v<Version>-apmultitool-release`
  - Example: `v0.5.0-apmultitool-release`
- **Tag Description**: Include the release changelog overview.
- **Commands to tag and push**:
  ```bash
  git tag -a v0.5.0-apmultitool-release -m "Release v0.5.0: Windows Installer & CLI Path Integration"
  git push origin v0.5.0-apmultitool-release
  ```
