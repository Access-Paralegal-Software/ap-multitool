from __future__ import annotations

from pathlib import Path

import docx

from doc_chameleon.engine.models import DocumentRecord, ParagraphRecord, SectionRecord


def load(path: Path) -> tuple[docx.Document, DocumentRecord]:
    doc = docx.Document(str(path))
    record = _build_record(doc, path)
    return doc, record


def _build_record(doc: docx.Document, source_path: Path | None) -> DocumentRecord:
    paragraphs = [
        ParagraphRecord(
            index=i,
            text=para.text,
            style_name=para.style.name if para.style else None,
        )
        for i, para in enumerate(doc.paragraphs)
    ]

    sections = [
        SectionRecord(
            page_width_emu=sec.page_width,
            page_height_emu=sec.page_height,
            left_margin_emu=sec.left_margin,
            right_margin_emu=sec.right_margin,
            top_margin_emu=sec.top_margin,
            bottom_margin_emu=sec.bottom_margin,
        )
        for sec in doc.sections
    ]

    return DocumentRecord(source_path=source_path, paragraphs=paragraphs, sections=sections)
