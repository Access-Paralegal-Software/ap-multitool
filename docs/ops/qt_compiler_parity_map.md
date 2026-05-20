# Document Compiler Parity Map & Audit

---
id: qt_compiler_parity_map
title: Document Compiler Parity Map
status: active
project: Access Paralegal
sprint: APMultitool-Qt-Compiler-Migration
created_at: 2026-05-20T03:19:00Z
updated_at: 2026-05-20T03:19:00Z
---

## 1. Executive Parity Audit

The legacy Document Compiler (`gui_apmultitool.py`) is a powerful multi-format merging interface. This document maps legacy Tkinter features to the PySide6 Qt implementation, detailing layout mapping, parameter mapping, and transition behaviors.

### Feature Parity Analysis

| Feature Area | Legacy Tkinter GUI | Target Qt Widgets View | Status |
| :--- | :--- | :--- | :--- |
| **Input Selection** | Directory Text Field + "Change Folder" Browse | Standard Folder Path LineEdit + "Browse" Button using `file_dialogs` | **Supported** |
| **File Queue** | `ttk.Treeview` containing index, file, and status | `QTableWidget` showing `#` index, `File Name`, `Path`, `Type`, `Size`, `Status` | **Supported** |
| **Add Files** | Native multi-file picker adding to list | `file_dialogs.get_open_files` feeding table | **Supported** |
| **Move Up / Down** | Manual `Move Up` and `Move Down` buttons | Selection-aware up/down swapping in `QTableWidget` | **Supported** |
| **Drag & Drop Reorder**| Custom Tkinter motion bindings | Interactive row selection and swapping or standard `QTableWidget` D&D | **Supported** (Via up/down buttons + D&D preview) |
| **Grayscale Toggle** | "Grayscale Output" check box | `QCheckBox("Grayscale Output")` mapped to `MergeParams` | **Supported** |
| **Bookmark Outline** | "Create Bookmarks per file" check box | `QCheckBox("Create Table of Contents Bookmarks")` | **Supported** |
| **Single-Page Fit** | "Enforce Single-Page Layout" checkbox | `QCheckBox("Enforce Standard Page Fit (Letter)")` | **Supported** |
| **Special Engines** | "Extract Email Attachments" checkbox | `QCheckBox("Extract Email Attachments")` | **Deferred** (Engine merge processes all kinds natively) |
| **Compress Streams** | "Optimize Output Size" checkbox | `QCheckBox("Compress Merged PDF Streams")` | **Supported** |
| **Progress Reporting** | `ctk.CTkProgressBar` + Progress text labels | Main Window status bar text & progress bar | **Supported** |
| **Cancellation Flow** | Cancellation flag checked inside merge loop | Cooperative job cancellation mapping to `EngineJobWorker` | **Supported** |

---

## 2. Option Parameter Mapping

All user parameters collected on the UI must map to `MergeParams` or `Job` attributes:

```python
# UI Option -> Job Input Specs & MergeParams
job_inputs = [InputSpec.from_path(file_path, order_index=idx) for idx, file_path in enumerate(queue_files)]
job_params = MergeParams(
    bookmarks=self.chk_bookmarks.isChecked(),
    enforce_page_size=self.chk_fit.isChecked(),
    grayscale=self.chk_grayscale.isChecked(),
    output_name=self.output_name_input.text().strip() or None
)
```

## 3. Intentional Deferrals

*   **Email Attachment Extraction Option Toggle**: Since the core engine's `merge` handler automatically processes `.eml` and `.msg` attachments if they exist, exposing a separate check box for this is redundant. The converter uses the sensible engine defaults.
*   **Target Page Size Dropdown**: Standard legal templates are configured at the engine/adapter layer. The dropdown dropdown menu can be deferred or styled as a static indicator to prevent layout crowding.
