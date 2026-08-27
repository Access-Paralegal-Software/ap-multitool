"""CRC 2.111 first-page layout tests."""
from __future__ import annotations

from pathlib import Path

from doc_chameleon.engine.export import save
from doc_chameleon.engine.ingest import load
from doc_chameleon.rules.ca.transformer import transform as transform_2108
from doc_chameleon.rules.ca.transformer_2111 import (
    ATTORNEY_PLACEHOLDER_LINES,
    CLERK_SPACE_LABEL,
    transform_2111,
)
from doc_chameleon.rules.ca.validator import validate, validate_2111

from tests.fixtures import make_cover_page, make_motion


def test_2111_enables_different_first_page(tmp_path: Path) -> None:
    src = tmp_path / "source.docx"
    make_motion(src)

    doc, _ = load(src)
    transform_2111(doc)

    assert doc.sections[0].different_first_page_header_footer is True


def test_2111_first_page_header_has_two_column_table(tmp_path: Path) -> None:
    src = tmp_path / "source.docx"
    out = tmp_path / "out.docx"
    make_motion(src)

    doc, _ = load(src)
    transform_2111(doc)
    save(doc, out)

    reloaded, _ = load(out)
    section = reloaded.sections[0]
    assert section.different_first_page_header_footer is True
    fp_tables = section.first_page_header.tables
    assert fp_tables, "First-page header must contain at least one table"
    assert len(fp_tables[0].rows[0].cells) == 2


def test_2111_attorney_placeholder_in_left_column(tmp_path: Path) -> None:
    src = tmp_path / "source.docx"
    out = tmp_path / "out.docx"
    make_motion(src)

    doc, _ = load(src)
    transform_2111(doc)
    save(doc, out)

    reloaded, _ = load(out)
    fp_header = reloaded.sections[0].first_page_header
    left_texts = [row.cells[0].text for row in fp_header.tables[0].rows]
    assert ATTORNEY_PLACEHOLDER_LINES[0] in left_texts
    assert ATTORNEY_PLACEHOLDER_LINES[1] in left_texts


def test_2111_clerk_space_label_in_right_column(tmp_path: Path) -> None:
    src = tmp_path / "source.docx"
    out = tmp_path / "out.docx"
    make_motion(src)

    doc, _ = load(src)
    transform_2111(doc)
    save(doc, out)

    reloaded, _ = load(out)
    fp_header = reloaded.sections[0].first_page_header
    right_top = fp_header.tables[0].rows[0].cells[1].text
    assert CLERK_SPACE_LABEL in right_top


def test_2111_default_header_retains_line_numbers_after_2111(tmp_path: Path) -> None:
    """2.108 default header must be untouched when 2.111 installs the first-page header."""
    src = tmp_path / "source.docx"
    out = tmp_path / "out.docx"
    make_motion(src)

    doc, _ = load(src)
    transform_2108(doc)
    transform_2111(doc)
    save(doc, out)

    reloaded, _ = load(out)
    default_header_xml = reloaded.sections[0].header._element.xml
    assert "doc-chameleon-ca-line-numbers" in default_header_xml


def test_2111_composes_with_2108_both_structures_present(tmp_path: Path) -> None:
    """After both transforms, default header has line numbers AND first-page header has attorney block."""
    src = tmp_path / "source.docx"
    out = tmp_path / "out.docx"
    make_motion(src)

    doc, _ = load(src)
    transform_2108(doc)
    transform_2111(doc)
    save(doc, out)

    reloaded, _ = load(out)
    assert "doc-chameleon-ca-line-numbers" in reloaded.sections[0].header._element.xml
    assert "doc-chameleon-ca-2111" in reloaded.sections[0].first_page_header._element.xml


def test_validator_warns_if_2108_present_but_not_2111(tmp_path: Path) -> None:
    src = tmp_path / "source.docx"
    make_motion(src)

    doc, record = load(src)
    transform_2108(doc)
    warnings = validate(doc, record)

    assert any("2.111" in w for w in warnings)


def test_validator_2111_warns_if_attorney_block_missing(tmp_path: Path) -> None:
    src = tmp_path / "source.docx"
    make_motion(src)

    doc, record = load(src)
    # Only run 2.108, not 2.111
    transform_2108(doc)
    warnings = validate_2111(doc, record)

    assert any("2.111" in w for w in warnings)


def test_cover_page_fixture_survives_full_ca_transform(tmp_path: Path) -> None:
    src = tmp_path / "cover.docx"
    out = tmp_path / "cover_ca.docx"
    make_cover_page(src)

    doc, record = load(src)
    original_count = len(record.paragraphs)
    transform_2108(doc)
    transform_2111(doc)
    save(doc, out)

    reloaded, reloaded_record = load(out)
    assert len(reloaded_record.paragraphs) == original_count
    assert "doc-chameleon-ca-line-numbers" in reloaded.sections[0].header._element.xml
    assert "doc-chameleon-ca-2111" in reloaded.sections[0].first_page_header._element.xml
