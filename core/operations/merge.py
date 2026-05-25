"""core/operations/merge.py — PDF merge operation.

Combines an ordered list of input files into a single output PDF.
Non-PDF inputs (images, text, Word, Excel, email) are converted to PDF in a
temporary staging area before merging. Conversion delegates to core operations
where available so that job logging and error handling remain consistent.
"""

from __future__ import annotations

import os
import tempfile
from datetime import date
from io import BytesIO
from pathlib import Path
from typing import Callable

import pikepdf

from core.job import Job, JobResult, MergeParams

_NOOP: Callable[[str, float], None] = lambda msg, val: None  # noqa: E731


def handle(job: Job, progress: Callable[[str, float], None]) -> JobResult:
    params: MergeParams = job.params
    inputs = sorted(job.inputs, key=lambda s: s.order_index)
    total = len(inputs)
    page_count_in = 0
    warnings: list[str] = []
    temp_pdfs: list[Path] = []

    # --- Stage 1: Convert all inputs to PDF ---
    pdf_paths: list[tuple[Path, str]] = []
    for i, spec in enumerate(inputs):
        progress(f"Converting {spec.path.name} …", i / (total * 2))
        try:
            if spec.kind == "pdf":
                pdf_paths.append((spec.path, spec.label or spec.path.stem))
            else:
                tmp = _convert_to_pdf(spec, params, warnings)
                temp_pdfs.append(tmp)
                pdf_paths.append((tmp, spec.label or spec.path.stem))
        except Exception as exc:
            warnings.append(f"Skipped {spec.path.name}: {exc}")

    # --- Stage 2: Merge with pikepdf ---
    output_name = params.output_name or _default_name(inputs[0].path if inputs else Path("output"))
    out_path = job.output.directory / output_name
    if not out_path.suffix:
        out_path = out_path.with_suffix(".pdf")

    progress("Merging pages …", 0.6)
    merger = pikepdf.Pdf.new()
    outline_items: list[pikepdf.OutlineItem] = []

    for idx, (pdf_path, bookmark_label) in enumerate(pdf_paths):
        try:
            with pikepdf.open(pdf_path) as src:
                page_start = len(merger.pages)
                for page in src.pages:
                    merger.pages.append(page)
                    page_count_in += 1
                if params.bookmarks:
                    outline_items.append(pikepdf.OutlineItem(bookmark_label, page_start))
        except Exception as exc:
            warnings.append(f"Could not merge {pdf_path.name}: {exc}")

    if outline_items:
        with merger.open_outline() as outline:
            for item in outline_items:
                outline.root.append(item)

    progress("Writing output …", 0.9)
    merger.save(out_path)
    merger.close()

    for tmp in temp_pdfs:
        try:
            tmp.unlink()
        except Exception:
            pass

    progress("Done.", 1.0)
    return JobResult(
        outputs=[out_path],
        page_count_in=page_count_in,
        page_count_out=page_count_in,
        warnings=warnings,
    )


def _default_name(first_input: Path) -> str:
    return f"{first_input.stem}_merged_{date.today():%Y-%m-%d}.pdf"


def _convert_to_pdf(spec, params: MergeParams, warnings: list[str]) -> Path:
    """Convert a non-PDF input to a temporary PDF. Returns the temp file path."""
    fd, tmp_str = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)  # release descriptor so downstream writers can replace the file
    tmp = Path(tmp_str)

    if spec.kind == "image":
        _image_to_pdf(spec.path, tmp, grayscale=params.grayscale)
    elif spec.kind == "text":
        _text_to_pdf(spec.path, tmp)
    elif spec.kind in ("eml", "msg"):
        _email_to_pdf(spec, tmp, params)
    elif spec.kind == "docx":
        _word_to_pdf(spec.path, tmp, warnings)
    elif spec.kind == "xlsx":
        _excel_to_pdf(spec.path, tmp, warnings)
    else:
        raise ValueError(f"Unsupported input kind: {spec.kind!r}")

    return tmp


def _image_to_pdf(src: Path, dest: Path, grayscale: bool = False) -> None:
    from PIL import Image
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas as rl_canvas

    img = Image.open(src)
    if grayscale:
        img = img.convert("L")
    img = img.convert("RGB")

    pw, ph = letter
    iw, ih = img.size
    scale = min(pw / iw, ph / ih)
    nw, nh = iw * scale, ih * scale
    x, y = (pw - nw) / 2, (ph - nh) / 2

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    c = rl_canvas.Canvas(str(dest), pagesize=letter)
    c.drawImage(ImageReader(buf), x, y, nw, nh)
    c.save()


def _text_to_pdf(src: Path, dest: Path) -> None:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

    text = src.read_text(encoding="utf-8", errors="replace")
    doc = SimpleDocTemplate(str(dest), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    for line in text.splitlines():
        story.append(Paragraph(line or "&nbsp;", styles["Normal"]))
        story.append(Spacer(1, 2))
    doc.build(story)


def _email_to_pdf(spec, dest: Path, params: MergeParams) -> None:
    import shutil
    from core import email_processing
    result_path = email_processing.process_email(
        Path(spec.path),
        dest.parent,
        keep_inline=True,
        grayscale=params.grayscale,
    )
    if result_path.exists() and result_path != dest:
        shutil.move(str(result_path), str(dest))


def _word_to_pdf(src: Path, dest: Path, warnings: list[str]) -> None:
    from core.operations.docx_to_pdf import handle as docx_handle
    from core.job import InputSpec, DocxToPdfParams, OutputSpec

    job = Job(
        operation="docx_to_pdf",
        inputs=[InputSpec(path=src, kind="docx", order_index=0)],
        params=DocxToPdfParams(output_name=dest.name),
        output=OutputSpec(directory=dest.parent, overwrite=True),
    )
    res = docx_handle(job, _NOOP)
    if res.error:
        raise RuntimeError(res.error)
    warnings.extend(res.warnings)


def _excel_to_pdf(src: Path, dest: Path, warnings: list[str]) -> None:
    from core.operations.xlsx_to_pdf import handle as xlsx_handle
    from core.job import InputSpec, XlsxToPdfParams, OutputSpec

    job = Job(
        operation="xlsx_to_pdf",
        inputs=[InputSpec(path=src, kind="xlsx", order_index=0)],
        params=XlsxToPdfParams(output_name=dest.name),
        output=OutputSpec(directory=dest.parent, overwrite=True),
    )
    res = xlsx_handle(job, _NOOP)
    if res.error:
        raise RuntimeError(res.error)
    warnings.extend(res.warnings)
