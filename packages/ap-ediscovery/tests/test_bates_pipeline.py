"""
tests.test_bates_pipeline
Integration test verifying end-to-end sequential Bates stamping and directory compilation.
"""

from pathlib import Path
import io
from reportlab.pdfgen import canvas

from ap_ediscovery.engine.bates_pipeline import ProductionBatchRunner

def _make_pdf(num_pages: int, marker: str) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(612.0, 792.0))
    for p in range(num_pages):
        c.drawString(72, 700, f"{marker} - Page {p + 1}")
        c.showPage()
    c.save()
    buf.seek(0)
    return buf.getvalue()

def test_production_batch_runner_compiles_deliverable(tmp_path: Path):
    doc1 = {
        "doc_id": 1,
        "custodian_id": 10,
        "custodian": "Doe, John",
        "family_id": 100,
        "file_name": "memo.pdf",
        "record_type": "Email",
        "text_content": "Privileged memo regarding settlement terms.",
        "pdf_bytes": _make_pdf(2, "Parent Email")
    }
    doc2 = {
        "doc_id": 2,
        "custodian_id": 10,
        "custodian": "Doe, John",
        "family_id": 100,
        "parent_doc_id": 1,
        "file_name": "financials.pdf",
        "record_type": "Attachment",
        "text_content": "Financial statement figures.",
        "pdf_bytes": _make_pdf(1, "Child Attachment")
    }

    runner = ProductionBatchRunner(prefix="ALPHA_", start_num=1, digits=6)
    out_dir = tmp_path / "VOL001_EXPORT"
    res = runner.process_production([doc1, doc2], out_dir, volume_label="VOL001")

    assert res["document_count"] == 2
    assert res["total_pages"] == 3

    # Check Directory Structure
    assert (out_dir / "DATA" / "VOL001.DAT").exists()
    assert (out_dir / "DATA" / "VOL001.OPT").exists()
    assert (out_dir / "IMAGES" / "ALPHA_000001.PDF").exists()
    assert (out_dir / "IMAGES" / "ALPHA_000003.PDF").exists()
    assert (out_dir / "TEXT" / "ALPHA_000001.TXT").exists()

    # Verify Concordance .DAT contents
    dat_raw = (out_dir / "DATA" / "VOL001.DAT").read_bytes()
    assert dat_raw.startswith(b"\xef\xbb\xbf")
    dat_text = dat_raw[3:].decode("utf-8")
    lines = [l for l in dat_text.split("\r\n") if l]
    assert len(lines) == 3  # Header + 2 Docs

    # Verify Family Attachment Bounds
    # Parent should span ALPHA_000001 to ALPHA_000002, with family ending at ALPHA_000003
    assert "ALPHA_000001" in lines[1]
    assert "ALPHA_000002" in lines[1]
    assert "ALPHA_000003" in lines[1]  # ENDATTACH
