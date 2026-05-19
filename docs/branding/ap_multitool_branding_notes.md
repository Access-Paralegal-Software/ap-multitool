# 🎨 APMultitool: Branding & Visual Direction Constraints

This document establishes the visual parameters, interface debt, and design boundaries for the upcoming aesthetic refresh of **APMultitool** (Access Paralegal Multitool). 

---

## 🏛️ 1. The Current CustomTkinter Look

APMultitool employs a custom-crafted GUI shell based on **CustomTkinter** that mimics modern, layered dark mode dashboards:
*   **Base Colorway**: High-contrast matte charcoal base (`#1E2222` in Dark Mode) and slate-white (`#EAEAEC` in Light Mode).
*   **Brand Accent**: Vibrant Access green (`#67BE5E`) with darkened forest-emerald hover states (`#4E9146`).
*   **Procedural Compositing**: Dynamically composites standard caustics textures (`water_texture.png`) and paints an emerald gradient slash watermark onto the main window canvas at runtime.
*   **Interface Concept**: "Frosted Glass Layering" — uses light semi-transparent frames (`#222727` and `#233627`) situated on top of the dark workspace background to create the illusion of translucent panels with high-contrast borders (`#5DA652`).

---

## ⚠️ 2. Aesthetic Gaps & Interface Debt

While functional, several design elements appear inconsistent or dated under close evaluation:
*   **Grid and Panel Density Mismatch**: 
    *   The **Document Compiler** tab has extremely high density, featuring tight listviews, multiple toggle buttons, and stacked controls.
    *   The **Bates & Security** tab has high empty-space layouts with sparse settings, creating a jarring visual transition.
*   **Dynamic Background Slashes**: The hardcoded diagonal green slash is painted directly onto the canvas. On high-DPI displays or custom window dimensions, it occasionally results in visual noise behind text panels.
*   **Interaction Friction**: 
    *   Manual file index reordering requires double-clicking a list row and entering a numeric value inside a separate pop-up modal. This lacks fluid modern drag-and-drop or immediate click-to-move-up/down controls.
    *   File scanning and loading queues lack real-time animations, utilizing static text status messages instead.

---

## 🔒 3. Invariant Elements (What Must Not Change)

To maintain legal-professional authority and protect existing client environments, several elements must remain unchanged:
*   **Dark & Light Mode Toggle Availability**: Paralegals operate in mixed lighting environments (including high-glare offices and late-night dark workspaces). High-contrast Light Mode (`#EAEAEC` base) and soft glowing Dark Mode (`#1E2222` base) are mandatory.
*   **Strict Legal-Professional Baseline**: No playful or informal palettes. The design must feel clean, corporate, sober, and secure.
*   **Attestation & Copyright Badging**: Alan Woodyard copyright blocks, license status overlays, and legal attestation frames must remain anchored in prominent locations.

---

## 🛑 4. Visual Direction Deferral Notice

> [!IMPORTANT]
> The final visual styling theme, font selection, and graphical overrides are **actively deferred** until the human operator provides example looks, layout wireframes, or a unified style guide. 
> No custom canvas drawing overrides, custom icon fonts, or external styling stylesheets are to be drafted in this sprint to avoid speculative design debt.

---

*System State: STAX ALIGNED | Visual Theme: DEFERRED PENDING OPERATOR STYLES*
