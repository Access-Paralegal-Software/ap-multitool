#!/usr/bin/env python3
"""
eml_to_pdf.py - Convert a folder of .eml files to merged PDFs.

Each output PDF contains the email body followed by all attachments.
Supported attachment types: images (jpg/jpeg/png/gif/bmp/tiff/webp),
plain text, CSV, HTML, PDF, DOCX. Unsupported types get a placeholder page.

Usage:
    python eml_to_pdf.py <input_folder> [output_folder]

If output_folder is omitted, a 'pdf_output' subfolder is created inside input_folder.
"""

import sys
import os
import re
import email
import email.policy
import subprocess
import tempfile
from io import BytesIO
from pathlib import Path

# ---------------------------------------------------------------------------
# Dependency bootstrap
# ---------------------------------------------------------------------------

def ensure_deps():
    pkg_map = {
        "reportlab": "reportlab",
        "Pillow": "PIL",
        "pypdf": "pypdf",
        "python-docx": "docx",
        "html2text": "html2text",
    }
    missing = [pkg for pkg, mod in pkg_map.items() if not _can_import(mod)]
    if missing:
        print(f"Installing: {', '.join(missing)} ...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install"] + missing,
            stdout=subprocess.DEVNULL,
        )
        print("Done installing.\n")

def _can_import(name):
    try:
        __import__(name)
        return True
    except ImportError:
        return False

ensure_deps()

# ---------------------------------------------------------------------------
# Imports (after deps are guaranteed)
# ---------------------------------------------------------------------------

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    HRFlowable, Image as RLImage,
)
from PIL import Image
import pypdf
import html2text as h2t

PAGE_W, PAGE_H = letter
MARGIN = inch

# ---------------------------------------------------------------------------
# XML/text helpers
# ---------------------------------------------------------------------------

def xml_escape(text: str) -> str:
    """Escape characters that would break ReportLab's XML parser."""
    if not text:
        return ""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    text = text.replace("'", "&#39;")
    # Strip ASCII control chars (except tab/newline)
    text = "".join(c if (ord(c) >= 32 or c in "\t\n") else " " for c in text)
    return text

def html_to_text(html: str) -> str:
    handler = h2t.HTML2Text()
    handler.ignore_links = False
    handler.ignore_images = True
    handler.body_width = 0
    return handler.handle(html)

# ---------------------------------------------------------------------------
# Shared ReportLab styles
# ---------------------------------------------------------------------------

_styles = getSampleStyleSheet()

def _style(name, **kwargs):
    return ParagraphStyle(name, parent=_styles["Normal"], **kwargs)

SUBJ_STYLE  = _style("Subject",  fontName="Helvetica-Bold",  fontSize=14, leading=20, spaceAfter=10)
HDR_STYLE   = _style("Header",   fontName="Helvetica-Bold",  fontSize=9,  leading=13, spaceAfter=2)
VAL_STYLE   = _style("Value",    fontName="Helvetica",       fontSize=9,  leading=13, spaceAfter=2, wordWrap="CJK")
BODY_STYLE  = _style("Body",     fontName="Helvetica",       fontSize=10, leading=14, spaceAfter=4, wordWrap="CJK")
LABEL_STYLE = _style("Label",    fontName="Helvetica-Bold",  fontSize=11, spaceAfter=8)
MONO_STYLE  = _style("Mono",     fontName="Courier",         fontSize=9,  leading=13, wordWrap="CJK")
TITLE_STYLE = _style("ATitle",   fontName="Helvetica-Bold",  fontSize=13, leading=18, spaceAfter=10)
H1_STYLE    = _style("H1",       fontName="Helvetica-Bold",  fontSize=13, leading=18, spaceAfter=6)
H2_STYLE    = _style("H2",       fontName="Helvetica-Bold",  fontSize=11, leading=15, spaceAfter=4)
NOTE_STYLE  = _style("Note",     fontName="Helvetica-Oblique", fontSize=10, leading=14, textColor=colors.grey)

def _new_doc(path):
    return SimpleDocTemplate(
        str(path),
        pagesize=letter,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN,  bottomMargin=MARGIN,
    )

# ---------------------------------------------------------------------------
# Email body → PDF  (with inline image support)
# ---------------------------------------------------------------------------

_IMG_PLACEHOLDER = "CIDIMAGE{n}CIDIMAGE"

def _build_cid_map(msg) -> dict:
    """Return {content-id: bytes} for all CID-referenced parts."""
    cid_map = {}
    for part in msg.walk():
        cid = part.get("Content-ID", "").strip()
        if not cid:
            continue
        data = part.get_payload(decode=True)
        if data:
            cid_map[cid.strip("<> ")] = data
            cid_map[cid] = data
    return cid_map

def _body_flowables(msg) -> list:
    """Return ReportLab flowables for the email body, inline images rendered in place."""
    cid_map = _build_cid_map(msg)
    html_body = text_body = None

    for part in msg.walk():
        ct  = part.get_content_type()
        cd  = str(part.get("Content-Disposition", ""))
        if "attachment" in cd:
            continue
        charset = part.get_content_charset() or "utf-8"
        try:
            payload = part.get_payload(decode=True)
            if payload is None:
                continue
            decoded = payload.decode(charset, errors="replace")
        except Exception:
            continue
        if ct == "text/html" and html_body is None:
            html_body = decoded
        elif ct == "text/plain" and text_body is None:
            text_body = decoded

    # Replace <img src="cid:..."> with unique text placeholders before html2text
    inline_images = {}   # placeholder-string -> bytes
    if html_body and cid_map:
        def _replace_cid_img(m):
            src = (re.search(r'src=["\']([^"\']*)["\']', m.group(0), re.IGNORECASE) or
                   re.search(r'src=([^\s\>]+)', m.group(0), re.IGNORECASE))
            if not src:
                return ""
            val = src.group(1)
            if not val.lower().startswith("cid:"):
                return ""
            cid = val[4:].strip()
            data = cid_map.get(cid) or cid_map.get(f"<{cid}>")
            if not data:
                return ""
            n = len(inline_images)
            placeholder = _IMG_PLACEHOLDER.format(n=n)
            inline_images[placeholder] = data
            return f"\n{placeholder}\n"

        html_body = re.sub(r'<img[^>]*>', _replace_cid_img, html_body, flags=re.IGNORECASE)

    # Now run html2text — it strips CSS/scripts/tags and gives clean text
    if html_body:
        body_text = html_to_text(html_body)
    else:
        body_text = text_body or "(No body)"

    # Build flowables, swapping placeholders for actual images.
    flowables = []
    max_img_w = PAGE_W - 2 * MARGIN
    max_img_h = PAGE_H * 0.45
    placeholder_re = re.compile(r'(CIDIMAGE\d+CIDIMAGE)')

    def _emit_image(ph):
        data = inline_images.get(ph)
        if not data:
            return
        try:
            img = Image.open(BytesIO(data))
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")
            iw, ih = img.size
            scale = min(max_img_w / iw, max_img_h / ih, 1.0)
            buf = BytesIO()
            img.save(buf, format="JPEG", quality=85)
            buf.seek(0)
            flowables.append(RLImage(buf, width=iw * scale, height=ih * scale))
            flowables.append(Spacer(1, 0.08 * inch))
        except Exception:
            pass

    for line in body_text.splitlines():
        stripped = line.strip()
        if not stripped:
            flowables.append(Spacer(1, 0.04 * inch))
            continue
        segments = placeholder_re.split(stripped)
        if len(segments) == 1:
            flowables.append(Paragraph(xml_escape(stripped), BODY_STYLE))
        else:
            for seg in segments:
                if placeholder_re.fullmatch(seg):
                    _emit_image(seg)
                elif seg.strip():
                    flowables.append(Paragraph(xml_escape(seg.strip()), BODY_STYLE))
    return flowables

def email_to_pdf(msg, out_path: Path):
    doc = _new_doc(out_path)
    story = []
    subject = msg.get("Subject", "(No Subject)")
    story.append(Paragraph(xml_escape(subject), SUBJ_STYLE))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.grey, spaceAfter=6))
    for hdr in ("From", "To", "CC", "BCC", "Date"):
        val = msg.get(hdr, "")
        if val:
            story.append(Paragraph(f"<b>{hdr}:</b>  {xml_escape(val)}", VAL_STYLE))
    story.append(Spacer(1, 0.2 * inch))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey, spaceAfter=8))
    story.extend(_body_flowables(msg))
    doc.build(story)

# ---------------------------------------------------------------------------
# Attachment converters
# ---------------------------------------------------------------------------

def image_to_pdf(data: bytes, filename: str, out_path: Path) -> bool:
    try:
        img = Image.open(BytesIO(data))
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")
        iw, ih = img.size
        max_w = PAGE_W - 2 * MARGIN
        max_h = PAGE_H - 2 * MARGIN - 0.6 * inch
        scale = min(max_w / iw, max_h / ih, 1.0)
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=85)
        buf.seek(0)
        doc = _new_doc(out_path)
        story = [
            Paragraph(xml_escape(filename), LABEL_STYLE),
            Spacer(1, 0.1 * inch),
            RLImage(buf, width=iw * scale, height=ih * scale),
        ]
        doc.build(story)
        return True
    except Exception as e:
        print(f"    [warn] image '{filename}': {e}")
        return False

def text_to_pdf(data: bytes, filename: str, out_path: Path) -> bool:
    try:
        text = data.decode("utf-8", errors="replace") if isinstance(data, bytes) else data
        doc = _new_doc(out_path)
        story = [Paragraph(xml_escape(filename), LABEL_STYLE)]
        for line in text.splitlines():
            if line.strip():
                story.append(Paragraph(xml_escape(line), MONO_STYLE))
            else:
                story.append(Spacer(1, 0.04 * inch))
        doc.build(story)
        return True
    except Exception as e:
        print(f"    [warn] text '{filename}': {e}")
        return False

def html_att_to_pdf(data: bytes, filename: str, out_path: Path) -> bool:
    try:
        html = data.decode("utf-8", errors="replace")
        plain = html_to_text(html)
        return text_to_pdf(plain.encode(), filename, out_path)
    except Exception as e:
        print(f"    [warn] html '{filename}': {e}")
        return False

def docx_to_pdf(data: bytes, filename: str, out_path: Path) -> bool:
    try:
        import docx as _docx
        doc_in = _docx.Document(BytesIO(data))
        doc_out = _new_doc(out_path)
        story = [
            Paragraph(xml_escape(filename), LABEL_STYLE),
            HRFlowable(width="100%", thickness=0.5, color=colors.grey, spaceAfter=6),
        ]
        for para in doc_in.paragraphs:
            text = para.text
            if not text.strip():
                story.append(Spacer(1, 0.08 * inch))
                continue
            sname = para.style.name or ""
            if "Heading 1" in sname:
                st = H1_STYLE
            elif "Heading 2" in sname:
                st = H2_STYLE
            else:
                st = BODY_STYLE
            story.append(Paragraph(xml_escape(text), st))
        doc_out.build(story)
        return True
    except Exception as e:
        print(f"    [warn] docx '{filename}': {e}")
        return False

def placeholder_to_pdf(filename: str, out_path: Path) -> bool:
    try:
        ext = Path(filename).suffix.lstrip(".").upper() or "unknown"
        doc = _new_doc(out_path)
        story = [
            Paragraph(xml_escape(f"Attachment: {filename}"), TITLE_STYLE),
            Spacer(1, 0.2 * inch),
            Paragraph(
                xml_escape(f"[{ext} file — cannot render inline]"),
                NOTE_STYLE,
            ),
        ]
        doc.build(story)
        return True
    except Exception:
        return False

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp"}
TEXT_EXTS  = {".txt", ".csv", ".log", ".md", ".json", ".xml", ".py",
              ".js", ".ts", ".css", ".yaml", ".yml", ".ini", ".cfg"}
HTML_EXTS  = {".html", ".htm"}

CT_EXT_MAP = {
    "image/jpeg": ".jpg", "image/jpg": ".jpg", "image/png": ".png",
    "image/gif": ".gif",  "image/bmp": ".bmp", "image/tiff": ".tiff",
    "image/webp": ".webp","application/pdf": ".pdf",
    "text/plain": ".txt", "text/html": ".html",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}

def attachment_to_pdf(data: bytes, filename: str, out_path: Path, ct: str = "") -> bool:
    ext = Path(filename).suffix.lower()
    # If extension is missing/unrecognised, fall back to content-type
    if not ext and ct:
        ext = CT_EXT_MAP.get(ct.split(";")[0].strip().lower(), "")
    # content-type always wins for images (catches inline images with no/wrong ext)
    if ct.startswith("image/"):
        return image_to_pdf(data, filename, out_path)
    if ext in IMAGE_EXTS:
        return image_to_pdf(data, filename, out_path)
    if ext in TEXT_EXTS:
        return text_to_pdf(data, filename, out_path)
    if ext in HTML_EXTS:
        return html_att_to_pdf(data, filename, out_path)
    if ext == ".pdf" or ct == "application/pdf":
        out_path.write_bytes(data)
        return True
    if ext == ".docx":
        return docx_to_pdf(data, filename, out_path)
    return placeholder_to_pdf(filename, out_path)

# ---------------------------------------------------------------------------
# Attachment extraction
# ---------------------------------------------------------------------------

def _decode_filename(raw: str) -> str:
    from email.header import decode_header
    parts = decode_header(raw)
    result = []
    for chunk, enc in parts:
        if isinstance(chunk, bytes):
            result.append(chunk.decode(enc or "utf-8", errors="replace"))
        else:
            result.append(chunk)
    return "".join(result)

def get_attachments(msg):
    """Yield (filename, data, content_type) for true attachments only.
    CID-referenced inline parts are excluded — they render inside the body.
    """
    for i, part in enumerate(msg.walk()):
        cd   = str(part.get("Content-Disposition", ""))
        ct   = part.get_content_type()
        name = part.get_filename()
        # Skip multipart containers and the email body parts
        if ct.startswith("multipart/"):
            continue
        if ct in ("text/plain", "text/html") and "attachment" not in cd:
            continue
        # Skip CID-referenced parts — they are inline and handled in the body
        if part.get("Content-ID") and "attachment" not in cd:
            continue
        # Must be explicitly attached or have a filename to count as an attachment
        if "attachment" not in cd and not name:
            continue
        filename = _decode_filename(name) if name else (
            f"attachment_{i}" + CT_EXT_MAP.get(ct.split(";")[0].strip().lower(), ".bin")
        )
        data = part.get_payload(decode=True)
        if not data:
            continue
        yield filename, data, ct

# ---------------------------------------------------------------------------
# Main processing pipeline
# ---------------------------------------------------------------------------

def process_eml(eml_path: Path, output_dir: Path) -> Path:
    with open(eml_path, "rb") as f:
        msg = email.message_from_binary_file(f, policy=email.policy.compat32)
    out_path = output_dir / (eml_path.stem + ".pdf")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        parts: list[Path] = []
        # 1. Email body
        body_pdf = tmp / "_body.pdf"
        email_to_pdf(msg, body_pdf)
        parts.append(body_pdf)
        # 2. Attachments
        for i, (filename, data, ct) in enumerate(get_attachments(msg)):
            att_pdf = tmp / f"_att_{i:03d}.pdf"
            ok = attachment_to_pdf(data, filename, att_pdf, ct)
            if ok and att_pdf.exists():
                parts.append(att_pdf)
                print(f"    + {filename}")
        # 3. Merge
        if len(parts) == 1:
            import shutil
            shutil.copy(parts[0], out_path)
        else:
            writer = pypdf.PdfWriter()
            for p in parts:
                try:
                    reader = pypdf.PdfReader(str(p))
                    for page in reader.pages:
                        writer.add_page(page)
                except Exception as e:
                    print(f"    [warn] merge {p.name}: {e}")
            with open(out_path, "wb") as f:
                writer.write(f)
    return out_path

# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    input_dir  = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else input_dir / "pdf_output"
    if not input_dir.is_dir():
        print(f"Error: '{input_dir}' is not a directory.")
        sys.exit(1)
    output_dir.mkdir(parents=True, exist_ok=True)
    eml_files = sorted(input_dir.glob("*.eml"))
    if not eml_files:
        print(f"No .eml files found in '{input_dir}'.")
        sys.exit(0)
    print(f"Found {len(eml_files)} .eml file(s)  →  {output_dir}\n")
    ok = fail = 0
    for eml in eml_files:
        print(f"  [{eml.name}]")
        try:
            out = process_eml(eml, output_dir)
            print(f"    → {out.name}\n")
            ok += 1
        except Exception as e:
            print(f"    FAILED: {e}\n")
            fail += 1
    print(f"Finished: {ok} succeeded, {fail} failed.")

if __name__ == "__main__":
    main()
