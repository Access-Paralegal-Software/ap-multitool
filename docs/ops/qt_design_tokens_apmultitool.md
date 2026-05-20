# APMultitool Qt Design Tokens & Stylesheet

This document defines the typography, spacing scale, color roles, and QSS style structures for the APMultitool PySide6 interface.

---

## 🎨 1. Color Palette & Semantic Roles

We employ a high-performance **Luxury Matte Charcoal & Silver** palette accented with a **Vibrant Jade Green** highlight.

| Token Name | Hex Code | Semantic Role |
| :--- | :--- | :--- |
| `COLOR_PRIMARY` | `#67BE5E` | Jade Green highlight for primary action buttons, toggles, and status progress. |
| `COLOR_PRIMARY_HOVER` | `#4C9945` | Deeper green feedback for hover states on primary components. |
| `COLOR_BG_DARK` | `#1E2222` | Glowing Charcoal background used for sidebar and main window backdrop in Dark Mode. |
| `COLOR_BG_LIGHT` | `#F3F4F6` | Light Silver backdrop used in Light Mode. |
| `COLOR_SURFACE` | `#FFFFFF` | Clean white panel backdrop in Light Mode. |
| `COLOR_SURFACE_DARK` | `#2D3232` | Slate grey panel container backdrop in Dark Mode. |
| `COLOR_TEXT_PRIMARY` | `#111827` | High-contrast dark grey/black body text (Light Mode). |
| `COLOR_TEXT_MUTED` | `#6B7280` | Low-contrast grey text for hints, descriptions, and tooltips. |
| `COLOR_ALERT` | `#E11D48` | Rose Red indicator for warnings and cancellation buttons. |
| `COLOR_BORDER` | `#E5E7EB` | Soft grey borders separating panels and frames. |

---

## 📐 2. Spacing Scale

To ensure layouts reflow cleanly and present adequate touch-target sizes, we align component margins to a baseline 4px grid:

- **XS (4px)**: Padding between text labels and their direct inputs.
- **S (8px)**: Internal padding inside buttons, text entries, and checkbutton layouts.
- **M (12px)**: Spacing between option rows and checkbox configurations.
- **L (16px)**: Margin borders separating panels, frames, and tables.
- **XL (24px)**: Outer window boundary margins.

---

## 🔤 3. Typography Scale

- **App Header**: 20px, Bold (Segoe UI / Outfit).
- **Section Headers**: 14px, Semi-Bold (Segoe UI / Outfit).
- **Body & Labels**: 12px, Regular (Segoe UI / Outfit).
- **Interactive Buttons**: 13px, Semi-Bold (Segoe UI / Outfit).
- **Muted Hints & Sub-labels**: 11px, Regular (Segoe UI / Outfit).
- **Console Outputs / Monospace**: 11px, Regular (Consolas / JetBrains Mono).

---

## 🔘 4. Core QSS Template (Sample)

To ensure cohesive styling, widgets are bound via Qt stylesheets (QSS).

```css
/* MainWindow Background */
QMainWindow {
    background-color: #F3F4F6;
}

/* Grouped Option Frames */
QFrame#GroupContainer {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 12px;
}

/* Primary Action Button */
QPushButton#PrimaryAction {
    background-color: #67BE5E;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    font-weight: bold;
    height: 40px;
}
QPushButton#PrimaryAction:hover {
    background-color: #4C9945;
}

/* Cancellation / Danger Button */
QPushButton#DangerAction {
    background-color: #E11D48;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    font-weight: bold;
    height: 40px;
}
QPushButton#DangerAction:hover {
    background-color: #BE123C;
}

/* Text Input Entries */
QLineEdit {
    border: 1px solid #E5E7EB;
    border-radius: 6px;
    padding: 8px;
    background-color: #FFFFFF;
    color: #111827;
}
QLineEdit:focus {
    border: 2px solid #67BE5E;
}
```
