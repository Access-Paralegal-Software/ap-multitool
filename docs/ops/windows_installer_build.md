# APMultitool Windows Installer Build Requirements & Workflow

Last verified on 2026-05-21 for the `v1.0.0-beta1` packaging lane.

This document details the build prerequisites, compile-time tools, and the step-by-step pipeline execution for generating the APMultitool Windows installer executable.

## Prerequisites

To compile the Windows installer, the build machine must have:

### 1. Python Environment

- Python 3.10 or later
- Application dependencies installed in the active environment
- `PyInstaller` available either on PATH or via `python -m PyInstaller`

```powershell
pip install -r requirements.txt
pip install pyinstaller
```

### 2. Inno Setup 6

- Install Inno Setup 6.2.0 or newer.
- The build orchestrator searches for `ISCC.exe` in:
  1. system `PATH`
  2. `$env:LocalAppData\Programs\Inno Setup 6\ISCC.exe`
  3. `C:\Program Files (x86)\Inno Setup 6\ISCC.exe`
  4. `C:\Program Files\Inno Setup 6\ISCC.exe`

### 3. Optional signing tools

- Windows SDK with `signtool.exe`
- Either:
  - a certificate thumbprint in the local certificate store, or
  - a local `.pfx` file plus password

Signing is optional for local build validation and expected for the beta1 release cut.

## Build Invocation

From the repository root:

```powershell
powershell -File packaging/windows/build_installer.ps1
```

Explicit beta1 invocation:

```powershell
powershell -File packaging/windows/build_installer.ps1 -AppVersion 1.0.0 -ReleaseChannel -beta1
```

Signed build via thumbprint:

```powershell
$env:APM_SIGN_CERT_THUMBPRINT = "YOUR_CERT_THUMBPRINT"
powershell -File packaging/windows/build_installer.ps1 -AppVersion 1.0.0 -ReleaseChannel -beta1
```

Signed build via PFX:

```powershell
$env:APM_SIGN_PFX_PATH = "C:\secure\apmultitool-signing.pfx"
$env:APM_SIGN_PFX_PASSWORD = "set-locally-only"
powershell -File packaging/windows/build_installer.ps1 -AppVersion 1.0.0 -ReleaseChannel -beta1
```

## Pipeline Phases

1. `prepare_bundle.ps1`
   - rebuilds the GUI and CLI executables
   - stages `dist\APMultitool_Bundle\`
   - stamps the bundle README with the current version

2. Bundle validation
   - verifies GUI exe, CLI exe, assets, license, and bundle README

3. Optional pre-installer signing
   - signs `Access_Paralegal_Multitool.exe`
   - signs `apmultitool.exe`
   - verifies signatures with `Get-AuthenticodeSignature`

4. Inno Setup compilation
   - compiles `packaging/windows/apmultitool_installer.iss`
   - emits `dist\APMultitool_Setup_v1.0.0-beta1.exe`

5. Optional installer signing and checksum
   - signs the final installer in signed mode
   - verifies the signature again
   - writes `dist\APMultitool_Setup_v1.0.0-beta1.exe.sha256`

## Build Modes

- Unsigned mode:
  - no signing inputs provided
  - useful for local packaging and uninstall validation

- Signed mode:
  - thumbprint or PFX inputs provided
  - required for the intended beta1 release artifact

If signing is requested but `signtool.exe` is not available, the build fails loudly instead of silently degrading.

## Output Artifacts

- `dist\Access_Paralegal_Multitool.exe`
- `dist\apmultitool.exe`
- `dist\APMultitool_Bundle\...`
- `dist\APMultitool_Setup_v1.0.0-beta1.exe`
- `dist\APMultitool_Setup_v1.0.0-beta1.exe.sha256`

## Troubleshooting

- `No module named PyInstaller`
  - install `pyinstaller` into the active Python environment

- `ISCC.exe was not found`
  - install Inno Setup 6 or add it to PATH

- signing requested but `signtool.exe` missing
  - install the Windows SDK or use unsigned mode for local-only validation

- signature status is not `Valid`
  - confirm the certificate chain and timestamp server reachability on the build host
