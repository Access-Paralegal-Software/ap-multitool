---
id: ci_overview
title: Continuous Integration (CI) Overview
type: ops-manual
status: active
project: APMultitool
created_at: 2026-05-21
---

# Continuous Integration (CI) Overview

This document describes the Continuous Integration (CI) pipelines configured for APMultitool. The CI workflows automate test execution across multiple operating systems and handle cross-platform packaging.

---

## ⚙️ Workflows

The repository contains two main GitHub Actions workflows under `.github/workflows/`:

1.  **`tests.yml` (CI Test Suite)**: Executes unit and integration test subsets on every push or pull request targeting `master`.
2.  **`build.yml` (Cross-Platform Build Master)**: Compiles standalone executable bundles and installer files on commits to `master` or manual triggering.

---

## 🧪 CI Test Runner: `tests.yml`

To ensure changes do not break core logic or UI structures, `tests.yml` runs a matrix job testing the subsets defined by [run_core_tests.py](file:///C:/Users/aewoo/Desktop/Repos/ap-multitool/scripts/run_core_tests.py).

### Test Matrix
- **Operating Systems**: `windows-latest`, `macos-latest`, `ubuntu-latest`
- **Subsets**: `unit`, `integration`, `core`, `qt`, `cli`, `telemetry`, `packaging`

### Headless Linux Qt Test Execution
Qt/PySide6 GUI widgets require a windowing system server (like X11 or Wayland) to instantiate and layout widgets. Because Linux runners are headless server environments, directly launching GUI tests will fail with connection errors.

**Mitigation**: The Linux workflow installs a virtual framebuffer (`xvfb`) and uses `xvfb-run` to execute the Python test launcher:
```yaml
- name: Run Tests with Xvfb (Linux)
  if: runner.os == 'Linux'
  run: |
    xvfb-run --auto-servernum python scripts/run_core_tests.py --subset ${{ matrix.subset }}
```
This isolates the graphical elements in virtual memory, allowing test assertions (like widget states, label values, and model bindings) to run successfully without graphical displays.

---

## 📦 Packaging Pipeline: `build.yml`

The packaging workflow automates standalone executable generation for non-Windows platforms (acting as probes for macOS and Linux):

### 1. Ubuntu Runner (Linux)
- Installs `python3-tk` system dependencies.
- Runs PyInstaller to bundle the application using a colon-separated `--add-data` separator.
- Compiles a native Debian package installer (`.deb`) by setting up a standard control folder structures and packaging it using `dpkg-deb --build`.

### 2. macOS Runner (macOS)
- Runs PyInstaller to build a `.app` bundle.
- Generates a standard compressed Apple Disk Image (`.dmg`) using the native `hdiutil` utility.

> [!WARNING]
> While `build.yml` creates macOS `.dmg` and Linux `.deb` installers, these builds are **unsigned** and are not subject to regular automated functional test verification. Windows remains the primary, active validated lane.
