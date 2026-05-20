# Qt Bates View Specification

This document details the layout structure, interactive states, and threading specifications of the Bates View inside `apmultitool_qt`.

## 1. Visual Layout Structure

- **Main Panel Layout**: Split layout using `QSplitter`.
  - **Left Sidebar Card (`SectionCard`)**:
    - **Target Group**: File picker input box + browse button.
    - **Protocol Group**: Form rows for Prefix entry, Start Index entry, and Separator combo box (`_`, `-`, `(None)`).
    - **Advanced Trigger**: An action button launching the `BatesOptionsDialog` modal.
    - **Stretch + Primary Action Bar**: Large action button to start/cancel stamping.
  - **Right Console Card (`SectionCard`)**:
    - Console Title label.
    - Console Output terminal (`QPlainTextEdit` in read-only mode).
    - "Clear Console" secondary button.

## 2. Interactive & State Behavior

- **State Lock (`toggle_inputs(enabled: bool)`)**:
  During active background stamping runs, all parameter fields, file browse buttons, separator dropdowns, and option settings triggers MUST be disabled to ensure input integrity.
- **Dynamic Run/Cancel Toggle**:
  - **Idle State**: The run button shows `⚡ FLATTEN & APPLY BATES STAMPS` in brand accent color.
  - **Active State**: The button transforms into a red `🛑 CANCEL PRODUCTION` button. Clicking it sets a cooperative cancellation flag, initiating a safe abort sequence on the background thread.
- **Autoincrement Focus Out Tracker**:
  Focus out events on the prefix box trigger an inspection of `self.bates_registry` mapped under the active Case/Matter ID reference. If a matching prefix index exists, it automatically pre-populates the starting index field.

## 3. Advanced Options Dialog

The `BatesOptionsDialog` inherits from `QtWidgets.QDialog` and configures the following settings:
- **Font Face**: Arial, Times New Roman, Calibri, Helvetica, Courier.
- **Font Size**: 10, 11, 12, 14.
- **Stamp Placement**: Bottom Right, Bottom Center, Top Center, Top Right, Top Left, Bottom Left.
- **Collision Avoidance**: A checkbox shrinking page contents to fit margin boundaries.
- **File Naming Protocol**: `Prefix_Start-End` or `Prefix_StartOnly`.
- **Output Folder Policy**: `Nested Folder` (creates a directory within the source location), `Same as Source` (overwrites or appends directly in the source directory), or `Custom Location` (prompts directory selection).
