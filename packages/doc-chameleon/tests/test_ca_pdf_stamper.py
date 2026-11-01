from pathlib import Path
import io
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from doc_chameleon.rules.ca.pdf_stamper import stamp_ca_pleading_pdf_bytes

def _make_sample_pdf(num_pages: int = 3) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(612.0, 792.0))
    for i in range(1, num_pages + 1):
        c.setFont("Helvetica", 12)
        c.drawString(108, 700, f"Page {i} of Sample Pleading Text")
        c.showPage()
    c.save()
    buf.seek(0)
    return buf.getvalue()

def test_pdf_pleading_stamping_page_count():
    sample = _make_sample_pdf(3)
    stamped = stamp_ca_pleading_pdf_bytes(sample, rail_style="none")
    reader = PdfReader(io.BytesIO(stamped))
    assert len(reader.pages) == 3

def test_pdf_pleading_stamping_rail_styles():
    sample = _make_sample_pdf(2)
    for style in ("none", "single", "double"):
        stamped = stamp_ca_pleading_pdf_bytes(sample, rail_style=style)
        assert len(stamped) > len(sample)

def test_pdf_pleading_preserves_text_layer():
    sample = _make_sample_pdf(2)
    stamped = stamp_ca_pleading_pdf_bytes(sample, rail_style="single")
    reader = PdfReader(io.BytesIO(stamped))
    text = reader.pages[0].extract_text()
    assert "Sample Pleading Text" in text
    assert "1" in text
    assert "28" in text
