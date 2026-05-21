---
id: ho_0040_pm_report
title: PM Report — LibreOffice Fallback Hardening (ho_0040)
type: pm_report
project: APMultitool
status: complete
created_at: 2026-05-21
batch: ho_0040
---

# PM Report — LibreOffice Fallback Hardening (ho_0040)

**Batch:** ho_0040  
**Date:** 2026-05-21  
**Lane:** Document Conversion — LibreOffice Fallback Hardening  
**Status:** ✅ Complete

---

## What Was Done

This batch hardened the LibreOffice fallback path implemented in ho_0034.
The objective was to move from a working but lightly-tested abstraction to a
well-documented, fixture-backed integration test suite with clear fidelity
expectations.

### Task 1 — Confirmed abstraction integrity

Reviewed `core/operations/docx_to_pdf.py`, `xlsx_to_pdf.py`, and
`_conversion_backend.py`. Confirmed:

- Public functions `convert_docx_to_pdf()` and `convert_xlsx_to_pdf()` are
  clean abstraction boundaries.
- `detect_backend()` selection order is correct (override → env var → Windows →
  soffice → NONE).
- `handle()` in both engine modules correctly delegates to the public functions.
- No regressions from ho_0034.

### Task 2 — Created real fixture files

Five fixture files were generated programmatically using `python-docx` and
`openpyxl`. No third-party content; no licensing issues.

Committed to `tests/fixtures/conversion/`:

| File | Type | Size |
|------|------|------|
| `simple_text.docx` | Word | 35 KB |
| `headings_and_lists.docx` | Word | 35 KB |
| `basic_table.docx` | Word | 36 KB |
| `simple_spreadsheet.xlsx` | Excel | 5 KB |
| `multi_sheet.xlsx` | Excel | 5.5 KB |

Regeneration script: `scripts/_gen_fixtures.py`.

### Task 3 — Backend selection tests

Added `TestBackendSelection` to `tests/test_conversion_integration.py` — 8
unit tests covering the full Office-vs-LibreOffice decision matrix:

- Windows primary is WIN32COM
- POSIX with soffice → LIBREOFFICE
- POSIX without soffice → NONE
- `APM_CONVERSION_BACKEND=libreoffice` overrides Windows
- `APM_CONVERSION_BACKEND=win32com` overrides POSIX
- Fallback disabled on POSIX → NONE
- win32com fails + fallback enabled → LibreOffice used, warning returned
- win32com fails + fallback disabled → RuntimeError raised

All tests are platform-agnostic (mock-based). These run in CI.

### Task 4 — LibreOffice integration tests

Added `TestLibreOfficeIntegration` to `tests/test_conversion_integration.py`
with an `autouse` fixture that skips the entire class when `soffice` is absent:

- `test_docx_produces_valid_pdf` — 3 parametrized fixtures (simple_text,
  headings_and_lists, basic_table)
- `test_xlsx_produces_valid_pdf` — 2 parametrized fixtures (simple_spreadsheet,
  multi_sheet)
- `test_multi_sheet_xlsx_all_sheets_present` — verifies ≥2 pages for
  `multi_sheet.xlsx`
- `test_simple_text_docx_text_survives` — pypdf text extraction sanity check
- `test_soffice_timeout_raises` — `subprocess.TimeoutExpired` propagates
  correctly

Total integration test suite: 26 tests (17 unit/mock + 9 soffice tests that
skip in CI). Validated on this machine: 64 passed, 8 skipped (correct).

Also added `TestFixturePresence` (5 tests) and `TestConversionWithMockedBackend`
(5 tests) — all always-run, all pass in CI.

### Task 5 — Fidelity documentation

Updated `docs/ops/doc_conversion_fallback_design.md`:

- Added Section 5: Fidelity expectations — what survives vs what may differ
  (tables covering text, headings, lists, tables, charts, fonts, page size)
- Added "what constitutes good enough" for integration tests (pikepdf opens,
  ≥1 page; soft text extraction check)
- Added Section 7: Non-Windows environment status — explicitly states no
  macOS/Linux smoke test has been performed; do not cite as support evidence
- Added Section 8: Future work (soffice startup check, UserInstallation
  isolation, fidelity comparison, grayscale post-processing)
- Added Section 6: Known limitations table

Updated `docs/ops/doc_conversion_test_strategy.md`:

- Added fixture library table (Section 5)
- Added interpretation guide for integration test results
- Added Section 6: CI integration strategy — Option B rationale (disabled in
  CI, easy locally)

### Task 6 — CI wiring

Updated `pytest.ini` — added markers: `conversion`, `libreoffice`,
`integration_windows`, `integration_libreoffice`.

Updated `scripts/run_core_tests.py` — added `conversion` and `libreoffice`
entries to `SUBSET_MARKERS`.

Updated `docs/ops/ci_overview.md` — added `conversion` and `libreoffice` rows
to the subset/marker table.

Updated `docs/ops/ci_known_issues.md` — added Issue #5 documenting the
LibreOffice auto-skip pattern with reproduction steps and future option for
self-hosted runners.

Updated `tests/test_conversion_backend.py` — added
`pytestmark = [pytest.mark.core, pytest.mark.conversion]` so existing 39 unit
tests are included in both the `core` and `conversion` CI subsets.

### Task 7 — UI/config surface check

Scanned `gui_apmultitool.py` and all Qt-layer files for LibreOffice, conversion
backend, or `APM_CONVERSION` references. **None found.** The three occurrences
of "fallback" in `gui_apmultitool.py` are visual color constants, unrelated to
conversion. No settings surface exposes the LibreOffice toggle to end users.
No misleading labels; no over-claims. No changes required. ✅

### Task 8 — Non-Windows smoke test

Not performed. This machine is Windows-only. The LibreOffice subprocess path
uses only standard `subprocess` and `shutil.move` — no platform-specific
Python code — so it is expected to work on macOS/Linux where `soffice` is on
PATH. However, no validation has been performed. This limitation is explicitly
documented in `doc_conversion_fallback_design.md` Section 7 and must not be
cited as support evidence.

---

## Test Run Summary

```
64 passed, 8 skipped in 2.47s
```

Skipped: `TestLibreOfficeIntegration` (8 tests) — soffice not on PATH, as
expected on Windows dev machine without LibreOffice installed.

---

## Files Changed This Batch

### New files
- `scripts/_gen_fixtures.py` — fixture regeneration script
- `tests/fixtures/conversion/simple_text.docx`
- `tests/fixtures/conversion/headings_and_lists.docx`
- `tests/fixtures/conversion/basic_table.docx`
- `tests/fixtures/conversion/simple_spreadsheet.xlsx`
- `tests/fixtures/conversion/multi_sheet.xlsx`
- `tests/fixtures/conversion/README.md`
- `tests/test_conversion_integration.py`
- `handoffs/ho_0040_pm_report_2026_05_21_libreoffice_fallback_hardening.md` ← this file

### Modified files
- `pytest.ini` — added 4 markers
- `scripts/run_core_tests.py` — added `conversion` and `libreoffice` subsets
- `tests/test_conversion_backend.py` — added `pytestmark`
- `docs/ops/doc_conversion_fallback_design.md` — fidelity docs, non-Windows status, future work
- `docs/ops/doc_conversion_test_strategy.md` — fixture table, CI strategy section
- `docs/ops/ci_overview.md` — conversion/libreoffice rows in marker table
- `docs/ops/ci_known_issues.md` — Issue #5: LibreOffice auto-skip behavior

---

## What Was Not Changed

- `core/operations/docx_to_pdf.py` — no changes
- `core/operations/xlsx_to_pdf.py` — no changes
- `core/operations/_conversion_backend.py` — no changes
- `gui_apmultitool.py` — no changes (no LibreOffice surface)
- `config.py` — no changes
- Primary backend priority (win32com first on Windows) — unchanged
- Licensing, vault, encryption, hardware identity — untouched

---

## Known Open Items

| Item | Priority | Status |
|------|----------|--------|
| soffice availability check at startup (not just at conversion time) | Medium | Open |
| `--env:UserInstallation` isolation for concurrent soffice calls | Medium | Open |
| Fidelity comparison: LibreOffice vs real-Office reference PDFs | High | Open |
| Apply `grayscale` param via pikepdf post-processing | Low | Open |
| macOS/Linux smoke test (blocked on non-Windows dev machine) | Low | Deferred |

---

## Predecessor Batches

- ho_0029 — conversion pipeline audit and architecture design
- ho_0034 — abstraction implementation + LibreOffice feature flag + 39 unit tests

---

## Sign-off

LibreOffice fallback hardening is complete. The conversion subsystem now has:
real fixtures, a full backend-selection test matrix, auto-skipping LibreOffice
integration tests, documented fidelity expectations, and clear CI wiring. The
Windows-first, Office-primary contract is preserved unchanged.
