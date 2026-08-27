# core/operations/bates_stamp.py — Bates Stamping operation
"""Handler for applying Bates numbering to a PDF document.

Supports configurable position, font, prefix/separator, zero-padding, and optional
collision-avoidance shrinking when existing page content overlaps the stamp zone.
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

# --- Stamp geometry constants (PDF points; 72 pts = 1 inch) ---
_STAMP_MARGIN = 54   # half-inch inset — matches standard legal margin
_ZONE_W = 150        # collision-detection zone width
_ZONE_H = 60         # collision-detection zone height


def _zone_bbox(pos: str, pw: float, ph: float) -> tuple[float, float, float, float]:
    """Return (x0, y0, x1, y1) collision-detection box for the given stamp position."""
    if "Bottom Right" in pos:
        return pw - _ZONE_W, 0, pw, _ZONE_H
    if "Bottom Left" in pos:
        return 0, 0, _ZONE_W, _ZONE_H
    if "Top Right" in pos:
        return pw - _ZONE_W, ph - _ZONE_H, pw, ph
    if "Top Left" in pos:
        return 0, ph - _ZONE_H, _ZONE_W, ph
    # Bottom Center / Top Center
    cx = pw / 2
    if "Top" in pos:
        return cx - _ZONE_W / 2, ph - _ZONE_H, cx + _ZONE_W / 2, ph
    return cx - _ZONE_W / 2, 0, cx + _ZONE_W / 2, _ZONE_H


def _stamp_xy(pos: str, pw: float, ph: float, tw: float) -> tuple[float, float]:
    """Return (x, y) drawString coordinates for the stamp label."""
    depth = _STAMP_MARGIN / 2
    if "Bottom Right" in pos:
        return pw - tw - _STAMP_MARGIN, depth
    if "Bottom Center" in pos:
        return (pw - tw) / 2, depth
    if "Top Center" in pos:
        return (pw - tw) / 2, ph - depth
    if "Top Right" in pos:
        return pw - tw - _STAMP_MARGIN, ph - depth
    if "Top Left" in pos:
        return _STAMP_MARGIN, ph - depth
    # Bottom Left
    return _STAMP_MARGIN, depth


def handle(job: Job, progress: Callable[[str, float], None]) -> JobResult:
    """Core engine entry point for the *bates_stamp* operation."""
    params: BatesParams = job.params
    if len(job.inputs) != 1:
        raise ValueError("Bates stamping requires exactly one input.")

    def check_cancelled():
        if job.status == JobStatus.CANCELLED:
            raise OperationCancelled("Bates stamping was cancelled by user.")

    src_path = Path(job.inputs[0].path)
    if not src_path.exists():
        raise FileNotFoundError(f"Source file not found: {src_path}")

    warnings: list[str] = []
    fd, tmp_pdf_str = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)  # release the descriptor so pikepdf can atomically replace the file
    tmp_pdf = Path(tmp_pdf_str)

    try:
        check_cancelled()
        progress("Initializing Bates production …", 0.1)

        out_dir = Path(job.output.directory)
        out_dir.mkdir(parents=True, exist_ok=True)

        prefix = params.prefix or ""
        sep = params.sep or ""
        pos = params.position or "Bottom Right"
        start_idx = params.start_number
        padding = params.padding or 7
        size = params.font_size or 10

        # Map friendly font name to a ReportLab built-in bold face
        font_name = params.font_name or "Helvetica"
        if "Times" in font_name:
            pdf_font = "Times-Bold"
        elif "Courier" in font_name:
            pdf_font = "Courier-Bold"
        else:
            pdf_font = "Helvetica-Bold"

        progress("Stamping pages …", 0.2)

        # Open the source once for collision detection (avoids re-reading per page)
        reader = pypdf.PdfReader(str(src_path.resolve()))

        with pikepdf.open(src_path) as pdf:
            page_count = len(pdf.pages)
            if page_count == 0:
                raise ValueError("PDF contains no pages.")

            curr_idx = start_idx
            for i, page in enumerate(pdf.pages):
                check_cancelled()
                progress(f"Processing page {i + 1} of {page_count} …", 0.2 + 0.6 * (i / page_count))

                mbox = page.mediabox
                pw = float(mbox[2] - mbox[0])
                ph = float(mbox[3] - mbox[1])

                if params.shrink_conflict:
                    x0, y0, x1, y1 = _zone_bbox(pos, pw, ph)
                    try:
                        found_text: list[str] = []

                        def visitor(text, cm, tm, fontDict, fontSize):
                            tx, ty = tm[4], tm[5]
                            if x0 <= tx <= x1 and y0 <= ty <= y1 and text.strip():
                                found_text.append(text)

                        reader.pages[i].extract_text(visitor_text=visitor)
                        if found_text:
                            scale = min((pw - 2 * _STAMP_MARGIN) / pw, (ph - 2 * _STAMP_MARGIN) / ph, 1.0)
                            tx = (pw - pw * scale) / 2
                            ty = (ph - ph * scale) / 2
                            matrix = f"q {scale:.4f} 0 0 {scale:.4f} {tx:.4f} {ty:.4f} cm ".encode()
                            page.contents_add(matrix, prepend=True)
                            page.contents_add(b" Q", prepend=False)
                    except Exception as exc:
                        warnings.append(f"Collision detection warning on page {i + 1}: {exc}")

                bates_str = f"{prefix}{sep}{str(curr_idx).zfill(padding)}"

                packet = BytesIO()
                c = canvas.Canvas(packet, pagesize=(pw, ph))
                c.setFont(pdf_font, size)
                tw = c.stringWidth(bates_str, pdf_font, size)
                x, y = _stamp_xy(pos, pw, ph, tw)
                c.drawString(x, y, bates_str)
                c.save()

                packet.seek(0)
                with pikepdf.open(packet) as overlay:
                    page.add_overlay(overlay.pages[0])

                curr_idx += 1

            check_cancelled()
            progress("Writing stamped PDF …", 0.85)

            if params.output_name:
                out_name = params.output_name
            else:
                end_idx = curr_idx - 1
                if params.naming == "Prefix_StartOnly":
                    out_name = f"{prefix}{sep}{str(start_idx).zfill(padding)}.pdf"
                else:
                    out_name = f"{prefix}{sep}{str(start_idx).zfill(padding)}-{str(end_idx).zfill(padding)}.pdf"

            final_dest = out_dir / out_name
            if final_dest.exists() and not job.output.overwrite:
                stem, ext = final_dest.stem, final_dest.suffix
                counter = 1
                while final_dest.exists():
                    final_dest = out_dir / f"{stem}_{counter:02d}{ext}"
                    counter += 1

            pdf.save(str(tmp_pdf), linearize=True)

        check_cancelled()
        progress("Saving production PDF …", 0.95)
        shutil.move(str(tmp_pdf), str(final_dest))

        progress("Done.", 1.0)
        return JobResult(
            outputs=[final_dest],
            page_count_in=page_count,
            page_count_out=page_count,
            warnings=warnings,
            error=None,
        )

    finally:
        try:
            if tmp_pdf.exists():
                tmp_pdf.unlink()
        except Exception:
            pass
