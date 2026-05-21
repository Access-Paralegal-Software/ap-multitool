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

## scripts/audit_logging.py

Purpose: scan production Python layers for direct `print()` calls, global logging configuration, and logger usage. The script is read-only and does not import application modules.

Common usage:

```powershell
python scripts/audit_logging.py
python scripts/audit_logging.py --json
```

The Markdown output is intended for developer review. The JSON output is intended for future automation or support bundle tooling.

## scripts/validate_telemetry_schema.py

Purpose: validate the local telemetry JSON structure before a developer or tester shares the file for diagnosis.

Common usage:

```powershell
python scripts/validate_telemetry_schema.py
python scripts/validate_telemetry_schema.py --json
python scripts/validate_telemetry_schema.py --file C:\Users\tester\.access_paralegal_telemetry.json
```

Validation checks:

- Required fields, including `build_id`.
- Expected string and integer types.
- Non-negative count values.
- Aggregate outcome counts do not exceed total counts.

The script returns exit code `0` when the schema passes and `1` when validation fails.

CLI hookup decision: no `cli.py` subcommand was added in this batch. The current CLI imports core PDF dependencies before argument dispatch, so a telemetry-only command would still require the full runtime dependency set. Keeping the validator as a standalone script is safer for tester and support machines.

## Logging Review

Scope reviewed: `core/`, `apmultitool_qt/`, `cli.py`, and `email_processing.py`.

Current findings:

- `cli.py` owns the only standard logger setup and uses the `APMultitool` logger for CLI progress, warnings, and failures.
- The core engine and operation modules currently avoid direct logging, which preserves the engine/UI separation and keeps background execution reporting callback-driven.
- The Qt layer currently surfaces most user-visible status through widgets and telemetry rather than Python log files.
- `email_processing.py` still uses `print()` for standalone legacy CLI warnings and progress.
- `apmultitool_qt/security.py` has two guarded `print()` calls for vault load/save failures.

Decision for this tooling lane: no runtime logging cleanup was applied. The obvious inconsistencies are low-risk legacy/standalone diagnostics, and changing them could alter visible behavior or hide tester-facing messages. A future logging pass should introduce named loggers consistently as `APMultitool.<layer>` and keep core operations Qt-unaware.

Follow-up tooling now exists in `scripts/audit_logging.py`; use `docs/ops/logging_audit_overview.md` to interpret the report before making any cleanup changes.

---

## 🔬 Alpha1 Specific Diagnostics

Here are common diagnostic flows tailored for the `v1.0.0-alpha1` release cycle:

### 1. Verification of Tester Build ID
When a tester submits their telemetry JSON snapshot, operators can verify they were running the correct `v1.0.0-alpha1` binary:
```powershell
# Filter output for the build identity field
python scripts/inspect_telemetry.py --file .\docs\feedback\v1.0.0-alpha1\telemetry_tester_smith_j.json | Select-String "Build:"
```
Expected output:
```text
Build: v1.0.0-alpha1
```

### 2. Validating Telemetry Code Paths Locally
Before shipping code edits to master, developers can run focused tests validating the local telemetry schema and About screen widget bindings:
```powershell
# Run the telemetry test suite
python scripts/run_core_tests.py --subset telemetry

# Run the packaging test suite (verifies versioning consistency)
python scripts/run_core_tests.py --subset packaging
```
