---
id: pm_report_dev_tooling
title: Project Manager Report - Developer Tooling Diagnostics
type: pm-report
status: complete
project: APMultitool
created_at: 2026-05-21
---

# Project Manager Report: Developer Tooling Diagnostics

## 1. Executive Summary

This lane added local-only developer and operator tooling for diagnostics and test execution convenience. No application runtime behavior was changed, and the core engine/UI boundary remains intact.

The work was completed and committed in `155f00a3` with the message `Add developer tooling scripts for telemetry inspection and tests`.

## 2. Delivered Artifacts

- `scripts/inspect_telemetry.py`: read-only CLI inspector for `~/.access_paralegal_telemetry.json`.
- `scripts/run_core_tests.py`: pytest wrapper with named subsets for `all`, `unit`, `integration`, `core`, `qt`, `cli`, `telemetry`, and `packaging`.
- `docs/ops/dev_tools.md`: operator/developer usage note with YAML frontmatter.
- `handoffs/ho_0032_2026_05_21_dev_tooling.md`: handoff documenting scripts, usage, logging review, and future tooling ideas.

## 3. Validation

- `python -m py_compile scripts\inspect_telemetry.py scripts\run_core_tests.py` passed.
- `python scripts\inspect_telemetry.py --help` passed.
- `python scripts\run_core_tests.py --subset unit --dry-run` produced the expected pytest command.
- `python scripts\run_core_tests.py --subset qt --dry-run` expanded the Qt test glob to concrete test files.
- `scripts/inspect_telemetry.py` successfully read a sample telemetry JSON file in both text and `--json` modes.

Full pytest execution was blocked in the available shell because the active Python environment does not have `pytest` installed (`No module named pytest`). The wrapper invocation path was still verified through dry-run and the observed failure mode.

## 4. Logging Review Outcome

Reviewed diagnostic output in `core/`, `apmultitool_qt/`, `cli.py`, and `email_processing.py`.

No logging cleanup was implemented in this lane. The decision was documented because the visible inconsistencies are low-risk legacy/standalone diagnostics, and changing them could alter tester-facing behavior. A future logging pass should introduce named loggers consistently as `APMultitool.<layer>` while keeping core operations Qt-unaware.

## 5. Remaining Work

- Add a static logging audit script that classifies direct `print()` calls by layer and intent.
- Add optional pytest markers so `scripts/run_core_tests.py` can select by marker instead of file grouping.
- Add a telemetry schema validation helper for support bundles.
