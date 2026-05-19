---
title: APMultitool Visual & Interaction Spec
type: reference
status: active
updated_at: "2026-05-18T00:00:00Z"
---

# APMultitool — Visual & Interaction Spec

## Brand Identity in the Interface

The product is a **craftsman's tool**, not a legal enterprise portal. The aesthetic should communicate: precise, capable, trustworthy, satisfying. Think high-quality hand tool — not tech-startup, not corporate ERP.

---

## Color System

| Role | Light Mode | Dark Mode | Usage |
|---|---|---|---|
| Brand accent | `#67BE5E` | `#67BE5E` | Primary buttons, active tabs, checkboxes, progress fill |
| Brand deep | `#4E9146` | `#4E9146` | Hover states, pressed buttons |
| Background | `#EAEAEC` | `#1E2222` | Main window surface |
| Left panel | `#ECEEF0` | `#222727` | Settings/config panel |
| Right panel | `#DBEBDB` | `#233627` | Queue/content panel (slight green tint) |
| Panel border | `#BFE2BD` | `#5DA652` | Frosted glass edge gleam |
| Text primary | `#222222` | `#ECECEC` | Body text, labels |
| Text muted | `#6B7280` | `#9CA3AF` | Hints, secondary info |
| Amber warning | `#B45309` | `#D97706` | Permanent/destructive action labels |
| Error red | `#DC2626` | `#EF4444` | Failure states |

The diagonal green slash in the background is intentional — it gives the window depth and brand presence without decorating the controls. Keep it subtle (40% opacity emblem blend).

---

## Typography

| Element | Font | Size | Weight |
|---|---|---|---|
| Section headers | Segoe UI | 16px | Bold |
| Control labels | Segoe UI | 14px | Regular |
| Queue filenames | Segoe UI | 14px | Regular |
| Status line | Segoe UI | 13px | Regular |
| Tab labels | Segoe UI | 16px | Bold |
| Menu items | Segoe UI | 18px | Regular |
| Small hints | Segoe UI | 12px | Regular |

No decorative fonts. No icon fonts. Emojis in tab labels and menu items are acceptable — they provide fast visual scanning without requiring icon assets.

---

## Controls

### Buttons
- Primary action: full-width, brand green, 40px height, bold label
- Secondary: dark grey (`#4B5563`), same height
- Hover: darken 10%. No animation delay.
- Disabled: 40% opacity, not grayed-out text on gray — keep the shape visible

### Checkboxes
- CustomTkinter checkboxes with brand green fill
- Label at 14px, left-aligned, adequate click target (full row)

### Dropdowns
- CustomTkinter OptionMenu, brand green button, readable font at 16px
- No more than 5–6 options in any dropdown

### Progress Bar
- Full width of the content area
- Green fill (`#67BE5E`) on neutral track
- Paired with a plain-English status label directly below it
- Never show an indeterminate spinner for operations with known page counts

### Queue (Treeview)
- Alternating row shading (subtle — 5% lightness difference)
- Selected row: brand green at 20% opacity
- Column headers: bold, non-sortable in MVP
- Drag handle on left edge of each row (or drag anywhere on the row)
- Row height: 32px minimum for touch-tolerance

---

## Interaction Patterns

### Loading a folder
1. User opens folder (via button or menu)
2. Status line: "Scanning…"
3. Files appear in queue as they're detected (async, not blocked)
4. Page count populates per file as scanning completes
5. Queue preview updates: "4 documents, ~17 pages"

### Running an operation
1. User clicks the primary action button
2. Button disables immediately (prevents double-fire)
3. Progress bar starts moving with real page-level granularity
4. Status line updates: "Merging page 12 of 47…"
5. On completion: status = "Done — output saved to Merged_Output/"
6. Button re-enables
7. Output path in footer becomes clickable (opens folder)

### Error handling
1. Status line turns red: "Failed: [plain-English reason]"
2. Progress bar resets to 0
3. Error does not close or replace the queue — user can fix and retry
4. If a single file in a batch fails: warn, skip, continue — don't abort the whole job

### Reversibility label
- Displayed as a small line below the primary action button
- "✅ Non-destructive — source files are never modified" (green)
- "⚠ Permanent — Bates stamps are vector-fused and cannot be undone" (amber)
- Never hidden. Always present when a button is visible.

---

## What To Avoid

- Modal dialogs for anything that isn't a one-time confirmation of a destructive action
- Spinners that don't represent real progress
- Tooltips that repeat the label text
- Decorative animations (fade-ins, slide transitions)
- Requiring the user to navigate away from their queue to change a setting
- More than one primary action button visible at a time
- Font sizes below 13px anywhere in the interface
