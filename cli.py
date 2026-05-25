"""cli.py — APMultitool command-line interface.

Headless execution of core document operations via DocEngine.
All output intended for downstream consumption goes to stdout; logs go to stderr.
"""

import argparse
import functools
import json
import sys
from enum import IntEnum
from pathlib import Path

from core import __version__ as CORE_VERSION, __channel__ as CORE_CHANNEL
from core.engine import DocEngine
from core.job import (
    Job, InputSpec, OutputSpec, JobStatus,
    EmailToPdfParams, MergeParams, DocxToPdfParams, XlsxToPdfParams, BatesParams,
)
from core.logging_config import configure_cli_logging

logger = None
CLI_VERSION = f"v{CORE_VERSION}{CORE_CHANNEL}"


class ExitCode(IntEnum):
    COMPLETE = 0
    FAILED = 1
    INVALID = 2   # bad arguments / missing input
    CANCELLED = 3


# ---------------------------------------------------------------------------
# Logging + progress
# ---------------------------------------------------------------------------

def configure_logging(args):
    global logger
    logger = configure_cli_logging(args)


def get_progress_cb(args):
    if getattr(args, "silent", False) or getattr(args, "quiet", False) or getattr(args, "json", False):
        return lambda msg, val: None

    def on_progress(msg, val):
        logger.info(f"Progress: {int(val * 100)}% - {msg}")
    return on_progress


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _require_input(args) -> InputSpec:
    """Validate --input exists and return an InputSpec. Exits INVALID on failure."""
    path = Path(args.input)
    if not path.exists():
        logger.error(f"Input file not found: {path}")
        if getattr(args, "json", False):
            print(json.dumps({"status": "failed", "error": f"Input file not found: {path}"}))
        sys.exit(ExitCode.INVALID)
    return InputSpec.from_path(path)


def _ensure_output_dir(args) -> Path:
    """Create and return the --output-dir path."""
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    return out


def _run(job: Job, args) -> None:
    """Submit *job* to DocEngine and delegate result handling."""
    logger.debug(f"Submitting Job {job.job_id} ({job.operation}) to DocEngine …")
    engine = DocEngine(write_audit=True)
    res = engine.submit(job, on_progress=get_progress_cb(args))
    handle_job_result(res, args)


def _print_dry_run(summary: dict, args) -> None:
    """Print a dry-run summary as JSON or human-readable text, then exit."""
    if getattr(args, "json", False):
        print(json.dumps(summary, indent=2))
    else:
        print("=== DRY RUN SUMMARY ===")
        for key, value in summary.items():
            if key == "dry_run":
                continue
            if isinstance(value, list):
                print(f"{key} ({len(value)}):")
                for item in value:
                    print(f"  - {item}")
            else:
                print(f"{key}: {value}")
        print("=======================")
    sys.exit(ExitCode.COMPLETE)


# ---------------------------------------------------------------------------
# Result handling + error decorator
# ---------------------------------------------------------------------------

def handle_job_result(res_job, args) -> None:
    is_json = getattr(args, "json", False)

    if res_job.status == JobStatus.COMPLETE:
        if is_json:
            print(json.dumps({
                "status": "success",
                "job_id": res_job.job_id,
                "operation": res_job.operation,
                "outputs": [str(p) for p in res_job.result.outputs],
                "page_count": res_job.result.page_count_out,
                "error": None,
            }, indent=2))
        else:
            logger.info("Job completed successfully!")
            logger.info(f"Output: {res_job.result.outputs[0]}")
            logger.info(f"Pages: {res_job.result.page_count_out}")
        sys.exit(ExitCode.COMPLETE)

    if res_job.status == JobStatus.CANCELLED:
        if is_json:
            print(json.dumps({
                "status": "cancelled",
                "job_id": res_job.job_id,
                "operation": res_job.operation,
                "outputs": [],
                "page_count": 0,
                "error": "Operation was cancelled by user.",
            }, indent=2))
        else:
            logger.warning("Job was cancelled.")
        sys.exit(ExitCode.CANCELLED)

    error_msg = res_job.result.error or "Unknown engine error"
    if is_json:
        print(json.dumps({
            "status": "failed",
            "job_id": res_job.job_id,
            "operation": res_job.operation,
            "outputs": [],
            "page_count": 0,
            "error": error_msg,
        }, indent=2))
    else:
        logger.error(f"Job failed: {error_msg}")
    sys.exit(ExitCode.FAILED)


def trap_execution(func):
    """Decorator: catch unhandled exceptions and emit structured output."""
    @functools.wraps(func)
    def wrapper(args, *extra, **kwargs):
        try:
            return func(args, *extra, **kwargs)
        except Exception as exc:
            if getattr(args, "verbose", False):
                import traceback
                traceback.print_exc()
            else:
                logger.error(f"Execution error: {exc}")
            if getattr(args, "json", False):
                print(json.dumps({"status": "failed", "error": str(exc)}))
            sys.exit(ExitCode.FAILED)
    return wrapper


# ---------------------------------------------------------------------------
# Operation handlers
# ---------------------------------------------------------------------------

@trap_execution
def handle_email_to_pdf(args):
    job_input = _require_input(args)
    job = Job(
        operation="email_to_pdf",
        inputs=[job_input],
        params=EmailToPdfParams(
            grayscale=args.grayscale,
            include_attachments=not args.no_attachments,
            output_name=args.output_name,
        ),
        output=OutputSpec(directory=_ensure_output_dir(args)),
    )
    _run(job, args)


@trap_execution
def handle_docx_to_pdf(args):
    job_input = _require_input(args)
    job = Job(
        operation="docx_to_pdf",
        inputs=[job_input],
        params=DocxToPdfParams(output_name=args.output_name),
        output=OutputSpec(directory=_ensure_output_dir(args)),
    )
    _run(job, args)


@trap_execution
def handle_xlsx_to_pdf(args):
    job_input = _require_input(args)
    job = Job(
        operation="xlsx_to_pdf",
        inputs=[job_input],
        params=XlsxToPdfParams(output_name=args.output_name),
        output=OutputSpec(directory=_ensure_output_dir(args)),
    )
    _run(job, args)


@trap_execution
def handle_merge(args):
    inputs = []
    for raw in args.inputs:
        p = Path(raw)
        if p.exists():
            inputs.append(InputSpec.from_path(p))
        else:
            logger.warning(f"Input path not found, skipping: {raw}")

    if not inputs:
        logger.error("No valid inputs provided for merge.")
        if getattr(args, "json", False):
            print(json.dumps({"status": "failed", "error": "No valid inputs provided for merge."}))
        sys.exit(ExitCode.INVALID)

    out_dir = _ensure_output_dir(args)

    if getattr(args, "dry_run", False):
        _print_dry_run({
            "dry_run": True,
            "operation": "merge",
            "inputs_resolved": [str(i.path) for i in inputs],
            "output_directory": str(out_dir),
            "output_name": args.output_name or "merged.pdf",
            "grayscale": args.grayscale,
        }, args)

    job = Job(
        operation="merge",
        inputs=inputs,
        params=MergeParams(grayscale=args.grayscale, output_name=args.output_name),
        output=OutputSpec(directory=out_dir),
    )
    _run(job, args)


@trap_execution
def handle_bates(args):
    job_input = _require_input(args)
    out_dir = _ensure_output_dir(args)

    if getattr(args, "dry_run", False):
        _print_dry_run({
            "dry_run": True,
            "operation": "bates_stamp",
            "input_resolved": str(job_input.path),
            "output_directory": str(out_dir),
            "output_name": args.output_name or f"{args.prefix or 'BATES'}_stamped.pdf",
            "prefix": args.prefix or "",
            "sep": args.sep,
            "start_number": args.start_number,
            "padding": args.padding,
            "position": args.position,
            "font_name": args.font_name,
            "font_size": args.font_size,
            "shrink_conflict": not args.no_shrink,
        }, args)

    job = Job(
        operation="bates_stamp",
        inputs=[job_input],
        params=BatesParams(
            prefix=args.prefix or "",
            start_number=args.start_number,
            padding=args.padding,
            position=args.position,
            font_size=args.font_size,
            shrink_conflict=not args.no_shrink,
            sep=args.sep,
            font_name=args.font_name,
            naming="Prefix_Range" if args.output_name is None else "Prefix_StartOnly",
            output_name=args.output_name,
        ),
        output=OutputSpec(directory=out_dir, overwrite=True),
    )
    _run(job, args)


def handle_support_bundle(args):
    try:
        from core.support import create_support_bundle
        output_dir = Path(args.output_dir) if args.output_dir else None
        logger.info("Generating offline support bundle …")
        zip_path = create_support_bundle(target_dir=output_dir)
        print(json.dumps({"status": "success", "support_bundle_path": str(zip_path.resolve())}, indent=2))
        logger.info(f"Support bundle written to: {zip_path}")
        sys.exit(ExitCode.COMPLETE)
    except Exception as exc:
        logger.error(f"Failed to generate support bundle: {exc}")
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
        sys.exit(ExitCode.FAILED)


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=f"APMultitool Command-Line Interface (Core {CLI_VERSION})",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  apmultitool merge -i folder/ -o out/ --output-name exhibit_pack.pdf
  apmultitool --json --silent email-to-pdf -i mail.eml -o out/
  apmultitool bates -i document.pdf --prefix CONF --start-number 1000 --padding 6
""",
    )
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable debug logging and show full error tracebacks")
    parser.add_argument("--silent", action="store_true",
                        help="Suppress informational output (errors still print)")
    parser.add_argument("-q", "--quiet", action="store_true", help="Alias for --silent")
    parser.add_argument("--json", action="store_true",
                        help="Emit structured JSON to stdout on completion")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        help="Override the log level for this invocation")
    parser.add_argument("--version", action="version", version=f"APMultitool CLI {CLI_VERSION}")

    sub = parser.add_subparsers(dest="operation", required=True)

    # email-to-pdf
    p = sub.add_parser("email-to-pdf", help="Convert .eml/.msg files to PDF")
    p.add_argument("-i", "--input", required=True, help="Source email file")
    p.add_argument("-o", "--output-dir", default=".", help="Output directory (default: .)")
    p.add_argument("--output-name", help="Override output filename")
    p.add_argument("--no-attachments", action="store_true", help="Skip attachment conversion")
    p.add_argument("--grayscale", action="store_true", help="PACER-compliant grayscale output")

    # merge
    p = sub.add_parser("merge", help="Merge PDFs, images, and documents into one PDF")
    p.add_argument("-i", "--inputs", nargs="+", required=True, help="Files or folders to merge")
    p.add_argument("-o", "--output-dir", default=".", help="Output directory (default: .)")
    p.add_argument("--output-name", help="Override output filename")
    p.add_argument("--grayscale", action="store_true", help="Flatten all pages to grayscale")
    p.add_argument("--dry-run", action="store_true",
                   help="Print merge plan without writing output")

    # docx-to-pdf
    p = sub.add_parser("docx-to-pdf", help="Convert .docx/.doc to PDF")
    p.add_argument("-i", "--input", required=True, help="Source Word document")
    p.add_argument("-o", "--output-dir", default=".", help="Output directory (default: .)")
    p.add_argument("--output-name", help="Override output filename")

    # xlsx-to-pdf
    p = sub.add_parser("xlsx-to-pdf", help="Convert .xlsx/.xls/.csv to PDF")
    p.add_argument("-i", "--input", required=True, help="Source spreadsheet")
    p.add_argument("-o", "--output-dir", default=".", help="Output directory (default: .)")
    p.add_argument("--output-name", help="Override output filename")

    # bates
    p = sub.add_parser("bates", help="Apply Bates serial numbering to a PDF")
    p.add_argument("-i", "--input", required=True, help="Source PDF to stamp")
    p.add_argument("-o", "--output-dir", default=".", help="Output directory (default: .)")
    p.add_argument("--output-name", help="Override output filename")
    p.add_argument("--prefix", default="", help="Alpha prefix (e.g. 'PROD')")
    p.add_argument("--sep", default="-", help="Separator between prefix and serial (default: '-')")
    p.add_argument("--start-number", type=int, default=1, help="Starting serial (default: 1)")
    p.add_argument("--padding", type=int, default=7, help="Zero-padding width (default: 7)")
    p.add_argument("--position", default="Bottom Right",
                   choices=["Bottom Right", "Bottom Center", "Top Center",
                            "Top Right", "Top Left", "Bottom Left"],
                   help="Stamp placement zone (default: 'Bottom Right')")
    p.add_argument("--font-name", default="Helvetica", help="Font face (default: 'Helvetica')")
    p.add_argument("--font-size", type=int, default=10, help="Font size in points (default: 10)")
    p.add_argument("--no-shrink", action="store_true",
                   help="Disable content shrinking for collision avoidance")
    p.add_argument("--dry-run", action="store_true",
                   help="Print Bates layout plan without writing output")

    # support-bundle
    p = sub.add_parser("support-bundle", help="Generate offline diagnostic support bundle")
    p.add_argument("-o", "--output-dir", default=None,
                   help="Directory for the bundle ZIP (default: Desktop or .)")

    args = parser.parse_args()
    configure_logging(args)

    dispatch = {
        "email-to-pdf": handle_email_to_pdf,
        "merge": handle_merge,
        "docx-to-pdf": handle_docx_to_pdf,
        "xlsx-to-pdf": handle_xlsx_to_pdf,
        "bates": handle_bates,
        "support-bundle": handle_support_bundle,
    }
    dispatch[args.operation](args)


if __name__ == "__main__":
    main()
