"""Texas statewide baseline transformer (TRCP-aligned).

Texas does not use CRC-style left-margin line numbering. Formatting is
principally structure- and caption-focused. This module applies standard
page geometry, double-spaced body style, and marks the transform for the
validator to detect.

Local venue overlays (Harris County, Travis County, etc.) are architecturally
reserved in the overlays/ directory but not implemented here.
"""
from __future__ import annotations

import docx
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_LINE_SPACING
from docx.shared import Inches, Pt
from lxml import etree

TX_FONT_NAME = "Times New Roman"
TX_FONT_SIZE_PT = 12
TX_MARKER = "doc-chameleon-tx-baseline"

EXPECTED_PAGE_WIDTH = Inches(8.5)
EXPECTED_PAGE_HEIGHT = Inches(11)
EXPECTED_MARGIN = Inches(1)


def transform(doc: docx.Document, venue_overlay: str | None = None) -> docx.Document:
    _apply_page_geometry(doc)
    _apply_body_style(doc)
    _normalize_body_flow(doc)
    _mark_transform(doc)
    return doc


def _apply_page_geometry(doc: docx.Document) -> None:
    for section in doc.sections:
        section.page_width = EXPECTED_PAGE_WIDTH
        section.page_height = EXPECTED_PAGE_HEIGHT
        section.left_margin = EXPECTED_MARGIN
        section.right_margin = EXPECTED_MARGIN
        section.top_margin = EXPECTED_MARGIN
        section.bottom_margin = EXPECTED_MARGIN


def _apply_body_style(doc: docx.Document) -> None:
    normal = doc.styles["Normal"]
    normal.font.name = TX_FONT_NAME
    normal.font.size = Pt(TX_FONT_SIZE_PT)
    normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(0)

    if "Doc Chameleon TX Body" not in doc.styles:
        body_style = doc.styles.add_style("Doc Chameleon TX Body", WD_STYLE_TYPE.PARAGRAPH)
    else:
        body_style = doc.styles["Doc Chameleon TX Body"]

    body_style.base_style = normal
    body_style.font.name = TX_FONT_NAME
    body_style.font.size = Pt(TX_FONT_SIZE_PT)
    body_style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    body_style.paragraph_format.space_before = Pt(0)
    body_style.paragraph_format.space_after = Pt(0)


def _normalize_body_flow(doc: docx.Document) -> None:
    for paragraph in doc.paragraphs:
        paragraph.style = doc.styles["Doc Chameleon TX Body"]
        paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
        paragraph.paragraph_format.space_before = Pt(0)
        paragraph.paragraph_format.space_after = Pt(0)


def _mark_transform(doc: docx.Document) -> None:
    doc.sections[0]._sectPr.append(etree.Comment(TX_MARKER))
