from pathlib import Path
import io
from reportlab.pdfgen import canvas
from doc_chameleon.bates.stamper import BatesStampConfig, stamp_pdf_bytes
from doc_chameleon.bates.loadfile import generate_production_loadfiles

prod_root = Path("demo_production")
img_dir = prod_root / "IMAGES"
data_dir = prod_root / "DATA"
img_dir.mkdir(parents=True, exist_ok=True)
data_dir.mkdir(parents=True, exist_ok=True)

# Generate 2 sample PDFs
def make_pdf(title, pages):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(612.0, 792.0))
    for p in range(1, pages + 1):
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, 700, f"{title} — Page {p} of {pages}")
        c.showPage()
    c.save()
    return buf.getvalue()

files = [
    ("Employment_Contract.pdf", make_pdf("CONFIDENTIAL EMPLOYMENT CONTRACT", 3)),
    ("Email_Chain_Breach.pdf", make_pdf("EMAIL REGARDING TERMINATION", 2)),
]

cfg = BatesStampConfig(prefix="ACME_", start=1001, digits=6, suffix="_CONF")
prod_docs = []

for idx, (fname, raw_data) in enumerate(files):
    stamped, manifest = stamp_pdf_bytes(raw_data, cfg)
    beg = manifest[0]["bates_id"]
    end = manifest[-1]["bates_id"]

    out_file = img_dir / f"{beg}_{fname}"
    out_file.write_bytes(stamped)

    prod_docs.append({
        "doc_id": idx + 1,
        "beg_bates": beg,
        "end_bates": end,
        "page_count": len(manifest),
        "file_name": fname,
        "dest_file": out_file.name,
        "file_size": len(stamped),
        "pages": manifest,
    })
    cfg.start += len(manifest)

# Generate load files
generate_production_loadfiles(prod_docs, data_dir, volume="VOL0001")
print(f"[OK] Production complete in: {prod_root.resolve()}")
print(f"[OK] Stamped images: {len(list(img_dir.glob('*.pdf')))} PDFs")
print(f"[OK] Concordance DAT:\n{ (data_dir / 'VOL0001.dat').read_text(encoding='utf-8') }")
print(f"[OK] Opticon OPT:\n{ (data_dir / 'VOL0001.opt').read_text(encoding='utf-8') }")
