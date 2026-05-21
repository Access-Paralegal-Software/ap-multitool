---
id: doc_conversion_pipeline_overview
title: Document Conversion Pipeline Overview
type: ops
project: APMultitool
status: current
created_at: 2026-05-21
---

# Document Conversion Pipeline Overview

Internal architecture note covering the Word-to-PDF and Excel-to-PDF conversion
paths as they exist in the codebase today.

---

## Pipeline entry points

All document operations are submitted through `DocEngine.submit(job)` in
`core/engine.py`. The engine resolves the operation name to a handler via the
`OPERATION_REGISTRY` dict in `core/operations/__init__.py`.

```
Caller (GUI / CLI)
    │
    ▼
DocEngine.submit(job)          core/engine.py
    │  resolves job.operation
    ▼
OPERATION_REGISTRY             core/operations/__init__.py
    ├── "docx_to_pdf" → core/operations/docx_to_pdf.handle
    └── "xlsx_to_pdf" → core/operations/xlsx_to_pdf.handle
```

Both handlers share the same function contract:

```python
def handle(job: Job, progress: Callable[[str, float], None]) -> JobResult
```

The `Job` type (defined in `core/job.py`) carries:
- `job.inputs` — list of `InputSpec` (path + SHA-256 hash)
- `job.params` — `DocxToPdfParams` or `XlsxToPdfParams`
- `job.output` — `OutputSpec` (destination directory, overwrite flag)

---

## Module map

| Module | Platform | Role |
|--------|----------|------|
| `core/engine.py` | cross-platform | Job dispatch, provenance, audit |
| `core/job.py` | cross-platform | Data model: Job, InputSpec, JobResult, params |
| `core/operations/__init__.py` | cross-platform | Operation registry |
| `core/operations/docx_to_pdf.py` | **Windows-primary**, LibreOffice fallback | Word → PDF |
| `core/operations/xlsx_to_pdf.py` | **Windows-primary**, LibreOffice fallback | Excel → PDF |
| `core/operations/_conversion_backend.py` | cross-platform | Backend detection helper |

---

## Conversion flow (per handler)

```
handle(job, progress)
    │
    ├─ Validate: input file exists, exactly one InputSpec
    ├─ Resolve output path (temp PDF → final destination)
    │
    ├─ if os.name == 'nt':
    │     attempt win32com Office automation
    │     success → skip fallback
    │     failure → append warning, proceed to fallback
    │
    ├─ if not success:
    │     attempt soffice --headless --convert-to pdf
    │     success → rename soffice output to tmp_pdf
    │     failure → raise RuntimeError (both paths failed)
    │
    ├─ Move tmp_pdf → final destination (with counter-suffix if no overwrite)
    ├─ Open with pikepdf to count pages
    └─ Return JobResult(outputs, page_count_in, page_count_out, warnings)
```

---

## Windows-specific components

### win32com Word automation (`docx_to_pdf.py:59–93`)

- Requires: `pywin32` package, Microsoft Word installed
- COM initialisation: `pythoncom.CoInitialize()` / `CoUninitialize()`
- Opens document with `Word.Application.DispatchEx`
- Saves as PDF via `doc.SaveAs(path, FileFormat=17)` (17 = `wdFormatPDF`)
- Application instance created with `DispatchEx` (isolated process per call)
- Always cleans up `doc.Close()` / `word.Quit()` in `finally`

### win32com Excel automation (`xlsx_to_pdf.py:59–93`)

- Requires: `pywin32` package, Microsoft Excel installed
- COM initialisation: same pattern as Word
- Opens workbook with `Excel.Application.DispatchEx`
- Exports via `wb.ExportAsFixedFormat(0, path)` (0 = `xlTypePDF`, all sheets)
- Always cleans up `wb.Close(SaveChanges=False)` / `excel.Quit()` in `finally`

---

## Cross-platform fallback

Both handlers share the same LibreOffice/soffice invocation pattern:

```python
subprocess.run(
    ["soffice", "--headless", "--convert-to", "pdf",
     "--outdir", str(tmp_pdf.parent), str(src_path.resolve())],
    capture_output=True, timeout=60, check=True
)
```

soffice writes `{stem}.pdf` into `--outdir`; the handler renames that file to
the expected `tmp_pdf` path before moving it to the final destination.

---

## Key dependencies

| Package | Purpose | Required on |
|---------|---------|-------------|
| `pywin32` (`win32com`, `pythoncom`) | Office COM automation | Windows only |
| `pikepdf` | Page count validation; used by all PDF operations | All platforms |
| `soffice` (LibreOffice) | Headless conversion fallback | macOS / Linux / Windows fallback |

---

## Known limitations

1. **soffice not verified at startup** — if `soffice` is not on PATH and win32com
   also fails, the error is only raised at conversion time, not during startup.
2. **No user-facing backend selection** — users cannot explicitly choose LibreOffice
   over Office; the fallback is automatic and silent (warning only).
3. **No macOS/Linux packaging** — `pywin32` is Windows-only; the application is
   currently packaged and distributed for Windows only.
4. **`grayscale` param unused in converters** — `DocxToPdfParams.grayscale` and
   `XlsxToPdfParams.grayscale` are modelled in the Job but not yet applied by
   the conversion handlers.

---

## Related docs

- `docs/ops/doc_conversion_fallback_design.md` — abstraction boundary and full fallback design
- `docs/ops/doc_conversion_test_strategy.md` — test matrix
- `docs/ops/macos_linux_packaging_plan.md` — cross-platform packaging strategy
- `handoffs/ho_0029_2026_05_21_doc_conversion_architecture.md` — future work handoff
