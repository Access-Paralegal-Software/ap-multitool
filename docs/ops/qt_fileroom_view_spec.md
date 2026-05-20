# Qt File Room & Trees View Specification

This document details the visual layouts, behaviors, validation rules, and async operations of the File Room view inside `apmultitool_qt`.

## 1. Visual Layout Structure

- **Main Panel Layout**: Split layout using `QSplitter`.
  - **Left Card (`SectionCard`)**:
    - **Header Title**: "FILE ROOM CONFIG"
    - **Matter ID Reference**: FormRow with a `QLineEdit` (`self.txt_case_id`) defaulting to `"2026-AP-9908"`.
    - **Blueprint Selection**: FormRow with a `QComboBox` (`self.cb_blueprints`) selecting folder tree archetypes.
    - **Custom Architect Actions**: Action buttons row to "+ Add Folder", "❌ Remove Folder", "🔄 Reset Defaults", and "🗑️ Clear All".
    - **Stretch + Primary Action Bar**: Primary action button to "Spin Up Folder Tree" and secondary run indicators.
  - **Right Card (`SectionCard`)**:
    - **Header Title**: "FOLDER TREE ARCHITECTURE PREVIEW"
    - **Preview Area**: A hierarchical `QTreeWidget` (`self.tree_widget`) showing root case node and child directories dynamically.

## 2. Interactive & State Behavior

- **Autobuild Tree Preview**:
  Any changes to the Matter ID text box, blueprint combo selection, or custom folder hierarchy will instantly trigger `self.rebuild_preview()`, refreshing the `QTreeWidget` hierarchy so the user sees their changes in real-time.
- **Dynamic Variable Substitution**:
  The directory builder replaces the `{Date}` placeholder with the current `YYYY-MM-DD` date at run-time, automatically.
- **Destination Validation & Safety**:
  Before spinning up directory trees, the system prompts the user to select the destination workspace folder.
  - If the directory already contains folders or files, the UI displays a warning confirmation.
  - Characters illegal in Windows file paths (e.g. `*`, `?`, `|`) are stripped or replaced with safe fallbacks.
