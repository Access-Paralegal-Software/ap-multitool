---
id: qt_package_size_and_efficiency_notes
title: Qt Package Size & Efficiency Notes
type: ops-audit
---

# Package Size and Efficiency Notes

## Footprint Audit
The PySide6 migration originally introduced a notably heavier binary footprint than the legacy CustomTkinter implementation.
- **Initial Estimate:** ~120MB - 160MB extracted due to Qt DLLs.
- **Post-Pruning Verification:** Following the aggressive exclusion of WebEngine, QML, and Hardware modules (Task 4), the compiled `Access_Paralegal_Multitool.exe` (GUI) weighs exactly **87.1 MB**.
- **CLI Weight:** The headless `apmultitool.exe` weighs **48.8 MB**.

## Pruning Opportunities
1. **PyInstaller Excludes:** We can explicitly exclude massive unused Qt modules in the `ap_multitool.spec` file:
   - `PySide6.QtWebEngine`
   - `PySide6.QtQml`
   - `PySide6.QtNetwork`
   - `PySide6.QtBluetooth`
2. **Icon & Asset Compression:** The existing `water_texture.png` and `logo_small.png` are fairly large. Converting these to compressed WebP or highly optimized PNGs will save immediate megabytes.

## Efficiency Posture Verdict
A ~100MB footprint is highly acceptable for a modern Desktop Legal utility replacing multiple expensive SaaS subscriptions. However, applying PyInstaller excludes for unused Qt modules is a zero-cost optimization that should be applied prior to generating the final Gold Master release to improve download conversion rates.
