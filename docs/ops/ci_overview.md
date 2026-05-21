---
id: ci_overview
title: CI Overview — Test Workflows and Developer Ergonomics
type: ops
status: active
project: Access Paralegal / APMultitool
created: 2026-05-21
---

# CI Overview — Test Workflows and Developer Ergonomics

---

## 1. Workflows at a Glance

| Workflow | File | Trigger | Purpose |
|---|---|---|---|
| **CI Test Suite** | `.github/workflows/tests.yml` | Push/PR to `master`, manual | Runs pytest on 3-platform × subset matrix |
| **Cross-Platform Build** | `.github/workflows/build.yml` | Push to `master`, manual | Legacy packaging probe (outdated entry point — see ho_0026) |
| **macOS Packaging Probe** | `.github/workflows/macos_packaging_probe.yml` | Manual, `release/**` push | macOS build probe; signing/notarization guarded |
| **Notion Sync** | `.github/workflows/notion-sync.yml` | Push any branch | Syncs commit metadata to Notion |

The **CI Test Suite** is the primary gate for code correctness.

---

## 2. Test Matrix

The test workflow runs a matrix of **3 operating systems × 7 named subsets**, producing 21 parallel jobs.

| OS | Qt tests | Packaging tests | Display |
|---|---|---|---|
| `windows-latest` | ✅ Native | ✅ Native | Native |
| `macos-latest` | ✅ Native | ✅ File checks pass | Native |
| `ubuntu-latest` | ✅ via xvfb | ✅ File checks pass | Virtual (xvfb) |

Linux installs `xvfb` and system Qt dependencies, then wraps the test runner with `xvfb-run --auto-servernum` to provide a virtual framebuffer. This allows PySide6 to instantiate `QApplication` without a real display server.

See `docs/ops/ci_known_issues.md` for platform-specific caveats.

---

## 3. Test Subsets and Markers

Named subsets (used in the CI matrix) map to pytest marker expressions via `run_core_tests.py`. Markers are declared in `pytest.ini`; all test files carry a `pytestmark` module-level variable.

| Subset / Marker | What it covers | Test files |
|---|---|---|
| `unit` → `core` | Headless engine tests — no UI dependency | test_core_folder_tree, test_docx_xlsx_bates, test_email_to_pdf, test_stability, test_conversion_backend, test_conversion_integration (non-libreoffice) |
| `integration` | Multi-component end-to-end tests | test_cli_ux, test_core_folder_tree, test_docx_xlsx_bates, test_email_to_pdf, test_stability, test_conversion_integration (non-libreoffice) |
| `core` | Same as unit | (see above) |
| `qt` | Tests requiring a live `QApplication` / PySide6 display | all test_qt_* files, test_telemetry, test_versioning |
| `cli` | Tests invoking the CLI via subprocess | test_cli_ux |
| `telemetry` | Telemetry subsystem | test_telemetry |
| `packaging` | Installer/packaging script checks | test_packaging |
| `smoke` | Quick import and wiring sanity | test_qt_foundation, test_versioning |
| `slow` | Computationally heavy (large PDFs, all Bates variants) | test_stability |
| `conversion` | Document conversion subsystem — all non-LibreOffice tests | test_conversion_backend, test_conversion_integration |
| `libreoffice` | LibreOffice integration tests — **local only, not in CI matrix** | test_conversion_integration (TestLibreOfficeIntegration) |

---

## 4. Developer Quickstart — Run Tests Locally

Install dependencies the same way CI does:

```bash
pip install pytest pytest-qt PySide6 pypdf reportlab pikepdf pymupdf extract-msg cryptography pillow
```

**Run all tests:**
```bash
pytest
python scripts/run_core_tests.py
```

**Run a named subset (mirrors CI matrix):**
```bash
python scripts/run_core_tests.py --subset core
python scripts/run_core_tests.py --subset qt
python scripts/run_core_tests.py --subset cli
python scripts/run_core_tests.py --subset unit
python scripts/run_core_tests.py --subset telemetry
```

**Run with a marker expression (ad-hoc):**
```bash
pytest -m core
pytest -m "core and not slow"
pytest -m "not qt and not packaging"
python scripts/run_core_tests.py --marker "core and not slow"
python scripts/run_core_tests.py --marker slow
```

**Fastest feedback loop:**
```bash
pytest -m smoke
python scripts/run_core_tests.py --subset smoke
```

**Print what would run without executing:**
```bash
python scripts/run_core_tests.py --subset qt --dry-run
```

**Generate a JUnit XML report:**
```bash
pytest --junitxml=test-results.xml
python scripts/run_core_tests.py --subset core --junit test-results.xml
```

**Qt tests on Linux (requires xvfb):**
```bash
sudo apt-get install -y xvfb libegl1-mesa libxkbcommon-x11-0 libxcb-icccm4 \
    libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 \
    libxcb-xinerama0 libxcb-xfixes0 libgl1-mesa-glx
xvfb-run --auto-servernum python scripts/run_core_tests.py --subset qt
```

---

## 5. CI Failure Response Guide

### Step 1: Find the failing job in GitHub Actions

1. Go to the repository on GitHub → **Actions** tab.
2. Click the failing workflow run.
3. The matrix summary shows which `subset (os)` combination failed.
4. Click the failing job leg to see the full pytest output inline.
5. Download the **test-results-\<os\>-\<subset\>.xml** artifact from the run summary for structured failure data.

### Step 2: Reproduce locally

```bash
# Reproduce a specific subset on your local platform
python scripts/run_core_tests.py --subset qt -v

# Reproduce a single failing test
pytest tests/test_qt_shutdown.py::test_shell_shutdown_cleans_workers -v

# Reproduce Linux leg locally (if you have xvfb)
xvfb-run --auto-servernum python scripts/run_core_tests.py --subset qt
```

### Step 3: Diagnose marker issues

```bash
# List all collected tests and their markers without running
pytest --collect-only -q

# Check which tests match a given subset/marker
pytest --collect-only -q -m core
python scripts/run_core_tests.py --subset qt --dry-run
```

If a marker is unknown (produces `PytestUnknownMarkWarning`), add it to the `markers` section in `pytest.ini` and apply `pytestmark` in the relevant test file.

### Step 4: Fix and update

- **Test logic fix:** Update the test, run locally, confirm it passes.
- **New marker needed:** Add to `pytest.ini` and set `pytestmark` in the test file. Update `SUBSET_MARKERS` in `run_core_tests.py` if a new subset name is needed.
- **Platform-specific failure:** Document in `ci_known_issues.md` with reproduction steps and mitigation options.
- **Flaky test:** Document in `ci_known_issues.md`, add retry logic, or isolate the test.

### Step 5: Push and verify

Push the branch. The CI Test Suite triggers automatically on PR. Confirm the previously failing job is green before merging.
