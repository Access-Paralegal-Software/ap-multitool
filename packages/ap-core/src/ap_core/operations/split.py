"""
core/operations/split.py — PDF split operation.

Splits a PDF into multiple output files by page range, fixed chunk size,
or blank-page detection. All outputs are new files; the source is never modified.

Dependencies: pikepdf
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

import pikepdf

from ap_core.job import Job, JobResult, SplitParams


def handle(job: Job, progress: Callable[[str, float], None]) -> JobResult:
    if not job.inputs:
        raise ValueError("Split requires exactly one input PDF.")

    spec = job.inputs[0]
    params: SplitParams = job.params
    warnings: list[str] = []

    progress("Opening source PDF …", 0.0)
    with pikepdf.open(spec.path) as src:
        total_pages = len(src.pages)
        chunks = _compute_chunks(params, total_pages, warnings)
        outputs: list[Path] = []

        for n, (start, end) in enumerate(chunks, start=1):
            fraction = n / len(chunks)
            label = f"Writing part {n}/{len(chunks)} (pages {start+1}–{end}) …"
            progress(label, fraction * 0.9)

            name = _render_name(params.name_template, spec.path.stem, n)
            out_path = job.output.directory / name
            if not out_path.suffix:
                out_path = out_path.with_suffix(".pdf")

            out_pdf = pikepdf.Pdf.new()
            for page_idx in range(start, end):
                out_pdf.pages.append(src.pages[page_idx])
            out_pdf.save(out_path)
            out_pdf.close()
            outputs.append(out_path)

    progress("Done.", 1.0)
    return JobResult(
        outputs=outputs,
        page_count_in=total_pages,
        page_count_out=total_pages,
        warnings=warnings,
    )


def _compute_chunks(
    params: SplitParams,
    total_pages: int,
    warnings: list[str],
) -> list[tuple[int, int]]:
    """Return list of (start_0based, end_exclusive) page index pairs."""

    if params.mode == "ranges":
        if not params.ranges:
            raise ValueError("SplitParams.mode='ranges' requires at least one range string.")
        return [_parse_range(r, total_pages) for r in params.ranges]

    elif params.mode == "fixed":
        n = params.pages_per_chunk
        if not n or n < 1:
            raise ValueError("SplitParams.pages_per_chunk must be >= 1 for mode='fixed'.")
        chunks = []
        for start in range(0, total_pages, n):
            chunks.append((start, min(start + n, total_pages)))
        return chunks

    elif params.mode == "blank_page":
        # Stub: blank-page detection requires image rendering (future)
        warnings.append(
            "blank_page split mode is not yet implemented. "
            "Falling back to single output containing all pages."
        )
        return [(0, total_pages)]

    else:
        raise ValueError(f"Unknown split mode: '{params.mode}'")


def _parse_range(spec_str: str, total_pages: int) -> tuple[int, int]:
    """Parse "3-7" into (2, 7) zero-based inclusive/exclusive."""
    spec_str = spec_str.strip()
    m = re.fullmatch(r"(\d+)\s*[-–]\s*(\d+)", spec_str)
    if m:
        start = int(m.group(1)) - 1
        end = int(m.group(2))
    elif spec_str.isdigit():
        start = int(spec_str) - 1
        end = int(spec_str)
    else:
        raise ValueError(f"Cannot parse page range: '{spec_str}'")

    if start < 0 or end > total_pages or start >= end:
        raise ValueError(
            f"Range '{spec_str}' is out of bounds for a {total_pages}-page document."
        )
    return (start, end)


def _render_name(template: str, source_stem: str, n: int) -> str:
    try:
        return template.format(source=source_stem, n=n)
    except (KeyError, ValueError):
        return f"{source_stem}_part{n:03d}"
