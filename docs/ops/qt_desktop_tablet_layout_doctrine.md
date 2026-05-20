# APMultitool Qt Desktop & Tablet Layout Doctrine

This document defines layout guidelines to support desktops (Windows, macOS, Linux) and tablets (iPads, Android tablets) within a single PySide6 codebase.

---

## 📱 1. Tablet-First Responsive Philosophy

Rather than developing separate desktop and mobile views, APMultitool leverages **Qt Widgets Layout Managers** configured to scale fluidly from standard 13" laptops up to 27" monitors, and down to 10" tablet landscapes.

- **Landscape Mode**: The primary viewport layout assumes a landscape orientation (minimum width `920px`, typical tablet ratio 4:3 or 16:10).
- **Portrait Reflow**: To preserve legibility when a tablet is rotated vertically:
  - We utilize a flexible `QSplitter` separating the configuration panels (left) and lists/consoles (right).
  - On narrow screens (width < `768px`), the left panel can collapse or slide out, or wrap above the list using a vertical scroll layout.
- **Phone Exclusion**: Sizing layouts for phone viewports (e.g. portrait 375x812) are **deferred** to reduce code complexity. The interface is optimized exclusively for screens of tablet scale and larger.

---

## 🎯 2. Touch Target & Sizing Guidelines

Legal professionals operating tablets require clear touch targets to prevent accidental execution triggers or mis-clicks:

1. **Minimum Touch Targets**:
   - All interactive components (buttons, dropdown menus, entries, checkboxes) must present a minimum clickable footprint of **48x48 pixels**.
   - Checkboxes are styled with larger indicator icons (`18x18px` minimum) and spaced labels.
2. **Interactive Gaps**:
   - Standardize a **12px margin** between adjacent touch fields. This prevents double-selection errors.
3. **Scrollable Container Zones**:
   - Touch screens rely on scrolling. Option groups that exceed 400px height are wrapped inside a `QScrollArea` equipped with wide scrollbars (minimum `12px` scrollbar width) to allow easy finger-dragging.

---

## 📐 3. Qt Widget Layout Architecture

To implement this doctrine:

### Grid & Stretch Sizing Policies:
- **Left Options Sidebar (Fixed Max-Width)**:
  - Width: Fixed at `340px`.
  - Sizing Policy: Horizontal: `Fixed` / Vertical: `MinimumExpanding`.
  - Enforces that settings stay readable without stretching into long, empty rows on wide monitors.
- **Right Queue/Output Panel (Stretching)**:
  - Width: Expanding (`QSizePolicy::Expanding`).
  - Occupies 100% of remaining screen width.
  - Table columns use stretch headers to auto-fit cell margins.
- **Layout Spacers**:
  - Always use layout stretch variables and spacer widgets (`QSpacerItem`) to push actions to the bottom or sides of screens, avoiding fixed layout coords.
- **High-DPI Scaling**:
  - Main bootstrap enables Qt Core scaling overrides:
    ```python
    from PySide6 import QtCore
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
    ```
