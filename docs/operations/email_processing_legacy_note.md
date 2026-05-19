---
title: Legacy email_processing.py Status Note
date: 2026-05-19
status: deprecated
project: Access Paralegal
tags: [ap_multitool, documentation, legacy]
---

# ⚠️ Legacy `email_processing.py` Status Note

This document specifies the status, usage boundaries, and decommissioning roadmaps for `email_processing.py` located at the root of the repository.

## 1. Status: Deprecated & Decoupled
The direct execution of helper functions inside `email_processing.py` from the GUI interface (`gui_apmultitool.py`) has been **completely retired**. 
All email-to-PDF conversion logic in the application must flow through the core engine using the registered `"email_to_pdf"` operation:

*   **GUI dispatches** compile operations exclusively via `DocEngine.submit()`.
*   **CLI commands** similarly call `DocEngine.submit()`.
*   **Future extensions** (such as a local browser app) must integrate directly with the core engine.

## 2. Retention Rationale
The file `email_processing.py` is currently retained *strictly* as an implementation shim / library provider containing low-level parsing utilities (`UnifiedEmail`, canvas setups, ReportLab flowable builders). 

## 3. Retirement Roadmap
In a future release, the utility functions inside `email_processing.py` will be moved into a structured package namespace (e.g. `core/utils/email_utils.py` or similar) and the root file `email_processing.py` will be deleted entirely to ensure the repository root remains sparse and clean.
