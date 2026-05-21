---
id: ho_0034_2026_05_21_doc_conversion_super_batch
title: Handoff - Document Conversion Abstraction + Experimental LibreOffice Fallback
type: handoff
status: completed
project: APMultitool
lane: document-conversion-cross-platform
created_at: 2026-05-21
---

# Document Conversion Architecture — Super Batch Handoff

## 1. Summary of work

This batch moved the conversion architecture from "design-only" to a minimal but
functional implementation.  No user-facing behavior was changed; all existing
Windows functionality is intact.

### Files changed

| File | Change type | What changed |
|------|-------------|--------------|
| `config.py` | Modified | Added `CONVERSION_BACKEND_OVERRIDE` and `LIBREOFFICE_FALLBACK_ENABLED` from env vars |
| `core/operations/_conversion_backend.py` | Modified | Added `libreoffice_fallback_enabled()`, env-var detection in `detect_backend()`, and `run_soffice_convert()` |
| `core/operations/docx_to_pdf.py` | Refactored | Extracted `_convert_via_win32com_word()`, added `convert_docx_to_pdf()` public abstraction; `handle()` now delegates to it |
| `core/operations/xlsx_to_pdf.py` | Refactored | Same pattern: `_convert_via_win32com_excel()`, `convert_xlsx_to_pdf()`, refactored `handle()` |
| `conftest.py` | New | Registers `integration_windows` and `integration_libreoffice` pytest markers |
| `tests/test_conversion_backend.py` | New | 39 unit tests covering detection, soffice utilities, and abstraction functions |
| `docs/ops/doc_conversion_fallback_design.md` | Updated | Status → implemented; added feature flag docs, cascade diagram, known limitations |
| `docs/ops/doc_conversion_test_strategy.md` | Updated | Marked implemented tests; added CI matrix; updated coverage section |

### Tests: 46 / 46 passing

---

## 2. What the abstraction gives you

### Before

`handle()` contained all backend logic inline with an `if os.name == 'nt':` check.
Untestable without a Job object and a full engine invocation.

### After

```python
from core.operations.docx_to_pdf import convert_docx_to_pdf
from core.operations._conversion_backend import ConversionBackend

# Use directly, no Job/engine required
warnings = convert_docx_to_pdf(
    src_path=Path("report.docx"),
    out_path=Path("/tmp/report.pdf"),
    backend=ConversionBackend.WIN32COM,   # or LIBREOFFICE, or None for auto
)
```

The `handle()` function still exists and its behavior is unchanged — it now
delegates to `convert_docx_to_pdf()` internally.

---

## 3. How to enable / disable the LibreOffice fallback

### Default behavior (no env var set)

- **Windows with Office**: win32com path succeeds. LibreOffice never invoked.
- **Windows without Office**: win32com fails → LibreOffice fallback attempted
  (if soffice is on PATH).
- **macOS / Linux**: LibreOffice used directly if soffice is on PATH.

### Disable LibreOffice entirely (Windows Office-only mode)

```powershell
$env:APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK = "0"
```

When disabled: if win32com fails, a `RuntimeError` is raised immediately with a
message explaining that the fallback is disabled.

### Force LibreOffice as primary backend (any platform)

```bash
export APM_CONVERSION_BACKEND=libreoffice
```

This bypasses win32com even on Windows.

---

## 4. How to test conversions on non-Windows OS

All unit tests are platform-agnostic — run them directly:

```bash
pytest tests/test_conversion_backend.py -v
```

To specifically test the LibreOffice path (mocked):

```bash
pytest tests/test_conversion_backend.py -k "libreoffice" -v
```

To run integration tests when LibreOffice is installed on macOS/Linux:

```bash
APM_CONVERSION_BACKEND=libreoffice \
    pytest tests/ -m integration_libreoffice -v
```

---

## 5. Open TODOs for the next batch

| # | Item | Priority |
|---|------|----------|
| 1 | Build `tests/fixtures/conversion/` with real `.docx` / `.xlsx` samples | High |
| 2 | Add `integration_libreoffice` tests using those fixtures | High |
| 3 | Validate LibreOffice rendering fidelity against Office reference PDFs | High |
| 4 | Add soffice startup check in DocEngine or CLI entry point | Medium |
| 5 | Add `--env:UserInstallation` profile isolation in `run_soffice_convert()` | Medium |
| 6 | Wire `APM_CONVERSION_BACKEND` / fallback flag into the Qt UI settings screen | Low |
| 7 | Apply `grayscale` param in soffice path (post-processing with pikepdf) | Low |
| 8 | macOS/Linux packaging (blocked on fidelity validation) | Low |

---

## 6. Key facts for the next engineer

- `detect_backend()` returns the **primary** backend only.  The LibreOffice
  **cascade** (used when WIN32COM fails) is handled inside `convert_docx/xlsx_to_pdf()`,
  gated by `libreoffice_fallback_enabled() and soffice_available()`.
- `run_soffice_convert()` always uses a temp dir for soffice output — never writes
  directly to `out_path`.  This prevents partial writes at the destination.
- `APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK` defaults to `"1"` (enabled). The flag
  value `"0"`, `"false"`, `"no"`, or `"off"` disables it.
- `APM_CONVERSION_BACKEND` overrides auto-detection entirely; the fallback cascade
  still applies if `"win32com"` is forced and COM fails.
