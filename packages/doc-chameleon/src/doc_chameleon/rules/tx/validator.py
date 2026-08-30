"""Texas statewide baseline validator."""
from __future__ import annotations

import docx
from docx.shared import Inches, Pt

from doc_chameleon.engine.models import DocumentRecord
from doc_chameleon.rules.tx.transformer import (
    EXPECTED_MARGIN,
    EXPECTED_PAGE_HEIGHT,
    EXPECTED_PAGE_WIDTH,
    TX_MARKER,
)

_STATEWIDE_ONLY_WARNING = (
    "This document reflects Texas statewide baseline formatting only. "
    "Local venue rules (Harris County, Travis County, etc.) are not applied. "
    "Verify local court requirements before filing."
)


def validate(doc: docx.Document, record: DocumentRecord, venue_overlay: str | None = None) -> list[str]:
    warnings: list[str] = []

    for i, section in enumerate(doc.sections, start=1):
        warnings.extend(_validate_section(i, section))

    if not _has_tx_baseline_transform(doc):
        warnings.append(
            "Texas statewide baseline transform not applied. "
            "Run the TX transformer before relying on TRCP-aligned formatting."
        )

    if not _has_caption_structure(doc):
        warnings.append(
            "No court caption detected in the opening paragraphs. "
            "Texas pleadings require a court identification and case style caption."
        )

    warnings.append(_STATEWIDE_ONLY_WARNING)
    return list(dict.fromkeys(warnings))


def validate_source_assumptions(doc: docx.Document, record: DocumentRecord) -> list[str]:
    """Warn on source structures that may need attention after TX baseline transform."""
    warnings: list[str] = []

    for paragraph in doc.paragraphs:
        fmt = paragraph.paragraph_format
        if fmt.space_before not in (None, Pt(0)) or fmt.space_after not in (None, Pt(0)):
            warnings.append(
                "Explicit paragraph spacing detected in source document. "
                "TX baseline transform resets paragraph spacing to zero."
            )
            break

    return warnings


def _validate_section(index: int, section: docx.section.Section) -> list[str]:
    warnings: list[str] = []
    checks = [
        ("page width", section.page_width, EXPECTED_PAGE_WIDTH),
        ("page height", section.page_height, EXPECTED_PAGE_HEIGHT),
        ("left margin", section.left_margin, EXPECTED_MARGIN),
        ("right margin", section.right_margin, EXPECTED_MARGIN),
        ("top margin", section.top_margin, EXPECTED_MARGIN),
        ("bottom margin", section.bottom_margin, EXPECTED_MARGIN),
    ]
    for label, actual, expected in checks:
        if actual != expected:
            warnings.append(
                f"Section {index} {label} is {actual} EMU; "
                f"Texas statewide baseline expects {expected} EMU."
            )
    return warnings


def _has_tx_baseline_transform(doc: docx.Document) -> bool:
    return TX_MARKER in doc.sections[0]._sectPr.xml


def _has_caption_structure(doc: docx.Document) -> bool:
    first_texts = [p.text.lower() for p in doc.paragraphs[:12]]
    return any("court" in t for t in first_texts)
