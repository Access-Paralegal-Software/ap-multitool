from pathlib import Path
import docx
from doc_chameleon.rules.ca.transformer_2111 import transform_2111

doc = docx.Document()

caption = [
    "Alan Woodyard, SBN 123456",
    "Woodyard Legal Solutions",
    "100 Main Street",
    "Katy, TX 77494",
    "Tel: (281) 555-0100",
    "Email: alan@alanwoodyard.com",
    "Attorney for Defendant",
    "SUPERIOR COURT OF THE STATE OF CALIFORNIA",
    "COUNTY OF LOS ANGELES - CENTRAL DISTRICT",
    "",
    "CASE NO. 24STCV12345",
    "DEFENDANT'S NOTICE OF MOTION AND",
    "MOTION FOR SUMMARY JUDGMENT",
    ""
]

for line in caption:
    doc.add_paragraph(line)

for i in range(1, 35):
    doc.add_paragraph(
        f"This is numbered statement of undisputed fact paragraph {i}. "
        "The moving party contends that reasonable diligence was exercised at all material times, "
        "and no triable issue of material fact exists under CCP Section 437c."
    )
    doc.add_paragraph("")

dst = Path("test_motion_modern_unruled.docx")
# rail_style="none" sets modern unruled format (no vertical line)
transform_2111(doc, output_path=dst, rail_style="none")
print(f"[OK] Saved modern unruled pleading to: {dst.resolve()}")
