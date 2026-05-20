# Qt / PySide6 Developer Setup Guide

This document describes how to configure your development environment, install the required PySide6 dependencies, and run the new cross-platform Qt version of APMultitool.

---

## 📦 1. Installation of Dependencies

The Qt version of APMultitool utilizes **PySide6** (Qt 6 bindings for Python). To set up your workspace:

### Step 1: Install PySide6
In your active virtual environment or python console, run:
```powershell
pip install PySide6
```

Verify the installation succeeded by checking version numbers in python:
```powershell
python -c "import PySide6; print(PySide6.__version__)"
# Expected output: 6.x.x
```

### Step 2: Install PyInstaller (For Packaging)
If you intend to build standalone executables, ensure PyInstaller is installed:
```powershell
pip install pyinstaller
```

---

## 🚀 2. Running the Qt Application

The Qt application is located in the `apmultitool_qt/` package directory, with a bootstrap launcher at `gui_apmultitool_qt.py` in the repository root.

To launch the desktop interface:
```powershell
python gui_apmultitool_qt.py
```

*Note: The existing Tkinter-based interface (`gui_apmultitool.py`) and command-line interface (`cli.py`) remain completely untouched and fully functional during the migration phase.*

---

## 🛠️ 3. Platform-Specific Setup Assumptions

### Windows:
- Native rendering utilizes standard Windows styles. QSS overrides are applied to enforce color roles and layout borders.

### macOS:
- To prevent thread-locking issues, ensure that all UI-updating signals are emitted from background processes back to the primary thread via `QtCore.Signal`. Do not execute GUI manipulations from raw Python threads.

### Linux:
- Requires standard X11 or Wayland display server backends. On minimal distributions, ensure standard system libraries (e.g., `libGL.so.1`, `fontconfig`) are installed.
- Run:
  ```bash
  sudo apt-get install python3-pyside6.qtwidgets
  ```
  if the pip version encounters system library loader conflicts.

### Tablets (Android / iOS):
- When developing for tablets, configure viewport layouts using standard scaling layouts (`QSplitter` and grids) rather than absolute pixel coordinates. Enforce touch margin paddings of at least 8px between components.
