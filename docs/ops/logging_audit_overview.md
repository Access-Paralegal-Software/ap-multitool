---
id: logging_audit_overview
title: Logging Audit Overview
type: ops-manual
status: active
project: APMultitool
created_at: 2026-05-21
---

# Logging Audit Overview

`scripts/audit_logging.py` provides a read-only scan of diagnostic output patterns in the APMultitool codebase. It is intended for developer review before any future logging cleanup pass.

## Scope

The audit scans:

- `core/`
- `apmultitool_qt/`
- `cli.py`
- `email_processing.py`

It reports:

- `print()` calls.
- `logging.basicConfig(...)` calls.
- `logging.getLogger(...)` setup.
- Calls to common logger methods such as `debug`, `info`, `warning`, `error`, `exception`, and `critical`.

## Usage

Human-readable Markdown:

```powershell
python scripts/audit_logging.py
```

Machine-readable JSON:

```powershell
python scripts/audit_logging.py --json
```

## Interpreting Results

Findings are classified by layer:

| Layer | Meaning |
| --- | --- |
| `core` | Core engine and operations. This layer must remain Qt-unaware. |
| `qt` | PySide6 application shell, views, telemetry, and security support. |
| `cli` | Headless CLI entry point. |
| `legacy_email` | Standalone legacy email processing module. |

Severity is a cleanup priority, not a test failure:

| Severity | Meaning |
| --- | --- |
| `high` | Logging pattern likely needs review before broadening use, especially direct output from core or global logging configuration. |
| `medium` | User-visible or operational diagnostics that may be valid but should be made consistent. |
| `low` | Expected CLI or legacy standalone diagnostics. |
| `info` | Logger setup or normal logger calls. |

## Current Policy

The audit script does not modify files and should not be used as a hard quality gate yet. Before enforcing it, the project should define the desired logger naming policy, expected CLI stdout/stderr behavior, and any exceptions for standalone legacy tools.
