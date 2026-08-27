from __future__ import annotations

import docx
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_LINE_SPACING
from docx.oxml import parse_xml
from docx.shared import Inches, Pt

PLEADING_LINE_COUNT = 28
PLEADING_LINE_SPACING_PT = 24
PLEADING_FONT_NAME = "Times New Roman"
PLEADING_FONT_SIZE_PT = 12


def transform(doc: docx.Document) -> docx.Document:
    """Apply the first controlled California pleading-paper prototype.

    This spike uses a page-header anchored VML text box for left-margin line
    numbers. The body remains editable Word content while the numbering layer is
    structurally inspectable in the `.docx` header XML.
    """
    _apply_page_geometry(doc)
    _apply_body_style(doc)
    _normalize_body_flow(doc)
    _install_line_number_header(doc)
    return doc


def _apply_page_geometry(doc: docx.Document) -> None:
    for section in doc.sections:
        section.page_width = Inches(8.5)
        section.page_height = Inches(11)
        section.left_margin = Inches(1.25)
        section.right_margin = Inches(1)
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.header_distance = Inches(0.35)
        section.footer_distance = Inches(0.35)


def _apply_body_style(doc: docx.Document) -> None:
    normal = doc.styles["Normal"]
    normal.font.name = PLEADING_FONT_NAME
    normal.font.size = Pt(PLEADING_FONT_SIZE_PT)
    normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    normal.paragraph_format.line_spacing = Pt(PLEADING_LINE_SPACING_PT)
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(0)

    if "Doc Chameleon CA Body" not in doc.styles:
        body_style = doc.styles.add_style("Doc Chameleon CA Body", WD_STYLE_TYPE.PARAGRAPH)
    else:
        body_style = doc.styles["Doc Chameleon CA Body"]

    body_style.base_style = normal
    body_style.font.name = PLEADING_FONT_NAME
    body_style.font.size = Pt(PLEADING_FONT_SIZE_PT)
    body_style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    body_style.paragraph_format.line_spacing = Pt(PLEADING_LINE_SPACING_PT)
    body_style.paragraph_format.space_before = Pt(0)
    body_style.paragraph_format.space_after = Pt(0)


def _normalize_body_flow(doc: docx.Document) -> None:
    for paragraph in doc.paragraphs:
        paragraph.style = doc.styles["Doc Chameleon CA Body"]
        paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
        paragraph.paragraph_format.line_spacing = Pt(PLEADING_LINE_SPACING_PT)
        paragraph.paragraph_format.space_before = Pt(0)
        paragraph.paragraph_format.space_after = Pt(0)


def _install_line_number_header(doc: docx.Document) -> None:
    for section in doc.sections:
        header = section.header
        _clear_header(header)
        paragraph = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
        paragraph._p.append(_line_number_pict())


def _clear_header(header: docx.section._Header) -> None:
    for paragraph in list(header.paragraphs):
        paragraph.clear()
    for table in list(header.tables):
        table._element.getparent().remove(table._element)


def _line_number_pict():
    number_paragraphs = "".join(
        f"""
        <w:p>
          <w:pPr>
            <w:spacing w:before="0" w:after="0" w:line="{PLEADING_LINE_SPACING_PT * 20}" w:lineRule="exact"/>
            <w:jc w:val="right"/>
          </w:pPr>
          <w:r>
            <w:rPr>
              <w:rFonts w:ascii="{PLEADING_FONT_NAME}" w:hAnsi="{PLEADING_FONT_NAME}"/>
              <w:sz w:val="{PLEADING_FONT_SIZE_PT * 2}"/>
            </w:rPr>
            <w:t>{line_number}</w:t>
          </w:r>
        </w:p>
        """
        for line_number in range(1, PLEADING_LINE_COUNT + 1)
    )

    return parse_xml(
        f"""
        <w:pict
          xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
          xmlns:v="urn:schemas-microsoft-com:vml"
          xmlns:o="urn:schemas-microsoft-com:office:office">
          <v:shape
            id="doc-chameleon-ca-line-numbers"
            o:spid="_x0000_s1025"
            type="#_x0000_t202"
            style="position:absolute;margin-left:48pt;margin-top:72pt;width:36pt;height:672pt;z-index:251659264;mso-position-horizontal-relative:page;mso-position-vertical-relative:page"
            stroked="f"
            filled="f">
            <v:textbox inset="0,0,0,0">
              <w:txbxContent>
                {number_paragraphs}
              </w:txbxContent>
            </v:textbox>
          </v:shape>
        </w:pict>
        """
    )
