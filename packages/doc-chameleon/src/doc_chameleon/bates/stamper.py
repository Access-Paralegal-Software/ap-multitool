"""
doc_chameleon.bates.stamper
Vector Bates stamping engine for discovery productions.
Supports 6-position canvas grid, confidentiality suffix slugs, and zero DPI loss.
Maintained strictly by Alan Woodyard.
"""

from __future__ import annotations
import io
from pathlib import Path
from typing import List, Dict, Any, Tuple, Union, Optional
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

class BatesStampConfig:
    def __init__(
        self,
        prefix: str = "ABC_",
        start: int = 1,
        digits: int = 8,
        suffix: str = "",
        position: str = "bottom_right",
        font_name: str = "Helvetica",
        font_size: float = 9.0,
        margin_x: float = 36.0,
        margin_y: float = 24.0,
    ):
        self.prefix = prefix
        self.start = start
        self.digits = digits
        self.suffix = suffix
        self.position = position.lower().strip()
        self.font_name = font_name
        self.font_size = font_size
        self.margin_x = margin_x
        self.margin_y = margin_y

    def format_bates(self, offset: int = 0) -> str:
        seq = self.start + offset
        num_part = f"{seq:0{self.digits}d}"
        return f"{self.prefix}{num_part}{self.suffix}"

def format_bates(seq: int, cfg: BatesStampConfig) -> str:
    num_part = f"{seq:0{cfg.digits}d}"
    suf = f" {cfg.suffix.strip()}" if cfg.suffix.strip() else ""
    return f"{cfg.prefix}{num_part}{suf}"

def create_bates_overlay(
    bates_text: str,
    width: float,
    height: float,
    cfg: BatesStampConfig
) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(width, height))
    c.setFont(cfg.font_name, cfg.font_size)
    c.setFillColor(colors.HexColor("#222222"))

    pos = cfg.position
    mx = cfg.margin_x
    my = cfg.margin_y

    # Calculate 6-position grid coordinates
    if pos == "top_left":
        c.drawString(mx, height - my, bates_text)
    elif pos == "top_center":
        c.drawCentredString(width / 2.0, height - my, bates_text)
    elif pos == "top_right":
        c.drawRightString(width - mx, height - my, bates_text)
    elif pos == "bottom_left":
        c.drawString(mx, my, bates_text)
    elif pos == "bottom_center":
        c.drawCentredString(width / 2.0, my, bates_text)
    else:  # "bottom_right" default
        c.drawRightString(width - mx, my, bates_text)

    c.save()
    buf.seek(0)
    return buf.getvalue()

def stamp_pdf_bytes(
    pdf_bytes: bytes,
    cfg: BatesStampConfig
) -> Tuple[bytes, List[Dict[str, Any]]]:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    manifest: List[Dict[str, Any]] = []

    cur_seq = cfg.start
    for idx, page in enumerate(reader.pages):
        w = float(page.mediabox.width)
        h = float(page.mediabox.height)
        bates_id = format_bates(cur_seq, cfg)

        overlay_bytes = create_bates_overlay(bates_id, w, h, cfg)
        overlay_reader = PdfReader(io.BytesIO(overlay_bytes))
        page.merge_page(overlay_reader.pages[0])
        writer.add_page(page)

        manifest.append({
            "page_index": idx,
            "page_num": idx + 1,
            "bates_id": bates_id,
            "sequence": cur_seq,
        })
        cur_seq += 1

    out_buf = io.BytesIO()
    writer.write(out_buf)
    out_buf.seek(0)
    return out_buf.getvalue(), manifest

# Backward compatibility alias
BatesConfiguration = BatesStampConfig



# --- Backward-Compatibility Aliases & File Helpers ---
BatesConfiguration = BatesStampConfig
create_bates_overlay_pdf = create_bates_overlay

def stamp_pdf_file(
    src_path: Union[str, Path],
    dst_path: Union[str, Path],
    cfg: BatesStampConfig
) -> Tuple[Path, List[Dict[str, Any]]]:
    src = Path(src_path)
    dst = Path(dst_path)
    raw_bytes = src.read_bytes()
    stamped_bytes, manifest = stamp_pdf_bytes(raw_bytes, cfg)
    dst.write_bytes(stamped_bytes)
    return dst, manifest

