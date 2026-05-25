"""core/email_processing.py — Email parsing and PDF rendering utilities.

Converts .eml and Outlook .msg files — including inline images and attachments —
to PDF using ReportLab. All processing is offline.

Public surface:
  UnifiedEmail            — parsed representation of an email file
  email_to_pdf()          — render email body + metadata to a PDF
  get_email_attachments() — yield (filename, data, content_type) tuples
  attachment_to_pdf()     — convert a single attachment to PDF
  placeholder_to_pdf()    — render an un-renderable attachment as a labelled placeholder
  process_email()         — convenience: parse → render → merge into one output PDF
"""

from __future__ import annotations

import logging
import re
from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Image as RLImage,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)
from PIL import Image
import pypdf
import docx as _docx
import html2text as h2t

_log = logging.getLogger(__name__)

PAGE_W, PAGE_H = letter
MARGIN = inch
ACCESS_GREEN = colors.HexColor("#67BE5E")

# ---------------------------------------------------------------------------
# ReportLab styles
# ---------------------------------------------------------------------------
_styles = getSampleStyleSheet()


def _style(name: str, **kwargs) -> ParagraphStyle:
    return ParagraphStyle(name, parent=_styles["Normal"], **kwargs)


SUBJ_STYLE = _style("Subject", fontName="Helvetica-Bold", fontSize=14, leading=20, spaceAfter=10)
HDR_STYLE  = _style("Header",  fontName="Helvetica-Bold", fontSize=9,  leading=13, spaceAfter=2)
VAL_STYLE  = _style("Value",   fontName="Helvetica",      fontSize=9,  leading=13, spaceAfter=2, wordWrap="CJK")
BODY_STYLE = _style("Body",    fontName="Helvetica",      fontSize=10, leading=14, spaceAfter=4, wordWrap="CJK")
LABEL_STYLE = _style("Label",  fontName="Helvetica-Bold", fontSize=11, spaceAfter=8)
NOTE_STYLE  = _style("Note",   fontName="Helvetica-Oblique", fontSize=10, leading=14, textColor=colors.grey)


def _new_doc(path: Path) -> SimpleDocTemplate:
    return SimpleDocTemplate(
        str(path), pagesize=letter,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
    )


# ---------------------------------------------------------------------------
# Type classification maps
# ---------------------------------------------------------------------------

# Maps MIME type → file extension (used when a filename has no extension).
_CT_TO_EXT: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/bmp": ".bmp",
    "image/tiff": ".tiff",
    "image/webp": ".webp",
    "application/pdf": ".pdf",
    "text/plain": ".txt",
    "text/html": ".html",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}

# Maps file extension → kind string used by attachment_to_pdf dispatch.
_EXT_KIND: dict[str, str] = {
    ".jpg": "image",  ".jpeg": "image", ".png": "image", ".gif": "image",
    ".bmp": "image",  ".tiff": "image", ".tif": "image", ".webp": "image",
    ".txt": "text",   ".csv": "text",   ".log": "text",  ".md": "text",
    ".json": "text",  ".xml": "text",   ".py": "text",   ".js": "text",
    ".ts": "text",    ".css": "text",   ".yaml": "text", ".yml": "text",
    ".ini": "text",   ".cfg": "text",
    ".html": "html",  ".htm": "html",
    ".pdf": "pdf",
    ".docx": "docx",  ".doc": "docx",
    ".xlsx": "xlsx",  ".xls": "xlsx",
}

# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def xml_escape(text: str) -> str:
    if not text:
        return ""
    text = (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                .replace('"', "&quot;").replace("'", "&#39;"))
    return "".join(c if (ord(c) >= 32 or c in "\t\n") else " " for c in text)


def html_to_text(html: str) -> str:
    handler = h2t.HTML2Text()
    handler.ignore_links = False
    handler.ignore_images = True
    handler.body_width = 0
    return handler.handle(html)


# ---------------------------------------------------------------------------
# UnifiedEmail — normalised wrapper for .eml and .msg
# ---------------------------------------------------------------------------

class UnifiedEmail:
    """Parse an .eml or .msg file into a common structure."""

    def __init__(self, file_path: Path) -> None:
        self.file_path = Path(file_path)
        self.subject = "(No Subject)"
        self.sender = "Unknown Sender"
        self.to = "Unknown Recipient"
        self.cc = ""
        self.bcc = ""
        self.date = "Unknown Date"
        self.html_body: str | None = None
        self.text_body: str | None = None
        self.cid_map: dict[str, bytes] = {}
        self.attachments: list[tuple[str, bytes, str]] = []

        if self.file_path.suffix.lower() == ".msg":
            self._parse_msg()
        else:
            self._parse_eml()

    def _parse_msg(self) -> None:
        import extract_msg
        msg = extract_msg.Message(str(self.file_path))
        self.subject = msg.subject or "(No Subject)"
        self.sender  = msg.sender or "Unknown Sender"
        self.to      = msg.to or "Unknown Recipient"
        self.cc      = msg.cc or ""
        self.bcc     = msg.bcc or ""
        self.date    = msg.date or "Unknown Date"

        if msg.htmlBody:
            self.html_body = msg.htmlBody.decode("utf-8", errors="ignore")
        elif msg.body:
            self.text_body = msg.body

        for idx, att in enumerate(msg.attachments or []):
            cid = att.cid or getattr(att, "contentId", None)
            filename = att.longFilename or att.shortFilename or f"attachment_{idx}.bin"
            data = att.data
            ct = att.mimetype or "application/octet-stream"
            if cid:
                cid_str = str(cid).strip("<> ")
                self.cid_map[cid_str] = data
                self.cid_map[f"<{cid_str}>"] = data
            else:
                self.attachments.append((filename, data, ct))
        msg.close()

    def _parse_eml(self) -> None:
        import email
        import email.policy
        from email.parser import BytesParser

        with open(self.file_path, "rb") as f:
            msg = BytesParser(policy=email.policy.compat32).parse(f)

        self.subject = self._decode_header(msg.get("Subject", "(No Subject)"))
        self.sender  = self._decode_header(msg.get("From", "Unknown Sender"))
        self.to      = self._decode_header(msg.get("To", "Unknown Recipient"))
        self.cc      = self._decode_header(msg.get("CC", ""))
        self.bcc     = self._decode_header(msg.get("BCC", ""))
        self.date    = self._decode_header(msg.get("Date", "Unknown Date"))

        for part in msg.walk():
            ct = part.get_content_type()
            cd = str(part.get("Content-Disposition", ""))
            cid = part.get("Content-ID", "").strip()

            if cid:
                cid_str = cid.strip("<> ")
                payload = part.get_payload(decode=True)
                if payload:
                    self.cid_map[cid_str] = payload
                    self.cid_map[f"<{cid_str}>"] = payload

            if part.get_content_maintype() == "multipart":
                continue

            charset = part.get_content_charset() or "utf-8"
            payload = part.get_payload(decode=True)
            if payload is None:
                continue

            if "attachment" not in cd and not part.get_filename():
                decoded = payload.decode(charset, errors="replace")
                if ct == "text/html" and self.html_body is None:
                    self.html_body = decoded
                elif ct == "text/plain" and self.text_body is None:
                    self.text_body = decoded
            else:
                name = part.get_filename()
                filename = self._decode_header(name) if name else f"attachment_{len(self.attachments)}.bin"
                self.attachments.append((filename, payload, ct))

    def _decode_header(self, raw: str) -> str:
        if not raw:
            return ""
        from email.header import decode_header
        try:
            parts = decode_header(raw)
            return "".join(
                chunk.decode(enc or "utf-8", errors="replace") if isinstance(chunk, bytes) else chunk
                for chunk, enc in parts
            )
        except Exception:
            return str(raw)


# ---------------------------------------------------------------------------
# Body rendering
# ---------------------------------------------------------------------------

# Sentinel format: CIDIMAGE{n}CIDIMAGE — chosen to be unlikely in real body text
# and to survive html2text conversion intact.
_IMG_PLACEHOLDER = "CIDIMAGE{n}CIDIMAGE"
_PLACEHOLDER_RE = re.compile(r"(CIDIMAGE\d+CIDIMAGE)")


def _body_flowables(email_obj: UnifiedEmail, grayscale: bool = False) -> list:
    """Convert email body text to a list of ReportLab flowables."""
    html_body = email_obj.html_body
    text_body = email_obj.text_body
    cid_map = email_obj.cid_map
    inline_images: dict[str, bytes] = {}

    if html_body and cid_map:
        def _replace_cid(m: re.Match) -> str:
            src = (re.search(r'src=["\']([^"\']*)["\']', m.group(0), re.IGNORECASE) or
                   re.search(r'src=([^\s>]+)', m.group(0), re.IGNORECASE))
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

        html_body = re.sub(r"<img[^>]*>", _replace_cid, html_body, flags=re.IGNORECASE)

    body_text = html_to_text(html_body) if html_body else (text_body or "(No body)")
    max_img_w = PAGE_W - 2 * MARGIN
    max_img_h = PAGE_H * 0.45
    flowables: list = []

    def _append_image(placeholder: str) -> None:
        data = inline_images.get(placeholder)
        if not data:
            return
        try:
            img = Image.open(BytesIO(data))
            if grayscale:
                img = img.convert("L")
            elif img.mode in ("RGBA", "LA", "P"):
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
        segments = _PLACEHOLDER_RE.split(stripped)
        if len(segments) == 1:
            flowables.append(Paragraph(xml_escape(stripped), BODY_STYLE))
        else:
            for seg in segments:
                if _PLACEHOLDER_RE.fullmatch(seg):
                    _append_image(seg)
                elif seg.strip():
                    flowables.append(Paragraph(xml_escape(seg.strip()), BODY_STYLE))

    return flowables


# ---------------------------------------------------------------------------
# Public rendering functions
# ---------------------------------------------------------------------------

def email_to_pdf(email_obj: UnifiedEmail, out_path: Path, grayscale: bool = False) -> None:
    """Render the email header + body to *out_path* as a PDF."""
    doc = _new_doc(out_path)
    story: list = [
        Paragraph(xml_escape(email_obj.subject), SUBJ_STYLE),
        HRFlowable(width="100%", thickness=2, color=ACCESS_GREEN, spaceAfter=8),
    ]
    for label, val in [("From", email_obj.sender), ("To", email_obj.to),
                        ("CC", email_obj.cc), ("BCC", email_obj.bcc), ("Date", email_obj.date)]:
        if val:
            story.append(Paragraph(f"<b>{label}:</b>  {xml_escape(val)}", VAL_STYLE))

    story.append(Spacer(1, 0.15 * inch))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CCCCCC"), spaceAfter=10))
    story.extend(_body_flowables(email_obj, grayscale=grayscale))
    doc.build(story)


def image_to_pdf(data: bytes, filename: str, out_path: Path, grayscale: bool = False) -> bool:
    try:
        img = Image.open(BytesIO(data))
        if grayscale:
            img = img.convert("L")
        elif img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")
        iw, ih = img.size
        max_w = PAGE_W - 2 * MARGIN
        max_h = PAGE_H - 2 * MARGIN - 0.6 * inch
        scale = min(max_w / iw, max_h / ih, 1.0)
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=85)
        buf.seek(0)
        doc = _new_doc(out_path)
        doc.build([
            Paragraph(xml_escape(filename), LABEL_STYLE),
            Spacer(1, 0.1 * inch),
            RLImage(buf, width=iw * scale, height=ih * scale),
        ])
        return True
    except Exception as exc:
        _log.warning("image attachment %r: %s", filename, exc)
        return False


def text_to_pdf(data: bytes, filename: str, out_path: Path) -> bool:
    try:
        text = data.decode("utf-8", errors="replace") if isinstance(data, bytes) else str(data)
        doc = _new_doc(out_path)
        story: list = [Paragraph(xml_escape(filename), LABEL_STYLE)]
        for line in text.splitlines():
            story.append(Paragraph(xml_escape(line), BODY_STYLE) if line.strip() else Spacer(1, 0.04 * inch))
        doc.build(story)
        return True
    except Exception as exc:
        _log.warning("text attachment %r: %s", filename, exc)
        return False


def html_att_to_pdf(data: bytes, filename: str, out_path: Path) -> bool:
    try:
        plain = html_to_text(data.decode("utf-8", errors="replace"))
        return text_to_pdf(plain.encode(), filename, out_path)
    except Exception as exc:
        _log.warning("html attachment %r: %s", filename, exc)
        return False


def docx_to_pdf(data: bytes, filename: str, out_path: Path) -> bool:
    try:
        doc_in = _docx.Document(BytesIO(data))
        doc_out = _new_doc(out_path)
        story: list = [
            Paragraph(xml_escape(filename), LABEL_STYLE),
            HRFlowable(width="100%", thickness=0.5, color=colors.grey, spaceAfter=6),
        ]
        for para in doc_in.paragraphs:
            txt = para.text
            if not txt.strip():
                story.append(Spacer(1, 0.08 * inch))
                continue
            style_name = para.style.name or ""
            if "Heading 1" in style_name:
                st = _style("H1", fontName="Helvetica-Bold", fontSize=13, leading=18, spaceAfter=6)
            elif "Heading 2" in style_name:
                st = _style("H2", fontName="Helvetica-Bold", fontSize=11, leading=15, spaceAfter=4)
            else:
                st = BODY_STYLE
            story.append(Paragraph(xml_escape(txt), st))
        doc_out.build(story)
        return True
    except Exception as exc:
        _log.warning("docx attachment %r: %s", filename, exc)
        return False


def placeholder_to_pdf(filename: str, out_path: Path) -> bool:
    try:
        ext = Path(filename).suffix.lstrip(".").upper() or "UNKNOWN"
        doc = _new_doc(out_path)
        doc.build([
            Paragraph(xml_escape(f"Attachment: {filename}"), SUBJ_STYLE),
            Spacer(1, 0.2 * inch),
            Paragraph(xml_escape(f"[{ext} file – cannot render inline]"), NOTE_STYLE),
        ])
        return True
    except Exception:
        return False


def attachment_to_pdf(data: bytes, filename: str, out_path: Path,
                      ct: str = "", grayscale: bool = False) -> bool:
    """Convert a single attachment to PDF. Returns True on success."""
    ext = Path(filename).suffix.lower()
    if not ext and ct:
        ext = _CT_TO_EXT.get(ct.split(";")[0].strip().lower(), "")

    # MIME image/* check covers subtypes not in _EXT_KIND
    if ct.startswith("image/") or _EXT_KIND.get(ext) == "image":
        return image_to_pdf(data, filename, out_path, grayscale)

    kind = _EXT_KIND.get(ext)
    if kind == "text":
        return text_to_pdf(data, filename, out_path)
    if kind == "html":
        return html_att_to_pdf(data, filename, out_path)
    if kind == "pdf":
        out_path.write_bytes(data)
        return True
    if kind == "docx":
        return docx_to_pdf(data, filename, out_path)
    return placeholder_to_pdf(filename, out_path)


def get_email_attachments(email_obj: UnifiedEmail, keep_inline: bool = True):
    """Yield (filename, data, content_type) for each attachment."""
    yield from email_obj.attachments
    if not keep_inline:
        for cid, data in email_obj.cid_map.items():
            if cid.startswith("<") and cid.endswith(">"):
                continue
            if data.startswith(b"\xff\xd8"):
                ext = ".jpg"
            elif data.startswith(b"\x89PNG"):
                ext = ".png"
            elif data.startswith(b"GIF8"):
                ext = ".gif"
            elif data.startswith(b"BM"):
                ext = ".bmp"
            else:
                ext = ".png"
            yield f"inline_{cid}{ext}", data, f"image/{ext.lstrip('.')}"


def process_email(email_path: Path, out_dir: Path,
                  keep_inline: bool = True, grayscale: bool = False) -> Path:
    """Parse *email_path* and write a single merged PDF to *out_dir*. Returns the PDF path."""
    import shutil
    email_path = Path(email_path)
    out_dir = Path(out_dir)

    email_obj = UnifiedEmail(email_path)

    body_pdf = out_dir / f"{email_path.stem}_body.pdf"
    email_to_pdf(email_obj, body_pdf, grayscale=grayscale)
    parts = [body_pdf]

    for idx, (fname, data, ct) in enumerate(get_email_attachments(email_obj, keep_inline=keep_inline)):
        att_pdf = out_dir / f"{email_path.stem}_att_{idx:03d}.pdf"
        if attachment_to_pdf(data, fname, att_pdf, ct, grayscale=grayscale) and att_pdf.exists():
            parts.append(att_pdf)

    final_pdf = out_dir / f"{email_path.stem}.pdf"
    if len(parts) == 1:
        shutil.copy2(parts[0], final_pdf)
    else:
        writer = pypdf.PdfWriter()
        for p in parts:
            try:
                for page in pypdf.PdfReader(str(p)).pages:
                    writer.add_page(page)
            except Exception as exc:
                _log.warning("merge %s: %s", p.name, exc)
        with open(final_pdf, "wb") as f:
            writer.write(f)

    for p in parts:
        try:
            p.unlink()
        except Exception:
            pass

    return final_pdf
