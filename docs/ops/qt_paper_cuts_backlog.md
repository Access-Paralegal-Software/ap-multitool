---
id: qt_paper_cuts_backlog
title: Qt Paper Cuts Backlog
type: ops-audit
---

# Paper Cuts Backlog

This document captures minor UX grievances, polish opportunities, and friction points deferred for later resolution.

## Minor Gripes
- **Tab Transitions**: Switching between Sidebar tabs snaps instantly. A smooth cross-fade animation would enhance the "premium" feel defined by STAX rules.
- **Compiler Output Input**: If a user clears the text in `Output PDF Name` and tabs out, it doesn't auto-reset to a safe fallback (like `compiled.pdf`), relying on execution-time validation to catch it.
- **File Room Reset Behavior**: Resetting the Custom Blueprint prompts with a confirmation dialog, but clearing it entirely does not always highlight the change visually.
- **Help Panel Empty**: The About/Help view (`views/about.py`) is primarily static placeholder text regarding diagnostics.

## Visual Polish
- Standard QScrollBars injected by OS on overflowing tables appear slightly unstyled compared to the deep CustomTkinter legacy equivalents. Custom QSS for QScrollBars could be integrated into `GLOBAL_STYLE`.
- Bates "Settings Gear" icon on `btn_options` uses an emoji rather than an SVG, leading to scaling artifacts on different display DPIs.
