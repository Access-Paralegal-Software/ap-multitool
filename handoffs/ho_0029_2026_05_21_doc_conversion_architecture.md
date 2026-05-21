---
id: ho_0029_2026_05_21_doc_conversion_architecture
title: Handoff - Document Conversion Architecture (Abstraction + LibreOffice Fallback Design)
type: handoff
status: completed
project: APMultitool
lane: document-conversion-cross-platform
created_at: 2026-05-21
---

# Document Conversion Architecture Handoff

## Purpose

This handoff documents the architecture work done in the document-conversion lane
to identify the Word/Excel → PDF pipeline, design a cross-platform abstraction,
and lay the groundwork for macOS/Linux support via a LibreOffice fallback.

No user-facing behaviour was changed. All existing Windows functionality is intact.

---

## 1. What was audited

### Conversion modules

| Module | Platform | Role |
|--------|----------|------|
| `core/operations/docx_to_pdf.py` | Windows-primary | `handle(job, progress) → JobResult` for `.docx`/`.doc` |
| `core/operations/xlsx_to_pdf.py` | Windows-primary | `handle(job, progress) → JobResult` for `.xlsx`/`.xls`/`.csv` |

Both modules were already present and already contained a functional LibreOffice
`subprocess` fallback path. This work formalises and documents that design.

### Engine dispatch

Jobs flow through `DocEngine.submit()` in `core/engine.py`, which resolves the
operation name via `OPERATION_REGISTRY` in `core/operations/__init__.py`. The
conversion handlers are already registered as `"docx_to_pdf"` and `"xlsx_to_pdf"`.

---

## 2. Current pipeline (as-is)

```
GUI / CLI
  → DocEngine.submit(job)
      → OPERATION_REGISTRY["docx_to_pdf" | "xlsx_to_pdf"]
          → handle(job, progress)
              ├── if os.name == 'nt': try win32com (Word.Application / Excel.Application)
              │     success → done
              │     failure → append warning
              └── if not success: try soffice --headless --convert-to pdf
                    success → done
                    failure → raise RuntimeError
```

Full details: `docs/ops/doc_conversion_pipeline_overview.md`

---

## 3. Abstraction boundary

The `handle(job, progress) → JobResult` function contract is the abstraction
boundary. The caller (DocEngine) is backend-agnostic. Neither the GUI nor the
CLI needs to know whether conversion happened via COM or LibreOffice.

**Function signatures:**

```python
# core/operations/docx_to_pdf.py
def handle(job: Job, progress: Callable[[str, float], None]) -> JobResult
# job.params: DocxToPdfParams(grayscale: bool, output_name: str | None)

# core/operations/xlsx_to_pdf.py
def handle(job: Job, progress: Callable[[str, float], None]) -> JobResult
# job.params: XlsxToPdfParams(grayscale: bool, output_name: str | None)
```

Full design: `docs/ops/doc_conversion_fallback_design.md`

---

## 4. LibreOffice fallback design

### Invocation pattern

```bash
soffice --headless --convert-to pdf --outdir <output_directory> <source_file>
```

- Output file: `<output_directory>/<source_stem>.pdf`
- Timeout: 60 seconds (`subprocess.run(..., timeout=60, check=True)`)
- Non-zero exit → `CalledProcessError` → wrapped in `RuntimeError`

### Known open issues (not yet resolved)

1. **No startup check** — soffice absence is only discovered at conversion time.
2. **Concurrent call isolation** — headless LibreOffice shares a user profile;
   parallel calls need `--env:UserInstallation=file:///tmp/soffice_<uuid>`.
3. **Output fidelity** — LibreOffice rendering has not been validated against a
   test corpus. Required before enabling as default on macOS/Linux.

---

## 5. Environment detection module

**New file:** `core/operations/_conversion_backend.py`

```python
from core.operations._conversion_backend import detect_backend, ConversionBackend

backend = detect_backend()
# ConversionBackend.WIN32COM    — Windows (Office expected)
# ConversionBackend.LIBREOFFICE — soffice on PATH
# ConversionBackend.NONE        — nothing available
```

Selection order: override string → Windows (`os.name == 'nt'`) → soffice on PATH → NONE.

The `override` parameter is the designated hook for future config/env/CLI wiring.
The two conversion handlers still use inline `if os.name == 'nt':` logic; wiring
them to `detect_backend()` is a future batch item (see Section 7).

---

## 6. Testing plan

Full matrix: `docs/ops/doc_conversion_test_strategy.md`

**Summary:**

| Suite | Runs on | What it covers |
|-------|---------|----------------|
| Unit (mock everything) | Any platform, any CI | Abstraction layer, error paths, cancellation, `detect_backend()` |
| Integration Windows | Windows + real Office | Real `.docx`/`.xlsx` conversion, edge cases |
| Integration LibreOffice | LibreOffice installed | Fallback path, timeout, fidelity baseline |

Existing tests in `tests/test_docx_xlsx_bates.py` already cover:
- Missing input → `FileNotFoundError`
- Successful conversion (mocked win32com)
- Job metadata and output path assertions

Tests still needed (per the matrix in `doc_conversion_test_strategy.md`):
- LibreOffice path (mocked subprocess)
- Both-backends-fail path
- `detect_backend()` unit tests
- Integration fixtures in `tests/fixtures/conversion/`

---

## 7. Exact next steps for the next batch

These items are out of scope for this lane but are the natural next batch:

### 7.1 Wire `detect_backend()` into the handlers

Replace the inline `if os.name == 'nt':` block in both `docx_to_pdf.py` and
`xlsx_to_pdf.py` with a call to `detect_backend()`. The logic is identical; this
just removes duplication and makes the detection testable via `override`.

```python
from core.operations._conversion_backend import detect_backend, ConversionBackend

backend = detect_backend()
if backend == ConversionBackend.WIN32COM:
    # current win32com block
elif backend == ConversionBackend.LIBREOFFICE:
    # current soffice block
else:
    raise RuntimeError("No conversion backend available ...")
```

### 7.2 Add soffice startup check

In `DocEngine.__init__` or in `detect_backend()` itself, check `soffice_available()`
and surface a clear warning at startup if neither Office nor soffice is available.

### 7.3 Add soffice isolation flag

Add `--env:UserInstallation=file:///tmp/apm_soffice_{uuid}` to the subprocess call
to prevent profile conflicts when multiple conversions run in parallel.

### 7.4 Build the test fixtures

Create `tests/fixtures/conversion/`:
- `sample.docx` — 3-page document with a table and an image
- `sample.xlsx` — 2-sheet workbook
- `password_protected.docx`

### 7.5 Validate LibreOffice output fidelity

Run the integration suite on macOS and Linux with the sample fixtures. Compare
page count and key visual elements against a reference PDF generated by Word.

### 7.6 macOS/Linux packaging

Once fidelity is validated, coordinate with `docs/ops/macos_linux_packaging_plan.md`
to include LibreOffice as a runtime dependency in the macOS and Linux packages.

---

## 8. Files created by this lane

| File | Description |
|------|-------------|
| `core/operations/_conversion_backend.py` | Backend detection module |
| `docs/ops/doc_conversion_pipeline_overview.md` | Pipeline architecture note |
| `docs/ops/doc_conversion_fallback_design.md` | Abstraction boundary + Windows + LibreOffice design |
| `docs/ops/doc_conversion_test_strategy.md` | Test matrix |
| `handoffs/ho_0029_2026_05_21_doc_conversion_architecture.md` | This document |

---

## 9. Files unchanged by this lane

- `core/operations/docx_to_pdf.py` — no changes (existing behaviour preserved)
- `core/operations/xlsx_to_pdf.py` — no changes (existing behaviour preserved)
- `core/operations/__init__.py` — no changes
- `core/engine.py` — no changes
- `tests/test_docx_xlsx_bates.py` — no changes (all existing tests still pass)
