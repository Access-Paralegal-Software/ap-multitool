---
id: pm_report_ho_0044_2026_05_21_feedback_support_bundle_lane
title: Project Manager Report - Windows Alpha Feedback & Support Bundle Lane
type: pm-report
status: completed
project: APMultitool
created_at: 2026-05-21
---

# Project Manager Report: Windows Alpha Feedback & Support Bundle Lane

## 1. Executive Summary

This lane successfully implemented and verified a secure, local-only offline support bundle diagnostics package for the APMultitool Windows Alpha (`v1.0.0-alpha1`). This system enables non-technical cohort testers to export critical diagnostics (telemetry stats, environment profiles, and application logs) to aid in troubleshooting, without compromising attorney-client privilege or security credentials.

All 123 unit and integration tests are passing successfully. The core engine remains fully decoupled from the Qt GUI layer.

---

## 2. Completed Scope

### Core Diagnostic Compilation (`core/support.py`)
- **System Profiler:** Gathers environment metadata including OS details, python versions, screen DPI scale factor, MS Office COM presence, and LibreOffice PATH resolution.
- **COM Leak Mitigation:** Added explicit reference uninitialization blocks for Excel/Word COM automation objects to avoid dangling background processes or RPC server unavailable exceptions.
- **Privacy & PII Sanitizer:** Added automatic lookup and replacement of user profiles, paths, and usernames with `<USERPROFILE>` inside the log files, telemetry database copy, and metadata JSON.
- **Archive Packager:** Collects the scrubbed datasets into a standard ZIP archive naming format (`apmultitool_support_bundle_YYYYMMDD_HHMMSS.zip`).

### Central & Rotating File Logging Config
- **Central Settings:** Consolidated shared logging parameters under `core/logging_config.py`.
- **GUI Bootstrap File Logger:** Configured rotating file logging on GUI application launch (`apmultitool_qt/main.py`), routing events to `apmultitool.log` inside the user's Local AppData log folder.
- **Job Event Tracer:** Wired background workers (`apmultitool_qt/core_bridge.py`) to log all job lifecycle states (initiate, progress, complete, cancel, exception/tracebacks) to the shared log file.

### CLI Subcommand
- **CLI Tooling:** Integrated a new subcommand `apmultitool support-bundle` allowing command line diagnostic packaging with a customizable target directory path option (`-o` / `--output-dir`).

### GUI Component Integration
- **Affordance Button:** Placed an `"Export Support Bundle..."` action trigger button within the About/Help card dashboard of `AboutView` (`apmultitool_qt/views/about.py`).
- **Smooth UX Flow:** Configured the button to display a Wait cursor during background COM profiling, show an export completion dialog box, and automatically open the containing folder in Windows Explorer using `QDesktopServices.openUrl()`.

### Technical Briefs and Cohort Handbooks
- **Technical Specification:** Documented `docs/ops/windows_alpha_support_bundle_spec.md` outlining folder structure, json schemas, privacy boundaries, and transmission guidelines.
- **Operator handbook updates:** Integrated step-by-step diagnostic capture instructions into `docs/ops/alpha_operator_brief_v1.0.0-alpha1.md`.
- **Cohort Form updates:** Added support bundle attachment checkboxes into `docs/ops/feedback_intake_v1.0.0.md`.
- **Docs Index:** Registered the new specification in the docs table of contents (`docs/README.md`).

---

## 3. Test & Verification Summary

### Automated Testing
- Developed comprehensive tests in `tests/test_support_bundle.py` verifying:
  - Scrubbing profiles detection.
  - Case-insensitive search-and-replace scrubbing for file paths and user directories.
  - Exclusion of sensitive files like license JSON files or case database vaults.
  - Proper compilation and folder structures inside the zip archive.
- Executed the full suite of **123 tests** with a **100% pass rate** in ~5.3s (`python -m pytest`).

### Manual Integration Validation
- Triggered `python cli.py support-bundle` locally.
- Confirmed a zip archive `apmultitool_support_bundle_20260521_074036.zip` was successfully generated on the Desktop.
- Verified ZIP layout contains exactly `metadata.json`, `telemetry.json`, and `logs/apmultitool.log`.
- Verified that all username paths and details were cleanly redacted and replaced with `<USERPROFILE>` inside the zip contents.

---

## 4. Touched File Index

All changes have been successfully committed to the `master` branch.

```
apmultitool_qt/core_bridge.py
apmultitool_qt/main.py
apmultitool_qt/views/about.py
core/support.py
docs/README.md
docs/ops/alpha_operator_brief_v1.0.0-alpha1.md
docs/ops/ci_overview.md
docs/ops/doc_conversion_fallback_design.md
docs/ops/doc_conversion_test_strategy.md
docs/ops/feedback_intake_v1.0.0.md
docs/ops/windows_alpha_support_bundle_spec.md
pytest.ini
scripts/_gen_fixtures.py
scripts/run_core_tests.py
tests/fixtures/conversion/README.md
tests/fixtures/conversion/basic_table.docx
tests/fixtures/conversion/headings_and_lists.docx
tests/fixtures/conversion/multi_sheet.xlsx
tests/fixtures/conversion/simple_spreadsheet.xlsx
tests/fixtures/conversion/simple_text.docx
tests/test_conversion_backend.py
tests/test_conversion_integration.py
tests/test_support_bundle.py
```
