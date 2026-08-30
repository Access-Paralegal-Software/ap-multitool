"""
core/operations/extract.py — Extract a page subset into a new PDF.

The source file is never modified. Output is always a new file.

Dependencies: pikepdf
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Callable

import pikepdf

from ap_core.job import Job, JobResult, ExtractParams


def handle(job: Job, progress: Callable[[str, float], None]) -> JobResult:
    if not job.inputs:
        raise ValueError("Extract requires exactly one input PDF.")

    spec = job.inputs[0]
    params: ExtractParams = job.params

    progress("Parsing page selection …", 0.0)
    with pikepdf.open(spec.path) as src:
        total_pages = len(src.pages)
        indices = _resolve_selection(params.page_selection, total_pages)

        if not indices:
            raise ValueError("Page selection is empty — nothing to extract.")

        out_name = params.output_name or f"{spec.path.stem}_extract_{date.today():%Y-%m-%d}.pdf"
        out_path = job.output.directory / out_name
        if not out_path.suffix:
            out_path = out_path.with_suffix(".pdf")

        progress("Extracting pages …", 0.3)
        out_pdf = pikepdf.Pdf.new()
        for i, idx in enumerate(indices):
            out_pdf.pages.append(src.pages[idx])
            progress(f"Page {idx + 1} …", 0.3 + 0.6 * (i / len(indices)))

        progress("Writing output …", 0.9)
        out_pdf.save(out_path)
        out_pdf.close()

    progress("Done.", 1.0)
    return JobResult(
        outputs=[out_path],
        page_count_in=total_pages,
        page_count_out=len(indices),
    )


def _resolve_selection(selection: str, total_pages: int) -> list[int]:
    """
    Parse a page selection string into a list of 0-based page indices.
    Accepts: "1-5", "3,7,12", "1,3-5,9", "all"
    """
    selection = selection.strip()
    if not selection or selection.lower() == "all":
        return list(range(total_pages))

    indices: list[int] = []
    for part in selection.split(","):
        part = part.strip()
        m = re.fullmatch(r"(\d+)\s*[-–]\s*(\d+)", part)
        if m:
            start = int(m.group(1)) - 1
            end = int(m.group(2)) - 1
            if start < 0 or end >= total_pages or start > end:
                raise ValueError(f"Range '{part}' out of bounds for {total_pages}-page document.")
            indices.extend(range(start, end + 1))
        elif part.isdigit():
            idx = int(part) - 1
            if idx < 0 or idx >= total_pages:
                raise ValueError(f"Page {part} out of bounds for {total_pages}-page document.")
            indices.append(idx)
        else:
            raise ValueError(f"Cannot parse page selection token: '{part}'")

    # Preserve specified order but remove duplicates
    seen: set[int] = set()
    result: list[int] = []
    for idx in indices:
        if idx not in seen:
            seen.add(idx)
            result.append(idx)
    return result
