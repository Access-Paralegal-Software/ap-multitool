---
id: dev_tools
title: Developer Tooling Scripts
type: ops-manual
status: active
project: APMultitool
created_at: 2026-05-21
---

# Developer Tooling Scripts

This note documents small local-only helper tools for diagnostics and maintenance. These scripts do not change application behavior and should be safe to run from a developer checkout or tester workstation when instructed.

## scripts/inspect_telemetry.py

Purpose: read the local Qt telemetry aggregate file and print job counts, outcome counts, per-operation counts, and recent error details.

Default input:

```powershell
~/.access_paralegal_telemetry.json
```

Common usage:

```powershell
python scripts/inspect_telemetry.py
python scripts/inspect_telemetry.py --errors 10
python scripts/inspect_telemetry.py --json
python scripts/inspect_telemetry.py --file C:\Users\tester\.access_paralegal_telemetry.json
```

Safety notes:

- The script is read-only.
- It does not import the Qt application or initialize telemetry state.
- It does not contact external services.
- It exits with code `1` when the telemetry file is missing or unreadable.

## scripts/run_core_tests.py

Purpose: wrap `python -m pytest` with named subsets that match the current test layout.

Common usage:

```powershell
python scripts/run_core_tests.py
python scripts/run_core_tests.py --subset unit
python scripts/run_core_tests.py --subset integration
python scripts/run_core_tests.py --subset qt -- -q
python scripts/run_core_tests.py --subset core -- --maxfail=1
python scripts/run_core_tests.py --subset all --dry-run
```

Available subsets:

| Subset | Scope |
| --- | --- |
| `all` | Entire `tests/` tree. |
| `unit` | Core operation and stability tests that avoid Qt-specific files. |
| `integration` | CLI, engine integration, and Qt infrastructure smoke coverage. |
| `core` | Core document operation tests. |
| `qt` | `tests/test_qt_*.py` files. |
| `cli` | CLI UX tests. |
| `telemetry` | Telemetry manager and About view integration tests. |
| `packaging` | Packaging and version metadata tests. |

The wrapper forwards any arguments after `--` directly to pytest.

Prerequisite: run from a Python environment with `pytest` and the subset's application dependencies installed.

## Logging Review

Scope reviewed: `core/`, `apmultitool_qt/`, `cli.py`, and `email_processing.py`.

Current findings:

- `cli.py` owns the only standard logger setup and uses the `APMultitool` logger for CLI progress, warnings, and failures.
- The core engine and operation modules currently avoid direct logging, which preserves the engine/UI separation and keeps background execution reporting callback-driven.
- The Qt layer currently surfaces most user-visible status through widgets and telemetry rather than Python log files.
- `email_processing.py` still uses `print()` for standalone legacy CLI warnings and progress.
- `apmultitool_qt/security.py` has two guarded `print()` calls for vault load/save failures.

Decision for this tooling lane: no runtime logging cleanup was applied. The obvious inconsistencies are low-risk legacy/standalone diagnostics, and changing them could alter visible behavior or hide tester-facing messages. A future logging pass should introduce named loggers consistently as `APMultitool.<layer>` and keep core operations Qt-unaware.

Future tooling idea: add a static logging audit script that reports direct `print()` calls in production modules and classifies them as CLI output, user-facing diagnostics, or cleanup candidates.
