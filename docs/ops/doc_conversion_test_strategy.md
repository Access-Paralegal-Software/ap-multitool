---
id: doc_conversion_test_strategy
title: Document Conversion Test Strategy
type: ops
project: APMultitool
status: current
created_at: 2026-05-21
---

# Document Conversion Test Strategy

Test matrix and approach for `core/operations/docx_to_pdf.py` and
`core/operations/xlsx_to_pdf.py`, covering the abstraction layer, the Windows
COM path, and the LibreOffice fallback path.

Existing test file: `tests/test_docx_xlsx_bates.py`

---

## 1. Test matrix

### 1.1 Unit tests — abstraction layer (no real Office or soffice)

These tests run on any platform without any Office or LibreOffice installation.
All backend calls are mocked.

| Test | Scenario | Expected result |
|------|----------|-----------------|
| `test_docx_conversion_fails_missing_input` | Input file does not exist | `FileNotFoundError` raised |
| `test_docx_conversion_success` | win32com mock returns valid PDF | `JobStatus.COMPLETE`, output PDF exists |
| `test_docx_conversion_wrong_input_count` | `job.inputs` has 0 or 2 entries | `ValueError` raised |
| `test_docx_conversion_cancellation` | `job.status` set to `CANCELLED` mid-progress | `OperationCancelled` raised, no output file |
| `test_docx_conversion_win32com_fails_libreoffice_succeeds` | win32com raises, soffice mock produces PDF | `JobStatus.COMPLETE`, warning in result |
| `test_docx_conversion_both_backends_fail` | win32com raises, soffice raises | `RuntimeError` raised with combined message |
| `test_xlsx_conversion_fails_missing_input` | Input file does not exist | `FileNotFoundError` raised |
| `test_xlsx_conversion_success` | win32com mock returns valid PDF | `JobStatus.COMPLETE`, output PDF exists |
| `test_xlsx_conversion_wrong_input_count` | `job.inputs` has 0 or 2 entries | `ValueError` raised |
| `test_xlsx_conversion_cancellation` | `job.status` set to `CANCELLED` mid-progress | `OperationCancelled` raised, no output file |
| `test_xlsx_conversion_win32com_fails_libreoffice_succeeds` | win32com raises, soffice mock produces PDF | `JobStatus.COMPLETE`, warning in result |
| `test_xlsx_conversion_both_backends_fail` | win32com raises, soffice raises | `RuntimeError` raised with combined message |
| `test_detect_backend_windows` | `os.name == 'nt'`, monkeypatched | Returns `ConversionBackend.WIN32COM` |
| `test_detect_backend_libreoffice` | `os.name == 'posix'`, soffice on PATH | Returns `ConversionBackend.LIBREOFFICE` |
| `test_detect_backend_none` | `os.name == 'posix'`, soffice absent | Returns `ConversionBackend.NONE` |
| `test_detect_backend_override` | `override="libreoffice"` | Returns `ConversionBackend.LIBREOFFICE` |
| `test_no_overwrite_counter_suffix` | Output file already exists, `overwrite=False` | New file has `_01` suffix |
| `test_overwrite_allowed` | Output file already exists, `overwrite=True` | Original file replaced |
| `test_temp_file_cleanup_on_failure` | Both backends fail | No temp files left in temp dir |

### 1.2 Integration tests — Windows + Microsoft Office

Require: Windows host, Microsoft Word installed, Microsoft Excel installed.

Mark with `@pytest.mark.integration_windows`.

| Test | Scenario | Expected result |
|------|----------|-----------------|
| `test_docx_real_conversion_windows` | Real `.docx` fixture file | Valid multi-page PDF produced |
| `test_docx_password_protected_windows` | Password-protected `.docx` | `RuntimeError` or warning; no corrupt output |
| `test_xlsx_real_conversion_windows` | Real `.xlsx` fixture file | Valid PDF produced, all sheets |
| `test_xlsx_multisheet_windows` | `.xlsx` with 3 sheets | All sheets present in output PDF |
| `test_docx_large_document_windows` | 100-page `.docx` | Conversion completes within 120 seconds |

Fixture files for this suite live in `tests/fixtures/conversion/`:
- `sample.docx` — 3-page Word document with a table and an image
- `sample.xlsx` — 2-sheet workbook
- `password_protected.docx` — password-protected (password: `test1234`)

### 1.3 Integration tests — LibreOffice fallback

Require: LibreOffice installed, `soffice` on PATH.

Mark with `@pytest.mark.integration_libreoffice`.

| Test | Scenario | Expected result |
|------|----------|-----------------|
| `test_docx_libreoffice_fallback` | `os.name != 'nt'` or win32com unavailable, soffice present | Valid PDF produced |
| `test_xlsx_libreoffice_fallback` | Same | Valid PDF produced |
| `test_soffice_not_on_path` | soffice absent from PATH | `RuntimeError` with clear message |
| `test_soffice_timeout` | soffice takes > 60 s (mocked) | `TimeoutExpired` propagated as `RuntimeError` |
| `test_libreoffice_output_fidelity` | Compare page count and image presence | Page count matches reference PDF |

### 1.4 CI matrix

| Environment | Unit tests | Integration Windows | Integration LibreOffice |
|-------------|------------|---------------------|------------------------|
| GitHub Actions — Windows (win32com mocked) | ✅ | ⬜ (requires real Office) | ⬜ |
| Local Windows dev box | ✅ | ✅ | ✅ (if LibreOffice installed) |
| macOS / Linux CI (future) | ✅ | ⬜ | ✅ |

---

## 2. Mocking strategy

### Mocking win32com on non-Windows hosts

```python
import sys
from unittest import mock

sys.modules['win32com'] = mock.MagicMock()
sys.modules['win32com.client'] = mock.MagicMock()
sys.modules['pythoncom'] = mock.MagicMock()

with mock.patch('win32com.client.DispatchEx', return_value=mock_word):
    ...
```

The mock `SaveAs` / `ExportAsFixedFormat` side-effect must write a real PDF to
the destination path, otherwise pikepdf page-count validation will fail or warn.
Use `reportlab` to produce a minimal valid PDF in the side effect.

### Mocking soffice subprocess

```python
with mock.patch('subprocess.run') as mock_run:
    mock_run.return_value = mock.MagicMock(returncode=0)
    # also create the expected output file manually
    (tmp_dir / (src.stem + ".pdf")).write_bytes(minimal_pdf_bytes)
    ...
```

For failure scenarios:
```python
from subprocess import CalledProcessError
mock_run.side_effect = CalledProcessError(1, ["soffice"])
```

---

## 3. Test fixtures

`tests/fixtures/conversion/` — place real document fixtures here for integration
tests. These files should be:
- Minimal (smallest possible files that exercise the target code path)
- Committed to the repo (no external download)
- Accompanied by a `README.md` describing what each fixture tests

---

## 4. Coverage targets

| Module | Target line coverage |
|--------|---------------------|
| `core/operations/docx_to_pdf.py` | 90 % |
| `core/operations/xlsx_to_pdf.py` | 90 % |
| `core/operations/_conversion_backend.py` | 100 % |

Run with:
```bash
pytest tests/test_docx_xlsx_bates.py -v --cov=core/operations/docx_to_pdf \
    --cov=core/operations/xlsx_to_pdf --cov=core/operations/_conversion_backend \
    --cov-report=term-missing
```

---

## Related docs

- `docs/ops/doc_conversion_pipeline_overview.md` — pipeline architecture
- `docs/ops/doc_conversion_fallback_design.md` — abstraction boundary and design
- `handoffs/ho_0029_2026_05_21_doc_conversion_architecture.md` — future work handoff
