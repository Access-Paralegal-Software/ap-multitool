# tests/test_cli_ux.py — CLI User Experience and streams tests
import sys
import subprocess
from pathlib import Path
import pytest


def run_cli(args: list[str]) -> subprocess.CompletedProcess:
    """Helper to run the CLI as a subprocess."""
    cli_path = Path(__file__).parent.parent / "cli.py"
    cmd = [sys.executable, str(cli_path)] + args
    return subprocess.run(cmd, capture_output=True, text=True)


# =============================================================================
# Task 7 — CLI UX Tests
# =============================================================================

def test_cli_version():
    """Verify that --version outputs the correct version and exits with 0."""
    res = run_cli(["--version"])
    assert res.returncode == 0
    assert "APMultitool CLI" in res.stdout or "APMultitool CLI" in res.stderr
    # argparse prints version to stdout in Python 3.4+, but could be stderr in older versions


def test_cli_top_level_help():
    """Verify that top-level help lists expected subcommands."""
    res = run_cli(["--help"])
    assert res.returncode == 0
    assert "email-to-pdf" in res.stdout
    assert "merge" in res.stdout
    assert "bates" in res.stdout


def test_cli_subcommand_help():
    """Verify subcommand help contains required arguments and descriptions."""
    for cmd in ["email-to-pdf", "merge", "docx-to-pdf", "xlsx-to-pdf", "bates"]:
        res = run_cli([cmd, "--help"])
        assert res.returncode == 0
        assert "--input" in res.stdout or "--inputs" in res.stdout


def test_cli_invalid_command():
    """Verify that invalid commands exit with code 2 and write errors to stderr."""
    res = run_cli(["invalid-cmd-name"])
    assert res.returncode == 2
    assert "invalid choice" in res.stderr or "error" in res.stderr


def test_cli_missing_required_arguments():
    """Verify that missing required arguments exits with code 2."""
    res = run_cli(["merge"])
    assert res.returncode == 2
    assert "required" in res.stderr or "the following arguments are required" in res.stderr


def test_cli_dry_run_merge():
    """Verify dry-run mode for merge displays config summary and exits with 0."""
    # Create temp files to satisfy input existence checks
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f1, \
         tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f2:
        p1 = Path(f1.name)
        p2 = Path(f2.name)

    try:
        res = run_cli(["merge", "-i", str(p1), str(p2), "-o", ".", "--dry-run"])
        assert res.returncode == 0
        assert "DRY RUN SUMMARY" in res.stdout
        assert "Operation: Merge" in res.stdout
        assert str(p1) in res.stdout
        assert str(p2) in res.stdout
    finally:
        if p1.exists():
            p1.unlink()
        if p2.exists():
            p2.unlink()


def test_cli_dry_run_bates():
    """Verify dry-run mode for bates displays parameter summary and exits with 0."""
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        p = Path(f.name)

    try:
        res = run_cli(["bates", "-i", str(p), "-o", ".", "--prefix", "DRYCONF", "--start-number", "500", "--dry-run"])
        assert res.returncode == 0
        assert "DRY RUN SUMMARY" in res.stdout
        assert "Operation: Bates Stamp" in res.stdout
        assert "Prefix: DRYCONF" in res.stdout
        assert "Start Number: 500" in res.stdout
    finally:
        if p.exists():
            p.unlink()


def test_cli_json_error_output():
    """Verify that validation failures under --json flag format output as JSON."""
    res = run_cli(["--json", "bates", "-i", "missing_file_path_12345.pdf"])
    assert res.returncode == 2
    import json
    data = json.loads(res.stdout)
    assert data["status"] == "failed"
    assert "missing_file_path" in data["error"]
