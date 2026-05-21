r"""Inspect local APMultitool telemetry aggregates.

Reads the local telemetry file written by the Qt application and prints a
human-readable summary. The script is intentionally read-only and does not
contact external services, so it is safe to run on tester machines.

Usage:
    python scripts/inspect_telemetry.py
    python scripts/inspect_telemetry.py --file C:\path\to\telemetry.json
    python scripts/inspect_telemetry.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


DEFAULT_TELEMETRY_FILE = Path.home() / ".access_paralegal_telemetry.json"


def _as_int(value: Any) -> int:
    """Return telemetry count values as integers without failing on bad data."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def load_telemetry(path: Path) -> dict[str, Any]:
    """Load telemetry JSON from disk."""
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("Telemetry root must be a JSON object.")
    return data


def collect_errors(data: dict[str, Any], limit: int) -> list[dict[str, str]]:
    """Collect recent errors from current and future-compatible schemas."""
    errors: list[dict[str, str]] = []

    raw_history = data.get("error_history") or data.get("errors") or []
    if isinstance(raw_history, list):
        for item in raw_history:
            if not isinstance(item, dict):
                continue
            message = str(item.get("error") or item.get("message") or "").strip()
            timestamp = str(item.get("timestamp") or item.get("time") or "").strip()
            if message:
                errors.append({"timestamp": timestamp or "(unknown time)", "message": message})

    last_error = str(data.get("last_error") or "").strip()
    if last_error:
        last_error_time = str(data.get("last_error_time") or "").strip()
        if not errors or errors[-1]["message"] != last_error:
            errors.append({"timestamp": last_error_time or "(unknown time)", "message": last_error})

    return errors[-limit:]


def summarize(data: dict[str, Any], error_limit: int) -> dict[str, Any]:
    """Build a stable summary object for display or JSON output."""
    operations = data.get("operations")
    if not isinstance(operations, dict):
        operations = {}

    return {
        "build_id": data.get("build_id", ""),
        "totals": {
            "total": _as_int(data.get("total_runs")),
            "success": _as_int(data.get("success_runs")),
            "failed": _as_int(data.get("failed_runs")),
            "cancelled": _as_int(data.get("cancelled_runs")),
        },
        "operations": {
            str(name): {
                "total": _as_int(stats.get("total")) if isinstance(stats, dict) else 0,
                "success": _as_int(stats.get("success")) if isinstance(stats, dict) else 0,
                "failed": _as_int(stats.get("failed")) if isinstance(stats, dict) else 0,
                "cancelled": _as_int(stats.get("cancelled")) if isinstance(stats, dict) else 0,
            }
            for name, stats in sorted(operations.items())
        },
        "recent_errors": collect_errors(data, error_limit),
    }


def print_summary(summary: dict[str, Any], path: Path) -> None:
    """Print the telemetry summary for humans."""
    totals = summary["totals"]
    print(f"Telemetry file: {path}")
    if summary["build_id"]:
        print(f"Build: {summary['build_id']}")
    print()
    print("Job counts")
    print(f"  Total:     {totals['total']}")
    print(f"  Success:   {totals['success']}")
    print(f"  Failed:    {totals['failed']}")
    print(f"  Cancelled: {totals['cancelled']}")

    operations = summary["operations"]
    if operations:
        print()
        print("By operation")
        for name, stats in operations.items():
            print(
                f"  {name}: total={stats['total']} "
                f"success={stats['success']} failed={stats['failed']} "
                f"cancelled={stats['cancelled']}"
            )

    print()
    print("Recent errors")
    if not summary["recent_errors"]:
        print("  None recorded.")
    for error in summary["recent_errors"]:
        print(f"  [{error['timestamp']}] {error['message']}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect local APMultitool telemetry.")
    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_TELEMETRY_FILE,
        help="Telemetry JSON file to inspect. Defaults to ~/.access_paralegal_telemetry.json.",
    )
    parser.add_argument(
        "--errors",
        type=int,
        default=5,
        help="Maximum number of recent errors to display.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the summary as JSON for scripts.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    path = args.file.expanduser()

    if args.errors < 1:
        print("--errors must be 1 or greater.", file=sys.stderr)
        return 2

    if not path.exists():
        print(f"Telemetry file not found: {path}", file=sys.stderr)
        return 1

    try:
        data = load_telemetry(path)
        summary = summarize(data, args.errors)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Unable to read telemetry file: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print_summary(summary, path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
