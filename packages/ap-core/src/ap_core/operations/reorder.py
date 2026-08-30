"""
core/operations/reorder.py — Reorder pages within a PDF.

Output is always a new file. Source is never modified.
page_order is a 1-based list of the desired page sequence.
Example: [3, 1, 2] means output page 1 = source page 3, etc.

Dependencies: pikepdf
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import pikepdf

from ap_core.job import Job, JobResult, ReorderParams


def handle(job: Job, progress: Callable[[str, float], None]) -> JobResult:
    if not job.inputs:
        raise ValueError("Reorder requires exactly one input PDF.")

    spec = job.inputs[0]
    params: ReorderParams = job.params

    progress("Opening PDF …", 0.0)
    with pikepdf.open(spec.path) as src:
        total_pages = len(src.pages)

        if not params.page_order:
            raise ValueError("ReorderParams.page_order must not be empty.")

        _validate_order(params.page_order, total_pages)

        out_name = f"{spec.path.stem}_reordered.pdf"
        out_path = job.output.directory / out_name

        out_pdf = pikepdf.Pdf.new()
        for i, page_num in enumerate(params.page_order):
            out_pdf.pages.append(src.pages[page_num - 1])
            progress(f"Page {i + 1}/{len(params.page_order)} …", (i + 1) / len(params.page_order) * 0.9)

        progress("Writing output …", 0.9)
        out_pdf.save(out_path)
        out_pdf.close()

    progress("Done.", 1.0)
    return JobResult(
        outputs=[out_path],
        page_count_in=total_pages,
        page_count_out=len(params.page_order),
    )


def _validate_order(order: list[int], total_pages: int) -> None:
    for n in order:
        if not isinstance(n, int) or n < 1 or n > total_pages:
            raise ValueError(
                f"Page number {n} in page_order is out of range "
                f"for a {total_pages}-page document."
            )
