# tests/fixtures/conversion — Conversion Test Fixtures

Minimal, programmatically generated documents used by the conversion integration
tests.  All files were created with open-source Python libraries (`python-docx`,
`openpyxl`) and carry no third-party content or licensing restrictions.

To regenerate:
```bash
python scripts/_gen_fixtures.py
```

---

## Word fixtures (.docx)

| File | Contents | Fidelity aspects exercised |
|------|----------|---------------------------|
| `simple_text.docx` | Three paragraphs of plain prose; Heading 0 title | Basic text flow, paragraph spacing, font rendering |
| `headings_and_lists.docx` | H0/H1/H2 headings; bullet list (3 items); numbered list (3 items) | Heading hierarchy, list styles, indentation |
| `basic_table.docx` | 4×4 table with bold header row and data rows; introductory paragraph | Table border rendering, cell alignment, bold text |

## Excel fixtures (.xlsx)

| File | Contents | Fidelity aspects exercised |
|------|----------|---------------------------|
| `simple_spreadsheet.xlsx` | Single sheet "Data"; 5 columns with bold/shaded header; 4 data rows including numeric values | Single-sheet export, header styling, column widths |
| `multi_sheet.xlsx` | Two sheets: "Summary" (quarterly financials) and "Detail" (line items); bold headers | Multi-sheet export, sheet boundary handling |

---

## What "good enough" looks like

These fixtures are not used to verify pixel-perfect fidelity — they confirm the
conversion pipeline produces a structurally valid PDF.  A passing integration test
verifies:
- Output PDF exists and is non-empty.
- Pikepdf can open the PDF without error.
- Page count is ≥ 1.

Text extraction (via `pypdf`) is used as an optional secondary check to confirm
key strings survive conversion (e.g., heading text, cell values).
