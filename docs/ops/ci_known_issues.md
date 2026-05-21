---
id: ci_known_issues
title: CI Known Issues — Platform-Specific Test Behavior
type: ops
status: active
project: Access Paralegal / APMultitool
created: 2026-05-21
---

# CI Known Issues — Platform-Specific Test Behavior

This document records known test failures or skips on non-Windows environments, with suggested fixes or workarounds. It is updated when new issues are discovered in CI.

---

## 1. Qt tests fail or hang on headless Linux

**Affected files:** `test_qt_bates.py`, `test_qt_compiler.py`, `test_qt_fileroom.py`, `test_qt_foundation.py`, `test_qt_infrastructure.py`, `test_qt_shutdown.py`, `test_telemetry.py`, `test_versioning.py`

**Marker:** `qt`

**Symptom:** Any test that instantiates `QtWidgets.QApplication` (directly or indirectly via `APMainWindow`) will crash or hang on a Linux runner that has no display server (`DISPLAY` not set).

Typical error:
```
qt.qpa.xcb: could not connect to display
Aborted (core dumped)
```
or a silent hang waiting for a display.

**Current mitigation:** The `tests.yml` workflow excludes `qt`-marked tests on `ubuntu-latest` using `-m "not qt and not packaging"`. The Qt suite runs only on `windows-latest`.

**Future fix options:**
1. **xvfb** — Use the `setup-xvfb` GitHub Action to provide a virtual framebuffer on Linux. Add to `tests.yml` before the Linux test step:
   ```yaml
   - name: Start Xvfb
     uses: coactions/setup-xvfb@v1
   ```
   Then change the Linux run command to `pytest --tb=short --junitxml=...` (no marker filter needed).
2. **offscreen platform** — Set `QT_QPA_PLATFORM=offscreen` before running pytest. PySide6 supports an offscreen backend that does not require a display:
   ```yaml
   - name: Run tests (Linux, offscreen Qt)
     env:
       QT_QPA_PLATFORM: offscreen
     run: pytest --tb=short --junitxml=test-results-linux.xml
   ```
   This is the lower-effort option and avoids the xvfb dependency entirely. Validate that all Qt widget tests pass with the offscreen backend before removing the marker filter.

---

## 2. Packaging tests are Windows-relevant only

**Affected file:** `test_packaging.py`

**Marker:** `packaging`

**Symptom:** `test_packaging.py` checks for the existence of Windows installer scripts (`apmultitool_installer.iss`, `build_installer.ps1`, `prepare_bundle.ps1`) using `os.path.exists()`. Because these files are committed to the repository, the file-existence tests **pass on all platforms**. However:

- The scripts themselves (Inno Setup, PowerShell) cannot be executed on Linux or macOS.
- Any future test that validates script *output* or *behavior* (not just existence) would fail on non-Windows.

**Current mitigation:** `tests.yml` excludes `packaging`-marked tests on Linux via `-m "not qt and not packaging"`. This is a forward-looking hygiene measure; the current tests themselves would pass on Linux.

**Future fix:** If packaging tests grow to invoke `build_installer.ps1` or `iscc.exe`, add a `pytest.mark.skipif` guard:
```python
import sys
pytestmark = [
    pytest.mark.packaging,
    pytest.mark.skipif(sys.platform != "win32", reason="Windows packaging scripts only"),
]
```

---

## 3. test_email_to_pdf.py depends on a scratch EML fixture

**Affected file:** `test_email_to_pdf.py`

**Marker:** `core`, `integration`

**Symptom:** The `test_email_path` fixture generates a temporary EML file dynamically if `scratch/test_temp/test_email.eml` is not present. This should work cross-platform. However, if the `scratch/` directory does not exist on a fresh clone, the fixture may fail.

**Mitigation:** The fixture creates the file dynamically; ensure `scratch/test_temp/` is created by the fixture before writing. Verify the fixture's `mkdir(parents=True, exist_ok=True)` call is in place. No CI change required at this time.

---

## 4. test_docx_xlsx_bates.py mocks win32com — passes cross-platform

**Affected file:** `test_docx_xlsx_bates.py`

**Marker:** `core`, `integration`

**Note (not a bug):** DOCX-to-PDF conversion in production uses `win32com.client` (Windows-only). The test file mocks this dependency using `unittest.mock`, so the tests pass on Linux and macOS. This is the intended behavior. No action needed.

---

## 5. LibreOffice integration tests auto-skip when soffice is absent

**Affected file:** `test_conversion_integration.py`

**Marker:** `libreoffice`

**Symptom (expected, not a bug):** `TestLibreOfficeIntegration` contains an `autouse` fixture (`require_soffice`) that calls `soffice_available()` at test setup time. If `soffice` is not on PATH — which is always the case on GitHub-hosted runners — every test in that class is skipped with the message:

```
SKIPPED [reason: LibreOffice not installed (soffice not on PATH)]
```

This produces 8 skips in the CI run. The overall job still passes (skips are not failures).

**Why it's excluded from the CI matrix:** Installing LibreOffice on GitHub-hosted runners would add 300–700 MB of download time to every run. The `libreoffice` subset is intentionally absent from `tests.yml`. Unit tests and mocked-backend integration tests continue to run in CI under the `core`, `conversion`, and `integration` subsets.

**To run LibreOffice tests locally:**
```bash
# Requires LibreOffice installed with soffice on PATH
python scripts/run_core_tests.py --subset libreoffice -v

# Force LibreOffice on any platform (even Windows if LibreOffice is installed)
set APM_CONVERSION_BACKEND=libreoffice
python scripts/run_core_tests.py --subset libreoffice -v
```

**Future option:** If a self-hosted runner with LibreOffice pre-installed is introduced, add a `libreoffice` job leg to `tests.yml` conditioned on `runner.os != 'GitHub-hosted'` or a dedicated `libreoffice` runner label.

---

## 6. Slow tests inflate CI wall time on Windows

**Affected file:** `test_stability.py`

**Marker:** `slow`

**Symptom:** `test_stability.py` includes large-file tests (50+ page PDFs, all six Bates placement positions, special characters). On a GitHub-hosted runner these add several minutes to the Windows CI leg.

**Mitigation options:**
- To skip slow tests in a fast feedback loop locally: `pytest -m "not slow"`
- To skip slow tests in a PR-only CI job, add a separate job step:
  ```yaml
  - name: Run fast tests only (PR)
    if: github.event_name == 'pull_request'
    run: pytest --tb=short -m "not slow" --junitxml=test-results-fast.xml
  ```
  Not currently implemented; add when CI wall time becomes a problem.
