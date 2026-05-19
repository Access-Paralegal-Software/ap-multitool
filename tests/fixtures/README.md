---
title: APMultitool Test Fixtures
type: reference
status: active
updated_at: "2026-05-18T00:00:00Z"
---

# APMultitool — Test Fixtures & Validation Scenarios

This directory contains realistic test scenarios for the core PDF manipulation operations. Fixtures are designed to cover the golden path and the edge cases that matter in real legal document workflows.

---

## Fixture Inventory

### Scenario 1 — Basic Merge (Golden Path)
**File:** `scenario_01_basic_merge.md`  
**Operations tested:** merge  
**Description:** Three clean PDFs merged in order, bookmarks on, US Letter. Validates output page count, bookmark presence, and output naming.

### Scenario 2 — Mixed-Format Merge
**File:** `scenario_02_mixed_merge.md`  
**Operations tested:** merge  
**Description:** Merge of PDF + DOCX + JPG + EML in one queue. Validates format adapters, bookmark labels per file, and email cover page presence.

### Scenario 3 — Rotated Scan Correction
**File:** `scenario_03_rotated_scan.md`  
**Operations tested:** rotate  
**Description:** A 10-page scanned PDF where pages 3, 7, and 10 are landscape (90° clockwise). Rotate those three pages 90° CCW. Validates that only target pages are changed and all other pages are untouched.

### Scenario 4 — Exhibit Extraction
**File:** `scenario_04_extract_exhibit.md`  
**Operations tested:** extract  
**Description:** A 47-page production PDF. Extract pages 14–22 as a standalone exhibit. Validates output page count (9 pages), output naming, and source file integrity.

### Scenario 5 — Reordered Packet
**File:** `scenario_05_reorder_packet.md`  
**Operations tested:** reorder  
**Description:** A 6-page scanned letter where the pages were scanned in reverse (6,5,4,3,2,1). Reorder to [1,2,3,4,5,6]. Validates correct page sequence in output.

### Scenario 6 — Split by Page Range
**File:** `scenario_06_split_ranges.md`  
**Operations tested:** split  
**Description:** A 30-page bulk production PDF. Split into three named ranges: pages 1–10 (Pleadings), 11–22 (Correspondence), 23–30 (Exhibits). Validates three output files with correct page counts.

### Scenario 7 — Split by Fixed Chunk
**File:** `scenario_07_split_fixed.md`  
**Operations tested:** split  
**Description:** A 25-page PDF split into chunks of 10. Validates three output files: 10 pages, 10 pages, 5 pages.

### Scenario 8 — Inserted Cover Page
**File:** `scenario_08_cover_insert.md`  
**Operations tested:** merge (packet assembly)  
**Description:** Merge a 1-page cover PDF followed by a 12-page exhibit. Validates that the cover is page 1 and the bookmark points to page 2.

### Scenario 9 — Grayscale Email Merge (PACER)
**File:** `scenario_09_grayscale_email.md`  
**Operations tested:** merge + email_to_pdf (grayscale)  
**Description:** Batch of 5 .eml files with mixed color attachments (JPG, PDF). Merge with grayscale=True. Validates output is grayscale, page count accounts for attachments, and file size is under 4MB.

### Scenario 10 — Output Naming Edge Cases
**File:** `scenario_10_naming_edges.md`  
**Operations tested:** merge, extract  
**Description:** Source file names containing spaces, parentheses, and special characters. Validates that output names are clean, don't break file system, and collisions are handled with `_01` suffixes.

### Scenario 11 — Corrupt / Unreadable Input
**File:** `scenario_11_corrupt_input.md`  
**Operations tested:** merge  
**Description:** Queue of 5 files where file 3 is a corrupt PDF (truncated). Validates that the engine skips file 3 with a warning, completes the merge with the remaining 4 files, and reports the warning in the job result.

### Scenario 12 — Bates on Mixed-Page Packet
**File:** `scenario_12_bates_mixed.md`  
**Operations tested:** bates  
**Description:** A 20-page merged packet with mixed portrait/landscape pages, some with content in the bottom-right corner. Validates stamp placement, smart-shrink activation only on conflict pages, and sequential numbering continuity.

---

## Fixture File Format

Each scenario file follows this structure:

```markdown
# Scenario N — Title

## Setup
- Input files: [description of source material]
- Operation: [operation name]
- Parameters: [key params]

## Expected Output
- Output files: [names and page counts]
- Assertions: [what to check]

## Edge Cases Exercised
- [list]

## Sample Data Notes
- [how to generate or obtain test inputs]
```

---

## Generating Sample PDFs

For scenarios requiring specific PDF content, use the existing `make_sample.py` pattern (from the `sws-multitool` project) or the ReportLab snippets below:

```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def make_test_pdf(path, pages=5, label="Test"):
    c = canvas.Canvas(path, pagesize=letter)
    for i in range(1, pages + 1):
        c.drawString(72, 720, f"{label} — Page {i} of {pages}")
        c.showPage()
    c.save()
```

Place generated fixtures in `tests/fixtures/sample_pdfs/` (gitignored for large files).
