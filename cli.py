# cli.py — APMultitool command-line interface
"""Command-line interface scaffold for APMultitool.

Allows headless execution of core operations (email_to_pdf, merge) using DocEngine.
"""

import argparse
import sys
from pathlib import Path

from core.engine import DocEngine
from core.job import (
    Job, InputSpec, EmailToPdfParams, MergeParams, OutputSpec, JobStatus,
    DocxToPdfParams, XlsxToPdfParams, BatesParams
)


def handle_email_to_pdf(args):
    """Handler for the email_to_pdf operation."""
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
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

    engine = DocEngine(write_audit=True)

    def on_progress(msg, progress_val):
        print(f"[{int(progress_val * 100)}%] {msg}")

    print(f"Submitting Job {job.job_id} ({job.operation}) ...")
    res_job = engine.submit(job, on_progress=on_progress)

    if res_job.status == JobStatus.COMPLETE:
        print("\nJob completed successfully!")
        print(f"Output: {res_job.result.outputs[0]}")
        print(f"Pages: {res_job.result.page_count_out}")
        sys.exit(0)
    else:
        print(f"\nJob failed: {res_job.result.error}", file=sys.stderr)
        sys.exit(2)


def handle_merge(args):
    """Handler for the merge operation."""
    inputs = []
    for path_str in args.inputs:
        path = Path(path_str)
        if not path.exists():
            print(f"Warning: Input path not found: {path}", file=sys.stderr)
            continue
        inputs.append(InputSpec.from_path(path))

    if not inputs:
        print("Error: No valid inputs provided for merge.", file=sys.stderr)
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

    engine = DocEngine(write_audit=True)

    def on_progress(msg, progress_val):
        print(f"[{int(progress_val * 100)}%] {msg}")

    print(f"Submitting Job {job.job_id} ({job.operation}) ...")
    res_job = engine.submit(job, on_progress=on_progress)

    if res_job.status == JobStatus.COMPLETE:
        print("\nJob completed successfully!")
        print(f"Output: {res_job.result.outputs[0]}")
        print(f"Pages: {res_job.result.page_count_out}")
        sys.exit(0)
    else:
        print(f"\nJob failed: {res_job.result.error}", file=sys.stderr)
        sys.exit(2)


def handle_docx_to_pdf(args):
    """Handler for the docx_to_pdf operation."""
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
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

    engine = DocEngine(write_audit=True)

    def on_progress(msg, progress_val):
        print(f"[{int(progress_val * 100)}%] {msg}")

    print(f"Submitting Job {job.job_id} ({job.operation}) ...")
    res_job = engine.submit(job, on_progress=on_progress)

    if res_job.status == JobStatus.COMPLETE:
        print("\nJob completed successfully!")
        print(f"Output: {res_job.result.outputs[0]}")
        print(f"Pages: {res_job.result.page_count_out}")
        sys.exit(0)
    else:
        print(f"\nJob failed: {res_job.result.error}", file=sys.stderr)
        sys.exit(2)


def handle_xlsx_to_pdf(args):
    """Handler for the xlsx_to_pdf operation."""
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
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

    engine = DocEngine(write_audit=True)

    def on_progress(msg, progress_val):
        print(f"[{int(progress_val * 100)}%] {msg}")

    print(f"Submitting Job {job.job_id} ({job.operation}) ...")
    res_job = engine.submit(job, on_progress=on_progress)

    if res_job.status == JobStatus.COMPLETE:
        print("\nJob completed successfully!")
        print(f"Output: {res_job.result.outputs[0]}")
        print(f"Pages: {res_job.result.page_count_out}")
        sys.exit(0)
    else:
        print(f"\nJob failed: {res_job.result.error}", file=sys.stderr)
        sys.exit(2)


def handle_bates(args):
    """Handler for the bates_stamp operation."""
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
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

    engine = DocEngine(write_audit=True)

    def on_progress(msg, progress_val):
        print(f"[{int(progress_val * 100)}%] {msg}")

    print(f"Submitting Job {job.job_id} ({job.operation}) ...")
    res_job = engine.submit(job, on_progress=on_progress)

    if res_job.status == JobStatus.COMPLETE:
        print("\nJob completed successfully!")
        print(f"Output: {res_job.result.outputs[0]}")
        print(f"Pages: {res_job.result.page_count_out}")
        sys.exit(0)
    else:
        print(f"\nJob failed: {res_job.result.error}", file=sys.stderr)
        sys.exit(2)


def main():
    parser = argparse.ArgumentParser(
        description="APMultitool Command-Line Interface (Core v1.0.0)"
    )
    subparsers = parser.add_subparsers(dest="operation", required=True)

    # Subparser: email_to_pdf
    email_parser = subparsers.add_parser(
        "email_to_pdf",
        help="Convert email file (.eml/.msg) to PDF"
    )
    email_parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to the input EML or MSG file"
    )
    email_parser.add_argument(
        "-o", "--output-dir",
        default=".",
        help="Path to the output directory"
    )
    email_parser.add_argument(
        "--output-name",
        help="Custom name for the output PDF"
    )
    email_parser.add_argument(
        "--no-attachments",
        action="store_true",
        help="Disable parsing and appending attachments"
    )
    email_parser.add_argument(
        "--grayscale",
        action="store_true",
        help="Convert to PACER-compliant grayscale"
    )

    # Subparser: merge
    merge_parser = subparsers.add_parser(
        "merge",
        help="Merge multiple files into a single PDF"
    )
    merge_parser.add_argument(
        "-i", "--inputs",
        nargs="+",
        required=True,
        help="List of paths to input files or folders to merge"
    )
    merge_parser.add_argument(
        "-o", "--output-dir",
        default=".",
        help="Path to the output directory"
    )
    merge_parser.add_argument(
        "--output-name",
        help="Custom name for the merged output PDF"
    )
    merge_parser.add_argument(
        "--grayscale",
        action="store_true",
        help="Convert PDF pages and attachments to grayscale"
    )

    # Subparser: docx-to-pdf
    docx_parser = subparsers.add_parser(
        "docx-to-pdf",
        help="Convert Word document (.docx/.doc) to PDF"
    )
    docx_parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to the input Word file"
    )
    docx_parser.add_argument(
        "-o", "--output-dir",
        default=".",
        help="Path to the output directory"
    )
    docx_parser.add_argument(
        "--output-name",
        help="Custom name for the output PDF"
    )

    # Subparser: xlsx-to-pdf
    xlsx_parser = subparsers.add_parser(
        "xlsx-to-pdf",
        help="Convert Excel spreadsheet (.xlsx/.xls/.csv) to PDF"
    )
    xlsx_parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to the input Excel/CSV file"
    )
    xlsx_parser.add_argument(
        "-o", "--output-dir",
        default=".",
        help="Path to the output directory"
    )
    xlsx_parser.add_argument(
        "--output-name",
        help="Custom name for the output PDF"
    )

    # Subparser: bates
    bates_parser = subparsers.add_parser(
        "bates",
        help="Apply Bates stamping numbers to a PDF"
    )
    bates_parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to the target PDF file"
    )
    bates_parser.add_argument(
        "-o", "--output-dir",
        default=".",
        help="Path to the output directory"
    )
    bates_parser.add_argument(
        "--output-name",
        help="Custom name for the output PDF"
    )
    bates_parser.add_argument(
        "--prefix",
        default="",
        help="Bates prefix label text"
    )
    bates_parser.add_argument(
        "--sep",
        default="-",
        help="Separator character between prefix and serial number"
    )
    bates_parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="Starting serial number index"
    )
    bates_parser.add_argument(
        "--padding",
        type=int,
        default=7,
        help="Serial zero-padding width"
    )
    bates_parser.add_argument(
        "--pos",
        default="Bottom Right",
        choices=["Bottom Right", "Bottom Center", "Top Center", "Top Right", "Top Left", "Bottom Left"],
        help="Stamp placement location"
    )
    bates_parser.add_argument(
        "--font",
        default="Helvetica",
        help="Stamp font name"
    )
    bates_parser.add_argument(
        "--size",
        type=int,
        default=10,
        help="Stamp font size in points"
    )
    bates_parser.add_argument(
        "--no-shrink",
        action="store_true",
        help="Disable automatic layout shrinking for collision avoidance"
    )

    args = parser.parse_args()

    if args.operation == "email_to_pdf":
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
