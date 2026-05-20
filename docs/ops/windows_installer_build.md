# APMultitool Windows Installer Build Requirements & Workflow

This document details the build prerequisites, installation of compile-time tools, and the step-by-step pipeline execution for generating the APMultitool Windows Installer executable.

## 📋 Prerequisites

To successfully compile the APMultitool Windows Installer, the build machine must have the following software installed:

### 1. Python Environment
- **Python Version**: Python 3.10 or later (tested on Python 3.14.4).
- **Core Dependencies**: The standard application package dependencies must be installed in the Python environment:
  ```powershell
  pip install -r requirements.txt
  ```
- **PyInstaller**: PyInstaller is required to freeze Python scripts into executable formats. Install it via pip:
  ```powershell
  pip install pyinstaller
  ```
  *Note: The compiler pipeline supports running PyInstaller both globally (if on system PATH) and as a fallback via the active Python interpreter module (`python -m PyInstaller`).*

### 2. Inno Setup 6
- **Tool**: Jordan Russell's Inno Setup 6 (specifically version 6.2.0 or newer).
- **Installation**: Can be downloaded from [Inno Setup Downloads](https://jrsoftware.org/isdl.php).
- **Default Installation Paths**: The compiler orchestrator searches for `ISCC.exe` in the following locations automatically:
  1. System `PATH` environment variable.
  2. Local AppData: `$env:LocalAppData\Programs\Inno Setup 6\ISCC.exe` (User-level install).
  3. Program Files (x86): `C:\Program Files (x86)\Inno Setup 6\ISCC.exe` (System-level install).
  4. Program Files: `C:\Program Files\Inno Setup 6\ISCC.exe` (System-level install).

---

## 🛠️ Build Pipeline Walkthrough

The entire packaging flow is wrapped inside a single PowerShell script: `packaging/windows/build_installer.ps1`.

### Build Invocation
From the repository root directory, execute:
```powershell
powershell -File packaging/windows/build_installer.ps1
```

### Pipeline Execution Phases:
1. **Unified Bundle Preparation (`prepare_bundle.ps1`)**:
   - Cleans the build caches (`build/` and `dist/`).
   - Runs PyInstaller to compile both `Access_Paralegal_Multitool.exe` (GUI) and `apmultitool.exe` (CLI).
   - populates the staging directory at `dist\APMultitool_Bundle\` with:
     - GUI & CLI executables.
     - Static UI texture assets.
     - License file.
     - Readme manual.
     - Batch script launcher helper (`launch_cli_help.bat`).

2. **Bundle Verification**:
   - Inspects the staging directory to ensure all required assets are present and are non-zero byte size.

3. **Inno Setup Location**:
   - Detects the presence of `ISCC.exe` from the standard location candidate list.

4. **Inno Setup Compilation (`apmultitool_installer.iss`)**:
   - Compiles the script into `dist\APMultitool_Setup_v0.5.0.exe`.
   - Packages files under solid LZMA2/max compression.
   - Registers user-level PATH additions.

5. **Release Integrity Checksum**:
   - Computes a SHA-256 hash of the generated installer.
   - Saves it in `dist\APMultitool_Setup_v0.5.0.exe.sha256`.

---

## ⚠️ Troubleshooting

- **Error: PyInstaller not found**: Ensure your virtual environment is active or run `pip install pyinstaller` under the global Python environment.
- **Error: ISCC.exe not found**: Make sure Inno Setup 6 is installed. If installed in a non-standard location, add its installation path to your Windows environment variables.
- **Permission Denied (`_append_data_to_exe` warning)**: Close any running instances of `Access_Paralegal_Multitool.exe` or `apmultitool.exe` before rebuilding.
