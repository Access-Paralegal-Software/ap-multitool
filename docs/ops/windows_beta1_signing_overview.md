---
id: windows_beta1_signing_overview
title: Windows Beta1 Signing Overview
type: ops-manual
status: active
project: APMultitool
created_at: 2026-05-21
---

# Windows Beta1 Signing Overview

This note defines the expected signing inputs and verification steps for the `v1.0.0-beta1` Windows release.

## Signing goals

For the beta1 release, sign:

- `dist\Access_Paralegal_Multitool.exe`
- `dist\apmultitool.exe`
- `dist\APMultitool_Setup_v1.0.0-beta1.exe`

Unsigned mode remains supported for local packaging and uninstall validation.

## Supported signing inputs

The Windows build pipeline supports two local-only signing modes:

1. Certificate thumbprint in the local certificate store
2. Local `.pfx` file plus password

Environment variables:

```powershell
$env:APM_SIGN_CERT_THUMBPRINT = "YOUR_CERT_THUMBPRINT"
$env:APM_SIGN_PFX_PATH = "C:\secure\apmultitool-signing.pfx"
$env:APM_SIGN_PFX_PASSWORD = "local-only-password"
$env:APM_SIGN_TIMESTAMP_URL = "http://timestamp.digicert.com"
```

None of these values should be committed to the repository.

## Build behavior

`packaging/windows/build_installer.ps1` now runs in:

- `unsigned` mode when no signing inputs are present
- `thumbprint` mode when `APM_SIGN_CERT_THUMBPRINT` is set
- `pfx` mode when `APM_SIGN_PFX_PATH` is set

If signing is requested but `signtool.exe` is unavailable, the build fails loudly.

## Verification

The build script verifies signatures with:

```powershell
Get-AuthenticodeSignature -FilePath "dist\APMultitool_Setup_v1.0.0-beta1.exe"
```

Expected result:

- `Status: Valid`

Manual UI verification:

1. Right-click the artifact
2. Open Properties
3. Check the Digital Signatures tab
4. Confirm publisher and timestamp

## Operator checklist

1. Confirm the active build host has `PyInstaller`, Inno Setup 6, and `signtool.exe`
2. Set thumbprint or PFX inputs locally
3. Run the beta1 build
4. Verify signatures on GUI exe, CLI exe, and installer
5. Save the SHA-256 checksum
6. Run the install, launch, support-bundle, uninstall, and reinstall smoke flow

## Current validation note

On the Codex workstation used for this batch:

- Inno Setup was present under Local AppData
- `PyInstaller` was not installed in the active Python environment
- no signing environment variables were present

That means signed beta1 artifact generation was wired and documented here, but not executed on this machine during this batch.
