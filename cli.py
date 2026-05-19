# cli.py — APMultitool command-line interface
"""Command-line interface for APMultitool.

Allows headless execution of core operations (email-to-pdf, merge, docx-to-pdf, xlsx-to-pdf, bates) using DocEngine.
"""

import argparse
import sys
import json
import logging
from pathlib import Path

from core.engine import DocEngine
from core.job import (
    Job, InputSpec, EmailToPdfParams, MergeParams, OutputSpec, JobStatus,
    DocxToPdfParams, XlsxToPdfParams, BatesParams
)

# Setup standard logger to stderr so stdout is reserved for stdout JSON payload redirecting.
logger = logging.getLogger("APMultitool")
logger.setLevel(logging.INFO)
log_handler = logging.StreamHandler(sys.stderr)
log_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
logger.addHandler(log_handler)


def configure_logging(args):
    """Adjust logging verbosity and format based on global CLI parameters."""
    if getattr(args, "silent", False):
        logger.setLevel(logging.ERROR)
    elif getattr(args, "verbose", False):
        logger.setLevel(logging.DEBUG)
        log_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) %(message)s"))
    else:
        logger.setLevel(logging.INFO)


def get_progress_cb(args):
    """Return a progress callback suitable for the selected verbosity."""
    if getattr(args, "silent", False) or getattr(args, "json", False):
        return lambda msg, val: None

    def on_progress(msg, progress_val):
        logger.info(f"Progress: {int(progress_val * 100)}% - {msg}")
    return on_progress


def handle_job_result(res_job, args):
    """Common result formatter and exit-code handler.

    Exits:
      0 = Complete
      2 = Failed Execution
      3 = Cancelled
    """
    is_json = getattr(args, "json", False)

    if res_job.status == JobStatus.COMPLETE:
        output_paths = [str(p) for p in res_job.result.outputs]
        page_count = res_job.result.page_count_out

        if is_json:
            result_data = {
                "status": "success",
                "job_id": res_job.job_id,
                "operation": res_job.operation,
                "outputs": output_paths,
                "page_count": page_count,
                "error": None
            }
            print(json.dumps(result_data, indent=2))
        else:
            logger.info("Job completed successfully!")
            logger.info(f"Output: {output_paths[0]}")
            logger.info(f"Pages: {page_count}")
        sys.exit(0)
    elif res_job.status == JobStatus.CANCELLED:
        if is_json:
            result_data = {
                "status": "cancelled",
                "job_id": res_job.job_id,
                "operation": res_job.operation,
                "outputs": [],
                "page_count": 0,
                "error": "Operation was cancelled by user."
            }
            print(json.dumps(result_data, indent=2))
        else:
            logger.warning("Job was cancelled.")
        sys.exit(3)
    else:
        error_msg = res_job.result.error or "Unknown engine error"
        if is_json:
            result_data = {
                "status": "failed",
                "job_id": res_job.job_id,
                "operation": res_job.operation,
                "outputs": [],
                "page_count": 0,
                "error": error_msg
            }
            print(json.dumps(result_data, indent=2))
        else:
            logger.error(f"Job failed: {error_msg}")
        sys.exit(2)


def trap_execution(func):
    """Decorator to trap execution errors and handle them according to verbosity/JSON config."""
    def wrapper(args, *extra, **kwargs):
        try:
            return func(args, *extra, **kwargs)
        except Exception as e:
            if getattr(args, "verbose", False):
                import traceback
                traceback.print_exc()
            else:
                logger.error(f"Execution Error: {e}")

            if getattr(args, "json", False):
                result_data = {
                    "status": "failed",
                    "error": str(e)
                }
                print(json.dumps(result_data, indent=2))
            sys.exit(2)
    return wrapper


@trap_execution
def handle_email_to_pdf(args):
    """Handler for the email-to-pdf operation."""
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        if args.json:
            print(json.dumps({"status": "failed", "error": f"Input file not found: {input_path}"}))
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    job_input = InputSpec.from_path(input_path)
    job_params = EmailToPdfParams(
        grayscale=args.grayscale,
        include_attachments=not args.no_attachments,
        output_name=args.output_name
    )
    job_output = OutputSpec(directory=output_dir)

    job = Job(
        operation="email_to_pdf",
        inputs=[job_input],
        params=job_params,
        output=job_output
    )

    logger.debug(f"Submitting Job {job.job_id} ({job.operation}) to DocEngine...")
    engine = DocEngine(write_audit=True)
    res_job = engine.submit(job, on_progress=get_progress_cb(args))
    handle_job_result(res_job, args)


@trap_execution
def handle_merge(args):
    """Handler for the merge operation."""
    inputs = []
    for path_str in args.inputs:
        path = Path(path_str)
        if not path.exists():
            logger.warning(f"Input path not found: {path}")
            continue
        inputs.append(InputSpec.from_path(path))

    if not inputs:
        logger.error("No valid inputs provided for merge.")
        if args.json:
            print(json.dumps({"status": "failed", "error": "No valid inputs provided for merge."}))
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    job_params = MergeParams(
        grayscale=args.grayscale,
        output_name=args.output_name
    )
    job_output = OutputSpec(directory=output_dir)

    job = Job(
        operation="merge",
        inputs=inputs,
        params=job_params,
        output=job_output
    )

    logger.debug(f"Submitting Job {job.job_id} ({job.operation}) to DocEngine...")
    engine = DocEngine(write_audit=True)
    res_job = engine.submit(job, on_progress=get_progress_cb(args))
    handle_job_result(res_job, args)


@trap_execution
def handle_docx_to_pdf(args):
    """Handler for the docx-to-pdf operation."""
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        if args.json:
            print(json.dumps({"status": "failed", "error": f"Input file not found: {input_path}"}))
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    job_input = InputSpec.from_path(input_path)
    job_params = DocxToPdfParams(
        output_name=args.output_name
    )
    job_output = OutputSpec(directory=output_dir)

    job = Job(
        operation="docx_to_pdf",
        inputs=[job_input],
        params=job_params,
        output=job_output
    )

    logger.debug(f"Submitting Job {job.job_id} ({job.operation}) to DocEngine...")
    engine = DocEngine(write_audit=True)
    res_job = engine.submit(job, on_progress=get_progress_cb(args))
    handle_job_result(res_job, args)


@trap_execution
def handle_xlsx_to_pdf(args):
    """Handler for the xlsx-to-pdf operation."""
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        if args.json:
            print(json.dumps({"status": "failed", "error": f"Input file not found: {input_path}"}))
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    job_input = InputSpec.from_path(input_path)
    job_params = XlsxToPdfParams(
        output_name=args.output_name
    )
    job_output = OutputSpec(directory=output_dir)

    job = Job(
        operation="xlsx_to_pdf",
        inputs=[job_input],
        params=job_params,
        output=job_output
    )

    logger.debug(f"Submitting Job {job.job_id} ({job.operation}) to DocEngine...")
    engine = DocEngine(write_audit=True)
    res_job = engine.submit(job, on_progress=get_progress_cb(args))
    handle_job_result(res_job, args)


@trap_execution
def handle_bates(args):
    """Handler for the bates operation."""
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        if args.json:
            print(json.dumps({"status": "failed", "error": f"Input file not found: {input_path}"}))
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    job_input = InputSpec.from_path(input_path)
    job_params = BatesParams(
        prefix=args.prefix or "",
        start_number=args.start,
        padding=args.padding,
        position=args.pos,
        font_size=args.size,
        shrink_conflict=not args.no_shrink,
        sep=args.sep,
        font_name=args.font,
        naming="Prefix_Range" if args.output_name is None else "Prefix_StartOnly",
        output_name=args.output_name
    )
    job_output = OutputSpec(directory=output_dir, overwrite=True)

    job = Job(
        operation="bates_stamp",
        inputs=[job_input],
        params=job_params,
        output=job_output
    )

    logger.debug(f"Submitting Job {job.job_id} ({job.operation}) to DocEngine...")
    engine = DocEngine(write_audit=True)
    res_job = engine.submit(job, on_progress=get_progress_cb(args))
    handle_job_result(res_job, args)


def main():
    parser = argparse.ArgumentParser(
        description="APMultitool Command-Line Interface (Core v1.1.0)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples of usage:
  # Merge PDFs in a directory:
  python cli.py merge -i document_folder/ -o output_folder/ --output-name final_pack.pdf

  # Convert an email to PDF silently with JSON output:
  python cli.py --json --silent email-to-pdf -i mail.eml -o out/

  # Apply Bates stamping starting at 1000:
  python cli.py bates -i document.pdf --prefix CONFIDENTIAL --start 1000 --padding 6
"""
    )
    # Global modifiers
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable debug log format and show error tracebacks"
    )
    parser.add_argument(
        "--silent",
        action="store_true",
        help="Suppress all informational output logs (error logs still print)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print structured execution status and outcomes in JSON to stdout on exit"
    )

    subparsers = parser.add_subparsers(dest="operation", required=True)

    # Subparser: email-to-pdf
    email_parser = subparsers.add_parser(
        "email-to-pdf",
        help="Convert email files (.eml/.msg) with attachments to PDF"
    )
    email_parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to the source email file"
    )
    email_parser.add_argument(
        "-o", "--output-dir",
        default=".",
        help="Target folder for the PDF output (default: current directory)"
    )
    email_parser.add_argument(
        "--output-name",
        help="Override naming template for generated PDF"
    )
    email_parser.add_argument(
        "--no-attachments",
        action="store_true",
        help="Disable parsing and appending attachments"
    )
    email_parser.add_argument(
        "--grayscale",
        action="store_true",
        help="Force PACER-compliant grayscale compression"
    )

    # Subparser: merge
    merge_parser = subparsers.add_parser(
        "merge",
        help="Merge multiple PDFs, images, and converted files into one PDF"
    )
    merge_parser.add_argument(
        "-i", "--inputs",
        nargs="+",
        required=True,
        help="Paths to files or folders to sequence and merge"
    )
    merge_parser.add_argument(
        "-o", "--output-dir",
        default=".",
        help="Target folder for output PDF (default: current directory)"
    )
    merge_parser.add_argument(
        "--output-name",
        help="Override name of output PDF"
    )
    merge_parser.add_argument(
        "--grayscale",
        action="store_true",
        help="Force all merged pages to grayscale layout representation"
    )

    # Subparser: docx-to-pdf
    docx_parser = subparsers.add_parser(
        "docx-to-pdf",
        help="Convert Word documents (.docx/.doc) to PDF"
    )
    docx_parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to the Word document"
    )
    docx_parser.add_argument(
        "-o", "--output-dir",
        default=".",
        help="Target folder for output PDF"
    )
    docx_parser.add_argument(
        "--output-name",
        help="Override output PDF filename"
    )

    # Subparser: xlsx-to-pdf
    xlsx_parser = subparsers.add_parser(
        "xlsx-to-pdf",
        help="Convert Excel spreadsheets (.xlsx/.xls/.csv) to PDF"
    )
    xlsx_parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to the source spreadsheet"
    )
    xlsx_parser.add_argument(
        "-o", "--output-dir",
        default=".",
        help="Target folder for output PDF"
    )
    xlsx_parser.add_argument(
        "--output-name",
        help="Override output PDF filename"
    )

    # Subparser: bates
    bates_parser = subparsers.add_parser(
        "bates",
        help="Overlay Bates serial numbering onto a PDF"
    )
    bates_parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to target PDF to number"
    )
    bates_parser.add_argument(
        "-o", "--output-dir",
        default=".",
        help="Target folder for stamped PDF"
    )
    bates_parser.add_argument(
        "--output-name",
        help="Override filename for the stamped PDF"
    )
    bates_parser.add_argument(
        "--prefix",
        default="",
        help="Alpha prefix to prepend to the Bates number (e.g. 'PROD')"
    )
    bates_parser.add_argument(
        "--sep",
        default="-",
        help="Separator character between prefix and serial (default: '-')"
    )
    bates_parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="Starting serial index (default: 1)"
    )
    bates_parser.add_argument(
        "--padding",
        type=int,
        default=7,
        help="Zero padding width for serial suffix (default: 7)"
    )
    bates_parser.add_argument(
        "--pos",
        default="Bottom Right",
        choices=["Bottom Right", "Bottom Center", "Top Center", "Top Right", "Top Left", "Bottom Left"],
        help="Placement zone on each page (default: 'Bottom Right')"
    )
    bates_parser.add_argument(
        "--font",
        default="Helvetica",
        help="Font face name (default: 'Helvetica')"
    )
    bates_parser.add_argument(
        "--size",
        type=int,
        default=10,
        help="Font size in points (default: 10)"
    )
    bates_parser.add_argument(
        "--no-shrink",
        action="store_true",
        help="Disable page margin shrinking for collision avoidance"
    )

    args = parser.parse_args()
    configure_logging(args)

    if args.operation == "email-to-pdf":
        handle_email_to_pdf(args)
    elif args.operation == "merge":
        handle_merge(args)
    elif args.operation == "docx-to-pdf":
        handle_docx_to_pdf(args)
    elif args.operation == "xlsx-to-pdf":
        handle_xlsx_to_pdf(args)
    elif args.operation == "bates":
        handle_bates(args)


if __name__ == "__main__":
    main()
