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

Last verified on 2026-05-21.

If you only remember one command, use this:

```powershell
python scripts/run_core_tests.py --fast
```

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
python scripts/run_core_tests.py --fast
python scripts/run_core_tests.py
python scripts/run_core_tests.py --subset unit
python scripts/run_core_tests.py --subset integration
python scripts/run_core_tests.py --subset qt -- -q
python scripts/run_core_tests.py --subset core -- --maxfail=1
python scripts/run_core_tests.py --subset all --dry-run
python scripts/run_core_tests.py --list-subsets
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

QoL additions:

- `--fast` runs the common local loop with the `core` subset.
- `--list-subsets` prints the available named subsets without starting pytest.
- If pytest is missing, the wrapper exits early with a direct install-the-deps message instead of a module import traceback.
- Extra pytest arguments must be passed after `--`, which avoids accidental flag parsing mistakes.

Prerequisite: run from a Python environment with `pytest` and the subset's application dependencies installed.

## scripts/audit_logging.py

Purpose: scan production Python layers for direct `print()` calls, global logging configuration, and logger usage. The script is read-only and does not import application modules.

Common usage:

```powershell
python scripts/audit_logging.py
python scripts/audit_logging.py --json
```

The Markdown output is intended for developer review. The JSON output is intended for future automation or support bundle tooling.

## Support Bundle Helper

Purpose: collect the shared local log file and telemetry JSON into an offline support bundle ZIP with path scrubbing applied to the bundle contents.

Entry point:

```powershell
python -c "from core.support import create_support_bundle; print(create_support_bundle())"
```

The helper stays local-only and is intended to work with the privacy rules documented in `docs/ops/logging_discipline.md`.

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

## Development Logging

Central logging now lives in `core/logging_config.py`.

Environment variables:

```powershell
$env:APMULTITOOL_LOG_LEVEL = "DEBUG"
$env:APMULTITOOL_LOG_FILE = "C:\temp\apmultitool.log"
```

CLI overrides:

```powershell
python cli.py --log-level DEBUG merge -i input.pdf -o out
python cli.py --verbose merge -i input.pdf -o out
python cli.py --silent merge -i input.pdf -o out
```

Effect on troubleshooting and support bundles:

- `APMULTITOOL_LOG_LEVEL=DEBUG` increases detail for the pilot logging slice.
- Default logging stays at `INFO`; the Qt bridge now sends per-progress chatter to `DEBUG` so the shared log file is easier to scan.
- `APMULTITOOL_LOG_FILE` redirects the shared local log file to an isolated location.
- `create_support_bundle()` collects the current shared local log file and telemetry JSON when present.

## Logging Review

Scope reviewed: `core/`, `apmultitool_qt/`, `cli.py`, and `email_processing.py`.

Current status:

- Central logging configuration now exists for the pilot slice in `core/logging_config.py`.
- The conversion path, support-bundle helper, Qt core bridge, and Qt security helper now use named `apmultitool.*` loggers.
- Other Qt modules and `email_processing.py` still contain legacy direct output or older logger patterns.

Use `scripts/audit_logging.py` together with `docs/ops/logging_audit_overview.md` and `docs/ops/logging_discipline.md` before broadening the migration beyond the pilot slice.

## Get Unstuck Fast

If something feels broken or confusing, try these first:

1. Run the fastest headless loop:

```powershell
python scripts/run_core_tests.py --fast
```

2. Validate the telemetry file before sharing it:

```powershell
python scripts/validate_telemetry_schema.py
```

3. Generate an offline support bundle:

```powershell
python cli.py support-bundle -o .
```

4. Check the shared local log file location:

```powershell
echo $env:APMULTITOOL_LOG_FILE
```

If `APMULTITOOL_LOG_FILE` is unset, use the default per-user path described in `core/logging_config.py`.

5. Check current CI and packaging status docs:

- `docs/ops/ci_overview.md`
- `docs/ops/ci_known_issues.md`
- `docs/ops/windows_alpha_support_bundle_spec.md`
- `docs/ops/macos_packaging_overview.md`

## Alpha1 Specific Diagnostics

Here are common diagnostic flows tailored for the `v1.0.0-alpha1` release cycle:

### 1. Verification of Tester Build ID

When a tester submits their telemetry JSON snapshot, operators can verify they were running the correct `v1.0.0-alpha1` binary:

```powershell
python scripts/inspect_telemetry.py --file .\docs\feedback\v1.0.0-alpha1\telemetry_tester_smith_j.json | Select-String "Build:"
```

Expected output:

```text
Build: v1.0.0-alpha1
```

### 2. Validating Telemetry Code Paths Locally

Before shipping code edits to master, developers can run focused tests validating the local telemetry schema and About screen widget bindings:

```powershell
python scripts/run_core_tests.py --subset telemetry
python scripts/run_core_tests.py --subset packaging
```
