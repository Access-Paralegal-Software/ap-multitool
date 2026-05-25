# core/operations/email_to_pdf.py — Email to PDF operation
"""Handler for converting an email file (.eml or .msg) to a PDF using the existing email_processing utilities.

The operation adheres to the core engine contract:
- Accepts a Job with EmailToPdfParams.
- Uses a progress callback to report stages.
- Checks job.status for cooperative cancellation at checkpoints.
- Writes output to a temporary file first, then moves it to the final output location.
- Merges body and attachments (if include_attachments is True) using pikepdf.
- Returns a JobResult with page counts, warnings, and the output path.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Callable

import pikepdf
from core import email_processing

from core.job import Job, JobResult, JobStatus, OperationCancelled, EmailToPdfParams


def _slugify(text: str) -> str:
    """Create a filesystem‑safe filename fragment from free‑form text.
    Simplified version: keep alphanumerics, replace spaces with underscores, limit length.
    """
    import re

    # Lowercase, replace spaces and punctuation with underscores
    safe = re.sub(r"[^a-z0-9]+", "_", text.lower())
    # Trim leading/trailing underscores and limit length
    safe = safe.strip("_")
    return safe[:50] or "email"


def handle(job: Job, progress: Callable[[str, float], None]) -> JobResult:
    """Core engine entry point for the *email_to_pdf* operation.

    Expected ``job.params`` type: :class:`EmailToPdfParams`.
    ``job.inputs`` should contain a single InputSpec pointing at the source email file.
    """
    params: EmailToPdfParams = job.params
    if len(job.inputs) != 1:
        raise ValueError("EmailToPdf operation requires exactly one input specification.")

    def check_cancelled():
        if job.status == JobStatus.CANCELLED:
            raise OperationCancelled("Email conversion was cancelled by user.")

    email_spec = job.inputs[0]
    warnings: list[str] = []
    temp_files: list[Path] = []

    try:
        check_cancelled()

        # ---------------------------------------------------------------------
        # Stage 1 – Parse email
        # ---------------------------------------------------------------------
        progress("Parsing email file …", 0.1)
        unified = email_processing.UnifiedEmail(email_spec.path)
        check_cancelled()

        # ---------------------------------------------------------------------
        # Stage 2 – Render cover/body PDF
        # ---------------------------------------------------------------------
        progress("Converting email body …", 0.3)
        body_tmp = Path(tempfile.mktemp(suffix=".pdf"))
        temp_files.append(body_tmp)
        
        email_processing.email_to_pdf(
            unified,
            body_tmp,
            grayscale=params.grayscale
        )
        check_cancelled()

        parts = [body_tmp]

        # ---------------------------------------------------------------------
        # Stage 3 – Process attachments (if requested)
        # ---------------------------------------------------------------------
        if params.include_attachments:
            progress("Processing attachments …", 0.5)
            # Yield attachments
            attachments = list(email_processing.get_email_attachments(unified, keep_inline=True))
            total_atts = len(attachments)
            
            for idx, (fname, data, ct) in enumerate(attachments):
                check_cancelled()
                progress(f"Converting attachment {idx+1}/{total_atts}: {fname[:20]} …", 0.5 + (idx / max(total_atts, 1)) * 0.3)
                
                # Write attachment data to a temp file because some converters expect a file on disk
                att_raw_tmp = Path(tempfile.mktemp(suffix=Path(fname).suffix))
                temp_files.append(att_raw_tmp)
                att_raw_tmp.write_bytes(data)
                
                att_pdf_tmp = Path(tempfile.mktemp(suffix=".pdf"))
                temp_files.append(att_pdf_tmp)
                
                success = False
                try:
                    # First try standard attachment conversion
                    success = email_processing.attachment_to_pdf(
                        data, fname, att_pdf_tmp, ct, grayscale=params.grayscale
                    )
                    
                    # Fallback for Word docx using Headless Office if available (matching merge.py patterns)
                    if not success or not att_pdf_tmp.exists():
                        att_low = fname.lower()
                        if att_low.endswith(('.docx', '.doc')):
                            from core.operations.merge import _word_to_pdf
                            _word_to_pdf(att_raw_tmp, att_pdf_tmp, warnings)
                            success = att_pdf_tmp.exists()
                except Exception as att_exc:
                    warnings.append(f"Failed to convert attachment {fname}: {att_exc}")
                    success = False
                    
                if success and att_pdf_tmp.exists():
                    parts.append(att_pdf_tmp)
                else:
                    # Render placeholder PDF for failed or non-renderable formats
                    try:
                        email_processing.placeholder_to_pdf(fname, att_pdf_tmp)
                        if att_pdf_tmp.exists():
                            parts.append(att_pdf_tmp)
                    except Exception:
                        warnings.append(f"Skipped attachment {fname} (could not render placeholder)")

        check_cancelled()

        # ---------------------------------------------------------------------
        # Stage 4 – Merge cover/body and attachments using pikepdf
        # ---------------------------------------------------------------------
        progress("Merging pages …", 0.8)
        merger = pikepdf.Pdf.new()
        
        page_count_in = 0
        for part in parts:
            check_cancelled()
            try:
                with pikepdf.open(part) as src:
                    for page in src.pages:
                        merger.pages.append(page)
                        page_count_in += 1
            except Exception as merge_exc:
                warnings.append(f"Failed to merge section {part.name}: {merge_exc}")

        check_cancelled()

        # Save to temp location first
        tmp_final_pdf = Path(tempfile.mktemp(suffix=".pdf"))
        merger.save(tmp_final_pdf)
        merger.close()
        temp_files.append(tmp_final_pdf)

        check_cancelled()

        # ---------------------------------------------------------------------
        # Stage 5 – Move to final location
        # ---------------------------------------------------------------------
        default_name = _slugify(unified.subject) + "_email.pdf"
        output_name = params.output_name or default_name
        final_path = Path(job.output.directory) / output_name
        if not final_path.suffix:
            final_path = final_path.with_suffix(".pdf")

        progress("Finalising output …", 0.9)
        final_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(tmp_final_pdf), str(final_path))

        # Count actual output pages
        page_count_out = 0
        try:
            with pikepdf.open(final_path) as final_pdf:
                page_count_out = len(final_pdf.pages)
        except Exception:
            page_count_out = page_count_in

        progress("Done.", 1.0)
        return JobResult(
            outputs=[final_path],
            page_count_in=page_count_in,
            page_count_out=page_count_out,
            warnings=warnings,
            error=None,
        )

    finally:
        # Cleanup all temp files
        for tmp in temp_files:
            try:
                if tmp.exists():
                    if tmp.is_file():
                        tmp.unlink()
                    elif tmp.is_dir():
                        shutil.rmtree(tmp)
            except Exception:
                pass
