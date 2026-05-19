---
title: CLI V1 Specification
date: 2026-05-19
status: active
project: Access Paralegal
tags: [ap_multitool, specifications, cli]
---

# 💻 CLI V1 Specification

This specification defines the interface requirements, subcommands, and parameter mappings for the command-line interface of the APMultitool suite.

## 1. Design Philosophy
- **Core-First**: CLI acts as a lightweight wrapper calling `DocEngine.submit()` directly.
- **Explicit Inputs**: Provide explicit options for input files/folders, parameter settings, and output directories.
- **Machine-Readable Outputs**: Support stdout printing of JSON results for easy integration into automation scripts.
- **Consistent Codes**: Return standard shell exit codes (`0` for success, non-zero for failures).

## 2. Command Structure
The CLI is invoked via:
```bash
python cli.py <operation> [options]
```

### Operation: `email_to_pdf`
Converts an email file and optional attachments to a PDF.
- **Options**:
  - `-i, --input PATH`: Path to the input `.eml` or `.msg` file. (Required)
  - `-o, --output-dir PATH`: Path to the output directory. (Default: current directory)
  - `--output-name FILENAME`: Custom name for the output PDF.
  - `--no-attachments`: Disable attachment parsing (only convert body).
  - `--grayscale`: Enable PACER-compliant grayscale compression.

### Operation: `merge`
Combines multiple files (PDFs, images, emails, DOCX) into a single PDF.
- **Options**:
  - `-i, --inputs PATH [PATH ...]`: List of paths to input files or folders to merge. (Required)
  - `-o, --output-dir PATH`: Path to the output directory. (Default: current directory)
  - `--output-name FILENAME`: Custom name for the merged output PDF.
  - `--grayscale`: Convert images and emails to grayscale.

### Operation: `docx-to-pdf`
Converts a Word document (`.docx` or `.doc`) to a PDF.
- **Options**:
  - `-i, --input PATH`: Path to the input Word file. (Required)
  - `-o, --output-dir PATH`: Path to the output directory. (Default: current directory)
  - `--output-name FILENAME`: Custom name for the output PDF.

### Operation: `xlsx-to-pdf`
Converts an Excel spreadsheet (`.xlsx`, `.xls`, or `.csv`) to a PDF.
- **Options**:
  - `-i, --input PATH`: Path to the input Excel file. (Required)
  - `-o, --output-dir PATH`: Path to the output directory. (Default: current directory)
  - `--output-name FILENAME`: Custom name for the output PDF.

### Operation: `bates`
Applies Bates numbering stamps to a PDF with optional collision avoidance.
- **Options**:
  - `-i, --input PATH`: Path to the target PDF file. (Required)
  - `-o, --output-dir PATH`: Path to the output directory. (Default: current directory)
  - `--output-name FILENAME`: Custom output filename.
  - `--prefix TEXT`: Bates prefix string (e.g. `PROD`).
  - `--sep CHAR`: Separator character between prefix and serial (e.g. `-`). (Default: `-`)
  - `--start NUMBER`: Suffix starting index. (Default: `1`)
  - `--padding WIDTH`: Width of zero-padded serial suffix. (Default: `7`)
  - `--pos POSITION`: Stamp placement coordinates. Choices: `Bottom Right`, `Bottom Center`, `Top Center`, `Top Right`, `Top Left`, `Bottom Left`. (Default: `Bottom Right`)
  - `--font NAME`: Stamp text font family. (Default: `Helvetica`)
  - `--size POINTS`: Font point size. (Default: `10`)
  - `--no-shrink`: Disable margin-moat collision detection and page contents shrinking.


## 3. Exit Codes
- `0`: Success.
- `1`: Validation error (missing arguments, invalid formats).
- `2`: Engine execution error (operation failed or was cancelled).
