r"""Validate the local APMultitool telemetry JSON schema.

This read-only helper validates the aggregate telemetry file written by the Qt
application. It checks required fields, types, and basic count invariants.

Usage:
    python scripts/validate_telemetry_schema.py
    python scripts/validate_telemetry_schema.py --file C:\path\to\telemetry.json
    python scripts/validate_telemetry_schema.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


DEFAULT_TELEMETRY_FILE = Path.home() / ".access_paralegal_telemetry.json"
COUNT_FIELDS = ("total_runs", "success_runs", "failed_runs", "cancelled_runs")
STRING_FIELDS = ("build_id", "last_error", "last_error_time")
OPERATION_COUNT_FIELDS = ("total", "success", "failed", "cancelled")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("Telemetry root must be a JSON object.")
    return data


def is_int_not_bool(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def validate_counts(data: dict[str, Any], errors: list[str]) -> None:
    for field in COUNT_FIELDS:
        value = data.get(field)
        if not is_int_not_bool(value):
            errors.append(f"`{field}` must be an integer.")
        elif value < 0:
            errors.append(f"`{field}` must not be negative.")

    if all(is_int_not_bool(data.get(field)) for field in COUNT_FIELDS):
        total = data["total_runs"]
        outcomes = data["success_runs"] + data["failed_runs"] + data["cancelled_runs"]
        if outcomes > total:
            errors.append("Outcome counts must not exceed `total_runs`.")


def validate_operations(data: dict[str, Any], errors: list[str]) -> None:
    operations = data.get("operations")
    if not isinstance(operations, dict):
        errors.append("`operations` must be an object.")
        return

    for operation, stats in operations.items():
        if not isinstance(operation, str) or not operation:
            errors.append("Operation names must be non-empty strings.")
        if not isinstance(stats, dict):
            errors.append(f"`operations.{operation}` must be an object.")
            continue

        for field in OPERATION_COUNT_FIELDS:
            value = stats.get(field)
            if not is_int_not_bool(value):
                errors.append(f"`operations.{operation}.{field}` must be an integer.")
            elif value < 0:
                errors.append(f"`operations.{operation}.{field}` must not be negative.")

        if all(is_int_not_bool(stats.get(field)) for field in OPERATION_COUNT_FIELDS):
            outcomes = stats["success"] + stats["failed"] + stats["cancelled"]
            if outcomes > stats["total"]:
                errors.append(f"`operations.{operation}` outcome counts must not exceed total.")


def validate_telemetry(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    for field in STRING_FIELDS:
        if field not in data:
            errors.append(f"Missing required field `{field}`.")
        elif not isinstance(data[field], str):
            errors.append(f"`{field}` must be a string.")

    if isinstance(data.get("build_id"), str) and not data["build_id"].strip():
        errors.append("`build_id` must not be empty.")

    for field in COUNT_FIELDS:
        if field not in data:
            errors.append(f"Missing required field `{field}`.")

    if "operations" not in data:
        errors.append("Missing required field `operations`.")

    validate_counts(data, errors)
    validate_operations(data, errors)
    return errors


def build_summary(path: Path, data: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    operations = data.get("operations") if isinstance(data, dict) else {}
    return {
        "path": str(path),
        "valid": not errors,
        "errors": errors,
        "build_id": data.get("build_id") if isinstance(data, dict) else None,
        "total_runs": data.get("total_runs") if isinstance(data, dict) else None,
        "operation_count": len(operations) if isinstance(operations, dict) else 0,
    }


def print_human(summary: dict[str, Any]) -> None:
    print(f"Telemetry schema: {'PASS' if summary['valid'] else 'FAIL'}")
    print(f"File: {summary['path']}")
    if summary.get("build_id") is not None:
        print(f"Build: {summary['build_id']}")
    if summary.get("total_runs") is not None:
        print(f"Total runs: {summary['total_runs']}")
    print(f"Operations tracked: {summary['operation_count']}")

    if summary["errors"]:
        print()
        print("Errors:")
        for error in summary["errors"]:
            print(f"  - {error}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate local APMultitool telemetry schema.")
    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_TELEMETRY_FILE,
        help="Telemetry JSON file to validate. Defaults to ~/.access_paralegal_telemetry.json.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    path = args.file.expanduser()

    if not path.exists():
        summary = {
            "path": str(path),
            "valid": False,
            "errors": [f"Telemetry file not found: {path}"],
            "build_id": None,
            "total_runs": None,
            "operation_count": 0,
        }
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print_human(summary)
        return 1

    try:
        data = load_json(path)
        errors = validate_telemetry(data)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        data = {}
        errors = [str(exc)]

    summary = build_summary(path, data, errors)
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print_human(summary)
    return 0 if summary["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
