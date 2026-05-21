---
id: logging_discipline
title: Logging Discipline
type: ops-manual
status: active
project: APMultitool
created_at: 2026-05-21
---

# Logging Discipline

This document defines the narrow logging-discipline pilot for APMultitool. The pilot covers the conversion path and the local support-bundle helper. Logs remain local, no remote sink is introduced, and the goal is better diagnostics without adding noisy default output for alpha testers.

## Logger Naming Convention

Use the shared root logger name `apmultitool`.

Child logger examples:

- `apmultitool.core.conversion.backend`
- `apmultitool.core.conversion.docx`
- `apmultitool.core.conversion.xlsx`
- `apmultitool.support.bundle`
- `apmultitool.cli`
- `apmultitool.ui.main`

Modules should obtain loggers through `core/logging_config.py` rather than configuring `logging` directly.

## Log Levels

| Level | Use |
| --- | --- |
| `DEBUG` | Deep developer diagnostics, backend selection, feature probes, and similar opt-in detail. |
| `INFO` | High-level lifecycle events such as conversion start, conversion success, and support-bundle creation. |
| `WARNING` | Recoverable issues such as a primary backend failing and a fallback being used. |
| `ERROR` | Failures that affect user workflows, such as missing converters or failed subprocess execution. |

Default level is `INFO`. Development can opt into more detail with `APMULTITOOL_LOG_LEVEL=DEBUG` or a CLI log-level override where available.

## Content Rules

Logs must not include:

- Document or email bodies.
- Secrets, vault contents, or hardware identifiers.
- Direct client names or case numbers.
- Full filesystem paths that may expose usernames or matter names.

Logs may include:

- Filenames such as `report.docx` or `matter-index.xlsx`.
- Backend names such as `win32com` and `libreoffice`.
- High-level counts, timing, and lifecycle state.

When a path is relevant, only the filename portion should be logged. If a broader path must appear in bundle metadata, it must be scrubbed before writing.

## Support Bundles

Support bundles may include local logs, but the logs themselves must already respect the above privacy rules.

Current support-bundle expectations:

- Collect the shared local log file.
- Collect the local telemetry JSON when present.
- Include a small metadata manifest.
- Never upload the bundle automatically.

## Pilot Scope

Current pilot modules:

- `core/logging_config.py`
- `core/operations/_conversion_backend.py`
- `core/operations/docx_to_pdf.py`
- `core/operations/xlsx_to_pdf.py`
- `core/support.py`

The rest of the codebase still contains legacy direct output and older logger usage. Those areas should be migrated only after this pilot proves the naming, level, and content rules are stable.
