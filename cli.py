# cli.py — APMultitool command-line interface
"""Command-line interface for APMultitool.

Allows headless execution of core operations (email-to-pdf, merge, docx-to-pdf, xlsx-to-pdf, bates) using DocEngine.
"""

import argparse
import sys
import json
from pathlib import Path

from core.logging_config import configure_cli_logging
from core.engine import DocEngine
from core.job import (
    Job, InputSpec, EmailToPdfParams, MergeParams, OutputSpec, JobStatus,
    DocxToPdfParams, XlsxToPdfParams, BatesParams
)

logger = None


def configure_logging(args):
    """Adjust logging verbosity and format based on global CLI parameters."""
    global logger
    logger = configure_cli_logging(args)


def get_progress_cb(args):
    """Return a progress callback suitable for the selected verbosity."""
    if getattr(args, "silent", False) or getattr(args, "quiet", False) or getattr(args, "json", False):
        return lambda msg, val: None

    def on_progress(msg, progress_val):
        logger.info(f"Progress: {int(progress_val * 100)}% - {msg}")
    return on_progress


def handle_job_result(res_job, args):
    """Common result formatter and exit-code handler.

    Exits:
      0 = Complete
      1 = Failed Execution
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
            # Output goes strictly to stdout
            print(json.dumps(result_data, indent=2))
        else:
            # Info logs go to stderr
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
        sys.exit(1) # Execution failure gets exit code 1


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
            sys.exit(1) # Operational failure exit code
    return wrapper


@trap_execution
def handle_email_to_pdf(args):
    """Handler for the email-to-pdf operation."""
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        if args.json:
            print(json.dumps({"status": "failed", "error": f"Input file not found: {input_path}"}))
        sys.exit(2) # Validation/Argument error gets exit code 2

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
        sys.exit(2) # Validation/Argument error gets exit code 2

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Dry run execution check
    if getattr(args, "dry_run", False):
        summary = {
            "dry_run": True,
            "operation": "merge",
            "inputs_resolved": [str(i.path) for i in inputs],
            "output_directory": str(output_dir),
            "output_name": args.output_name or "merged.pdf",
            "grayscale": args.grayscale
        }
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            # Print human-readable summary to stdout
            print("=== DRY RUN SUMMARY ===")
            print(f"Operation: Merge")
            print(f"Inputs Resolved ({len(inputs)}):")
            for inp in summary["inputs_resolved"]:
                print(f"  - {inp}")
            print(f"Output Directory: {summary['output_directory']}")
            print(f"Output Name Override: {summary['output_name']}")
            print(f"Grayscale: {summary['grayscale']}")
            print("=======================")
        sys.exit(0)

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
        sys.exit(2) # Validation/Argument error gets exit code 2

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
        sys.exit(2) # Validation/Argument error gets exit code 2

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
        sys.exit(2) # Validation/Argument error gets exit code 2

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Dry run execution check
    if getattr(args, "dry_run", False):
        summary = {
            "dry_run": True,
            "operation": "bates_stamp",
            "input_resolved": str(input_path),
            "output_directory": str(output_dir),
            "output_name": args.output_name or f"{args.prefix or 'BATES'}_stamped.pdf",
            "prefix": args.prefix or "",
            "sep": args.sep,
            "start_number": args.start_number,
            "padding": args.padding,
            "position": args.position,
            "font_name": args.font_name,
            "font_size": args.font_size,
            "shrink_conflict": not args.no_shrink
        }
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print("=== DRY RUN SUMMARY ===")
            print(f"Operation: Bates Stamp")
            print(f"Input File: {summary['input_resolved']}")
            print(f"Output Directory: {summary['output_directory']}")
            print(f"Output Name Override: {summary['output_name']}")
            print(f"Prefix: {summary['prefix']}")
            print(f"Separator: '{summary['sep']}'")
            print(f"Start Number: {summary['start_number']}")
            print(f"Padding Width: {summary['padding']}")
            print(f"Position: {summary['position']}")
            print(f"Font Name: {summary['font_name']}")
            print(f"Font Size: {summary['font_size']}")
            print(f"Shrink Conflict Page Contents: {summary['shrink_conflict']}")
            print("=======================")
        sys.exit(0)

    job_input = InputSpec.from_path(input_path)
    job_params = BatesParams(
        prefix=args.prefix or "",
        start_number=args.start_number,
        padding=args.padding,
        position=args.position,
        font_size=args.font_size,
        shrink_conflict=not args.no_shrink,
        sep=args.sep,
        font_name=args.font_name,
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


def handle_support_bundle(args):
    """Compile diagnostic support bundle ZIP archive."""
    try:
        from core.support import create_support_bundle
        
        output_dir = Path(args.output_dir) if args.output_dir else None
        
        logger.info("Generating offline support bundle...")
        zip_path = create_support_bundle(target_dir=output_dir)
        
        print(json.dumps({
            "status": "success",
            "support_bundle_path": str(zip_path.resolve())
        }, indent=2))
        
        logger.info(f"Support bundle generated successfully at: {zip_path}")
        logger.info("Please manually copy and share this file with support as requested.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to generate support bundle: {e}")
        print(json.dumps({
            "status": "error",
            "error": str(e)
        }, indent=2))
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="APMultitool Command-Line Interface (Core v1.2.0)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples of usage:
  # Merge PDFs in a directory:
  python cli.py merge -i document_folder/ -o output_folder/ --output-name final_pack.pdf

  # Convert an email to PDF silently with JSON output:
  python cli.py --json --silent email-to-pdf -i mail.eml -o out/

  # Apply Bates stamping starting at 1000:
  python cli.py bates -i document.pdf --prefix CONFIDENTIAL --start-number 1000 --padding 6
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
        "-q", "--quiet",
        action="store_true",
        help="Alias for --silent"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print structured execution status and outcomes in JSON to stdout on exit"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Override the shared local log level for this CLI invocation"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="APMultitool CLI v1.2.0",
        help="Show program's version number and exit"
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
    merge_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform configuration validation and print merge outline without generating output files"
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
        "--start-number",
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
        "--position",
        default="Bottom Right",
        choices=["Bottom Right", "Bottom Center", "Top Center", "Top Right", "Top Left", "Bottom Left"],
        help="Placement zone on each page (default: 'Bottom Right')"
    )
    bates_parser.add_argument(
        "--font-name",
        default="Helvetica",
        help="Font face name (default: 'Helvetica')"
    )
    bates_parser.add_argument(
        "--font-size",
        type=int,
        default=10,
        help="Font size in points (default: 10)"
    )
    bates_parser.add_argument(
        "--no-shrink",
        action="store_true",
        help="Disable page margin shrinking for collision avoidance"
    )
    bates_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform parameters check and print Bates layout summary without generating output file"
    )

    # Subparser: support-bundle
    support_parser = subparsers.add_parser(
        "support-bundle",
        help="Generate a local-only offline support bundle ZIP archive for troubleshooting"
    )
    support_parser.add_argument(
        "-o", "--output-dir",
        default=None,
        help="Optional directory to save the support bundle (default: Desktop or current directory)"
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
    elif args.operation == "support-bundle":
        handle_support_bundle(args)


if __name__ == "__main__":
    main()
