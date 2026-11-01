from pathlib import Path
import docx
from doc_chameleon.rules.ca.transformer import transform as transform_2108
from doc_chameleon.rules.ca.transformer_2111 import transform_2111, AttorneyInfo

doc = docx.Document()

attorney = AttorneyInfo(
    name="Alan Woodyard",
    sbn="123456",
    firm="Woodyard Legal Solutions",
    address="100 Main Street",
    city_state_zip="Katy, TX 77494",
    phone="(281) 555-0100",
    email="alan@alanwoodyard.com",
    representing="Defendant",
)

caption = [
    "SUPERIOR COURT OF THE STATE OF CALIFORNIA",
    "COUNTY OF LOS ANGELES - CENTRAL DISTRICT",
    "",
    "CASE NO. 24STCV12345",
    "DEFENDANT'S NOTICE OF MOTION AND",
    "MOTION FOR SUMMARY JUDGMENT",
    "",
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

transform_2108(doc)
transform_2111(doc, attorney=attorney)

out_file = Path("test_ca_28lines_p1_verified.docx")
doc.save(str(out_file))
print(f"[OK] Saved verified 28-line pleading to: {out_file.resolve()}")
