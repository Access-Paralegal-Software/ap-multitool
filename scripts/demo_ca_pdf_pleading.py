from pathlib import Path
import io
from reportlab.pdfgen import canvas
from doc_chameleon.rules.ca.pdf_stamper import stamp_ca_pleading_pdf

# 1. Create a 3-page unformatted motion PDF
raw_pdf = Path("test_raw_motion.pdf")
buf = io.BytesIO()
c = canvas.Canvas(buf, pagesize=(612.0, 792.0))

for page in range(1, 4):
    c.setFont("Times-Roman", 12)
    c.drawString(108, 720, "Alan Woodyard, SBN 123456")
    c.drawString(108, 696, "Woodyard Legal Solutions")
    c.drawString(108, 672, "100 Main Street, Katy, TX 77494")
    c.drawString(108, 648, "Attorney for Defendant")
    c.drawString(108, 600, "SUPERIOR COURT OF THE STATE OF CALIFORNIA")
    c.drawString(108, 576, "COUNTY OF LOS ANGELES - CENTRAL DISTRICT")
    c.drawString(108, 528, "CASE NO. 24STCV12345")
    c.drawString(108, 504, "DEFENDANT'S MOTION FOR SUMMARY JUDGMENT")

    # Body lines at exact 24pt double spacing
    y = 456
    for k in range(1, 16):
        c.drawString(108, y, f"This is motion body text paragraph {k} on page {page}.")
        y -= 24

    c.showPage()

c.save()
raw_pdf.write_bytes(buf.getvalue())
print(f"[OK] Generated raw draft PDF: {raw_pdf.resolve()}")

# 2. Stamp with CRC 2.111 Pleading Paper (Modern Unruled default)
out_pdf = Path("test_ca_pleading_stamped.pdf")
stamp_ca_pleading_pdf(raw_pdf, out_pdf, rail_style="none", include_clerk_box=True)
print(f"[OK] Successfully stamped PDF pleading: {out_pdf.resolve()}")
