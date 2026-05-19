# CLI UX Audit and Baseline

This document captures the baseline audit of the APMultitool Command-Line Interface (CLI), outlining its current subcommands, help layout, exit code conventions, error reporting behavior, and areas needing improvement.

## 1. Current Command Namespace & Interface Shape

APMultitool exposes a single CLI entrypoint: `cli.py` (which compiles to `apmultitool.exe`).

### Subcommands:
- `email-to-pdf`: Converts `.eml`/`.msg` files to PDF.
- `merge`: Combines PDF and image arrays.
- `docx-to-pdf`: Converts Word files to PDF via win32com or headless LibreOffice.
- `xlsx-to-pdf`: Converts Excel sheets to PDF via win32com or headless LibreOffice.
- `bates`: Applies Bates numbering overlays.

### Existing Argument Inconsistencies:
- **Prefix Naming**: Some subcommands use `--input` / `-i` for a single file, while `merge` uses `--inputs` / `-i` for a list of items.
- **Output Argument**: All commands use `-o` or `--output-dir` for target directory outputs. Some use `--output-name` for file naming overrides.
- **Help Output**: Basic help messages exist but lack explicit argument validation ranges and inline examples.

## 2. Help Command Structure

- Top-level help: `python cli.py --help` shows subparsers list.
- Subcommand help: `python cli.py <subcommand> --help` shows command arguments.
- **Improvement Target**: Standardize help formats to show 2-4 concrete, copy-pasteable execution examples per subcommand.

## 3. Exit Code Conventions

Prior execution flows utilized:
- `0`: Success.
- `1`: Invalid arguments or file-not-found failures.
- `2`: Execution / engine operation failure.
- `3`: Operational cancellation.

### Improvement Target:
- Reserve `2` specifically for usage/argument/validation errors (argparse default).
- Use `1` for operation execution failures (e.g., conversion engine failures).
- Use `3` for cancellation.

## 4. Error Message Style and Output Hygiene

- **Streams**: Standard logs write to `stderr` to avoid contaminating stdout redirects. However, tracebacks are currently suppressed by default unless `--verbose` is set.
- **Improvements**: Validate and separate output streams strictly: informational output to `stdout` (or JSON formats to `stdout` if `--json` is set), and diagnostic errors/warnings to `stderr`.

## 5. Summary of Actions Required in This Batch
1. Normalize command names and options to standard patterns.
2. Standardize argparse exit codes (exit with `2` on validation/arg errors, `1` on engine failure).
3. Introduce `--version` at top-level.
4. Integrate `-q`/--quiet alias matching the `--silent` option.
5. Create a `--dry-run` execution loop for testing pipelines without writing output.
6. Verify stream hygiene.
