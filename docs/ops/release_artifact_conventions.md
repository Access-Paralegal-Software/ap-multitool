# APMultitool Release Artifact Structure & Naming Conventions

This document specifies the standard locations, file names, structure, and git tagging conventions for release builds of APMultitool.

Last verified on 2026-05-21 for the `v1.0.0-beta1` Windows lane.

## Directory Structure of Release Artifacts

All release builds are compiled into the `dist/` directory at the repository root.

```text
dist/
|-- APMultitool_Bundle/                         raw staged executables and assets
|   |-- Access_Paralegal_Multitool.exe
|   |-- apmultitool.exe
|   |-- logo_small.png
|   |-- water_texture.png
|   |-- LICENSE
|   |-- README_BUNDLE.txt
|   `-- launch_cli_help.bat
|-- APMultitool_Setup_v1.0.0-beta1.exe
`-- APMultitool_Setup_v1.0.0-beta1.exe.sha256
```

## Artifact Naming Conventions

All Windows setup installers must follow:

- installer: `APMultitool_Setup_v<Version><Channel>.exe`
- checksum: `APMultitool_Setup_v<Version><Channel>.exe.sha256`

Examples:

- `APMultitool_Setup_v1.0.0-beta1.exe`
- `APMultitool_Setup_v1.0.0-rc1.exe`
- `APMultitool_Setup_v1.0.0.exe`

`<Version>` must follow semantic versioning. `<Channel>` may be empty for stable releases.

## Hash Generation

```powershell
$sha256 = (Get-FileHash -Path "dist\APMultitool_Setup_v1.0.0-beta1.exe" -Algorithm SHA256).Hash
$sha256 | Out-File -FilePath "dist\APMultitool_Setup_v1.0.0-beta1.exe.sha256" -Encoding ascii
Get-FileHash -Path "dist\APMultitool_Setup_v1.0.0-beta1.exe" -Algorithm SHA256
```

## Git Tagging

Suggested format:

- `v<Version><Channel>-apmultitool-release`

Example:

```bash
git tag -a v1.0.0-beta1-apmultitool-release -m "Release v1.0.0-beta1: signed installer and uninstall validation"
git push origin v1.0.0-beta1-apmultitool-release
```
