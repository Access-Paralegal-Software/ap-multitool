---
id: macos_host_profile_apmultitool
title: macOS Host Profile — APMultitool Packaging
type: ops
status: placeholder
project: Access Paralegal / APMultitool
created: 2026-05-21
---

# macOS Host Profile — APMultitool Packaging

This document records the macOS host environment used to perform a local packaging dry-run. It is intended to be filled in by the operator who runs the first bare-metal macOS build.

## Current State

**No macOS host was available during lane ho_0046 (2026-05-21).** The development environment is Windows 11 Home (x64). All changes in this lane were static-review and script corrections; no DMG was produced locally.

This file is a placeholder for the operator who will perform the first bare-metal run.

---

## Host Profile Template

Fill in this section when running the first local macOS build:

| Field | Value |
|---|---|
| macOS version | _(e.g., Sonoma 14.x, Ventura 13.x)_ |
| Architecture | _(Intel x86_64 / Apple Silicon ARM64)_ |
| Xcode version | _(output of `xcode-select --version`)_ |
| CLT installed | _(yes/no — `xcode-select -p`)_ |
| Python source | _(Homebrew / pyenv / system / other)_ |
| Python version | _(output of `python3 --version`)_ |
| pip version | _(output of `pip3 --version`)_ |
| Virtual env tool | _(venv / conda / pyenv-virtualenv / none)_ |
| PyInstaller version | _(output of `pyinstaller --version` after install)_ |
| PySide6 version | _(output of `python3 -c "import PySide6; print(PySide6.__version__)"`)_ |

---

## Setup Steps (to Record on First Run)

1. **Clone the repo:**
   ```bash
   git clone https://github.com/woodyardae/ap-multitool.git
   cd ap-multitool
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install pyinstaller pypdf reportlab pikepdf pillow PySide6 pymupdf extract-msg cryptography
   ```

4. **Run the unsigned build:**
   ```bash
   chmod +x packaging/macos/build_app.sh
   bash packaging/macos/build_app.sh
   ```

5. **Record any deviations from the above steps in this document.**

---

## First-Run Observations Template

Fill in after the first bare-metal run:

| Check | Result |
|---|---|
| Script completes without error | _(yes/no)_ |
| `dist/Access_Paralegal_Multitool.app` produced | _(yes/no)_ |
| `dist/apmultitool` CLI binary produced | _(yes/no)_ |
| `dist/APMultitool_Setup_v*.dmg` produced | _(yes/no)_ |
| `.app` launches on macOS | _(yes/no / crashes with: ...)_ |
| UI renders without immediate crash | _(yes/no)_ |
| DMG mounts and displays app layout | _(yes/no)_ |
| Any Gatekeeper / quarantine issues | _(note if applicable)_ |

---

## Known Pre-Run Issues (Identified by Static Review — ho_0046)

The following issues were identified from static code review on Windows and corrected before any bare-metal run:

| File | Issue | Fix Applied |
|---|---|---|
| `packaging/macos/build_app.sh` line 109 | Referenced legacy `gui_apmultitool.py` (CustomTkinter) instead of active `gui_apmultitool_qt.py` (PySide6 Qt) | Changed to `gui_apmultitool_qt.py` |
| `.github/workflows/macos_packaging_probe.yml` pip install | Installed `customtkinter` (legacy) instead of `PySide6` (active Qt framework) | Replaced `customtkinter` with `PySide6` |
| `docs/ops/qt_macos_packaging_readiness.md` | Stated "No build scripts exist in `packaging/macos/`" — stale since ho_0030 | Updated to reflect current pipeline state |

---

## Disclaimer

macOS is a **probe/preparation** platform for APMultitool. No macOS support is claimed until an end-to-end notarized build has been validated on bare-metal hardware. Windows is the active alpha release track.
