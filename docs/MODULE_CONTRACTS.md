---
title: APMultitool Module Contracts — Bates & Email-to-PDF
type: reference
status: active
updated_at: "2026-05-18T00:00:00Z"
---

# APMultitool — Module Contracts

These contracts define how future modules plug into the job model and engine. The contracts are binding architecture decisions — they do not need to be fully implemented in this batch, but the architecture must support them cleanly from the start.

---

## Module Contract: Bates Numbering

### Identity
`operation = "bates"`

### What it does
Applies permanent, sequential alphanumeric stamps to every page of a PDF. Stamps are vector-fused (burned into the page stream), making them impossible to remove without visible damage to the document. This is the legal standard for production numbering.

### Inputs
- Exactly one PDF file (`InputSpec.kind = "pdf"`)
- May be a merged packet or a standalone document

### Parameters (`BatesParams`)
```python
prefix: str           # e.g. "SMITH" → stamps as "SMITH000001"
start_number: int     # First stamp value (default: 1)
padding: int          # Zero-pad width (default: 6)
position: str         # "bottom_right" | "bottom_left" | "bottom_center"
font_size: int        # Points (default: 10)
shrink_conflict: bool # If True, shrink page content to avoid stamp overlap
```

### Output
One output PDF with stamps burned in. The output name defaults to `{source}_BATES.pdf`. Source file is not modified.

### Reversibility
`permanent` — stamps are vector-fused and cannot be removed programmatically.

### Engine integration
Register as `OPERATION_REGISTRY["bates"]` in `core/operations/__init__.py`.

The existing implementation in `gui_apmultitool.py:execute_bates_production()` contains the working coordinate-visitor scanner and smart-shrink logic. When migrating to `core/operations/bates.py`, that logic should be extracted as-is and wrapped in the `handle(job, progress)` interface. **Do not rewrite the coordinate scanner** — it is tested and correct.

### Constraints
- Must preserve all existing page content and metadata
- Stamp placement must respect the 150×60pt "Danger Zone" scan
- The `shrink_conflict` mode must only activate on pages where a collision is detected — clean pages stay at 100% scale
- Output must be court-ready: no watermarks, no overlays, no interactive elements added beyond the stamp itself

### Future enhancements (not in MVP)
- Multi-document sequential numbering (continue Bates across multiple input files without merging first)
- Custom stamp fonts
- Stamp on first page only (cover exclusion)
- Export a Bates index CSV alongside the output

---

## Module Contract: Email-to-PDF

### Identity
`operation = "email_to_pdf"`

### What it does
Converts one or more email files (`.eml`, `.msg`) into a litigation-ready PDF. Each email produces a cover page with metadata (From, To, Date, Subject) followed by the body and optionally the attachments, all in a single PDF per email or merged into one combined output.

### Inputs
- One or more files with `InputSpec.kind` in `{"eml", "msg"}`
- Mixed EML/MSG batches are supported

### Parameters (`EmailToPdfParams`)
```python
grayscale: bool              # PACER-compliant grayscale mode (default: False)
include_attachments: bool    # Whether to append attachments as pages (default: True)
paper_size: str              # "letter" | "legal" | "a4" (default: "letter")
output_name: str | None      # Override auto-name
```

### Attachment policy
Attachment handling is the core complexity of this module. The policy in MVP:

| Attachment type | Action |
|---|---|
| PDF | Append pages directly |
| Image (jpg, png, gif, bmp, tiff) | Convert to PDF page(s), append |
| Plain text | Render as PDF page, append |
| HTML | Strip to text, render as PDF page, append |
| DOCX | Convert via LibreOffice or python-docx, append |
| CSV | Render as plain text, append |
| Unsupported (xlsx, xlsb, etc.) | Insert placeholder page: "Attachment: filename.xlsx (not rendered)" |

Future enhancement: user-configurable attachment policy (include all / exclude all / whitelist by type).

### Output
- Single combined PDF if multiple inputs are provided (default: merge all emails + attachments)
- Per-email PDFs if `output_name` is not set and multiple inputs are given (future option)
- Each email gets a bookmarked section in the combined output

### Reversibility
`non-destructive` — source `.eml`/`.msg` files are never modified.

### Engine integration
Register as `OPERATION_REGISTRY["email_to_pdf"]` in `core/operations/__init__.py`.

The existing `email_processing.py` module (`UnifiedEmail`, `email_to_pdf`, `attachment_to_pdf`) is the working implementation. Migrate to `core/operations/email_to_pdf.py` as a thin wrapper:
```python
def handle(job: Job, progress) -> JobResult:
    # iterate job.inputs, call email_processing functions per file
    # merge results via pikepdf if multiple inputs
    # return JobResult
```

### Constraints
- 100% offline: no external HTTP calls during processing
- Grayscale mode must apply to both body rendering and image attachments
- Cover page must include: From, To, CC (if present), Date, Subject, attachment count
- Brand styling (Access Green `#67BE5E`) on cover page header is intentional and should be preserved
- PACER compliance: grayscale output must not exceed typical ECF file size limits (5MB per document is a common limit — warn if output exceeds 4MB)

### Future enhancements
- Configurable attachment include/exclude list
- Thread-aware rendering (group email chain into single logical document)
- Batch harvest mode with a progress-per-email UI
- Auto-detect Outlook PST export folders
