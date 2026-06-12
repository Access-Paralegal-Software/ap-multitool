---
id: pm-report-batch-07-doc-chameleon
title: PM Report — Batch 07
type: pm-report
status: completed
project: doc-chameleon
created: 2026-06-12
batch: 07
---

# PM Report — Batch 07 — doc-chameleon

## What Was Done

This batch polished the CLI, added end-to-end smoke tests covering all fixture/jurisdiction combinations, and brought the README fully up to date. The project is now at a stable, well-documented state suitable for a first real-document install test.

## Files Created / Updated

| File | Status |
|------|--------|
| `src/doc_chameleon/__init__.py` | Updated — `__version__ = "0.7.0"` |
| `src/doc_chameleon/cli.py` | Updated — `--version` flag, expanded `list-jurisdictions`, output alignment cleanup, deduplication consolidated |
| `tests/test_e2e_smoke.py` | Created — 12 end-to-end smoke tests |
| `README.md` | Fully rewritten — jurisdiction status table, CLI reference, what each conversion does, project structure, 53-test count, full PM report index |
| `pyproject.toml` | Bumped to `0.7.0` |

## Test Results

```text
53 passed in 2.51s
```

Breakdown:
- 5 round-trip fidelity tests
- 5 CA 2.108 numbering tests
- 10 CA fixture and conversion report tests
- 9 CA 2.111 first-page layout tests
- 12 TX statewide baseline tests
- 12 end-to-end smoke tests

## CLI Changes

**`--version`** — Added via Click's `version_option`. Reads from `__version__` in `__init__.py`.

**`list-jurisdictions`** — Replaced the flat description strings with a structured output showing status, implemented rules, and overlay notes per jurisdiction.

**Warning deduplication** — Consolidated `dict.fromkeys()` call to a single point per jurisdiction branch in `convert`. Confirmed the current CA pipeline behavior is correct: `validate_source_assumptions` fires pre-transform (on source doc) and again inside `validate()` post-transform (where spacing warnings no longer fire but table warnings may). Deduplication handles any overlap. No logic changes were needed.

## End-to-End Smoke Test Coverage

| Fixture | CA | TX |
|---------|----|----|
| motion | ✓ zero warnings | — |
| declaration | ✓ zero warnings | — |
| notice | ✓ zero warnings | — |
| cover_page | ✓ zero warnings | — |
| hostile | ✓ warnings expected, no crash | — |
| tx_motion | — | ✓ disclaimer only |
| tx_notice | — | ✓ disclaimer only |

Cross-jurisdiction guards:
- CA output must not contain TX marker
- TX output must not contain CA line-number headers

## MVP Milestone Assessment

The MVP definition from the genesis brief is substantially complete:

| MVP Requirement | Status |
|----------------|--------|
| Ingest `.docx` legal working documents | ✓ |
| Apply California jurisdiction formatting | ✓ CRC 2.108 + 2.111 |
| Apply Texas statewide baseline formatting | ✓ TRCP baseline |
| Export editable `.docx` output | ✓ |
| Produce a conversion report | ✓ companion _report.txt |
| CLI interface | ✓ convert, validate, list-jurisdictions, --version |
| Common litigation documents | ✓ motion, declaration, notice, cover page tested |

**Not yet complete:**
- CRC 2.111 court title / case caption injection into document body (validator warns but does not inject)
- Texas local venue overlays
- Desktop shell (Phase 3, not MVP)
- Visual alignment verified in Word across real multi-page filings

## Ready for Real-Document Test

The engine is ready for a first install test with a real paralegal working document. The recommended test is:

1. Take a real CA motion or declaration `.docx` (no tables, standard formatting).
2. Run `doc-chameleon convert --input <file> --jurisdiction ca --output <file>_ca.docx`.
3. Open the output in Microsoft Word.
4. Verify: line numbers appear on all pages, attorney/clerk split is in the first-page header, body text is properly spaced and editable.
5. Make a small text edit and verify line numbers do not break.

Known fragility to watch for: if the source document uses custom page sizes or non-standard margins, the transform will override them (expected behavior) and may produce unexpected results if the source content was tightly laid out for those dimensions.

## Recommended Next Batch

**Batch 08: Real-Document Validation and First Acceptance Test**

Suggested scope:

- Provide one or more real working drafts (CA motion, TX pleading) for test.
- Run the full pipeline and open outputs in Word.
- Document any visual alignment issues discovered.
- Fix any bugs found during real-document testing.
- Consider: is CRC 2.111 caption injection worth scoping, or defer to a later batch?
- If the attorney placeholder fill-in is a friction point, scope a `--attorney-info` CLI option.
