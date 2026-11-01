from pathlib import Path
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_LINE_SPACING
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from doc_chameleon.rules.ca.transformer_2111 import transform_2111
from doc_chameleon.rules.ca.transformer import transform as transform_ca_core

doc = docx.Document()

# 1. Attorney Header block (Lines 1-7)
attorney_lines = [
    "Alan Woodyard, SBN 123456",
    "Woodyard Legal Solutions",
    "100 Main Street",
    "Katy, TX 77494",
    "Tel: (281) 555-0100",
    "Email: alan@alanwoodyard.com",
    "Attorney for Defendant"
]

# 2. Court & Case Caption (Lines 8-14)
caption_lines = [
    "SUPERIOR COURT OF THE STATE OF CALIFORNIA",
    "COUNTY OF LOS ANGELES - CENTRAL DISTRICT",
    "",
    "CASE NO. 24STCV12345",
    "DEFENDANT'S NOTICE OF MOTION AND",
    "MOTION FOR SUMMARY JUDGMENT",
    ""
]

# Build body with individual paragraphs for the preamble
for line in caption_lines:
    doc.add_paragraph(line)

# Body paragraphs (Lines 15+)
for i in range(1, 40):
    p = doc.add_paragraph(
        f"This is numbered statement of undisputed fact paragraph {i}. "
        "The moving party contends that reasonable diligence was exercised at all material times, "
        "and no triable issue of material fact exists under CCP Section 437c."
    )
    # Add an empty line between paragraphs that sits on the grid
    doc.add_paragraph("")

# First apply core CA transform (geometry, margins, styles)
transform_ca_core(doc)

# Apply Rule 2.111 header
transform_2111(doc)

# FORCE EXACT 24pt (480 twips) LINE SPACING ON EVERY PARAGRAPH
for p in doc.paragraphs:
    pPr = p._p.get_or_add_pPr()
    # Remove any existing spacing element
    for child in list(pPr):
        if child.tag.endswith('spacing'):
            pPr.remove(child)
    
    # Exact 24pt line height (480 twips), 0pt before, 0pt after
    spacing = parse_xml(r'<w:spacing %s w:before="0" w:after="0" w:line="480" w:lineRule="exact"/>' % nsdecls('w'))
    pPr.append(spacing)

out_file = Path("test_motion_aligned.docx")
doc.save(out_file)
print(f"[OK] Saved strictly locked pleading to: {out_file.resolve()}")
