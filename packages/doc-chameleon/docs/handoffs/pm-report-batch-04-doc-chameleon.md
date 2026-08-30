---
id: pm-report-batch-04-doc-chameleon
title: PM Report — Batch 04
type: pm-report
status: completed
project: doc-chameleon
created: 2026-06-12
batch: 04
---

# PM Report — Batch 04 — doc-chameleon

## What Was Done

This batch expanded test coverage with synthetic document fixtures, introduced the conversion report artifact, and completed the header-anchored vs. table-column numbering strategy comparison.

## Files Created / Updated

| File | Status |
|------|--------|
| `tests/fixtures.py` | Created — factory functions for motion, declaration, notice, hostile layout |
| `tests/test_ca_fixtures.py` | Created — 10 tests covering all four fixture classes plus conversion report |
| `src/doc_chameleon/engine/report.py` | Created — companion `.txt` report writer |
| `src/doc_chameleon/cli.py` | Updated — `convert` now auto-writes a `_report.txt` companion file |
| `pyproject.toml` | Bumped to `0.4.0` |

## Test Results

```text
20 passed in 1.02s
```

Breakdown:
- 5 round-trip fidelity tests (unchanged from Batch 03)
- 5 CA numbering spike tests (unchanged from Batch 03)
- 10 new fixture and report tests

## Synthetic Fixture Classes

| Fixture | Content | Source warnings expected |
|---------|---------|--------------------------|
| `make_motion` | Title, body paragraphs, numbered facts, argument, conclusion | None |
| `make_declaration` | Numbered declaration paragraphs (1–11), signature block | None |
| `make_notice` | Short notice of motion — 4 paragraphs | None |
| `make_hostile` | Mixed paragraph spacing + embedded 2×2 table | Spacing + tables |

All four are generated in-memory via `python-docx` — no checked-in binary fixtures required.

## Conversion Report

The `convert` CLI command now automatically writes a companion `<output_stem>_report.txt` next to the output `.docx`. The report includes:
- Input/output filenames
- Jurisdiction
- Generation timestamp
- Warnings list (or a clean-state message if none)
- Legal posture disclaimer (tool assists formatting, does not provide legal advice)

Warnings are no longer stdout-only.

## Numbering Strategy Comparison

The PM report for Batch 03 flagged comparing the header-anchored VML approach against a left-column table approach. Analysis completed; no second implementation is required.

### Header-anchored VML text box (current approach)

**How it works:** A VML `<v:shape>` with 28 numbered paragraphs is placed in the page header. It is absolutely positioned on the left margin and repeats automatically on every page via Word's header mechanism.

**Advantages:**
- Repeats per page automatically — no per-page logic required.
- Body paragraphs remain ordinary Word paragraphs, fully editable.
- No disruption to paragraph flow when content is added or removed.
- Structurally inspectable in the `.docx` header XML.

**Risks:**
- VML is a legacy format (Office Open XML drawing is the modern path). Word still renders it correctly, but LibreOffice support is less reliable.
- Alignment is sensitive to top margin and header distance settings; any post-conversion change to those values will shift the numbers visually even though the XML is unchanged.

### Left-column table (evaluated, not implemented)

**How it would work:** A two-column table: narrow left column with line numbers in each row, wide right column with body text. Each row set to exact 24 pt height.

**Why it is inferior for this product:**

1. **No automatic page repetition.** A Word table does not repeat its rows on a new page with new line numbers. Implementing repeating numbers in a table requires either (a) one row per line (28 rows per page), with manual page breaks tracked programmatically — fragile and complex — or (b) accepting that numbers reset to 1 at the top of each table, which is incorrect for CRC 2.108.

2. **Body content is not a free-flowing document.** Placing body text inside table cells breaks normal paragraph flow. Users editing the document post-conversion would be working inside a table, not a document, which is unintuitive and increases risk of layout corruption.

3. **Row height rigidity.** Exact-height table rows clip overflowing cell content rather than reflowing it, which is a correctness risk for longer paragraphs.

**Conclusion:** Header-anchored VML remains the correct approach. The known risk — LibreOffice rendering gaps — is acceptable given the stated target platform of Microsoft Word on Windows.

## Known Limits (Carried Forward)

- CRC 2.111 first-page caption/court-block layout not yet implemented.
- Visual alignment in Word has not been verified against a long real filing (20+ pages). Structural tests confirm XML correctness; pixel-level alignment across page breaks has not been observed.
- Hostile source documents are warned on but not deeply normalized. Tables and embedded objects are flagged; content within them is passed through unchanged.

## Recommended Next Batch

**Batch 05: CRC 2.111 First-Page Layout**

Suggested scope:

- Implement the California Rule of Court 2.111 first-page attorney information block and court-title block.
- Define the caption area geometry: attorney block top-left, court name centered, case number and department block top-right.
- Add a fixture for a full pleading cover page and tests confirming structural presence of the 2.111 elements.
- Keep 2.111 as an additive layer on top of the existing 2.108 line-numbering transform — they compose, not replace.
- Validator should warn if a document has been run through 2.108 but not 2.111, and vice versa.
