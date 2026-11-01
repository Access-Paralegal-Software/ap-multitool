from pathlib import Path
import docx
from doc_chameleon.rules.ca.transformer_2111 import transform_2111

src = Path("test_motion_unformatted.docx")
doc = docx.Document()

doc.add_paragraph("Alan Woodyard, SBN 123456\nWoodyard Legal Solutions\n100 Main Street, Katy, TX 77494\nTel: (281) 555-0100\nEmail: alan@alanwoodyard.com")
doc.add_paragraph("Attorney for Defendant")
doc.add_paragraph("SUPERIOR COURT OF THE STATE OF CALIFORNIA\nCOUNTY OF LOS ANGELES - CENTRAL DISTRICT")
doc.add_paragraph("CASE NO. 24STCV12345\nDEFENDANT'S NOTICE OF MOTION AND MOTION FOR SUMMARY JUDGMENT")

for i in range(1, 95):
    doc.add_paragraph(
        f"This is numbered statement of undisputed fact paragraph {i}. "
        "The moving party contends that reasonable diligence was exercised at all material times, "
        "and no triable issue of material fact exists under California Code of Civil Procedure Section 437c."
    )

doc.save(src)
print(f"[OK] Generated unformatted motion: {src.resolve()} ({src.stat().st_size} bytes)")

# Apply Rule 2.111 formatting in-memory
transform_2111(doc)

dst = Path("test_motion_ca2111_formatted.docx")
doc.save(dst)
print(f"[OK] Successfully transformed pleading: {dst.resolve()} ({dst.stat().st_size} bytes)")
