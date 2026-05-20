# APMultitool GUI UX & Visual Audit

This document audits the layout, alignment, typography, visual semantics, keyboard accessibility, and flow of the APMultitool desktop interface to identify release-ready refinements.

---

## 🎨 Visual Audit (Aesthetics & Layout)

1. **Hierarchy & Spacing**:
   - The left panels in `Document Compiler` and `Bates & Security` have multiple checkbox options stacked directly under headers. They lack visual groupings or category dividers.
   - Vertically, the spacing between options is tight (6px padding), making it look cramped on high-DPI displays.
   - Text inputs and dropdown menu controls have varying widths (e.g., OptionMenus at 260px vs target entries at 310px). They should be normalized.

2. **Typography**:
   - The application mixes default UI font settings with explicit fonts ("Segoe UI" 14/15/16, "Inter" 9, etc.). Font usage must be standardized using theme-inherited configurations.
   - Header labels within left option boxes require standard bolding and size hierarchy to distinguish from regular options.

3. **Backgrounds & Contrast**:
   - Tiled water texture caustics composite nicely, but high transparency in dark mode can sometimes lead to lower readability in text inputs.
   - High-contrast text selections in CustomTkinter are handled correctly via the theme, but dropdown lists are styled via custom fonts without clear select-contrast styling.

---

## ⌨️ Keyboard & Interaction Audit (Accessibility)

1. **Modal Focus Traps**:
   - Windows like `show_bates_options_modal`, `show_activation_window`, `show_about_window`, and `show_settings_modal` invoke `.grab_set()`. This locks interaction to the dialog window, which is correct, but there is no keyboard route to exit the dialog.
   - Pressing the **Escape** key does not close any of the modals, requiring users to locate and click the "Dismiss" or "Close" button manually.
   - Tabbing order behaves unpredictably. When inside the `Bates Options Modal`, pressing `Tab` should navigate logically through input fields (`Prefix`, `Font`, `Size`, `Position`, etc.) and focus on the final "Save Protocol" action before looping back. Explicit tab ordering is required.

2. **Confirm & Enter Defaults**:
   - Modals containing input forms (e.g. the activation window) require a default action handler. Pressing **Enter** while typing in the license input box should automatically trigger `attempt_activation()` rather than requiring a mouse click.

---

## 🏎️ Flow & Perceived Speed

1. **In-Flight Visual Feedback**:
   - When clicking **Combine & Merge Files** or **Execute Production**, buttons stay active or change text to "Processing..." but do not provide explicit disable guards. If clicked again, this could spawn secondary threads and corrupt output documents.
   - Cancellation requests during long compiles need to visual update the status line immediately to inform users the process is winding down.

2. **Terminology Alignment**:
   - Labels like "EXECUTE PRODUCTION PRODUCTION" (duplicate word) or "Combine & Merge Files" should be polished to match CLI command references (e.g., `merge` and `bates-stamp`).
   - The interface is missing context-sensitive tooltips for advanced flags (e.g., explaining what "Collision Avoidance: Shrink page" does).
