---
title: Email to PDF Status Audit
date: 2026-05-19
status: active
project: Access Paralegal
tags: [ap_multitool, audit, email-ops]
---

# 🔗 Email to PDF Status Audit

This document tracks the refactoring state of the EML/MSG email conversion pipeline within the APMultitool engine.

## 1. Context & Current State
The codebase previously relied on raw script execution via `email_processing.py`. 
An initial engine-registered handler `core/operations/email_to_pdf.py` has been stubbed and registered. However, the integration is not complete:
- The GUI still makes legacy calls to `email_processing.py` directly inside the Document Compiler compile loop (`gui_apmultitool.py`).
- The newly created `core/operations/email_to_pdf.py` currently calls the legacy `email_to_pdf` function which only renders the email body, omitting the attachments even when `include_attachments` is requested.
- There are no tests for the new operation.
- No CLI surface is hooked up yet.

## 2. Dependencies
The email conversion pipeline relies on:
- `extract_msg`: Outlook `.msg` parsing.
- `reportlab`: Document generation (canvas, paragraphs, flowables).
- `Pillow`: Image conversion.
- `pypdf` (or `pikepdf`): PDF merging and reading.
- `html2text`: HTML body conversion to plain text.
- `docx`: DOCX attachment conversion.

## 3. Known Call Sites & Integration Gaps
- **GUI Integration**: `gui_apmultitool.py` (around line 1053) directly performs email parsing and attachment conversion using `email_processing.UnifiedEmail` and associated helpers. This needs to be refactored to use the standardized job structure, supporting progress reporting and cancellation.
- **Engine Operation**: `core/operations/email_to_pdf.py` must support:
  - Cooperative cancellation (`job.status == JobStatus.CANCELLED` or checking exceptions).
  - Merging attachments securely with progress increments.
  - Correct metadata mapping (e.g. page counts).

---
*Status: GAPS IDENTIFIED | Action: Proceeding with Refactoring*
