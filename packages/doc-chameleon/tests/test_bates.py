"""
tests.test_bates
Validates vector Bates stamp formatting, page numbering increments, and vector layer merging.
"""

from doc_chameleon.bates.stamper import BatesStampConfig, stamp_pdf_bytes
from reportlab.pdfgen import canvas
import io
from pypdf import PdfReader

def _generate_test_pdf(num_pages: int = 3) -> bytes:
    """Helper generating a clean multi-page vector PDF in memory."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(612.0, 792.0))
    for i in range(num_pages):
        c.drawString(100, 700, f"Original Discovery Evidence Page {i + 1}")
        c.showPage()
    c.save()
    buf.seek(0)
    return buf.getvalue()

def test_bates_formatting_and_sequence():
    cfg = BatesStampConfig(prefix="DOE_V_ROE_", start=14, digits=6, suffix="_CONF")
    assert cfg.format_bates(0) == "DOE_V_ROE_000014_CONF"
    assert cfg.format_bates(1) == "DOE_V_ROE_000015_CONF"
    assert cfg.format_bates(10) == "DOE_V_ROE_000024_CONF"

def test_stamp_pdf_preserves_pages_and_injects_bates():
    source_pdf = _generate_test_pdf(num_pages=3)
    cfg = BatesStampConfig(prefix="PROD_", start=101, digits=5)
    
    stamped_bytes, manifest = stamp_pdf_bytes(source_pdf, cfg)
    
    # 1. Assert Manifest Integrity
    assert len(manifest) == 3
    assert manifest[0]["bates_id"] == "PROD_00101"
    assert manifest[1]["bates_id"] == "PROD_00102"
    assert manifest[2]["bates_id"] == "PROD_00103"
    
    # 2. Inspect Merged PDF Text Extraction (Vector Verification)
    reader = PdfReader(io.BytesIO(stamped_bytes))
    assert len(reader.pages) == 3
    
    page1_text = reader.pages[0].extract_text()
    assert "Original Discovery Evidence Page 1" in page1_text
    assert "PROD_00101" in page1_text
    
    page3_text = reader.pages[2].extract_text()
    assert "Original Discovery Evidence Page 3" in page3_text
    assert "PROD_00103" in page3_text
