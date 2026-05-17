# email_processing.py
"""Access Email Attachment Harvester Utility
Convert standard .eml and Outlook .msg files (with inline and regular attachments) to PDFs.
All processing is offline and uses local dependencies (ReportLab, Pillow, pypdf, python-docx, html2text, extract-msg).
Supports high-contrast PACER-compliant grayscale mode.
"""

import os
import re
import email
import email.policy
from pathlib import Path
from io import BytesIO
import tempfile
import sys

# ReportLab imports
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Image as RLImage

# Pillow
from PIL import Image

# PDF handling
import pypdf

# DOCX handling
import docx as _docx

# HTML to text
import html2text as h2t

PAGE_W, PAGE_H = letter
MARGIN = inch
ACCESS_GREEN = colors.HexColor("#67BE5E")

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
_styles = getSampleStyleSheet()

def _style(name, **kwargs):
    return ParagraphStyle(name, parent=_styles["Normal"], **kwargs)

SUBJ_STYLE = _style("Subject", fontName="Helvetica-Bold", fontSize=14, leading=20, spaceAfter=10)
HDR_STYLE = _style("Header", fontName="Helvetica-Bold", fontSize=9, leading=13, spaceAfter=2)
VAL_STYLE = _style("Value", fontName="Helvetica", fontSize=9, leading=13, spaceAfter=2, wordWrap="CJK")
BODY_STYLE = _style("Body", fontName="Helvetica", fontSize=10, leading=14, spaceAfter=4, wordWrap="CJK")
LABEL_STYLE = _style("Label", fontName="Helvetica-Bold", fontSize=11, spaceAfter=8)
NOTE_STYLE = _style("Note", fontName="Helvetica-Oblique", fontSize=10, leading=14, textColor=colors.grey)

def _new_doc(path: Path):
    return SimpleDocTemplate(
        str(path),
        pagesize=letter,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
    )

# ---------------------------------------------------------------------------
# XML escape & HTML conversion
# ---------------------------------------------------------------------------
def xml_escape(text: str) -> str:
    if not text:
        return ""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = text.replace('"', "&quot;").replace("'", "&#39;")
    # Remove control chars except tab/newline
    return "".join(c if (ord(c) >= 32 or c in "\t\n") else " " for c in text)

def html_to_text(html: str) -> str:
    handler = h2t.HTML2Text()
    handler.ignore_links = False
    handler.ignore_images = True
    handler.body_width = 0
    return handler.handle(html)

# ---------------------------------------------------------------------------
# Unified Email Wrapper (Handles both .eml and .msg formats natively)
# ---------------------------------------------------------------------------
class UnifiedEmail:
    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)
        self.ext = self.file_path.suffix.lower()
        self.subject = "(No Subject)"
        self.sender = "Unknown Sender"
        self.to = "Unknown Recipient"
        self.cc = ""
        self.bcc = ""
        self.date = "Unknown Date"
        self.html_body = None
        self.text_body = None
        self.cid_map = {}
        self.attachments = []  # List of tuples (filename, data, content_type)
        
        if self.ext == ".msg":
            self._parse_msg()
        else:
            self._parse_eml()

    def _parse_msg(self):
        import extract_msg
        msg = extract_msg.Message(str(self.file_path))
        self.subject = msg.subject or "(No Subject)"
        self.sender = msg.sender or "Unknown Sender"
        self.to = msg.to or "Unknown Recipient"
        self.cc = msg.cc or ""
        self.bcc = msg.bcc or ""
        self.date = msg.date or "Unknown Date"
        
        if msg.htmlBody:
            self.html_body = msg.htmlBody.decode("utf-8", errors="ignore")
        elif msg.body:
            self.text_body = msg.body
            
        # Parse attachments & inline images (CIDs)
        if msg.attachments:
            for idx, att in enumerate(msg.attachments):
                cid = att.cid
                if not cid and hasattr(att, "contentId"):
                    cid = att.contentId
                
                filename = att.longFilename or att.shortFilename or f"attachment_{idx}.bin"
                data = att.data
                content_type = att.mimetype or "application/octet-stream"
                
                if cid:
                    cid_str = str(cid).strip("<> ")
                    self.cid_map[cid_str] = data
                    self.cid_map[f"<{cid_str}>"] = data
                else:
                    self.attachments.append((filename, data, content_type))
        msg.close()

    def _parse_eml(self):
        from email.parser import BytesParser
        
        with open(self.file_path, "rb") as f:
            msg = BytesParser(policy=email.policy.compat32).parse(f)
            
        self.subject = self._decode_header(msg.get("Subject", "(No Subject)"))
        self.sender = self._decode_header(msg.get("From", "Unknown Sender"))
        self.to = self._decode_header(msg.get("To", "Unknown Recipient"))
        self.cc = self._decode_header(msg.get("CC", ""))
        self.bcc = self._decode_header(msg.get("BCC", ""))
        self.date = self._decode_header(msg.get("Date", "Unknown Date"))
        
        for part in msg.walk():
            ct = part.get_content_type()
            cd = str(part.get("Content-Disposition", ""))
            
            # Extract content ID if available
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
                
            # If not an attachment, read as body text
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
            result = []
            for chunk, enc in parts:
                if isinstance(chunk, bytes):
                    result.append(chunk.decode(enc or "utf-8", errors="replace"))
                else:
                    result.append(chunk)
            return "".join(result)
        except Exception:
            return str(raw)

# ---------------------------------------------------------------------------
# CID handling for inline images & body generation
# ---------------------------------------------------------------------------
_IMG_PLACEHOLDER = "CIDIMAGE{n}CIDIMAGE"

def _body_flowables(email_obj: UnifiedEmail, grayscale: bool = False) -> list:
    cid_map = email_obj.cid_map
    html_body = email_obj.html_body
    text_body = email_obj.text_body
    
    inline_images = {}
    if html_body and cid_map:
        def _replace_cid_img(m):
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
        html_body = re.sub(r'<img[^>]*>', _replace_cid_img, html_body, flags=re.IGNORECASE)
        
    body_text = html_to_text(html_body) if html_body else (text_body or "(No body)")
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

def email_to_pdf(email_obj: UnifiedEmail, out_path: Path, grayscale: bool = False):
    doc = _new_doc(out_path)
    story = []
    
    # Premium Subject Line with Access Green branding
    story.append(Paragraph(xml_escape(email_obj.subject), SUBJ_STYLE))
    story.append(HRFlowable(width="100%", thickness=2, color=ACCESS_GREEN, spaceAfter=8))
    
    # Metadata Grid
    headers = [
        ("From", email_obj.sender),
        ("To", email_obj.to),
        ("CC", email_obj.cc),
        ("BCC", email_obj.bcc),
        ("Date", email_obj.date),
    ]
    for hdr, val in headers:
        if val:
            story.append(Paragraph(f"<b>{hdr}:</b>  {xml_escape(val)}", VAL_STYLE))
            
    story.append(Spacer(1, 0.15 * inch))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CCCCCC"), spaceAfter=10))
    
    # Body Flowables
    story.extend(_body_flowables(email_obj, grayscale=grayscale))
    doc.build(story)

# ---------------------------------------------------------------------------
# Attachment conversion helpers
# ---------------------------------------------------------------------------
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
        text = data.decode("utf-8", errors="replace") if isinstance(data, bytes) else str(data)
        doc = _new_doc(out_path)
        story = [Paragraph(xml_escape(filename), LABEL_STYLE)]
        for line in text.splitlines():
            if line.strip():
                story.append(Paragraph(xml_escape(line), BODY_STYLE))
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
        doc_in = _docx.Document(BytesIO(data))
        doc_out = _new_doc(out_path)
        story = [
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
    except Exception as e:
        print(f"    [warn] docx '{filename}': {e}")
        return False

def placeholder_to_pdf(filename: str, out_path: Path) -> bool:
    try:
        ext = Path(filename).suffix.lstrip('.').upper() or "UNKNOWN"
        doc = _new_doc(out_path)
        story = [
            Paragraph(xml_escape(f"Attachment: {filename}"), SUBJ_STYLE),
            Spacer(1, 0.2 * inch),
            Paragraph(xml_escape(f"[{ext} file – cannot render inline]"), NOTE_STYLE),
        ]
        doc.build(story)
        return True
    except Exception:
        return False

# Mapping helpers
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp"}
TEXT_EXTS = {".txt", ".csv", ".log", ".md", ".json", ".xml", ".py", ".js", ".ts", ".css", ".yaml", ".yml", ".ini", ".cfg"}
HTML_EXTS = {".html", ".htm"}
CT_EXT_MAP = {
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

def attachment_to_pdf(data: bytes, filename: str, out_path: Path, ct: str = "", grayscale: bool = False) -> bool:
    ext = Path(filename).suffix.lower()
    if not ext and ct:
        ext = CT_EXT_MAP.get(ct.split(";")[0].strip().lower(), "")
    if ct.startswith("image/"):
        return image_to_pdf(data, filename, out_path, grayscale)
    if ext in IMAGE_EXTS:
        return image_to_pdf(data, filename, out_path, grayscale)
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

def get_email_attachments(email_obj: UnifiedEmail, keep_inline: bool = True):
    # Yield standard attachments first
    for name, data, ct in email_obj.attachments:
        yield name, data, ct
    # Yield inline images if not keep_inline
    if not keep_inline:
        for cid, data in email_obj.cid_map.items():
            if cid.startswith("<") and cid.endswith(">"):
                continue
            ext = ".png"
            if data.startswith(b"\xff\xd8"): ext = ".jpg"
            elif data.startswith(b"\x89PNG"): ext = ".png"
            elif data.startswith(b"GIF8"): ext = ".gif"
            elif data.startswith(b"BM"): ext = ".bmp"
            yield f"inline_{cid}{ext}", data, f"image/{ext.lstrip('.')}"

# ---------------------------------------------------------------------------
# Public entry point for a single email file
# ---------------------------------------------------------------------------
def process_email(email_path: Path, out_dir: Path, keep_inline: bool = True, grayscale: bool = False) -> Path:
    """Convert a single .eml/.msg file into a PDF and return the PDF path.
    If `keep_inline` is False, any CID‑referenced images are stripped from the body
    and appended after the email body as separate pages.
    """
    email_path = Path(email_path)
    out_dir = Path(out_dir)
    
    # 1. Parse unified email
    email_obj = UnifiedEmail(email_path)
    
    # 2. Output PDF for the email body
    body_pdf = out_dir / f"{email_path.stem}_body.pdf"
    email_to_pdf(email_obj, body_pdf, grayscale=grayscale)
    parts = [body_pdf]
    
    # 3. Attachments (including inline images if keep_inline=False)
    for idx, (fname, data, ct) in enumerate(get_email_attachments(email_obj, keep_inline=keep_inline)):
        att_pdf = out_dir / f"{email_path.stem}_att_{idx:03d}.pdf"
        success = attachment_to_pdf(data, fname, att_pdf, ct, grayscale=grayscale)
        if success and att_pdf.exists():
            parts.append(att_pdf)
            
    # 4. Merge parts into a single PDF
    final_pdf = out_dir / f"{email_path.stem}.pdf"
    if len(parts) == 1:
        import shutil
        shutil.copy2(parts[0], final_pdf)
    else:
        writer = pypdf.PdfWriter()
        for p in parts:
            try:
                reader = pypdf.PdfReader(str(p))
                for page in reader.pages:
                    writer.add_page(page)
            except Exception as e:
                print(f"    [warn] merge {p.name}: {e}")
        with open(final_pdf, "wb") as out_f:
            writer.write(out_f)
            
    # Clean up intermediate PDFs
    for p in parts:
        try:
            p.unlink()
        except Exception:
            pass
            
    return final_pdf

# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python email_processing.py <input_file_or_folder> [output_folder] [--grayscale]")
        sys.exit(1)
        
    path = Path(sys.argv[1])
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else Path("./pdf_output")
    grayscale = "--grayscale" in sys.argv
    
    out_dir.mkdir(parents=True, exist_ok=True)
    
    if path.is_file():
        if path.suffix.lower() in (".eml", ".msg"):
            print(f"Processing single file: {path.name}...")
            out = process_email(path, out_dir, grayscale=grayscale)
            print(f" -> Generated: {out.name}")
        else:
            print("Error: Target file must be .eml or .msg format.")
    elif path.is_dir():
        files = sorted(list(path.glob("*.eml")) + list(path.glob("*.msg")))
        if not files:
            print(f"No .eml or .msg files found in: {path}")
            sys.exit(0)
        print(f"Found {len(files)} email file(s) -> {out_dir}\n")
        ok = fail = 0
        for f in files:
            print(f"  [{f.name}]")
            try:
                out = process_email(f, out_dir, grayscale=grayscale)
                print(f"    -> {out.name}\n")
                ok += 1
            except Exception as e:
                print(f"    FAILED: {e}\n")
                fail += 1
        print(f"Finished: {ok} succeeded, {fail} failed.")

if __name__ == "__main__":
    main()
