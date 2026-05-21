---
id: pm_report_ho_0050_2026_05_21_windows_beta1_signed_installer_and_clean_uninstall
title: Project Manager Report - Windows Beta1 Signed Installer and Clean Uninstall
type: pm-report
status: completed
project: APMultitool
created_at: 2026-05-21
---

# Project Manager Report: Windows Beta1 Signed Installer and Clean Uninstall

## 1. Executive Summary

This lane moved the Windows packaging path onto `v1.0.0-beta1`, tightened installer metadata, added explicit unsigned-versus-signed build behavior, documented uninstall expectations, and produced a beta1 installer from the current staged Windows bundle.

The result is mixed:

- the installer script and docs are materially better aligned for a beta1 cut
- a beta1 installer was successfully compiled and inspected locally
- a real install and uninstall cycle was executed successfully
- signing was not performed because no local signing inputs were present
- reinstall validation was blocked after uninstall because the local `dist/` artifacts disappeared during the validation sequence and `PyInstaller` is not installed on this workstation to regenerate them
- the installed CLI binaries were confirmed to be stale relative to current source and did not include the newer `support-bundle` subcommand, which is a beta1 packaging blocker until the bundle is rebuilt from current source

## 2. Version and Naming Confirmation

Confirmed and updated:

- app version target: `v1.0.0-beta1`
- installer filename target: `APMultitool_Setup_v1.0.0-beta1.exe`

Updated versioning surfaces:

- `config.py` now exports `v1.0.0-beta1`
- `core/__init__.py` now exports `1.0.0` plus `-beta1`
- `apmultitool_qt/views/about.py` now defaults the Build ID label from the shared version source
- `apmultitool_qt/main.py` now sets application metadata version from core version constants
- `cli.py` now reports `APMultitool CLI v1.0.0-beta1` from shared core version constants

Observed artifact:

- compiled installer: `dist\APMultitool_Setup_v1.0.0-beta1.exe`
- generated checksum during validation: `A3981DA9F9A1C69318266F5E30CD062C0AB95338079B59C0613665627B71CC5D`

## 3. Packaging and Metadata Changes

### Installer metadata

Updated `packaging/windows/apmultitool_installer.iss` to:

- default to `-beta1`
- include the release suffix in `AppVerName`
- populate additional installer version metadata:
  - company
  - description
  - product name
  - text version

Observed metadata on the compiled beta1 installer:

- `ProductName`: `APMultitool`
- `CompanyName`: `Access Paralegal Systems`
- `FileDescription`: `APMultitool Windows Setup Installer`
- `ProductVersion`: `1.0.0`
- `FileVersion`: `v1.0.0-beta1`

### Executable metadata wiring

Added `packaging/windows/apmultitool_version_info.txt` and wired it into both GUI and CLI executables through `ap_multitool.spec`.

Important limitation:

- the existing staged executables in `dist/` were not rebuilt on this workstation because `PyInstaller` is not installed
- that means the spec-level version metadata wiring is implemented in source, but not validated against freshly rebuilt beta1 executables here

## 4. Signing Inputs and Actual Signing Status

Expected signing inputs:

- `APM_SIGN_CERT_THUMBPRINT`
- `APM_SIGN_PFX_PATH`
- `APM_SIGN_PFX_PASSWORD`
- optional `APM_SIGN_TIMESTAMP_URL`

Implemented behavior in `packaging/windows/build_installer.ps1`:

- unsigned mode when no signing inputs are provided
- thumbprint mode when a local certificate-store thumbprint is provided
- PFX mode when a local `.pfx` path is provided
- loud failure if signing is requested but `signtool.exe` is unavailable
- signature verification via `Get-AuthenticodeSignature`

Actual signing performed in this batch:

- **not performed**

Reason:

- no signing environment variables were present on this workstation

Observed signature state:

- existing alpha installer: `NotSigned`
- existing alpha GUI executable: `NotSigned`
- compiled beta1 installer: `NotSigned`

No certificates, PFX files, passwords, or secret signing material were committed.

## 5. Install, Use, Uninstall, and Reinstall Validation

### Install

Executed a silent install of the compiled beta1 installer into:

- `C:\Users\aewoo\AppData\Local\Programs\APMultitool`

Observed installed files:

- `Access_Paralegal_Multitool.exe`
- `apmultitool.exe`
- `launch_cli_help.bat`
- `LICENSE`
- `logo_small.png`
- `README_BUNDLE.txt`
- `unins000.dat`
- `unins000.exe`
- `water_texture.png`

Observed Start Menu entries:

- `APMultitool.lnk`
- `APMultitool CLI Help.lnk`
- `Uninstall APMultitool.lnk`

Observed uninstall entry:

- `DisplayName`: `APMultitool (Remove Only)`
- `DisplayVersion`: `1.0.0`

Observed PATH state:

- user PATH contained `C:\Users\aewoo\AppData\Local\Programs\APMultitool`

### Run / hero-flow validation

The GUI hero-flow pass was **not** completed in this batch because the desktop app launch path is gated by the activation dialog and that is outside the conservative scope of this packaging lane.

Instead, a real installed Bates flow was validated through the installed CLI binary:

- created sample file: `C:\tmp\stax_beta1_sample.pdf`
- executed installed CLI Bates operation
- produced output:
  - `C:\tmp\beta1_bates_output\BETA-0000001-0000001.pdf`

This confirms that the installed package can execute at least one real document-processing flow after install.

### Support bundle validation

Attempted:

- installed CLI `support-bundle` subcommand

Observed result:

- failed because the installed `apmultitool.exe` did not include `support-bundle`

Interpretation:

- the staged Windows bundle currently present in `dist/` is stale relative to current repository source
- beta1 should not ship until the bundle is rebuilt from current source on a machine with `PyInstaller`

### Uninstall

Executed silent uninstall via:

- `%LOCALAPPDATA%\Programs\APMultitool\unins000.exe /VERYSILENT /SUPPRESSMSGBOXES`

Observed uninstall behavior:

- install directory removed successfully
- Start Menu group removed
- uninstall registry entry removed
- user PATH entry removed

Observed non-removal behavior:

- no evidence that uninstall attempted to delete vault files, support bundles, or arbitrary user documents

### Reinstall

Intended next step:

- reinstall the same beta1 installer and confirm no stale-state conflict

Blocked result:

- reinstall was **not completed**

Reason:

- after uninstall, the local workspace `dist/` artifacts used for validation were no longer present
- `PyInstaller` is not installed on this workstation, so the bundle could not be regenerated to recreate the beta1 installer in-session

## 6. Leftover Artifacts and Assessment

Observed acceptable retained items:

- none were explicitly created by this packaging-only validation outside the sample test output in `C:\tmp`

Observed problematic or surprising artifacts:

- the repository `dist/` directory remained present but its installer/bundle contents were no longer available after the validation cycle

Assessment:

- this is not user-data loss
- it is a packaging-validation environment issue and should be treated as a blocker for fully repeatable reinstall validation on this workstation until the build host is restored with `PyInstaller`

## 7. Files Changed

- `config.py`
- `core/__init__.py`
- `cli.py`
- `apmultitool_qt/main.py`
- `apmultitool_qt/views/about.py`
- `ap_multitool.spec`
- `packaging/windows/apmultitool_installer.iss`
- `packaging/windows/build_installer.ps1`
- `packaging/windows/prepare_bundle.ps1`
- `packaging/windows/apmultitool_version_info.txt`
- `docs/ops/windows_installer_build.md`
- `docs/ops/windows_installer_validation.md`
- `docs/ops/windows_beta1_signing_overview.md`
- `docs/ops/windows_uninstall_behavior_beta1.md`
- `docs/ops/release_artifact_naming_windows.md`
- `docs/ops/release_artifact_conventions.md`
- `docs/README.md`
- `tests/test_packaging.py`

## 8. Safety Confirmation

- No certificates, PFX files, passwords, or secret signing material were committed.
- User vaults, user-created documents, and support bundles were not silently deleted by uninstall during observed behavior.
- Vault persistence, encryption, and hardware identity logic were untouched.
- Core remains Qt-unaware.

## 9. Release Readiness Call

Current status for Windows `v1.0.0-beta1`:

- **packaging path:** improved
- **installer metadata:** improved and locally observed
- **signing hooks:** implemented
- **signed build:** not yet produced
- **uninstall behavior:** observed and acceptable
- **reinstall cycle:** incomplete on this workstation
- **beta blocker:** stale staged binaries missing the current `support-bundle` CLI functionality

Recommended next step before shipping beta1:

1. restore a Windows build host with `PyInstaller`
2. rebuild the GUI and CLI binaries from current source
3. regenerate the beta1 installer
4. sign it if credentials are available
5. rerun install, support-bundle, uninstall, and reinstall validation end to end
