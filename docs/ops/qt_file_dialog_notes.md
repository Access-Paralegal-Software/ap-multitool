# APMultitool Qt File Dialog Notes

This document specifies conventions for native file and directory selection dialogs.

---

## 🏛️ 1. API Architecture

All dialog helpers are exported from `apmultitool_qt.components.file_dialogs` and automatically resolve to the host operating system's native look and feel.

```python
from apmultitool_qt.components import file_dialogs
```

### Common Filters Specifications
To maintain visual consistency, use standard file types filter strings:

| Target Operations | Filter String |
| :--- | :--- |
| **All Supported Formats** | `Supported Files (*.pdf *.docx *.xlsx *.eml *.msg)` |
| **PDF Documents** | `PDF Documents (*.pdf)` |
| **Word Documents** | `Word Documents (*.docx)` |
| **Excel Spreadsheets** | `Excel Spreadsheets (*.xlsx)` |
| **Email Files** | `Email Archives (*.eml *.msg)` |

---

## 📦 2. Implementation Usage Examples

### A. Selecting a Single PDF (e.g. Bates View)
```python
file_path = file_dialogs.get_open_file(
    self,
    title="Select PDF for Stamping",
    filter_str="PDF Documents (*.pdf)"
)
if file_path:
    self.txt_target.setText(file_path)
```

### B. Adding Multiple Files to Compilation Queue
```python
files = file_dialogs.get_open_files(
    self,
    title="Add Documents to Queue",
    filter_str="Supported Files (*.pdf *.docx *.xlsx *.eml *.msg)"
)
for path in files:
    # insert path into table widget
    pass
```

### C. Spin Up Matter Workspace Folder Selection
```python
target_dir = file_dialogs.get_existing_directory(
    self,
    title="Choose Parent Workspace Location"
)
```

---

## ⚙️ 3. Native Platform Resiliencies

- **Default Start Location**: All helper dialogues default to the user's home directory (`~`) utilizing `os.path.expanduser("~")` instead of hardcoding root directories like `C:\` or `/` which crash on alternative platforms.
- **Null Selection Handling**: The helpers normalize cancel clicks by returning empty strings (`""`) or lists (`[]`). Views must verify that strings are not empty before proceeding with file operations.
