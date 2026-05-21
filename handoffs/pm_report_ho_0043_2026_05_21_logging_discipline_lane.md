---
id: pm_report_ho_0043_2026_05_21_logging_discipline_lane
title: Project Manager Report - Logging Discipline Lane
type: pm-report
status: completed
project: APMultitool
created_at: 2026-05-21
---

# Project Manager Report: Logging Discipline Lane

## 1. Executive Summary

This lane established a narrow logging-discipline pilot for APMultitool. The implementation adds a central logging configuration module, documents naming and privacy rules, pilots named local loggers in the conversion path, and aligns the support-bundle helper with the same local log file.

No remote logging sinks were introduced, and no licensing, vault, encryption, or hardware identity logic was modified.

## 2. Implemented Logging Plan

- Added `docs/ops/logging_discipline.md` to define:
  - the `apmultitool.*` logger naming convention,
  - level usage for `DEBUG`, `INFO`, `WARNING`, and `ERROR`,
  - privacy and content restrictions,
  - support-bundle handling rules.
- Added `core/logging_config.py` as the central logging configuration module and `get_logger(...)` helper.
- Added environment-driven configuration through:
  - `APMULTITOOL_LOG_LEVEL`
  - `APMULTITOOL_LOG_FILE`
- Added a CLI log-level override via `--log-level`.

## 3. Modules Using the New Logging Discipline

- `core/logging_config.py`
- `core/operations/_conversion_backend.py`
- `core/operations/docx_to_pdf.py`
- `core/operations/xlsx_to_pdf.py`
- `core/support.py`
- `cli.py` now routes CLI logging setup through the central configuration module.

## 4. Privacy and Support-Bundle Outcome

- No document bodies, email bodies, vault contents, secrets, or hardware identifiers are logged by the pilot slice.
- Conversion logs use filenames only and avoid full user or client paths through filename redaction.
- No remote logging sinks were introduced.
- The support-bundle helper now collects the shared local log file and local telemetry JSON while preserving the existing content-scrubbing behavior for bundle contents.

## 5. Risks and Remaining Legacy Areas

- The logging discipline is still only a pilot slice. The rest of the codebase still contains legacy direct output and older logger usage.
- Known legacy areas still using direct output include:
  - `apmultitool_qt/security.py`
  - `email_processing.py`
- Some user-facing exception strings outside the new log records may still include full paths. That remains a broader error-message hygiene pass rather than a log-sink issue.

## 6. Validation

- Added focused logging tests in `tests/test_logging_discipline.py`.
- Confirmed the conversion backend can emit log records without leaking simulated client-directory names into the log file.
- Confirmed the support-bundle helper can package logs and telemetry into a local ZIP archive.
- Added compile-time and direct script verification for the touched logging modules and support-bundle flow.
- Full pytest execution was not possible in this shell because `pytest` is not installed.
- Direct `cli.py --help` verification was blocked by the existing import-time `pikepdf` dependency chain in `cli.py`.
