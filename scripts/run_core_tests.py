#!/usr/bin/env python
"""scripts/run_core_tests.py — APMultitool local test runner.

Named subsets (--subset) map to pytest marker expressions and match the names
used in the CI matrix. Use --marker for ad-hoc expressions.

Usage examples:
  python scripts/run_core_tests.py --fast                  # fast default loop
  python scripts/run_core_tests.py                          # all tests
  python scripts/run_core_tests.py --subset core            # core engine only
  python scripts/run_core_tests.py --subset qt              # Qt widget tests
  python scripts/run_core_tests.py --subset cli             # CLI tests
  python scripts/run_core_tests.py --subset unit            # alias for core
  python scripts/run_core_tests.py --marker slow            # slow tests
  python scripts/run_core_tests.py --marker "core and not slow"
  python scripts/run_core_tests.py --marker "not qt and not packaging"
  python scripts/run_core_tests.py -v --subset smoke        # verbose smoke
  python scripts/run_core_tests.py --subset qt --dry-run   # print, don't run
"""
from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

# Named subsets used by the CI matrix. Each maps to a pytest marker expression.
# Keep in sync with the matrix.subset list in .github/workflows/tests.yml.
SUBSET_MARKERS: dict[str, str | None] = {
    "all":         None,
    "unit":        "core",          # unit-style core engine tests
    "integration": "integration",
    "core":        "core",
    "qt":          "qt",
    "cli":         "cli",
    "telemetry":   "telemetry",
    "packaging":   "packaging",
    "smoke":       "smoke",
    "slow":        "slow",
    "conversion":  "conversion",    # document conversion subsystem (docx/xlsx to PDF)
    "libreoffice": "libreoffice",   # requires LibreOffice installed locally; not in CI matrix
}

FAST_DEFAULT_SUBSET = "core"


def _build_subset_help() -> str:
    return (
        "Named subset (mirrors CI matrix names). "
        f"Use --fast for the common local loop ({FAST_DEFAULT_SUBSET}). "
        "Mutually exclusive with --marker."
    )


def _ensure_pytest_available() -> None:
    if importlib.util.find_spec("pytest") is None:
        raise RuntimeError(
            "pytest is not installed in this environment. "
            "Install test dependencies first, then rerun this helper."
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="APMultitool local test runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    selection = parser.add_mutually_exclusive_group()
    selection.add_argument(
        "--subset", "-s",
        choices=sorted(SUBSET_MARKERS),
        default="all",
        help=_build_subset_help(),
    )
    selection.add_argument(
        "--marker", "-m",
        metavar="EXPR",
        help=(
            "Pytest marker expression. Valid markers: core, qt, cli, integration, "
            "slow, telemetry, packaging, smoke, conversion, libreoffice. "
            "Combine with 'and'/'or'/'not'. Mutually exclusive with --subset."
        ),
    )
    selection.add_argument(
        "--fast",
        action="store_true",
        help=f"Run the common fast local loop ({FAST_DEFAULT_SUBSET}).",
    )

    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable verbose pytest output.")
    parser.add_argument("--tb", metavar="STYLE", default="short",
                        choices=["short", "long", "line", "no"],
                        help="Traceback style (default: short).")
    parser.add_argument("--junit", metavar="PATH",
                        help="Write JUnit XML report to PATH.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the command without running it.")
    parser.add_argument("--list-subsets", action="store_true",
                        help="Print available named subsets and exit.")
    parser.add_argument("pytest_args", nargs=argparse.REMAINDER,
                        help="Extra pytest args (prefix with --).")

    args = parser.parse_args(argv or sys.argv[1:])

    if args.list_subsets:
        for name in sorted(SUBSET_MARKERS):
            marker = SUBSET_MARKERS[name] or "(all tests)"
            print(f"{name}: {marker}")
        return 0

    if args.fast:
        args.subset = FAST_DEFAULT_SUBSET

    if args.pytest_args and args.pytest_args[0] != "--":
        parser.error("extra pytest arguments must be prefixed with `--`")

    cmd = [sys.executable, "-m", "pytest"]

    marker_expr = args.marker if args.marker else SUBSET_MARKERS.get(args.subset)
    if marker_expr:
        cmd += ["-m", marker_expr]

    if args.verbose:
        cmd.append("-v")
    cmd += ["--tb", args.tb]
    if args.junit:
        cmd += [f"--junitxml={args.junit}"]

    extra = args.pytest_args
    if extra and extra[0] == "--":
        extra = extra[1:]
    cmd.extend(extra)

    print(f"[run_core_tests] {' '.join(cmd)}\n", flush=True)
    if args.dry_run:
        return 0

    try:
        _ensure_pytest_available()
    except RuntimeError as exc:
        print(f"[run_core_tests] {exc}", file=sys.stderr)
        return 1

    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


if __name__ == "__main__":
    raise SystemExit(main())
