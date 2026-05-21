"""Run focused APMultitool pytest subsets.

This is a convenience wrapper around `python -m pytest`. It keeps test
selection discoverable for developers without changing pytest behavior.

Examples:
    python scripts/run_core_tests.py
    python scripts/run_core_tests.py --subset unit
    python scripts/run_core_tests.py --subset qt -- -q
    python scripts/run_core_tests.py --subset integration -- --maxfail=1
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

SUBSETS = {
    "all": ["tests"],
    "unit": [
        "tests/test_core_folder_tree.py",
        "tests/test_docx_xlsx_bates.py",
        "tests/test_email_to_pdf.py",
        "tests/test_stability.py",
        "tests/test_versioning.py",
    ],
    "integration": [
        "tests/test_cli_ux.py",
        "tests/test_core_folder_tree.py",
        "tests/test_email_to_pdf.py",
        "tests/test_qt_infrastructure.py",
    ],
    "core": [
        "tests/test_core_folder_tree.py",
        "tests/test_docx_xlsx_bates.py",
        "tests/test_email_to_pdf.py",
        "tests/test_stability.py",
    ],
    "qt": ["tests/test_qt_*.py"],
    "cli": ["tests/test_cli_ux.py"],
    "telemetry": ["tests/test_telemetry.py"],
    "packaging": ["tests/test_packaging.py", "tests/test_versioning.py"],
}


def expand_targets(targets: list[str]) -> list[str]:
    """Expand simple test globs before passing paths to pytest."""
    expanded: list[str] = []
    for target in targets:
        if any(char in target for char in "*?[]"):
            matches = sorted(str(path.relative_to(REPO_ROOT)) for path in REPO_ROOT.glob(target))
            expanded.extend(matches or [target])
        else:
            expanded.append(target)
    return expanded


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run APMultitool pytest subsets.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--subset",
        choices=sorted(SUBSETS),
        default="all",
        help="Named test subset to run.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the pytest command without running it.",
    )
    parser.add_argument(
        "pytest_args",
        nargs=argparse.REMAINDER,
        help="Additional pytest arguments. Prefix with -- before pytest flags.",
    )
    return parser.parse_args(argv)


def clean_pytest_args(args: list[str]) -> list[str]:
    if args and args[0] == "--":
        return args[1:]
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    selected = expand_targets(SUBSETS[args.subset])
    pytest_args = clean_pytest_args(args.pytest_args)
    command = [sys.executable, "-m", "pytest", *selected, *pytest_args]

    print("Running:", " ".join(command), flush=True)
    if args.dry_run:
        return 0

    completed = subprocess.run(command, cwd=REPO_ROOT)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
