---
id: pm-report-batch-05-doc-chameleon
title: PM Report — Batch 05
type: pm-report
status: completed
project: doc-chameleon
created: 2026-06-12
batch: 05
---

# PM Report — Batch 05 — doc-chameleon

## What Was Done

This batch implemented the CRC 2.111 first-page attorney/clerk layout as an additive layer on top of the existing CRC 2.108 line-numbering transform. Both transforms now compose cleanly and the full CA convert pipeline applies both in sequence.

## Files Created / Updated

| File | Status |
|------|--------|
| `src/doc_chameleon/rules/ca/transformer_2111.py` | Created — CRC 2.111 transform: enables different first-page header, installs attorney/clerk two-column table + line numbers |
| `src/doc_chameleon/rules/ca/validator.py` | Updated — added `validate_2111()`, `_has_ca_attorney_block_header()`, cross-validation warnings between 2.108 and 2.111 |
| `src/doc_chameleon/cli.py` | Updated — `convert` applies both transforms in sequence; `validate` checks both rule layers |
| `tests/fixtures.py` | Updated — added `make_cover_page()` fixture |
| `tests/test_ca_2111.py` | Created — 9 tests for the 2.111 structural layer |
| `pyproject.toml` | Bumped to `0.5.0` |

## Test Results

```text
29 passed in 1.89s
```

Breakdown:
- 5 round-trip fidelity tests
- 5 CA 2.108 numbering spike tests
- 10 CA fixture and report tests
- 9 CA 2.111 first-page layout tests

## Technical Decisions

**Additive composition model.** `transform_2111(doc)` is a separate function from `transform(doc)` (2.108). The CLI calls both in sequence. Neither transform overwrites the other's work — 2.108 installs the default (continuing pages) header with line numbers, 2.111 enables `titlePg` and installs a separate first-page header with line numbers + the attorney/clerk table.

**First-page header, not body injection.** The attorney/clerk split is placed in the Word first-page header rather than injected into the document body. This leaves the user's body content (court title, case caption, paragraphs) completely untouched.

**Raw XML construction via `parse_xml`.** The attorney/clerk table is built as an OOXML string and parsed with `parse_xml`, consistent with the VML approach used in the 2.108 transformer. This avoids reliance on python-docx's `add_table` on header objects, which has unreliable `_block_width` behavior in header/footer contexts.

**Marker via XML comment.** The 2.111 first-page header is marked with `<!-- doc-chameleon-ca-2111 -->` appended to the `<w:hdr>` element. The validator detects this marker. This is consistent with the 2.108 approach (VML shape ID as marker).

**Cross-validation warnings.** `validate()` (2.108) warns if line numbers are present but the attorney block is missing. `validate_2111()` warns if the attorney block is present but line numbers are missing. These warnings guide the user to run the complete pipeline.

## First-Page Layout Structure

```
┌──────────────────────────────────────────────────────┐
│  [line number VML — absolutely positioned, left margin] │
│                                                          │
│  ┌────────────────────────┬──────────────────────────┐  │
│  │ [Attorney Name], SBN   │ FOR COURT USE ONLY       │  │
│  │ [Firm Name]            │                          │  │
│  │ [Street Address]       │                          │  │
│  │ [City, State ZIP]      │                          │  │
│  │ Tel: [Phone]           │                          │  │
│  │ Email: [email]         │                          │  │
│  │                        │                          │  │
│  │ Attorney for [Party]   │                          │  │
│  └────────────────────────┴──────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

- Left column: 3.5" — attorney placeholder lines
- Right column: 2.75" — clerk space, no borders
- Table borders: all none
- Spacing: same 24 pt exact as body (line-number aligned)

## Known Limits

- Attorney placeholder lines are static. The user must manually fill in their information after conversion. A future batch could accept attorney info as CLI arguments or a config file.
- Court title, case caption, and document title remain in the document body — the transformer does not validate or restructure them. The body content is treated as the user's responsibility.
- Visual alignment of the first-page header table relative to the line numbers has not been verified in Word. Structural correctness is confirmed; pixel alignment is not.

## Recommended Next Batch

**Batch 06: Texas Statewide Baseline Transformer**

Suggested scope:

- Implement the TX statewide baseline transformer (TRCP-aligned formatting).
- Texas does not use CRC-style line numbering. TX formatting is principally caption/structure-focused.
- Implement `transform_tx(doc)` in `rules/tx/transformer.py` with: correct page geometry, body style normalization, Texas caption placeholder injection.
- Add TX validator with appropriate warnings.
- Wire TX into the CLI `convert` and `validate` commands.
- Add TX fixture (motion, notice) and 5+ tests.
- The TX overlays/ directory is already reserved for future county-specific packs; do not populate it in this batch.
