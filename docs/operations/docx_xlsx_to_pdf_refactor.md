---
title: Docx and Xlsx to PDF Refactor Design Specification
date: 2026-05-19
status: active
project: Access Paralegal
tags: [ap_multitool, specifications, design, docx, xlsx]
---

# 📐 Docx and Xlsx to PDF Refactor Design Specification

This specification outlines the parameters, operations, and engine integration for headless conversion of Word and Excel documents to PDF.

## 1. Registry Keys
- `OPERATION_REGISTRY["docx_to_pdf"]` -> `core/operations/docx_to_pdf.py`
- `OPERATION_REGISTRY["xlsx_to_pdf"]` -> `core/operations/xlsx_to_pdf.py`

## 2. Parameter Structures

### `DocxToPdfParams`
Used by the `"docx_to_pdf"` operation:
- `output_name: str | None`: Optional custom filename override.
- `grayscale: bool`: PACER-compliant grayscale compression.

### `XlsxToPdfParams`
Used by the `"xlsx_to_pdf"` operation:
- `output_name: str | None`: Optional custom filename override.
- `grayscale: bool`: PACER-compliant grayscale compression.

## 3. Job Interface Expectations
- **Inputs**: Exactly one input file (`InputSpec.kind = "docx"` or `"doc"` for Word; `"xlsx"`, `"xls"`, or `"csv"` for Excel).
- **Progress Reporting**:
  - `0.1` -> COM initialization and application launch.
  - `0.3` -> Document/Workbook opening.
  - `0.7` -> Native PDF generation.
  - `0.9` -> Grayscale/compression post-processing.
  - `1.0` -> Completion and COM cleanup.
- **Cancellation checkpoints**: Checked before opening, after opening, and during post-processing.
- **Output naming**: Auto-generated `{source}.pdf` if `output_name` is omitted.

## 4. Engine Registry Usage Notes
The registry keys `docx_to_pdf` and `xlsx_to_pdf` map to their respective conversion handlers in `core/operations/__init__.py`. When the engine's `submit()` method is called with a job specifying either key, it validates the parameters (`DocxToPdfParams` or `XlsxToPdfParams`) and dispatches execution to the registered worker. This allows both CLI and GUI interfaces to run document conversions consistently via the same centralized execution pipeline.

