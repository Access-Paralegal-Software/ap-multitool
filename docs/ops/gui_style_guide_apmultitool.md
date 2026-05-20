# APMultitool GUI Style Guide

This style guide establishes design conventions for the Access Paralegal Multitool interface using CustomTkinter, ensuring consistent spacing, color harmony, typography hierarchies, and layout structures.

---

## 🎨 Color Palette & Semantics

The layout uses a **Luxury Neutral** theme accented with **Glowing Velvet / Jade Green** highlights.

*   **Primary Accent**: `#67BE5E` (Jade Green)
*   **Deep Hover Accent**: `#4C9945`
*   **Alert/Warning**: `#E11D48` (Rose Red)
*   **Warning Hover**: `#BE123C`
*   **Dark Neutral Background**: `#1E2222`
*   **White Panel (Light Mode)**: `#FFFFFF`
*   **Silver BG (Light Mode)**: `#F3F4F6`
*   **Border Light**: `#E5E7EB`
*   **Text Dark**: `#111827`
*   **Text Light Muted**: `#4B5563`
*   **Text Dark Muted**: `#9CA3AF`

---

## 📐 Layout & Grids

### 1. Panel Layouts
*   **Left-Side Controls (Width 320px)**: Uses glassmorphism styling (`GLASS_LEFT`, `GLASS_BORDER`). All labels and inputs have a uniform left/right padding of 15px.
*   **Right-Side Data/Preview (Expanded)**: Uses high-contrast backgrounds for tables (`ttk.Treeview`) or previews. Left/right margin padding of 15px.

### 2. Spacing
*   **Inter-component vertical spacing**: 10px.
*   **Inside frame borders**: 15px padding.
*   **Outer main window margin**: 20px padding.

---

## 🔤 Typography Hierarchies

*   **App Header**: `Segoe UI` or `Inter`, Size 20, Bold.
*   **Tab Sections / Panel Headers**: `Segoe UI` or `Inter`, Size 14, Bold.
*   **Options & Checkboxes Labels**: `Segoe UI` or `Inter`, Size 12, Regular.
*   **Input fields and entries**: `Segoe UI` or `Inter`, Size 12, Regular.
*   **Console logs / Code / Tokens**: `JetBrains Mono` or `Consolas`, Size 11, Regular.

---

## 🔘 Buttons & Interactive Guidelines

### 1. Primary Action Buttons
*   **Accent**: Green (`#67BE5E`), Text: White (`#FFFFFF`).
*   **Height**: 45px (for major actions like Run / Execute).
*   **Font**: Bold, Size 13.

### 2. Secondary/Utility Buttons
*   **Accent**: Dark Grey (`#4B5563`), Text: White (`#FFFFFF`).
*   **Height**: 30px (for utility controls like Relocate, Preset, etc.).
*   **Font**: Bold, Size 11.

---

## ⌨️ Focus & Modal Behavior

1.  **Modal Settings**:
    *   Toplevel windows must configure `win.transient(parent)` and `win.grab_set()` to act as true modal popups.
    *   Must center relative to the main window during creation.
2.  **Keyboard Escape**:
    *   All modal dialogs must bind the `<Escape>` key to automatically destroy the window.
3.  **Tabbing Order**:
    *   Widget creation sequence must align with logical reading layout (Top-Left to Bottom-Right) to ensure standard keyboard tab traversal operates correctly.
