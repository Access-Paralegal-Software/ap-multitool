---
id: pm-report-batch-08-doc-chameleon
title: PM Report — Batch 08
type: pm-report
status: completed
project: doc-chameleon
created: 2026-06-12
batch: 08
---

# PM Report — Batch 08 — doc-chameleon

## What Was Done

This batch delivered the `AttorneyInfo` dataclass and `--attorney-*` CLI flags, eliminating the manual placeholder-editing step that was the main friction point in the CA convert workflow. Also added multi-page structural tests and the `make_long_motion` fixture.

## Files Created / Updated

| File | Status |
|------|--------|
| `src/doc_chameleon/rules/ca/transformer_2111.py` | Updated — `AttorneyInfo` dataclass, `_attorney_lines()`, `transform_2111(attorney=)` |
| `src/doc_chameleon/cli.py` | Updated — 8 optional `--attorney-*` flags on `convert` command |
| `tests/fixtures.py` | Updated — `make_long_motion()` (38-paragraph multi-page document) |
| `tests/test_ca_attorney_info.py` | Created — 9 tests: dataclass, partial overrides, header population, XML safety, multi-page |
| `src/doc_chameleon/__init__.py` | Bumped to `0.8.0` |
| `pyproject.toml` | Bumped to `0.8.0` |

## Test Results

```text
62 passed in 3.08s
```

Breakdown:
- 5 round-trip fidelity tests
- 5 CA 2.108 numbering tests
- 10 CA fixture and report tests
- 9 CA 2.111 first-page tests
- 9 CA attorney info tests (new)
- 12 TX statewide baseline tests
- 12 end-to-end smoke tests

## AttorneyInfo Design

`AttorneyInfo` is a plain `@dataclass` in `transformer_2111.py`. All fields default to `[bracket placeholder]` strings, so `transform_2111(doc)` with no argument produces identical output to before this batch. The `ATTORNEY_PLACEHOLDER_LINES` module-level constant is now derived from `_attorney_lines(AttorneyInfo())` — it stays in sync with the dataclass automatically.

## CLI Usage

```sh
# With all attorney info pre-filled:
doc-chameleon convert \
  --input motion.docx \
  --jurisdiction ca \
  --output motion_ca.docx \
  --attorney-name "Jane Smith" \
  --attorney-sbn "123456" \
  --firm "Smith & Associates" \
  --address "123 Main St" \
  --city-state-zip "Los Angeles, CA 90001" \
  --phone "(213) 555-0100" \
  --email "jane@smithlaw.com" \
  --client "Plaintiff, ACME Corp"

# With partial info (unspecified fields use bracket placeholders):
doc-chameleon convert \
  --input motion.docx \
  --jurisdiction ca \
  --output motion_ca.docx \
  --attorney-name "Jane Smith" \
  --attorney-sbn "123456"
```

Attorney flags are silently ignored when `--jurisdiction tx`.

## Note on Real-Document Testing

The original Batch 08 goal included testing with a real paralegal working draft opened in Word. This has not been completed — no real document was provided for testing. The structural and XML-level tests confirm correctness at the code level, but visual alignment in Word across a real multi-page filing has not been observed.

**This remains the most important open validation step before the product is ready for paralegal use.** The recommended test is:
1. A real CA motion or declaration from practice (no tables, standard formatting).
2. Run convert with attorney info flags.
3. Open output in Microsoft Word on Windows.
4. Verify: line numbers on all pages, attorney block on page 1, editable body text.
5. Make a text edit and confirm line numbers do not drift.

## Recommended Next Batch

**Batch 09: Real-Document Acceptance Test or TX Local Overlay Architecture**

Two paths depending on resource availability:

**Path A — Real-Document Test (preferred)**
- Obtain one real CA motion and one real TX pleading.
- Run the full pipeline on each.
- Open outputs in Word and document any visual alignment issues.
- Fix any bugs discovered.

**Path B — TX Local Overlay Architecture (if real docs not available)**
- Define the overlay interface: how a county-specific pack declares its formatting deltas.
- Implement a minimal Harris County overlay as a proof-of-concept.
- Add overlay selection to the CLI (`--venue harris`).
- Tests confirming the overlay composes correctly with the TX baseline.
