---
id: pm-report-batch-03-doc-chameleon
title: PM Report - Batch 03
type: pm-report
status: completed
project: doc-chameleon
created: 2026-06-03
batch: 03
---

# PM Report - Batch 03 - doc-chameleon

## What Was Done

This batch implemented the first controlled California pleading-paper line-numbering spike. The goal was not full California filing automation; it was to prove a concrete, inspectable `.docx` strategy for CRC 2.108-style line numbering while keeping body content editable.

## Files Created / Updated

| File | Status |
|------|--------|
| `src/doc_chameleon/rules/ca/transformer.py` | Implemented controlled CA page geometry, exact body flow, and header-anchored left-margin line numbers |
| `src/doc_chameleon/rules/ca/validator.py` | Implemented warnings for unsupported layout assumptions and missing CA numbering structure |
| `src/doc_chameleon/cli.py` | Wired `convert` and `validate` to the CA transformer/validator |
| `tests/test_ca_numbering.py` | Added structural tests for CA numbering, page geometry, body flow, source-assumption warnings, and hostile layout warnings |
| `README.md` | Updated current status and CLI behavior |
| `pyproject.toml` | Bumped package version to `0.3.0` |

## Technical Decision

The selected prototype uses a Word header-anchored VML text box containing 28 right-aligned line numbers. This makes the numbering layer repeat per page and keeps body paragraphs as ordinary editable Word content. The transformer also forces controlled assumptions that make alignment testable:

- Letter page size, 8.5 x 11 inches.
- Left margin 1.25 inches; right, top, and bottom margins 1 inch.
- Times New Roman, 12 pt body text.
- Exact 24 pt line spacing.
- Zero paragraph spacing before and after.
- Shared `Doc Chameleon CA Body` paragraph style.

## Validation Behavior

The CA validator now warns on:

- Page geometry outside the controlled assumptions.
- Multiple sections.
- Tables.
- Images, drawings, text boxes, embedded objects, or other layout-affecting XML.
- Non-exact line spacing.
- Paragraph spacing before or after.
- Missing CA line-number header.

## Test Results

```text
10 passed in 0.61s
```

Coverage now includes:

- 5 no-op round-trip fidelity tests.
- 5 California numbering spike tests.

## Known Limits

This is still a controlled spike. It does not yet prove visual alignment in Microsoft Word across long, real filings. It also does not implement CRC 2.111 first-page caption/court-block layout. Hostile source documents are warned on rather than fully normalized.

## Recommended Next Batch

**Batch 04: California Visual Verification and Fixture Expansion**

Suggested scope:

- Add generated synthetic fixtures for motion, declaration, notice, and hostile layout classes.
- Render or otherwise inspect generated `.docx` output in a repeatable way.
- Compare the header-anchored numbering strategy against at least one fallback strategy, likely a left-column table layout.
- Add a conversion report artifact instead of stdout-only warnings.
- Keep CRC 2.111 first-page formatting separate until CRC 2.108 alignment is more thoroughly verified.
