# APMultitool Qt Dialog Patterns

This document details the standardized patterns for modal notifications and confirmations inside the PySide6 views.

---

## 🏛️ 1. Usage API

Import the standard utilities from `apmultitool_qt.components.dialogs` to guarantee visual and keyboard parity across all tabs.

```python
from apmultitool_qt.components import dialogs
```

### A. Success & Operations Complete (`show_info`)
Use this to report successful operations (e.g. Bates Stamps complete, Case tree created).
```python
dialogs.show_info(self, "Spin Up Complete", "The matter directory structures were created successfully.")
```

### B. Parameter Warnings (`show_warning`)
Use this for inputs validation checks (e.g. missing matter path, empty prefix).
```python
dialogs.show_warning(self, "Invalid Prefix", "Bates Prefix cannot contain numeric or special characters.")
```

### C. Execution Failures (`show_error`)
Use this to output system tracebacks or process crashes. If a detailed error trace is passed, the modal will display a togglable "Show Details" area.
```python
try:
    # merge logic
    pass
except Exception as e:
    import traceback
    dialogs.show_error(
        self,
        "Compilation Failed",
        "An unexpected error occurred while parsing the Word streams.",
        details=traceback.format_exc()
    )
```

### D. Destructive Confirmations (`show_confirmation`)
Use this before clearing a files list or terminating an active run. It defaults to "No" to prevent accidental selection.
```python
if dialogs.show_confirmation(self, "Clear Queue?", "Are you sure you want to remove all files?"):
    self.table.setRowCount(0)
```

---

## ⌨️ 2. Accessibility & Behavior Rules

1. **Window Parent Bounds**: Always pass `self` (the active View or Window) as the parent parameter. This anchors the modal to the parent window center and blocks user focus interactions behind it.
2. **Keyboard Esc Escape Binds**: `QMessageBox` modals are wired to close and return `No` or cancel triggers immediately upon receiving an Escape key event.
3. **No Raw QMessageBox Constructing**: Views must not instantiate raw `QMessageBox` boxes directly; all prompts should route through the components helper package.
