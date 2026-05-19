"""
core/operations/merge.py — PDF merge operation.

Combines an ordered list of input files into a single output PDF.
Inputs may be PDF, image, Word, or email — format adapters are applied
per file before merging.

Dependencies: pikepdf (merge/bookmarks), Pillow (images), reportlab (text).
"""

from __future__ import annotations

import tempfile
from datetime import date
from pathlib import Path
from typing import Callable

import pikepdf

from core.job import Job, JobResult, MergeParams


def handle(job: Job, progress: Callable[[str, float], None]) -> JobResult:
    params: MergeParams = job.params
    inputs = sorted(job.inputs, key=lambda s: s.order_index)
    total = len(inputs)
    page_count_in = 0
    warnings: list[str] = []
    temp_pdfs: list[Path] = []

    # --- Stage 1: Convert all inputs to PDF ---
    pdf_paths: list[tuple[Path, str]] = []  # (path, label)
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

    for label, (pdf_path, bookmark_label) in enumerate(pdf_paths):
        try:
            with pikepdf.open(pdf_path) as src:
                page_start = len(merger.pages)
                for page in src.pages:
                    merger.pages.append(page)
                    page_count_in += 1
                if params.bookmarks:
                    item = pikepdf.OutlineItem(bookmark_label, page_start)
                    outline_items.append(item)
        except Exception as exc:
            warnings.append(f"Could not merge {pdf_path.name}: {exc}")

    if outline_items:
        with merger.open_outline() as outline:
            for item in outline_items:
                outline.root.append(item)

    progress("Writing output …", 0.9)
    save_kwargs: dict = {}
    if params.enforce_page_size:
        pass  # Page normalization is a future enhancement; pikepdf doesn't resize natively
    merger.save(out_path)
    merger.close()

    # --- Cleanup temp files ---
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
    """Convert a non-PDF input to a temporary PDF file."""
    tmp = Path(tempfile.mktemp(suffix=".pdf"))

    if spec.kind == "image":
        _image_to_pdf(spec.path, tmp, grayscale=params.grayscale)
    elif spec.kind == "text":
        _text_to_pdf(spec.path, tmp)
    elif spec.kind in ("eml", "msg"):
        _email_to_pdf(spec, tmp, params)
    elif spec.kind == "docx":
        _word_to_pdf(spec.path, tmp, warnings)
    else:
        raise ValueError(f"Unsupported input kind: {spec.kind}")

    return tmp


def _image_to_pdf(src: Path, dest: Path, grayscale: bool = False) -> None:
    from PIL import Image
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas as rl_canvas

    img = Image.open(src)
    if grayscale:
        img = img.convert("L")
    img = img.convert("RGB")
    pw, ph = letter
    iw, ih = img.size
    scale = min(pw / iw, ph / ih)
    nw, nh = iw * scale, ih * scale
    c = rl_canvas.Canvas(str(dest), pagesize=letter)
    x, y = (pw - nw) / 2, (ph - nh) / 2
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
        tmp_img = tf.name
    img.save(tmp_img)
    c.drawImage(tmp_img, x, y, nw, nh)
    c.save()
    os.unlink(tmp_img)


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
    import email_processing
    import shutil
    temp_dir = dest.parent
    result_path = email_processing.process_email(
        Path(spec.path),
        temp_dir,
        keep_inline=True,
        grayscale=params.grayscale,
    )
    if result_path.exists() and result_path != dest:
        shutil.move(str(result_path), str(dest))



def _word_to_pdf(src: Path, dest: Path, warnings: list[str]) -> None:
    try:
        import subprocess
        result = subprocess.run(
            ["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(dest.parent), str(src)],
            capture_output=True, timeout=60,
        )
        converted = dest.parent / (src.stem + ".pdf")
        if converted.exists() and converted != dest:
            converted.rename(dest)
    except Exception as exc:
        warnings.append(f"Word conversion failed for {src.name} ({exc}). File skipped.")
        raise
