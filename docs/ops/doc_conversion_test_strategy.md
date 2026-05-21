---
id: doc_conversion_test_strategy
title: Document Conversion Test Strategy
type: ops
project: APMultitool
status: current
created_at: 2026-05-21
updated_at: 2026-05-21
---

# Document Conversion Test Strategy

Test matrix and approach for `core/operations/docx_to_pdf.py`,
`core/operations/xlsx_to_pdf.py`, and `core/operations/_conversion_backend.py`.

Test files:
- `tests/test_docx_xlsx_bates.py` — existing engine-level tests (7 tests)
- `tests/test_conversion_backend.py` — new abstraction + detection tests (39 tests)

All tests are platform-agnostic. No real Office or LibreOffice installation required.

---

## 1. Test matrix

### 1.1 Unit tests — backend detection (✅ implemented)

`tests/test_conversion_backend.py` — `TestLibreOfficeFallbackEnabled`, `TestDetectBackend`,
`TestSofficeAvailable`

| Test | Scenario | Status |
|------|----------|--------|
| `test_default_enabled` | No env var set | ✅ |
| `test_zero_disables` | `APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK=0` | ✅ |
| `test_false_disables` / `test_no_disables` / `test_off_disables` | Alternate false values | ✅ |
| `test_override_param_win32com` | `override="win32com"` | ✅ |
| `test_override_param_libreoffice` | `override="libreoffice"` | ✅ |
| `test_env_var_libreoffice` | `APM_CONVERSION_BACKEND=libreoffice` | ✅ |
| `test_windows_returns_win32com` | `os.name == 'nt'` (mocked) | ✅ |
| `test_posix_soffice_present_fallback_enabled` | posix + soffice on PATH + enabled | ✅ |
| `test_posix_soffice_present_fallback_disabled` | posix + soffice on PATH + disabled | ✅ |
| `test_posix_no_soffice` | posix + no soffice | ✅ |
| `test_override_takes_priority_over_env_var` | param overrides env var | ✅ |
| `test_invalid_override_falls_through` | bad override string | ✅ |
| `test_env_var_invalid_falls_through` | bad env var value | ✅ |

### 1.2 Unit tests — `run_soffice_convert()` (✅ implemented)

`tests/test_conversion_backend.py` — `TestRunSofficeConvert`

| Test | Scenario | Status |
|------|----------|--------|
| `test_success_moves_output_to_out_path` | soffice mock succeeds + writes file | ✅ |
| `test_raises_file_not_found_when_soffice_absent` | `FileNotFoundError` from subprocess | ✅ |
| `test_raises_runtime_on_nonzero_exit` | `CalledProcessError` with exit 1 | ✅ |
| `test_raises_runtime_if_output_missing_after_success` | subprocess exit 0, no file | ✅ |
| `test_timeout_propagates` | `TimeoutExpired` raised | ✅ |

### 1.3 Unit tests — `convert_docx_to_pdf()` abstraction (✅ implemented)

`tests/test_conversion_backend.py` — `TestConvertDocxToPdf`

| Test | Scenario | Status |
|------|----------|--------|
| `test_win32com_success_returns_empty_warnings` | win32com mock succeeds | ✅ |
| `test_libreoffice_success_returns_empty_warnings` | soffice mock succeeds | ✅ |
| `test_none_backend_raises` | `ConversionBackend.NONE` | ✅ |
| `test_missing_source_raises_file_not_found` | src file absent | ✅ |
| `test_win32com_fails_fallback_enabled_soffice_present` | COM fails, soffice succeeds | ✅ |
| `test_win32com_fails_fallback_disabled_raises` | COM fails, flag=0 | ✅ |
| `test_win32com_fails_fallback_enabled_soffice_absent_raises` | COM fails, no soffice | ✅ |

### 1.4 Unit tests — `convert_xlsx_to_pdf()` abstraction (✅ implemented)

`tests/test_conversion_backend.py` — `TestConvertXlsxToPdf`

| Test | Scenario | Status |
|------|----------|--------|
| `test_win32com_success_returns_empty_warnings` | win32com mock succeeds | ✅ |
| `test_libreoffice_success_returns_empty_warnings` | soffice mock succeeds | ✅ |
| `test_none_backend_raises` | `ConversionBackend.NONE` | ✅ |
| `test_missing_source_raises_file_not_found` | src file absent | ✅ |
| `test_win32com_fails_fallback_enabled_soffice_present` | COM fails, soffice succeeds | ✅ |
| `test_win32com_fails_fallback_disabled_raises` | COM fails, flag=0 | ✅ |

### 1.5 Engine-level tests (✅ existing, still passing)

`tests/test_docx_xlsx_bates.py`

| Test | Status |
|------|--------|
| `test_docx_conversion_fails_missing_input` | ✅ |
| `test_docx_conversion_success` | ✅ |
| `test_xlsx_conversion_fails_missing_input` | ✅ |
| `test_xlsx_conversion_success` | ✅ |
| `test_bates_stamp_success` | ✅ |
| `test_bates_stamp_custom_name` | ✅ |
| `test_bates_stamp_cancellation` | ✅ |

### 1.6 Integration tests — Windows + Microsoft Office

Require: Windows host, Microsoft Word and Excel installed.

Mark with `@pytest.mark.integration_windows`.

| Test | Scenario | Status |
|------|----------|--------|
| `test_docx_real_conversion_windows` | Real `.docx` fixture → valid multi-page PDF | ⬜ future |
| `test_docx_password_protected_windows` | Password-protected `.docx` | ⬜ future |
| `test_xlsx_real_conversion_windows` | Real `.xlsx` → valid PDF with all sheets | ⬜ future |
| `test_xlsx_multisheet_windows` | `.xlsx` with 3 sheets | ⬜ future |
| `test_docx_large_document_windows` | 100-page `.docx`, must complete < 120 s | ⬜ future |

Fixtures needed in `tests/fixtures/conversion/`:
- `sample.docx` — 3-page document with a table and image
- `sample.xlsx` — 2-sheet workbook
- `password_protected.docx` — password: `test1234`

### 1.7 Integration tests — LibreOffice fallback

Require: LibreOffice installed, `soffice` on PATH.

Mark with `@pytest.mark.integration_libreoffice`.

| Test | Scenario | Status |
|------|----------|--------|
| `test_docx_libreoffice_fallback` | Non-Windows or flag forced, soffice present | ⬜ future |
| `test_xlsx_libreoffice_fallback` | Same | ⬜ future |
| `test_soffice_not_on_path` | soffice absent | ⬜ future |
| `test_soffice_timeout` | soffice takes > 60 s (mocked) | ⬜ future |
| `test_libreoffice_output_fidelity` | Page count matches reference | ⬜ future |

---

## 2. Mocking strategy

### Mocking win32com on any platform

```python
import sys
from unittest import mock

sys.modules.setdefault("pythoncom", mock.MagicMock())

with mock.patch("win32com.client.DispatchEx", return_value=mock_word, create=True):
    ...
```

The mock `SaveAs` / `ExportAsFixedFormat` side-effect must write a real PDF:

```python
from reportlab.pdfgen import canvas as rl_canvas

def _save_as(dest, FileFormat):
    c = rl_canvas.Canvas(dest)
    c.drawString(72, 720, "Test page")
    c.save()

mock_doc.SaveAs.side_effect = _save_as
```

### Mocking soffice subprocess

```python
def _soffice_fake_run(src_path):
    def _run(cmd, **kwargs):
        outdir = Path(cmd[cmd.index("--outdir") + 1])
        (outdir / (src_path.stem + ".pdf")).write_bytes(b"%PDF-1.4 minimal")
        return mock.MagicMock(returncode=0)
    return _run

with mock.patch("subprocess.run", side_effect=_soffice_fake_run(src)):
    ...
```

For failure:
```python
mock.patch("subprocess.run",
    side_effect=subprocess.CalledProcessError(1, ["soffice"], stderr=b"error"))
```

---

## 3. CI matrix

| Environment | Unit tests | Integration Windows | Integration LibreOffice |
|-------------|------------|---------------------|------------------------|
| GitHub Actions — Windows | ✅ 46/46 | ⬜ (requires real Office) | ⬜ |
| Local Windows dev box | ✅ | ✅ | ✅ (if LibreOffice installed) |
| macOS / Linux CI (future) | ✅ | ⬜ | ✅ |

---

## 4. Coverage targets

| Module | Target | Current (mocked) |
|--------|--------|-----------------|
| `core/operations/docx_to_pdf.py` | 90% | ~85% (integration lines excluded) |
| `core/operations/xlsx_to_pdf.py` | 90% | ~85% |
| `core/operations/_conversion_backend.py` | 100% | ✅ |

Run coverage:
```bash
pytest tests/test_conversion_backend.py tests/test_docx_xlsx_bates.py -v \
    --cov=core/operations/docx_to_pdf \
    --cov=core/operations/xlsx_to_pdf \
    --cov=core/operations/_conversion_backend \
    --cov-report=term-missing
```

---

## Related docs

- `docs/ops/doc_conversion_pipeline_overview.md` — pipeline architecture
- `docs/ops/doc_conversion_fallback_design.md` — implementation design
- `handoffs/ho_0034_2026_05_21_doc_conversion_super_batch.md` — this batch's handoff
