---
id: qt_cross_screen_parity_audit
title: Qt Cross-Screen Parity Audit
type: ops-audit
---

# Qt Cross-Screen Parity Audit

## Compiler View
- **Legacy Behavior**: Supported adding documents, enforcing page fit, toggling bookmarks, grayscale, and compression. Relied on synchronous execution.
- **Qt Behavior**: Fully mirrors feature set. Adds asynchronous background execution (`EngineJobWorker`) and Drag & Drop directly from the OS.
- **Differences/Gaps**: UI is completely non-blocking now. Queue re-ordering is visual and immediate.
- **Status**: Complete parity. No deferred items.

## Bates Stamping View
- **Legacy Behavior**: Used tkinter dialogs for font, size, and margin collision handling. Auto-incremented ledger via config file.
- **Qt Behavior**: Dedicated `BatesOptionsDialog`. Uses global `bates_registry` mapped to current active `Matter ID` in the File Room view to auto-increment properly. Console terminal output added for real-time tracking.
- **Differences/Gaps**: Qt version natively groups by Matter ID for auto-incrementing.
- **Status**: Complete parity with UX improvements.

## File Room View
- **Legacy Behavior**: Simple dropdown with hardcoded archetypes. Custom structure required manual text editing.
- **Qt Behavior**: Live `QTreeWidget` previews the exact structural hierarchy. Blueprint selection populates the tree immediately.
- **Status**: Strict superset of legacy capabilities.

## Shell Navigation & Help
- **Legacy Behavior**: Toplevel windows spawned for different tools.
- **Qt Behavior**: Unified `QStackedWidget` sidebar navigation.
- **Differences/Gaps**: Help view added natively to the stack rather than relying on external web hooks only.
