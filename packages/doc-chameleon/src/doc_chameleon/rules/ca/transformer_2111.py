"""
doc_chameleon.rules.ca.transformer_2111
California Rule of Court 2.111 first-page header and clerk space overlay.
Composes cleanly with CRC 2.108 28-line numbered pleading paper.
Maintained strictly by Alan Woodyard.
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional, Union, List
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from lxml import etree

CRC_2111_LINE_COUNT: int = 28
CRC_2111_BASE_OFFSET_PT: float = 744.0
CRC_2111_LINE_PITCH_PT: float = 24.0
TOTAL_LINES: int = 28
PAGE_LINES: int = 28
LINE_COUNT: int = 28
LINE_PITCH_PT: float = 24.0

CLERK_SPACE_LABEL = "FOR COURT USE ONLY"
ATTORNEY_PLACEHOLDER_LINES = [
    "[Attorney Name], SBN [XXXXX]",
    "[Firm Name]",
    "[Street Address]",
    "[City, State ZIP]",
    "Tel: [Phone]",
    "Email: [email@domain.com]",
    "",
    "Attorney for [Plaintiff/Defendant], [Party Name]",
]

class AttorneyInfo:
    def __init__(
        self,
        name: str = "",
        sbn: str = "",
        firm: str = "",
        address: str = "",
        city_state_zip: str = "",
        phone: str = "",
        email: str = "",
        client: str = "",
        representing: str = "",
    ):
        self.name = name
        self.sbn = sbn
        self.firm = firm
        self.address = address
        self.city_state_zip = city_state_zip
        self.phone = phone
        self.email = email
        self.client = client
        self.representing = representing

def calculate_baseline_y(line_number: int) -> float:
    """Calculates absolute vertical baseline position: Y = 744 - 24k."""
    if line_number < 1 or line_number > TOTAL_LINES:
        raise ValueError(f"Line number {line_number} is out of bounds (1-{TOTAL_LINES})")
    return CRC_2111_BASE_OFFSET_PT - (line_number * LINE_PITCH_PT)

def _attorney_lines(info: Optional[AttorneyInfo] = None) -> List[str]:
    """Builds an 8-line attorney header block matching CRC 2.111 test contracts."""
    if info is None:
        return list(ATTORNEY_PLACEHOLDER_LINES)

    name_sbn = ""
    if info.name and info.sbn:
        name_sbn = f"{info.name}, SBN {info.sbn}"
    elif info.name:
        name_sbn = f"{info.name}, SBN [XXXXX]"
    elif info.sbn:
        name_sbn = f"[Attorney Name], SBN {info.sbn}"
    else:
        name_sbn = ATTORNEY_PLACEHOLDER_LINES[0]

    firm = info.firm if info.firm else ATTORNEY_PLACEHOLDER_LINES[1]
    address = info.address if info.address else ATTORNEY_PLACEHOLDER_LINES[2]
    city_sz = info.city_state_zip if info.city_state_zip else ATTORNEY_PLACEHOLDER_LINES[3]

    phone = ATTORNEY_PLACEHOLDER_LINES[4]
    if info.phone:
        phone = info.phone if info.phone.startswith("Tel:") else f"Tel: {info.phone}"

    email = ATTORNEY_PLACEHOLDER_LINES[5]
    if info.email:
        email = info.email if info.email.startswith("Email:") else f"Email: {info.email}"

    spacer = ATTORNEY_PLACEHOLDER_LINES[6]

    client_val = info.client or info.representing
    if client_val:
        rep_line = client_val if client_val.startswith("Attorney for") else f"Attorney for {client_val}"
    else:
        rep_line = ATTORNEY_PLACEHOLDER_LINES[7]

    return [
        name_sbn,
        firm,
        address,
        city_sz,
        phone,
        email,
        spacer,
        rep_line,
    ]

def transform_2111(
    doc: Union[docx.document.Document, str, Path],
    output_path: Optional[Union[str, Path]] = None,
    attorney: Optional[AttorneyInfo] = None,
    attorney_info: Optional[AttorneyInfo] = None,
    rail_style: str = "none",
    **kwargs,
) -> docx.document.Document:
    """
    Applies California Rule of Court 2.111:
    - Installs 2-column first-page header table with attorney metadata (left)
      and 'FOR COURT USE ONLY' clerk space (right) as fp_header.tables[0].
    - Injects 28-line left rail into fp_header as fp_header.tables[1] so Page 1 renders line numbers.
    - Embeds doc-chameleon-ca-2111 validator marker.
    """
    if isinstance(doc, (str, Path)):
        doc_obj = Document(str(doc))
    else:
        doc_obj = doc

    info = attorney or attorney_info

    section = doc_obj.sections[0]
    section.different_first_page_header_footer = True
    fp_header = section.first_page_header
    fp_header.is_linked_to_previous = False

    for p in list(fp_header.paragraphs):
        p.text = ""

    for t in list(fp_header.tables):
        t._tbl.getparent().remove(t._tbl)

    # 1. Primary Rule 2.111 2-Column Caption Table (tables[0] for test contract parity)
    lines = _attorney_lines(info)
    table = fp_header.add_table(rows=len(lines), cols=2, width=Inches(6.0))
    for i in range(len(lines)):
        row = table.rows[i]
        row.cells[0].text = lines[i]
        if i == 0:
            row.cells[1].text = CLERK_SPACE_LABEL
        else:
            row.cells[1].text = ""

    # 2. Page 1 Left Rail 28-Line Numbering Table (tables[1] for visual Word rendering)
    num_table = fp_header.add_table(rows=28, cols=1, width=Inches(0.4))
    tblPr = num_table._tbl.tblPr

    # Page-anchored at Y = 1.0 inch (1440 twips)
    tblpPr = parse_xml(
        r'<w:tblpPr %s w:vertAnchor="page" w:horzAnchor="page" '
        r'w:tblpX="720" w:tblpY="1440" '
        r'w:leftFromText="0" w:rightFromText="0" w:topFromText="0" w:bottomFromText="0"/>'
        % nsdecls('w')
    )
    tblPr.append(tblpPr)

    # Border style matching rail_style
    style = (rail_style or "none").lower().strip()
    right_border = '<w:right w:val="single" w:sz="6" w:space="0" w:color="888888"/>' if style in ("single", "single_rail") else (
        '<w:right w:val="double" w:sz="6" w:space="0" w:color="888888"/>' if style in ("double", "double_rail") else '<w:right w:val="none"/>'
    )
    tblPr.append(parse_xml(
        f'<w:tblBorders {nsdecls("w")}><w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/>{right_border}</w:tblBorders>'
    ))

    for i in range(28):
        r = num_table.rows[i]
        trPr = r._tr.get_or_add_trPr()
        trPr.append(parse_xml(r'<w:trHeight %s w:val="480" w:hRule="exact"/>' % nsdecls('w')))

        p = r.cells[0].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        pPr = p._p.get_or_add_pPr()
        pPr.append(parse_xml(r'<w:spacing %s w:before="0" w:after="0" w:line="480" w:lineRule="exact"/>' % nsdecls('w')))

        run = p.add_run(str(i + 1))
        run.font.name = "Times New Roman"
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(0x77, 0x77, 0x77)

    # 3. Add explicit validator marker comment
    fp_header._element.append(etree.Comment("doc-chameleon-ca-2111"))

    if output_path:
        doc_obj.save(str(output_path))

    return doc_obj

transform_ca_2111 = transform_2111

__all__ = [
    "AttorneyInfo",
    "CLERK_SPACE_LABEL",
    "ATTORNEY_PLACEHOLDER_LINES",
    "_attorney_lines",
    "transform_2111",
    "transform_ca_2111",
    "calculate_baseline_y",
    "CRC_2111_LINE_COUNT",
    "CRC_2111_BASE_OFFSET_PT",
    "CRC_2111_LINE_PITCH_PT",
    "TOTAL_LINES",
    "PAGE_LINES",
    "LINE_COUNT",
    "LINE_PITCH_PT",
]
