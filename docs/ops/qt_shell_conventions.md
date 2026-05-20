# APMultitool Qt Shell Conventions

This document establishes design conventions for views and layouts loaded inside the APMultitool Qt application.

---

## 🏛️ 1. Panel Layout Structure

All primary tabs must follow the **Sidebar Configuration + Queue/Output Content** split-screen model.

1. **Left Sidebar Panel (Options & Actions)**:
   - Contains inputs, checkboxes, parameters.
   - Standard width: `320px` minimum, `360px` maximum.
   - Primary execution triggers (buttons) are pinned to the bottom of the left layout.
2. **Right Content Panel (Data & Preview)**:
   - Contains scrollable tables (`QTableWidget`), trees (`QTreeWidget`), or terminals (`QPlainTextEdit`).
   - Occupies all remaining screen width.

---

## 📐 2. Margins, Padding, & Spacing Scale

To ensure design consistency, never apply ad-hoc pixel values to widget layout spaces. Use standard margins:

- **Inner Container Margins**: Layouts within a `SectionCard` or option frame must use a standard padding of **15px** on all sides (`layout.setContentsMargins(15, 15, 15, 15)`).
- **Element Spacings**: Standard spacing between adjacent fields is **12px** (`layout.setSpacing(12)`).
- **Sub-hints Indents**: Low-contrast descriptions below checkbox fields must align with a **26px left margin** to sit directly under the checkbox text rather than the box icon.

---

## 🏷️ 3. Header Banner and Title Labels

Every tab view switch updates the top header banner labels:
- **Title**: Section name in 18px Bold.
- **Subtitle**: Action description in 12px Regular, muted grey.
Views should not include internal top headers within their panels; the window shell manages the central banner context.

---

## ⚙️ 4. Status Bar & Execution Feedback

- **Standard State**: Statusbar reads `Ready`.
- **Active Job State**: Statusbar reads `Running [Job Name]...` and displays a determinate progress bar overlay.
- **Finished/Completion State**: Displays a completion alert box and updates statusbar to `Job Complete` or `Job Failed`.
- **Button Locking**: During active runs, the main execution button must transition to **🛑 Cancel [Job Name]** (styled Rose Red), and all other options inputs are completely disabled.
