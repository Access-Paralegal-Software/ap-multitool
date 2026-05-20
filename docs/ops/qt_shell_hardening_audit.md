# APMultitool Qt Shell Hardening Audit

This audit evaluates the architectural infrastructure of the PySide6 prototype to identify vulnerabilities, boilerplate duplications, and layout inconsistencies prior to full feature migration.

---

## 🎨 1. Visual & Layout Boilerplate

1. **Repetitive Frame Margins**:
   - Every placeholder view manually configures layout margins (`left_layout.setContentsMargins(15, 15, 15, 15)` and `left_layout.setSpacing(12)`). This leads to minor variations across tabs. Margins and layouts should be inherited from standard layout constants or custom container components.
2. **Inline Styling Leakage**:
   - The tip labels underneath checkbuttons use hardcoded colors (`lbl_tip_bookmarks.setStyleSheet("color: #6B7280; font-size: 10px; margin-left: 26px;")`). This style should be isolated inside `styles.py` or wrapped in a custom `HintLabel` widget.
3. **Rigid Viewport Assumptions**:
   - Sidebars are constrained to strict fixed sizes (`left_panel.setMinimumWidth(320)`). This could truncate content on high-DPI displays or look too small on wide landscape tablet screens. Sidebars should leverage relative stretch ratios combined with absolute minimum thresholds.

---

## ⌨️ 2. Modal & Interaction Inconsistencies

1. **Ad-hoc Native Dialogs**:
   - Browsing targets uses raw system setups without folder filters or default output folder paths, leading to divergent behaviors across Windows/macOS/Linux. A unified `FileDialogHelper` wrapper is required.
2. **Lack of Dialog Standardizations**:
   - Alert notifications are built as ad-hoc `QMessageBox` popups inside individual views. Error messaging layout should be standardized to ensure that traceback details are scrollable and action prompts are uniform.

---

## 🧵 3. Engine Threading & Status Reporting

1. **Operation-Specific Workers**:
   - The `DiagnosticWorker` works for checking engine status, but copying this code for Bates Stamping and Document Compiler will lead to significant logic duplication. We need a generic `EngineJobWorker` that wraps `DocEngine.submit()` asynchronously and handles progress mapping.
2. **Ad-Hoc Progress UI**:
   - The views have to maintain local progress bars (`QProgressBar`) and console outputs. The statusbar should act as a centralized system indicator that can display progress percentages and cancel actions globally.
