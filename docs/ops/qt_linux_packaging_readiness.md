---
id: qt_linux_packaging_readiness
title: Linux Packaging Readiness
type: ops-audit
---

# Linux Packaging Readiness

## Current Status
Linux packaging is **NOT YET IMPLEMENTED**. The codebase is primarily optimized for Windows enterprise environments.

## Deployment Assumptions
- PySide6 and core engine logic (PyPDF2) are highly portable to Linux.
- The `wmic` dependency used for motherboard UUID extraction in `security.py` is **strictly Windows-only**. On Linux, the codebase natively falls back to `platform.node()` or `uuid.getnode()`. This fallback is less spoof-resistant than WMI.

## Recommended Packaging Format
- **AppImage:** For a target audience of paralegals or law firms potentially running Linux, AppImage provides the lowest-friction "download and run" experience without battling DEB/RPM dependency hell across Ubuntu/Fedora/Arch.

## Verification Required
1. Ensure the UI scales correctly on common Linux Desktop Environments (GNOME/KDE) with varying DPI fractional scaling.
2. Validate that `os.startfile()` (used to open output directories upon completion) is gracefully intercepted and handled via `xdg-open` on Linux.

## Verdict
Linux is compatible in principle, but `security.py` licensing logic must be audited to ensure the `uuid.getnode()` fallback provides sufficient commercial protection before release.
