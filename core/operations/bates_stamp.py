# core/operations/bates_stamp.py — Bates Stamping operation
"""Handler for applying bates stamping to a PDF document.

Includes precision text collision detection and page content shrinking.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Callable

import pikepdf
import pypdf
from reportlab.pdfgen import canvas

from core.job import Job, JobResult, JobStatus, OperationCancelled, BatesParams


def handle(job: Job, progress: Callable[[str, float], None]) -> JobResult:
    """Core engine entry point for the *bates_stamp* operation."""
    params: BatesParams = job.params
    if len(job.inputs) != 1:
        raise ValueError("Bates stamping operation requires exactly one input specification.")

    def check_cancelled():
        if job.status == JobStatus.CANCELLED:
            raise OperationCancelled("Bates stamping was cancelled by user.")

    input_spec = job.inputs[0]
    src_path = Path(input_spec.path)
    if not src_path.exists():
        raise FileNotFoundError(f"Source file not found: {src_path}")

    warnings: list[str] = []
    temp_files: list[Path] = []

    try:
        check_cancelled()
        progress("Initializing Bates production ...", 0.1)

        # Output folder and name
        out_dir = Path(job.output.directory)
        out_dir.mkdir(parents=True, exist_ok=True)

        # Retrieve parameters
        prefix = params.prefix or ""
        sep = params.sep or ""
        font = params.font_name or "Helvetica"
        size = params.font_size or 10
        pos = params.position or "Bottom Right"
        start_idx = params.start_number
        padding = params.padding or 7

        # Font mapping (ReportLab standard font names)
        pdf_font = "Helvetica-Bold"
        if "Times" in font:
            pdf_font = "Times-Bold"
        elif "Courier" in font:
            pdf_font = "Courier-Bold"
        elif "Arial" in font:
            pdf_font = "Helvetica"

        curr_idx = start_idx
        tmp_pdf = Path(tempfile.mktemp(suffix=".pdf"))
        temp_files.append(tmp_pdf)

        # We will copy the source PDF to the temp file first, then modify it in-place or write to it.
        # However, pikepdf is excellent at modifying or saving.
        # Let's open the source PDF with pikepdf.
        progress("Stamping pages ...", 0.2)

        with pikepdf.open(src_path) as pdf:
            page_count = len(pdf.pages)
            if page_count == 0:
                raise ValueError("PDF document contains no pages.")

            for i, page in enumerate(pdf.pages):
                check_cancelled()
                # Report incremental progress from 0.2 to 0.8
                percent = 0.2 + (0.6 * (i / page_count))
                progress(f"Processing page {i+1} of {page_count} ...", percent)

                mbox = page.mediabox
                p_w = float(mbox[2] - mbox[0])
                p_h = float(mbox[3] - mbox[1])

                # Margin and collision parameters
                LEGAL_MARGIN = 54
                needs_shrink = False

                if params.shrink_conflict:
                    try:
                        # Define corner boxes for collision detection
                        zone_w, zone_h = 150, 60
                        if "Bottom Right" in pos:
                            x0, y0, x1, y1 = p_w - zone_w, 0, p_w, zone_h
                        elif "Bottom Left" in pos:
                            x0, y0, x1, y1 = 0, 0, zone_w, zone_h
                        elif "Top Right" in pos:
                            x0, y0, x1, y1 = p_w - zone_w, p_h - zone_h, p_w, p_h
                        elif "Top Left" in pos:
                            x0, y0, x1, y1 = 0, p_h - zone_h, zone_w, p_h
                        else:  # Center / Bottom Center / Top Center
                            x0, y0, x1, y1 = p_w/2 - zone_w/2, 0, p_w/2 + zone_w/2, zone_h

                        # Read text positions via pypdf visitor
                        reader = pypdf.PdfReader(str(src_path.resolve()))
                        found_text = []

                        def visitor(text, cm, tm, fontDict, fontSize):
                            tx, ty = tm[4], tm[5]
                            if x0 <= tx <= x1 and y0 <= ty <= y1:
                                if text.strip():
                                    found_text.append(text)

                        reader.pages[i].extract_text(visitor_text=visitor)
                        if found_text:
                            needs_shrink = True
                    except Exception as e_visitor:
                        warnings.append(f"Visitor text extraction warning on page {i+1}: {e_visitor}")

                if needs_shrink:
                    # Apply collision avoidance shrink transformation
                    scale_x = (p_w - 2 * LEGAL_MARGIN) / p_w
                    scale_y = (p_h - 2 * LEGAL_MARGIN) / p_h
                    scale = min(scale_x, scale_y, 1.0)
                    tx = (p_w - p_w * scale) / 2
                    ty = (p_h - p_h * scale) / 2
                    matrix = f"q {scale:.4f} 0 0 {scale:.4f} {tx:.4f} {ty:.4f} cm ".encode()
                    page.contents_add(matrix, prepend=True)
                    page.contents_add(b" Q", prepend=False)

                # Format the serial number
                bates_str = f"{prefix}{sep}{str(curr_idx).zfill(padding)}"

                # Draw the stamp overlay using ReportLab
                packet = BytesIO()
                can = canvas.Canvas(packet, pagesize=(p_w, p_h))
                can.setFont(pdf_font, size)

                # Position calculation (perfect center in margin moat)
                tw = can.stringWidth(bates_str, pdf_font, size)
                stamp_depth = LEGAL_MARGIN / 2

                if "Bottom Right" in pos:
                    x, y = p_w - tw - LEGAL_MARGIN, stamp_depth
                elif "Bottom Center" in pos:
                    x, y = (p_w / 2) - (tw / 2), stamp_depth
                elif "Top Center" in pos:
                    x, y = (p_w / 2) - (tw / 2), p_h - stamp_depth
                elif "Top Right" in pos:
                    x, y = p_w - tw - LEGAL_MARGIN, p_h - stamp_depth
                elif "Top Left" in pos:
                    x, y = LEGAL_MARGIN, p_h - stamp_depth
                else:  # Bottom Left
                    x, y = LEGAL_MARGIN, stamp_depth

                can.drawString(x, y, bates_str)
                can.save()

                packet.seek(0)
                with pikepdf.open(packet) as overlay:
                    page.add_overlay(overlay.pages[0])

                curr_idx += 1

            check_cancelled()
            progress("Writing stamped PDF output ...", 0.85)

            # Determine output filename
            if params.output_name:
                out_name = params.output_name
            else:
                end_idx = curr_idx - 1
                if params.naming == "Prefix_StartOnly":
                    out_name = f"{prefix}{sep}{str(start_idx).zfill(padding)}.pdf"
                else:
                    out_name = f"{prefix}{sep}{str(start_idx).zfill(padding)}-{str(end_idx).zfill(padding)}.pdf"

            final_dest = out_dir / out_name

            # Resolve naming conflicts
            if final_dest.exists() and not job.output.overwrite:
                stem = final_dest.stem
                ext = final_dest.suffix
                counter = 1
                while final_dest.exists():
                    final_dest = out_dir / f"{stem}_{counter:02d}{ext}"
                    counter += 1

            pdf.save(str(tmp_pdf), linearize=True)

        check_cancelled()
        progress("Saving production PDF ...", 0.95)
        shutil.move(str(tmp_pdf), str(final_dest))

        progress("Done.", 1.0)
        return JobResult(
            outputs=[final_dest],
            page_count_in=page_count,
            page_count_out=page_count,
            warnings=warnings,
            error=None
        )

    finally:
        for tmp in temp_files:
            try:
                if tmp.exists():
                    tmp.unlink()
            except Exception:
                pass
