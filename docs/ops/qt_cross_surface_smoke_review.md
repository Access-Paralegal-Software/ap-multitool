---
id: qt_cross_surface_smoke_review
title: Cross-Surface Smoke Path Review
type: ops-audit
---

# Cross-Surface Smoke Path Review

## Goal
Verify that the product story remains coherent across the three APMultitool deployment surfaces:
1. **CLI (Active / Automation)**
2. **Desktop Qt (Active / Serious Local Utility)**
3. **Browser App (Roadmap / Lightweight Future)**

## Surface Matrix Review

### 1. Command Line Interface (`cli.py`)
- **Posture:** Automation companion for advanced users writing batch scripts.
- **Verification:** The CLI successfully routes its parameters to the exact same `Job` models used by the Qt UI. The output format and logs match the terminal console built into the Qt Bates view.
- **Alignment Status:** Coherent. The CLI serves as a headless equivalent to the Qt app without duplicating business logic.

### 2. Desktop Qt Application (`apmultitool_qt`)
- **Posture:** The primary workhorse for legal professionals requiring absolute privacy, zero-latency local processing, and heavy file manipulation.
- **Verification:** The UI exposes deep parameterization (compression, grayscale, custom blueprints) safely and asynchronously. The local machine bounding via Vault cryptography positions this explicitly as a native desktop utility.
- **Alignment Status:** Coherent. It successfully replaced the CustomTkinter prototype with a scalable STAX-compliant design.

### 3. Future Browser App (Roadmap)
- **Posture:** Lightweight SaaS or internal STAX server layer for quick access without desktop installations.
- **Verification:** As audited in `qt_browser_surface_alignment_audit.md`, the UI has not entangled the engine. The exact dictionary parameters dispatched by the Desktop UI can easily be replicated via a web frontend dispatching to a REST API.
- **Alignment Status:** Coherent. The boundary discipline has been rigorously preserved.

## Documentation Drift
- No significant drift was detected. The STAX fleet rules appropriately categorize this tool as a standalone lane that can scale from script to heavy UI natively.
