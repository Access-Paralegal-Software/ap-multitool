# Document Compiler View Specification

---
id: qt_compiler_view_spec
title: Document Compiler View Specification
status: active
project: Access Paralegal
sprint: APMultitool-Qt-Compiler-Migration
created_at: 2026-05-20T03:20:00Z
updated_at: 2026-05-20T03:20:00Z
---

## 1. Screen Layout & Widgets

The Document Compiler view is split horizontally using `QSplitter` to separate configuration settings from the compilation queue.

```
+-------------------------------------------------------+
|  DOCUMENT COMPILER (Header Title)                    |
+------------------------------------+------------------+
| Settings (Left Card, 340px max)    | Queue (Right Card)|
|                                    |                  |
| [ ] Create Outline Bookmarks       | Output Folder:   |
| [ ] Enforce Standard Page Fit      | [ /path/to/dir ] |
| [ ] Compress PDF Streams           |                  |
| [ ] Grayscale Output               | Queue Table:     |
|                                    | [ # | Name | Size|]
| Output PDF Name:                   | [ 1 | doc1 | 2MB ]|
| [ MyMerge.pdf                  ]   |                  |
|                                    | [ Move Up ][Down]|
| +--------------------------------+ |                  |
| | 🚀 COMBINE & MERGE FILES       | | [ Add ][ Remove ]|
| +--------------------------------+ | [ Clear Queue  ] |
+------------------------------------+------------------+
```

### Components Used (from `apmultitool_qt.components`):
- `SectionCard` (Left Panel & Right Panel Containers)
- `FormRow` (Aligned parameters and directory inputs)
- `ActionBar` (Control alignments for buttons)
- `HintLabel` (Detailed setting guidance text)
- `EmptyStateWidget` (Renders inside the stacked queue table layout when empty)

---

## 2. Interactive Behaviors

### Queue Ordering Control
- **Up / Down Swapping**: If a row is selected in the queue, clicking "Move Up" swaps the selected row's data and selection focus with the row above it. "Move Down" swaps with the row below it.
- **Index Normalization**: Every modification to the queue triggers an index recalculation to refresh the `#` column with sequential numbers starting at `1`.

### Engine Integration & Async Job execution
1. **Intake Validation**: The interface verifies that the queue has at least one file, that the output folder exists, and that the output PDF name is not empty.
2. **Control Disabling**: During execution, settings checkboxes, browse buttons, and queue modifier buttons are disabled.
3. **Execution Worker**:
   - Spawns an `EngineJobWorker` running on a separate `QThread`.
   - Connects status updates to the status bar and progress bar.
   - Converts the primary action button to a red "🛑 CANCEL COMPILE" button.
4. **Completion / Failure States**:
   - Re-enables all disabled settings.
   - Refreshes status labels.
   - Shows standardized alerts upon completion or cancellation.
