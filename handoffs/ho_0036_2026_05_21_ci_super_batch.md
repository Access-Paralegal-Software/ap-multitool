---
id: ho_0036_2026_05_21_ci_super_batch
title: Handoff — CI Super Batch: Test Markers, Matrix Hygiene, and Docs
type: handoff
status: completed
project: Access Paralegal / APMultitool
lane: ci-test-hygiene
created: 2026-05-21
---

# Handoff: CI Super Batch — Test Markers, Matrix Hygiene, and Docs

## 1. Summary

This batch introduced structured pytest markers across all 14 test files, a dedicated `tests.yml` CI workflow with an OS matrix, a developer-facing local test runner script, and comprehensive ops documentation covering CI ergonomics and known platform issues. The goal was to give CI a clean foundation that separates test categories, handles platform differences explicitly, and makes local reproduction of CI runs trivial.

---

## 2. Files Created

| File | Description |
|---|---|
| `pytest.ini` | Marker declarations for `core`, `qt`, `cli`, `integration`, `slow`, `telemetry`, `packaging`, `smoke` |
| `.github/workflows/tests.yml` | Dedicated test workflow: Ubuntu (core/CLI subset) + Windows (all) matrix |
| `scripts/run_core_tests.py` | Local test runner with `--marker`, `--verbose`, `--tb`, `--junit` flags |
| `docs/ops/ci_overview.md` | Developer quickstart, test matrix reference, CI failure response guide |
| `docs/ops/ci_known_issues.md` | Platform-specific issues: Qt on headless Linux, packaging Windows-only scope |
| `handoffs/ho_0036_2026_05_21_ci_super_batch.md` | This handoff |

---

## 3. Files Modified (Markers Added)

All 14 test files received a `pytestmark` module-level variable after their import block.

| File | Markers Applied |
|---|---|
| `tests/test_cli_ux.py` | `cli`, `integration` |
| `tests/test_core_folder_tree.py` | `core`, `integration` |
| `tests/test_docx_xlsx_bates.py` | `core`, `integration` |
| `tests/test_email_to_pdf.py` | `core`, `integration` |
| `tests/test_packaging.py` | `packaging` |
| `tests/test_qt_bates.py` | `qt` |
| `tests/test_qt_compiler.py` | `qt` |
| `tests/test_qt_fileroom.py` | `qt` |
| `tests/test_qt_foundation.py` | `qt`, `smoke` |
| `tests/test_qt_infrastructure.py` | `qt` |
| `tests/test_qt_shutdown.py` | `qt` |
| `tests/test_stability.py` | `core`, `integration`, `slow` |
| `tests/test_telemetry.py` | `qt`, `telemetry` |
| `tests/test_versioning.py` | `qt`, `smoke` |

---

## 4. CI Matrix Behavior

| Runner | Command | Active markers |
|---|---|---|
| `windows-latest` | `pytest --tb=short --junitxml=test-results-windows.xml` | All |
| `ubuntu-latest` | `pytest --tb=short -m "not qt and not packaging" --junitxml=test-results-linux.xml` | core, cli, integration, slow, telemetry, smoke |

`fail-fast: false` ensures both legs report independently. JUnit XML artifacts are uploaded on every run (including failures) for log inspection.

---

## 5. Known Gaps and Recommended Next Steps

| Item | Priority | Notes |
|---|---|---|
| **Qt tests on Linux** | Medium | Add `QT_QPA_PLATFORM=offscreen` env var to Linux test step to run Qt tests cross-platform without xvfb. Validate all Qt tests pass before removing `-m "not qt"` filter. |
| **Packaging tests with Windows skip guard** | Low | Current tests are file-existence checks that pass cross-platform. If packaging tests ever invoke scripts, add `pytest.mark.skipif(sys.platform != 'win32', ...)`. |
| **Slow test PR gating** | Low | Add a fast-feedback step on PRs that runs `-m "not slow"`. Only needed when `test_stability.py` wall time becomes painful. |
| **`build.yml` entry point** | Low | The legacy `build.yml` still references `gui_merger.py`. Update when macOS/Linux packaging lane is promoted. |
| **conftest.py** | Low | If shared fixtures are needed across test files in the future, introduce `tests/conftest.py`. Not required now. |

---

## 6. Commit

All changes committed as: `"CI super batch: test markers, matrix hygiene, and docs"`
