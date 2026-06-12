---
id: pm-report-batch-06-doc-chameleon
title: PM Report — Batch 06
type: pm-report
status: completed
project: doc-chameleon
created: 2026-06-12
batch: 06
---

# PM Report — Batch 06 — doc-chameleon

## What Was Done

This batch replaced the Texas transformer and validator stubs with a working TRCP statewide baseline implementation. Both jurisdictions (CA and TX) are now functional end-to-end through the CLI. The Texas overlay architecture remains reserved but empty, as planned.

## Files Created / Updated

| File | Status |
|------|--------|
| `src/doc_chameleon/rules/tx/transformer.py` | Replaced stub — full TRCP baseline transform |
| `src/doc_chameleon/rules/tx/validator.py` | Replaced stub — geometry checks, caption detection, statewide-only warning |
| `src/doc_chameleon/rules/tx/rules_meta.json` | Updated — `implemented: true`, last_verified date set |
| `src/doc_chameleon/cli.py` | Updated — TX `convert` and `validate` commands fully wired; stubs removed |
| `tests/fixtures.py` | Updated — added `make_tx_motion()` and `make_tx_notice()` with district court captions |
| `tests/test_tx_baseline.py` | Created — 12 tests covering geometry, style, marker, no-CA-header, validator warnings |
| `pyproject.toml` | Bumped to `0.6.0` |

## Test Results

```text
41 passed in 1.94s
```

Breakdown:
- 5 round-trip fidelity tests
- 5 CA 2.108 numbering tests
- 10 CA fixture and report tests
- 9 CA 2.111 first-page layout tests
- 12 TX statewide baseline tests

## TX vs CA Design Differences

| Dimension | California | Texas |
|-----------|------------|-------|
| Line numbering | Required (CRC 2.108) — VML header | None |
| First-page layout | Required (CRC 2.111) — attorney/clerk header | No equivalent statewide rule |
| Line spacing | Exactly 24 pt (rigid, locked) | Double (auto, relative to font size) |
| Margins | 1.25" left, 1" right/top/bottom | 1" all sides |
| Caption check | Not validated | Warned if "court" not in first 12 paragraphs |
| Overlay architecture | N/A — monolithic statewide | Reserved for county-specific local packs |
| Transform marker | XML comment in `<w:hdr>` | XML comment in `<w:sectPr>` |

## Validator Behavior

Every TX `validate` call includes a permanent statewide-only disclaimer:

> "This document reflects Texas statewide baseline formatting only. Local venue rules (Harris County, Travis County, etc.) are not applied. Verify local court requirements before filing."

This is not a warning the user can resolve — it is a permanent notice about coverage scope. It appears on every TX validation, even on a fully conformant document.

## Known Limits

- Caption detection is heuristic only: checks for the word "court" in the first 12 paragraphs. This is intentionally loose — the goal is to flag documents that are missing a caption entirely, not to validate caption format.
- TX double spacing uses `WD_LINE_SPACING.DOUBLE` (auto, relative). Unlike CA's exact 24 pt, this will reflow if the user changes the font size. This is correct behavior for Texas — TX formatting is not as prescriptive as CA.
- The TX overlay slot remains empty. No county-specific rules are implemented.

## Recommended Next Batch

**Batch 07: CLI Polish and End-to-End Smoke Test**

Suggested scope:

- End-to-end smoke test: run `doc-chameleon convert` on all fixture classes for both CA and TX, verify the output `.docx` and `_report.txt` exist and are well-formed.
- Update `list-jurisdictions` output to reflect current implementation state (CA: both 2.108 + 2.111 implemented; TX: statewide baseline implemented).
- Add `--version` flag.
- Review and clean up warning deduplication across CA and TX pipelines.
- Update README with current CLI usage and status for both jurisdictions.
- Consider: is the product ready for a first local install test with a real paralegal document?
