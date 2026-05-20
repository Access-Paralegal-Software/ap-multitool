# APMultitool Qt Application Structure

To maintain a clean, modular separation of visual components, styles, and background engine workers, the new Qt application is structured as follows.

---

## 📁 Repository Directory Layout

```
Access_Paralegal_PDF_Merger/
├── gui_apmultitool_qt.py           # Top-level bootstrap execution launcher
└── apmultitool_qt/                 # Qt PySide6 Application package
    ├── __init__.py                 # Package initializer
    ├── main.py                     # QApplication bootstrap & theme manager
    ├── shell.py                    # Main QMainWindow shell & sidebar layout
    ├── styles.py                   # Global style tokens and QSS stylesheet
    ├── core_bridge.py              # QThread and Qt Signal wrapper for core engine
    └── views/                      # Content views (swapped insideStackedLayout)
        ├── __init__.py             # Views export mappings
        ├── compiler.py             # Tab 1: Document Compiler panel
        ├── bates.py                # Tab 2: Bates Stamping & Log Console panel
        ├── fileroom.py             # Tab 3: File Room Case Tree builder
        └── about.py                # Help / About & CLI Companion description
```

---

## 📄 Module Responsibilities

### 1. `gui_apmultitool_qt.py` (Root)
- Entry point for the user or pyinstaller shortcuts. Imports `main` from `apmultitool_qt` and runs the application thread.

### 2. `apmultitool_qt/main.py`
- Instantiates the global `QApplication`.
- Configures environment-wide scale attributes (e.g. High-DPI scaling policies).
- Sets window title, loads application icons, loads the QSS stylesheet, and displays the `APMainWindow` shell.

### 3. `apmultitool_qt/shell.py`
- Inherits from `QMainWindow`.
- Implements the main window shell containing:
  - **Left Navigation Sidebar**: Contains flat, modern buttons representing tabs, allowing users to toggle visible frames.
  - **Right Content Frame**: Employs a `QStackedWidget` container displaying the active view.
  - **Bottom Status Bar**: Displays job progress and connectivity notices.

### 4. `apmultitool_qt/styles.py`
- Centralized style registry. Holds color role codes (`BRAND_JADE`, `BRAND_CHARCOAL`, `BRAND_LIGHT_GREY`), font definitions (using Outfit and JetBrains Mono fonts if available, falling back to Segoe UI/Consolas), and exports the QSS styling template.

### 5. `apmultitool_qt/core_bridge.py`
- Maps UI widgets to background processors using safe `QThread` wrappers and `QtCore.Signal` bounds. Prevents UI thread-blocking during long merge operations or Bates stamping loops.

### 6. `apmultitool_qt/views/`
- Contains decoupled widget classes representing each workflow area:
  - `CompilerView`: Document Compiler queue, options, and actions.
  - `BatesView`: Stamping target, parameters, console log, and settings modal.
  - `FileRoomView`: Case Matters and visual directory trees.
  - `AboutView`: App details, support tokens, and CLI instruction pointers.
