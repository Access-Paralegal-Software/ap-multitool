"""
core/operations/rotate.py — Rotate pages in a PDF.

Output is always a new file. Source is never modified.

Dependencies: pikepdf
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import pikepdf

from core.job import Job, JobResult, RotateParams
from core.operations.extract import _resolve_selection


def handle(job: Job, progress: Callable[[str, float], None]) -> JobResult:
    if not job.inputs:
        raise ValueError("Rotate requires exactly one input PDF.")

    spec = job.inputs[0]
    params: RotateParams = job.params

    if params.angle not in (90, 180, 270):
        raise ValueError(f"Rotation angle must be 90, 180, or 270. Got: {params.angle}")

    out_name = f"{spec.path.stem}_rotated.pdf"
    out_path = job.output.directory / out_name

    progress("Opening PDF …", 0.0)
    with pikepdf.open(spec.path) as src:
        total_pages = len(src.pages)
        target_indices = set(_resolve_selection(params.page_selection, total_pages))

        out_pdf = pikepdf.Pdf.new()
        for i, page in enumerate(src.pages):
            out_pdf.pages.append(page)
            if i in target_indices:
                _rotate_page(out_pdf.pages[i], params.angle)
            progress(f"Processing page {i + 1}/{total_pages} …", (i + 1) / total_pages * 0.9)

        progress("Writing output …", 0.9)
        out_pdf.save(out_path)
        out_pdf.close()

    progress("Done.", 1.0)
    return JobResult(
        outputs=[out_path],
        page_count_in=total_pages,
        page_count_out=total_pages,
    )


def _rotate_page(page: pikepdf.Page, angle: int) -> None:
    """Apply rotation to a pikepdf page object in place."""
    existing = int(page.get("/Rotate", 0))
    new_angle = (existing + angle) % 360
    page["/Rotate"] = new_angle
