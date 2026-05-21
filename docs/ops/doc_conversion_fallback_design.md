---
id: doc_conversion_fallback_design
title: Document Conversion Fallback Design
type: ops
project: APMultitool
status: current
created_at: 2026-05-21
---

# Document Conversion Fallback Design

Architecture design for the cross-platform Word/Excel → PDF conversion layer,
covering the abstraction boundary, current Windows implementation, LibreOffice
fallback strategy, and environment detection logic.

---

## 1. Abstraction boundary

All conversion operations conform to the engine's standard operation contract:

```python
def handle(job: Job, progress: Callable[[str, float], None]) -> JobResult
```

The caller (DocEngine) knows nothing about COM automation or LibreOffice. It
submits a `Job` and receives a `JobResult`. Backend selection is entirely
internal to the handler.

### Effective public signatures

**Word conversion** (`core/operations/docx_to_pdf.py`)
```python
handle(job: Job, progress: Callable[[str, float], None]) -> JobResult
# job.operation == "docx_to_pdf"
# job.params    == DocxToPdfParams(grayscale: bool, output_name: str | None)
# job.inputs[0].path must be an existing .docx or .doc file
```

**Excel conversion** (`core/operations/xlsx_to_pdf.py`)
```python
handle(job: Job, progress: Callable[[str, float], None]) -> JobResult
# job.operation == "xlsx_to_pdf"
# job.params    == XlsxToPdfParams(grayscale: bool, output_name: str | None)
# job.inputs[0].path must be an existing .xlsx, .xls, or .csv file
```

### Expected behaviour — success

On success the handler returns a `JobResult` with:
- `outputs` — single-element list containing the absolute path to the produced PDF
- `page_count_in` / `page_count_out` — page count read back from the output PDF
- `warnings` — empty list (or non-empty if the primary path failed and the
  fallback succeeded)
- `error` — `None`

### Expected behaviour — failure modes

| Scenario | Result |
|----------|--------|
| Input file does not exist | `FileNotFoundError` raised before conversion starts |
| `job.inputs` length ≠ 1 | `ValueError` raised |
| Win32com fails, soffice also fails | `RuntimeError` with both error messages |
| Win32com fails, soffice succeeds | `JobResult` with warning message, `error=None` |
| Conversion succeeds but output PDF is unreadable by pikepdf | `JobResult` with `page_count=0`; not treated as failure |
| Job cancelled mid-flight | `OperationCancelled` raised; temp files cleaned up |

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
- Microsoft Office (Word and/or Excel) is installed and licensed
- The process has permission to instantiate COM objects (`DispatchEx`)
- No other Word/Excel process is holding a conflicting lock on the file

### Invocation pattern — Word

```python
pythoncom.CoInitialize()
word = win32com.client.DispatchEx("Word.Application")
word.Visible = False
word.DisplayAlerts = False
doc = word.Documents.Open(str(src_path.resolve()), ReadOnly=True)
doc.SaveAs(str(tmp_pdf.resolve()), FileFormat=17)  # 17 = wdFormatPDF
```

Cleanup is unconditional (runs in `finally`):
```python
doc.Close(SaveChanges=0)
word.Quit()
pythoncom.CoUninitialize()
```

### Invocation pattern — Excel

```python
pythoncom.CoInitialize()
excel = win32com.client.DispatchEx("Excel.Application")
excel.Visible = False
excel.DisplayAlerts = False
wb = excel.Workbooks.Open(str(src_path.resolve()), ReadOnly=True)
wb.ExportAsFixedFormat(0, str(tmp_pdf.resolve()))  # 0 = xlTypePDF
```

### Known failure cases

- **Office not installed** — `win32com.client.DispatchEx` raises `pywintypes.com_error`
- **File password-protected** — Word/Excel prompts; `word.DisplayAlerts = False` will
  silently fail; `SaveAs` will raise
- **Macro/security dialog** — Office macro security prompts block headless runs
- **Thread-safety** — COM must be initialised per-thread; calling from a worker
  thread without `CoInitialize()` raises `CoUninitializedException`
- **Licence / activation dialog** — an unlicensed Office install may raise or hang

---

## 3. Fallback implementation (LibreOffice / soffice)

### Overview

When the Windows COM path is unavailable or fails, both handlers fall back to
headless LibreOffice via the `soffice` CLI. This path works on macOS, Linux, and
Windows (if LibreOffice is installed).

### Dependencies

| Requirement | Notes |
|-------------|-------|
| LibreOffice ≥ 6.x | `soffice` binary must be on PATH |
| No Python packages | pure subprocess invocation |

### Invocation pattern

```python
result = subprocess.run(
    [
        "soffice",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", str(output_directory),
        str(src_path.resolve()),
    ],
    capture_output=True,
    timeout=60,
    check=True,        # raises CalledProcessError on non-zero exit
)
```

soffice writes the converted file as `{src_stem}.pdf` into `--outdir`. The
handler moves this to the expected `tmp_pdf` path immediately after:

```python
converted_file = tmp_pdf.parent / (src_path.stem + ".pdf")
if converted_file.exists():
    shutil.move(str(converted_file), str(tmp_pdf))
```

### Expected return codes

| Exit code | Meaning |
|-----------|---------|
| 0 | Conversion succeeded; output file is in `--outdir` |
| Non-zero | Conversion failed; `check=True` raises `CalledProcessError` |
| Timeout | `subprocess.run` raises `TimeoutExpired` after 60 seconds |

### Error handling strategy

All LibreOffice errors are caught and wrapped in a `RuntimeError` that includes
both the win32com error message (if any) and the subprocess error. This gives
operators a single error that explains the full failure chain.

### Known limitations of the LibreOffice path

- **Formatting fidelity** — LibreOffice may render some Word/Excel formatting
  slightly differently from native Office.
- **soffice not on PATH** — raises `FileNotFoundError` (subprocess.run on
  Windows) or `CalledProcessError`; no installation check at startup.
- **Concurrent calls** — headless LibreOffice uses a user profile directory;
  parallel calls may conflict. Mitigation: pass `--env:UserInstallation=...` to
  isolate per-call (not yet implemented; tracked as future work).
- **Output file naming** — soffice derives the output filename from the source
  stem; if the stem contains characters invalid on the host filesystem, the
  output path lookup may fail.

---

## 4. Environment detection and selection

### Current detection logic

Both handlers apply this selection inline:

```python
success = False

if os.name == 'nt':          # Windows
    try:
        # attempt win32com path
        success = ...
    except Exception as exc:
        warnings.append(f"Win32com ... failed: {exc}. Attempting LibreOffice fallback.")

if not success:              # macOS / Linux / Windows fallback
    # attempt soffice path
```

### Centralised detection helper

`core/operations/_conversion_backend.py` provides `detect_backend()` as a
single, testable function that encapsulates the selection rule:

```python
from core.operations._conversion_backend import detect_backend, ConversionBackend

backend = detect_backend()
# ConversionBackend.WIN32COM    — Windows, Office expected
# ConversionBackend.LIBREOFFICE — soffice on PATH
# ConversionBackend.NONE        — nothing available
```

Selection order implemented by `detect_backend(override=None)`:

1. If `override` is set (e.g. from a config flag), use it.
2. On Windows (`os.name == 'nt'`), return `WIN32COM`.
3. If `shutil.which("soffice")` is not None, return `LIBREOFFICE`.
4. Otherwise return `NONE`.

### Config override hook

`detect_backend()` accepts an `override: str | None` parameter. Future
integration paths:

- Read `config.CONVERSION_BACKEND_OVERRIDE` from `config.py`
- Expose as a CLI flag: `--backend libreoffice`
- Expose as an environment variable: `APM_CONVERSION_BACKEND=libreoffice`

None of these are wired today; the override parameter exists as the hook point.

### Rationale for current inline approach

The current inline `if os.name == 'nt'` check was sufficient for the initial
Windows-only release. The `_conversion_backend.py` module is the designated
location for this logic once the fallback path is exercised in production on
macOS/Linux. The handlers will be updated to call `detect_backend()` in a
future batch.

---

## 5. Future work

| Item | Priority | Notes |
|------|----------|-------|
| Wire `detect_backend()` into both handlers | High | Replace inline `if os.name == 'nt'` |
| Add soffice availability check at startup | Medium | Surface clear error before conversion attempt |
| Implement `--env:UserInstallation` isolation for parallel calls | Medium | Prevent concurrent soffice profile conflicts |
| Apply `grayscale` param in LibreOffice path | Low | Not supported by soffice CLI; may require post-processing |
| Validate LibreOffice output fidelity against test corpus | High | Required before enabling as default on macOS/Linux |

---

## Related docs

- `docs/ops/doc_conversion_pipeline_overview.md` — pipeline architecture
- `docs/ops/doc_conversion_test_strategy.md` — test matrix
- `handoffs/ho_0029_2026_05_21_doc_conversion_architecture.md` — future work handoff
