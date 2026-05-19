---
title: Docx, Xlsx, and Bates Handling Status Audit
date: 2026-05-19
status: active
project: Access Paralegal
tags: [ap_multitool, status-audit, docx, xlsx, bates]
---

# 🕵️ Docx, Xlsx, and Bates Stamping: Current Codebase Audit

This document summarizes where the conversion and stamping logic lives in the current codebase, their dependencies, and known limitations.

## 1. Word and Excel Conversion

### Current Location
- The conversion logic for Word (`.doc`, `.docx`) and Excel (`.xls`, `.xlsx`, `.csv`) resides inside `gui_apmultitool.py` (lines 809-860) as private GUI methods `_convert_word_to_pdf` and `_convert_excel_to_pdf`.
- These are called directly inside the Document Compiler thread loop (`execute_audit_merge`).

### Dependencies & Environment Requirements
- **Windows win32com client**: Both methods use `win32com.client.DispatchEx("Word.Application")` and `win32com.client.DispatchEx("Excel.Application")`.
- **Microsoft Office installation**: They require a local copy of MS Word/Excel.
- **Threading**: They initialize COM threads using `pythoncom.CoInitialize()` and `pythoncom.CoUninitialize()`.

### Limitations
- **Platform-locked**: Requires a Windows environment and installed Microsoft Office software.
- **GUI-tied**: Because the methods are methods on the application class, they cannot easily be called in a headless context (like the CLI or a web engine) without spawning/mocking GUI classes.
- **Failures**: If MS Office is absent or errors out, there is no cross-platform/LibreOffice fallback in these specific conversion lines (unlike `merge.py` which has a command-line subprocess fallback to `soffice`).

---

## 2. Bates Stamping

### Current Location
- The stamping logic lives inside `gui_apmultitool.py` (lines 1356-1493) in the method `execute_bates_production`.
- The user triggers this by clicking the `Execute Production` button in the `⚖️ Bates & Security` tab, which spawns `execute_bates_production` inside a background thread.

### Dependencies
- **ReportLab**: Renders the stamp overlay (`canvas.Canvas`, `pdf_font`).
- **pikepdf**: Modifies the original PDF structure, Prepends scale matrices for collision avoidance, and inserts overlays.
- **pypdf**: Reads the page text via a text extractor visitor `visitor_text` to scan the corner "Danger Zones" for potential overlapping text.

### Logic Details
- **Danger Zone**: Scans a 150×60pt boundary at the chosen position.
- **Collision Avoidance**: If text is found inside the danger zone, the page contents are prepended with a scaling matrix (`q {scale} 0 0 {scale} {tx} {ty} cm`) and appended with ` Q` to isolate the matrix, effectively shrinking page contents towards the center.
- **Format**: Dynamic serial suffix starting from a user-specified index, zero-padded to 7 characters (e.g. `PREFIX_0000001`).

### Limitations
- **GUI-tied**: Reads inputs directly from Tkinter elements (`self.bates_target_entry.get()`, `self.bates_start.get()`, `self.bates_opts`) and outputs UI alerts (`messagebox.showinfo`, `messagebox.showerror`).
- **Error handling**: Any error triggers a GUI messagebox instead of registering as a structured engine failure.
