from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

doc = docx.Document()

# 1. Page Geometry: Exactly 1.0 in Top and Bottom Margins (72 pt = 1440 twips)
section = doc.sections[0]
section.page_width = Inches(8.5)
section.page_height = Inches(11.0)
section.top_margin = Inches(1.0)
section.bottom_margin = Inches(1.0)
section.left_margin = Inches(1.4)    # Leaves room for left-rail line numbers
section.right_margin = Inches(1.0)
section.different_first_page_header_footer = False

# 2. Inject Page-Anchored 28-Line Rail in Header
header = section.header
header.is_linked_to_previous = False
for p in header.paragraphs:
    p.text = ""

table = header.add_table(rows=28, cols=1, width=Inches(0.4))

# Force floating table anchored to PAGE, starting at Y = 1.0 inch (1440 twips)
tblPr = table._tbl.tblPr
tblpPr = parse_xml(
    r'<w:tblpPr %s w:vertAnchor="page" w:horzAnchor="page" '
    r'w:tblpX="720" w:tblpY="1440" '
    r'w:leftFromText="0" w:rightFromText="0" w:topFromText="0" w:bottomFromText="0"/>'
    % nsdecls('w')
)
tblPr.append(tblpPr)

# Strip default table cell padding and add right border rail
tblCellMar = parse_xml(
    r'<w:tblCellMar %s>'
    r'<w:top w:w="0" w:type="dxa"/><w:bottom w:w="0" w:type="dxa"/>'
    r'<w:left w:w="0" w:type="dxa"/><w:right w:w="72" w:type="dxa"/>'
    r'</w:tblCellMar>' % nsdecls('w')
)
tblPr.append(tblCellMar)

borders = parse_xml(
    r'<w:tblBorders %s>'
    r'<w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/>'
    r'<w:right w:val="single" w:sz="6" w:space="0" w:color="888888"/>'
    r'</w:tblBorders>' % nsdecls('w')
)
tblPr.append(borders)

for i in range(28):
    row = table.rows[i]
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(r'<w:trHeight %s w:val="480" w:hRule="exact"/>' % nsdecls('w')))
    
    cell = row.cells[0]
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    pPr = p._p.get_or_add_pPr()
    pPr.append(parse_xml(r'<w:spacing %s w:before="0" w:after="0" w:line="480" w:lineRule="exact"/>' % nsdecls('w')))
    
    run = p.add_run(str(i + 1))
    run.font.name = "Times New Roman"
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0x77, 0x77, 0x77)

# 3. Add Body Paragraphs (All with Exact 24pt Leading, 0 Before, 0 After)
lines = [
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

for l in lines:
    doc.add_paragraph(l)

for i in range(1, 35):
    doc.add_paragraph(
        f"This is numbered statement of undisputed fact paragraph {i}. "
        "The moving party contends that reasonable diligence was exercised at all material times, "
        "and no triable issue of material fact exists under CCP Section 437c."
    )
    doc.add_paragraph("")

# Lock every body paragraph to exact 24pt pitch
for p in doc.paragraphs:
    pPr = p._p.get_or_add_pPr()
    for child in list(pPr):
        if child.tag.endswith('spacing'):
            pPr.remove(child)
    pPr.append(parse_xml(r'<w:spacing %s w:before="0" w:after="0" w:line="480" w:lineRule="exact"/>' % nsdecls('w')))
    for r in p.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)

out_file = Path("test_motion_phase_locked.docx")
doc.save(out_file)
print(f"[OK] Saved phase-locked pleading: {out_file.resolve()}")
