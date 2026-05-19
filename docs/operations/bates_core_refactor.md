---
title: Bates Stamping Core Operation Design Specification
date: 2026-05-19
status: active
project: Access Paralegal
tags: [ap_multitool, specifications, design, bates]
---

# 📐 Bates Stamping Core Operation Design Specification

This specification details the parameters, operation key, and behavior of the headless Bates stamping engine.

## 1. Registry Key
- `OPERATION_REGISTRY["bates_stamp"]` -> `core/operations/bates_stamp.py`

## 2. Parameter Structure

### `BatesParams`
Used by the `"bates_stamp"` operation:
- `prefix: str`: Bates prefix label (e.g. `A-` or `PROD-`).
- `sep: str`: Separator character between prefix and serial number (e.g., `-` or `_`).
- `start_idx: int`: Suffix serial starting value (default: `1`).
- `padding: int`: Total character width of the padded serial number (default: `7`).
- `font: str`: Font family for the stamp (`"Arial"`, `"Times New Roman"`, `"Courier New"`).
- `size: int`: Point size of the stamp text (default: `10`).
- `pos: str`: Position coordinates boundary (`"Bottom Right"`, `"Bottom Center"`, `"Top Center"`, `"Top Right"`, `"Top Left"`, `"Bottom Left"`).
- `shrink: bool`: Enable precision visitor collision detection and page scaling (default: `True`).
- `output_name: str | None`: Custom filename template or path override.

## 3. Job Interface Expectations
- **Inputs**: Exactly one input file (`InputSpec.kind = "pdf"`).
- **Progress Reporting**:
  - `0.0` -> `0.1` -> Initializing input document and parsing pages.
  - `0.1` -> `0.8` -> Iterative page-by-page scan, matrix collision check, overlay generation, and stamping.
  - `0.8` -> `0.9` -> Writing final output.
  - `1.0` -> Complete.
- **Cancellation Checkpoints**: Evaluated at the start of each page iteration.
- **Output naming**: Format `[Prefix][Sep][Start_Padded]-[End_Padded].pdf` or custom.
