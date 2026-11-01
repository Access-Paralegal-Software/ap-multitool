"""
doc_chameleon.rules.ca.pdf_stamper
Vector-based California Rule of Court 2.108/2.111 PDF pleading paper overlay.
Injects mathematically exact 28-line left rail, configurable margin rails,
and Page 1 clerk space reservation onto arbitrary PDFs without rasterization.
Maintained strictly by Alan Woodyard.
"""

from __future__ import annotations
import io
from pathlib import Path
from typing import Union, Optional
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

from doc_chameleon.rules.ca.transformer_2111 import (
    TOTAL_LINES,
    calculate_baseline_y,
)

def create_pleading_page_overlay(
    page_num: int,
    width: float = 612.0,
    height: float = 792.0,
    rail_style: str = "none",
    include_clerk_box: bool = True,
) -> bytes:
    """Generates an in-memory single-page PDF containing the 28-line vector overlay."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(width, height))

    # 1. 28-Line Left Margin Numbers (1 to 28)
    c.setFont("Times-Roman", 10)
    c.setFillColor(colors.HexColor("#666666"))
    num_x = 54.0  # 0.75 in from left edge

    for line_no in range(1, TOTAL_LINES + 1):
        y = calculate_baseline_y(line_no)
        c.drawRightString(num_x, y, str(line_no))

    # 2. Configurable Margin Divider Rails
    rail = (rail_style or "none").lower().strip()
    rail_x = 68.0
    c.setStrokeColor(colors.HexColor("#888888"))
    c.setLineWidth(0.75)
    y_bottom = calculate_baseline_y(TOTAL_LINES) - 4
    y_top = calculate_baseline_y(1) + 12

    if rail in ("single", "single_rail"):
        c.line(rail_x, y_bottom, rail_x, y_top)
    elif rail in ("double", "double_rail"):
        c.line(rail_x - 3.0, y_bottom, rail_x - 3.0, y_top)
        c.line(rail_x, y_bottom, rail_x, y_top)

    # 3. Page 1 Clerk Space Reservation
    if page_num == 1 and include_clerk_box:
        c.setFont("Times-Roman", 9)
        c.setFillColor(colors.HexColor("#777777"))
        c.drawString(360.0, calculate_baseline_y(1), "FOR COURT USE ONLY")

    c.save()
    buf.seek(0)
    return buf.getvalue()

def stamp_ca_pleading_pdf_bytes(
    pdf_bytes: bytes,
    rail_style: str = "none",
    include_clerk_box: bool = True,
) -> bytes:
    """Merges the CRC 2.111 pleading overlay into an in-memory PDF without DPI loss."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()

    for idx, page in enumerate(reader.pages):
        w = float(page.mediabox.width)
        h = float(page.mediabox.height)
        overlay_bytes = create_pleading_page_overlay(
            page_num=idx + 1,
            width=w,
            height=h,
            rail_style=rail_style,
            include_clerk_box=include_clerk_box,
        )
        overlay_reader = PdfReader(io.BytesIO(overlay_bytes))
        page.merge_page(overlay_reader.pages[0])
        writer.add_page(page)

    out_buf = io.BytesIO()
    writer.write(out_buf)
    out_buf.seek(0)
    return out_buf.getvalue()

def stamp_ca_pleading_pdf(
    src_path: Union[str, Path],
    dst_path: Union[str, Path],
    rail_style: str = "none",
    include_clerk_box: bool = True,
) -> Path:
    """Stamps an on-disk PDF with CRC 2.111 pleading geometry."""
    src = Path(src_path)
    dst = Path(dst_path)
    data = src.read_bytes()
    stamped = stamp_ca_pleading_pdf_bytes(
        data,
        rail_style=rail_style,
        include_clerk_box=include_clerk_box,
    )
    dst.write_bytes(stamped)
    return dst
