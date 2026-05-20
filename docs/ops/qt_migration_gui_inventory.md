# APMultitool GUI Migration Inventory

This inventory document maps the visual components, operations, and states of the existing CustomTkinter desktop interface to prepare for the Qt/PySide6 migration.

---

## 🗂️ 1. Main Screens & Tab Control

The primary interface is contained in a single main window (`960x760` pixels minimum size `920x600`) using a tabbed control structure:

| Screen / Tab | Purpose | Input Widgets | Action Triggers | Output / Status Views |
| :--- | :--- | :--- | :--- | :--- |
| **Document Compiler** | Queue files for conversion and merge | File room table (draggable list), Bookmarks check, Standardize Fit check, Compress check | Add files, Move Up/Down, Remove, Clear, **Combine & Merge Files**, **Cancel Merge** | Status bar, success folder-opener popup |
| **Bates Stamping** | Apply Bates stamping to document | Target path entry, Case prefix, Start number, Separator, Collision check, Show Console check | Browse PDF, **Flatten & Apply Bates**, **Cancel Production**, **Advanced Stamp Options** | Real-time console logs box, status text line |
| **File Room & Case Trees** | Generate structured folder trees | Case Matter ID input field | Load Case Structure, **Spin Up Folder Tree** | File tree visualization container |

---

## 💬 2. Popups, Modals, & Dialogs

All modal popups block parent focus (`grab_set`) and center relative to the main window:

1. **About Software**:
   - Displays application title, version metadata (`config.py`), copyright, support security token (SHA-256 hash of hostname + username + version), and the CLI companion helper instruction card.
2. **License Agreement (EULA)**:
   - Displays scrollable, read-only license agreement text terms.
3. **Settings & Preferences**:
   - Displays appearance mode option menu (System, Light, Dark), current Master Case Folder workspace path (with a browse relocator), a toggle switch for Safeguard staging, and a button to open the Case Blueprint Architect.
4. **License Activation Modal**:
   - Form containing a text field for key input, validating on Return/Enter or clicking "Activate App".
5. **Advanced Case File-Tree Architect**:
   - Lists directories currently in the blueprints, allowing users to add or edit folder structures.
6. **Advanced Bates Stamping Options**:
   - Advanced compliance options for Bates placement (Top/Bottom, Left/Center/Right), text prefix spacing, font name (Arial/Courier/Calibri), font size, and color.

---

## ⚙️ 3. Core Engine Hooks & Background Processing

The GUI communicates with `core/engine.py` (which wraps background workers under `core/operations/`):

- **Merge/Compile Execution**:
  - Spawns a background `threading.Thread`.
  - Operates on a safe clone staging directory (if safeguarding is enabled).
  - Iterates through the files, calling PDF readers/writers.
  - Monitors `self.cancel_requested`. If True, stops processing immediately and deletes shadow staging folder.
- **Bates Stamping Execution**:
  - Invokes `DocEngine.submit(bates_job)`.
  - Pass progress callback `progress_cb()` to log execution lines in the console text box.
  - Monitors cancel action: sets `bates_job.status = JobStatus.CANCELLED`.

---

## ⚡ 4. High-Risk Migration Areas

1. **Thread-Safe Cancellation**:
   - CustomTkinter utilizes Tkinter's event loop, which can freeze if not carefully updated. Qt uses a much cleaner event loop with `QThread` and Signals/Slots.
   - **Risk**: Rewriting cooperative threading loops without causing deadlock or core engine issues.
2. **Custom File List Drag-and-Drop**:
   - Draggable lists and manual row reordering in Tkinter was built via treeview offsets.
   - **Risk**: Transitioning to `QListWidget` or `QTableWidget` drag-and-drop actions while keeping row moves intuitive.
3. **Dynamic Canvas Watermark**:
   - CustomTkinter loaded customized canvas slash graphics and blended logos at runtime using `Pillow`.
   - **Risk**: Doing the same graphics operations in Qt requires using `QPainter`, `QPixmap`, or stylesheet gradients.
4. **Settings & Registry Keys Sync**:
   - Licensing states and Bates start sequences are read/written directly via registry pathways (`pywin32` / `winreg`).
   - **Risk**: Ensuring the Qt app reads/writes the exact same registry keys to maintain seamless user data continuity.
