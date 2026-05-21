---
id: doc_conversion_fallback_design
title: Document Conversion Fallback Design
type: ops
project: APMultitool
status: implemented
created_at: 2026-05-21
updated_at: 2026-05-21
hardened_at: 2026-05-21
---

# Document Conversion Fallback Design

Architecture and implementation record for the cross-platform Word/Excel → PDF
conversion layer.  Covers the abstraction boundary, current Windows implementation,
LibreOffice fallback strategy, environment detection logic, and the feature flag.

---

## 1. Abstraction boundary

### Engine-level contract (unchanged)

All conversion operations conform to the engine's standard operation contract:

```python
def handle(job: Job, progress: Callable[[str, float], None]) -> JobResult
```

The caller (DocEngine) knows nothing about COM automation or LibreOffice.

### Implemented public abstraction functions

Two public functions now expose the conversion logic independently of the Job
model.  They are directly callable and directly testable without a full engine
invocation:

**Word conversion** (`core/operations/docx_to_pdf.py`)
```python
def convert_docx_to_pdf(
    src_path: Path,
    out_path: Path,
    backend: ConversionBackend | None = None,
) -> list[str]:
    ...
```

**Excel conversion** (`core/operations/xlsx_to_pdf.py`)
```python
def convert_xlsx_to_pdf(
    src_path: Path,
    out_path: Path,
    backend: ConversionBackend | None = None,
) -> list[str]:
    ...
```

Both functions:
- Accept `backend=None` (auto-detect) or an explicit `ConversionBackend` value.
- Return a list of warning strings (empty on clean success).
- Raise `FileNotFoundError` if the source file is missing.
- Raise `RuntimeError` if all available backends fail.

### Private backend implementations

Each module contains a private function for the Windows COM path:
- `docx_to_pdf._convert_via_win32com_word(src_path, out_path) → None`
- `xlsx_to_pdf._convert_via_win32com_excel(src_path, out_path) → None`

The LibreOffice path is shared via `_conversion_backend.run_soffice_convert(src_path, out_path)`.

---

## 2. Current Windows implementation

### Dependencies

| Requirement | Package | Notes |
|-------------|---------|-------|
| Python binding for COM | `pywin32` (`win32com.client`, `pythoncom`) | Windows only |
| Microsoft Word | installed separately | Required for `wdFormatPDF` export |
| Microsoft Excel | installed separately | Required for `xlTypePDF` export |

### Environment assumptions

- Operating system: Windows (`os.name == 'nt'`)
- Microsoft Office (Word and/or Excel) installed and licensed
- The process has permission to instantiate COM objects (`DispatchEx`)
- No other Word/Excel process holds a conflicting lock on the file

### Invocation pattern — Word

```python
# inside _convert_via_win32com_word()
pythoncom.CoInitialize()
word = win32com.client.DispatchEx("Word.Application")
word.Visible = False
word.DisplayAlerts = False
doc = word.Documents.Open(str(src_path.resolve()), ReadOnly=True)
doc.SaveAs(str(out_path.resolve()), FileFormat=17)  # 17 = wdFormatPDF
```

Cleanup is unconditional (runs in `finally`):
```python
doc.Close(SaveChanges=0)
word.Quit()
pythoncom.CoUninitialize()
```

### Invocation pattern — Excel

```python
# inside _convert_via_win32com_excel()
pythoncom.CoInitialize()
excel = win32com.client.DispatchEx("Excel.Application")
excel.Visible = False
excel.DisplayAlerts = False
wb = excel.Workbooks.Open(str(src_path.resolve()), ReadOnly=True)
wb.ExportAsFixedFormat(0, str(out_path.resolve()))  # 0 = xlTypePDF
```

### Known failure cases

- **Office not installed** — `win32com.client.DispatchEx` raises `pywintypes.com_error`
- **File password-protected** — Word/Excel prompts; `DisplayAlerts = False` silently fails
- **Macro/security dialog** — Office macro security prompts block headless runs
- **Thread-safety** — COM must be initialised per-thread; calling from a worker thread
  without `CoInitialize()` raises
- **Licence/activation dialog** — an unlicensed Office install may raise or hang

---

## 3. LibreOffice fallback implementation

### Overview

`core/operations/_conversion_backend.run_soffice_convert()` is the shared
LibreOffice invocation used by both `convert_docx_to_pdf` and `convert_xlsx_to_pdf`.
It works on macOS, Linux, and Windows (if LibreOffice is installed).

### Dependencies

| Requirement | Notes |
|-------------|-------|
| LibreOffice ≥ 6.x | `soffice` binary must be on PATH |
| No Python packages | pure subprocess invocation |

### Invocation pattern

```python
# inside run_soffice_convert()
with tempfile.TemporaryDirectory() as _tmp:
    tmp_dir = Path(_tmp)
    subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf",
         "--outdir", str(tmp_dir), str(src_path.resolve())],
        capture_output=True, timeout=60, check=True,
    )
    converted = tmp_dir / (src_path.stem + ".pdf")
    shutil.move(str(converted), str(out_path))
```

An isolated `TemporaryDirectory` is used for soffice output to prevent file naming
collisions between the source stem and the destination path.

### Expected return codes

| Exit code | Meaning |
|-----------|---------|
| 0 | Conversion succeeded; output file is in temp dir |
| Non-zero | `CalledProcessError` → wrapped in `RuntimeError` |
| Timeout | `subprocess.TimeoutExpired` propagates uncaught |

### Error handling

| Exception type | Cause | Result |
|----------------|-------|--------|
| `FileNotFoundError` | soffice not on PATH | re-raised with clear install message |
| `CalledProcessError` | non-zero exit | wrapped in `RuntimeError` with exit code + stderr |
| `TimeoutExpired` | soffice took > 60 s | propagates to caller |
| Output file absent | soffice exit 0 but no file | `RuntimeError` with path details |

---

## 4. Environment detection and selection

### Feature flag

| Setting | Env var | Default |
|---------|---------|---------|
| Enable/disable LibreOffice fallback | `APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK` | `1` (enabled) |
| Override primary backend | `APM_CONVERSION_BACKEND` | (auto-detect) |

```bash
# Disable LibreOffice fallback (Windows users who want Office-only)
set APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK=0

# Force LibreOffice as primary backend (any platform)
set APM_CONVERSION_BACKEND=libreoffice
```

`config.py` exposes these as `LIBREOFFICE_FALLBACK_ENABLED` and
`CONVERSION_BACKEND_OVERRIDE` for use by other modules.

### Backend selection — `detect_backend(override=None)`

Selection order:
1. `override` parameter (testing / programmatic override)
2. `APM_CONVERSION_BACKEND` env var
3. Windows (`os.name == 'nt'`) → `WIN32COM`
4. Non-Windows + soffice on PATH + fallback enabled → `LIBREOFFICE`
5. → `NONE`

### Backend cascade inside `convert_docx/xlsx_to_pdf()`

```
backend = detect_backend()   # WIN32COM on Windows

if WIN32COM:
    try: _convert_via_win32com_*()
    except:
        if libreoffice_fallback_enabled() AND soffice_available():
            warnings.append(...)
            run_soffice_convert()     ← LibreOffice fallback
        else:
            raise RuntimeError(...)  ← fail with clear message

elif LIBREOFFICE:
    run_soffice_convert()             ← non-Windows primary path

else (NONE):
    raise RuntimeError(...)           ← no backend available
```

---

## 5. Fidelity expectations for LibreOffice output

LibreOffice renders most documents correctly for paralegal use, but differs from
Microsoft Office in predictable ways.  The following table records what is expected
to survive and what may not.

### What survives (expected ✅)

| Element | Notes |
|---------|-------|
| Plain text paragraphs | Always preserved |
| Headings and paragraph hierarchy | Preserved; font and spacing may differ slightly |
| Bullet and numbered lists | Items preserved; indentation may vary |
| Basic tables (uniform column widths) | Cell content preserved; border styling may differ |
| Multi-sheet spreadsheets | All sheets converted; sheet boundaries preserved as page breaks |
| Numeric cell values | Always preserved |
| Column header formatting (bold) | Generally preserved |

### What may differ (known fidelity gaps ⚠️)

| Element | Behaviour |
|---------|-----------|
| Complex table layouts (merged cells, nested tables) | May reflow or lose merge structure |
| Advanced Word styles / custom themes | May fall back to generic formatting |
| Charts and embedded images in .xlsx | May not render or may be omitted |
| Page size and margin settings | May default to LibreOffice defaults if not explicitly set |
| Fonts not installed on the host | Substituted; may change layout |
| `.xls` (legacy binary format) | Conversion attempted; fidelity lower than `.xlsx` |

### What constitutes "good enough" for integration tests

A passing integration test requires:
1. Output PDF file exists and is non-empty.
2. `pikepdf.open()` succeeds without error.
3. Page count ≥ 1.

Optional secondary checks (text extraction via `pypdf`):
- Key strings from headings or cell headers are present in extracted text.
- Exact layout, font size, or visual rendering is **not** asserted.

---

## 6. Known limitations

| Limitation | Status |
|------------|--------|
| soffice not verified at startup — absent soffice only fails at conversion time | Open |
| `grayscale` param not applied by either backend (modelled but ignored) | Open |
| Concurrent soffice calls share user profile directory (no `--env:UserInstallation` isolation) | Open |
| No macOS/Linux packaging — application currently distributed for Windows only | Open |
| LibreOffice output fidelity not validated beyond structural checks | Open (real-Office comparison required before recommending as default) |
| No macOS/Linux smoke test performed — Windows-only development environment | **Not a support claim; macOS/Linux not supported** |

---

## 7. Non-Windows environment status

This implementation was developed and tested exclusively on **Windows**.

The LibreOffice path uses only `subprocess` (no platform-specific Python code),
so it is expected to work on macOS and Linux wherever `soffice` is on PATH.
However:

- **No macOS or Linux smoke test has been performed.**
- **No fidelity comparison against reference output has been done.**
- APMultitool is currently **distributed and supported on Windows only**.

Do not cite this document as evidence of macOS or Linux support.

---

## 8. Future work

| Item | Priority |
|------|----------|
| Add soffice availability check at startup | Medium |
| Implement `--env:UserInstallation` isolation per soffice call | Medium |
| Compare LibreOffice output fidelity against real-Office reference PDFs | High |
| Apply `grayscale` param via pikepdf post-processing | Low |
| macOS/Linux packaging (see `docs/ops/macos_linux_packaging_plan.md`) | Low (blocked on fidelity validation) |

---

## Related docs

- `docs/ops/doc_conversion_pipeline_overview.md` — pipeline architecture
- `docs/ops/doc_conversion_test_strategy.md` — test matrix (updated with fixture table)
- `handoffs/ho_0040_pm_report_2026_05_21_libreoffice_fallback_hardening.md` — this batch's PM report
