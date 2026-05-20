---
id: qt_pyinstaller_profile
title: Qt PyInstaller Profile
type: ops-audit
---

# Qt PyInstaller Excludes Profile

## Context
By default, PyInstaller recursively traces dependencies and includes everything imported by the primary GUI library. PySide6 is extremely heavy because it bundles an entire C++ application framework, including embedded Chromium (WebEngine), QML scripting engines, and low-level hardware controllers. APMultitool only requires the `QtWidgets`, `QtCore`, and `QtGui` namespaces.

## Pruning Applied
We explicitly appended the following blocks to `ap_multitool.spec` to forcibly exclude massive unused libraries:

### Web & Network
- `PySide6.QtWebEngine`
- `PySide6.QtWebEngineCore`
- `PySide6.QtWebEngineWidgets`
- `PySide6.QtNetwork`
- `PySide6.QtWebSockets`

### QML & Scripting
- `PySide6.QtQml`
- `PySide6.QtQuick`

### Hardware & Peripherals
- `PySide6.QtBluetooth`
- `PySide6.QtMultimedia`
- `PySide6.QtPositioning`
- `PySide6.QtLocation`
- `PySide6.QtSensors`
- `PySide6.QtNfc`

### Databases
- `PySide6.QtSql`

### Legacy GUI Framework
- `tkinter` (Explicitly dropped from both CLI and GUI builds as we have finalized the migration to Qt).
- `PySide6` entirely excluded from the CLI build since the CLI is completely headless.

## Reverting Prunes
If a future sprint introduces a new feature that inherently relies on these submodules (e.g., embedding a web browser using WebEngine, or migrating to QML for animations), simply remove the specific string from the `excludes=[]` list in `ap_multitool.spec` and re-run the build pipeline.
