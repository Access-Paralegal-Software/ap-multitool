"""Tests for AttorneyInfo dataclass and CA first-page attorney block population."""
from __future__ import annotations

from pathlib import Path

from doc_chameleon.engine.export import save
from doc_chameleon.engine.ingest import load
from doc_chameleon.rules.ca.transformer import transform as transform_2108
from doc_chameleon.rules.ca.transformer_2111 import (
    ATTORNEY_PLACEHOLDER_LINES,
    AttorneyInfo,
    transform_2111,
    _attorney_lines,
)

from tests.fixtures import make_long_motion, make_motion


# ── AttorneyInfo dataclass ────────────────────────────────────────────────────

def test_attorney_info_defaults_match_placeholder_constant() -> None:
    """ATTORNEY_PLACEHOLDER_LINES must stay in sync with AttorneyInfo defaults."""
    assert _attorney_lines(AttorneyInfo()) == ATTORNEY_PLACEHOLDER_LINES


def test_attorney_info_partial_override_keeps_other_defaults() -> None:
    attorney = AttorneyInfo(name="Jane Smith", sbn="123456")
    lines = _attorney_lines(attorney)
    assert lines[0] == "Jane Smith, SBN 123456"
    assert lines[1] == "[Firm Name]"       # default
    assert lines[3] == "[City, State ZIP]"  # default


def test_attorney_info_full_override() -> None:
    attorney = AttorneyInfo(
        name="Jane Smith",
        sbn="123456",
        firm="Smith & Associates",
        address="123 Main St",
        city_state_zip="Los Angeles, CA 90001",
        phone="(213) 555-0100",
        email="jane@smithlaw.com",
        client="Plaintiff, ACME Corp",
    )
    lines = _attorney_lines(attorney)
    assert lines[0] == "Jane Smith, SBN 123456"
    assert lines[1] == "Smith & Associates"
    assert lines[2] == "123 Main St"
    assert lines[3] == "Los Angeles, CA 90001"
    assert lines[4] == "Tel: (213) 555-0100"
    assert lines[5] == "Email: jane@smithlaw.com"
    assert lines[6] == ""
    assert lines[7] == "Attorney for Plaintiff, ACME Corp"


# ── Header population ─────────────────────────────────────────────────────────

def test_custom_attorney_name_appears_in_first_page_header(tmp_path: Path) -> None:
    src = tmp_path / "source.docx"
    out = tmp_path / "out_ca.docx"
    make_motion(src)

    attorney = AttorneyInfo(name="Jane Smith", sbn="123456")
    doc, _ = load(src)
    transform_2108(doc)
    transform_2111(doc, attorney=attorney)
    save(doc, out)

    reloaded, _ = load(out)
    fp_header = reloaded.sections[0].first_page_header
    left_texts = [row.cells[0].text for row in fp_header.tables[0].rows]
    assert any("Jane Smith" in t for t in left_texts)
    assert any("123456" in t for t in left_texts)


def test_custom_firm_appears_in_first_page_header(tmp_path: Path) -> None:
    src = tmp_path / "source.docx"
    out = tmp_path / "out_ca.docx"
    make_motion(src)

    attorney = AttorneyInfo(firm="Smith & Associates")
    doc, _ = load(src)
    transform_2108(doc)
    transform_2111(doc, attorney=attorney)
    save(doc, out)

    reloaded, _ = load(out)
    fp_header = reloaded.sections[0].first_page_header
    left_texts = [row.cells[0].text for row in fp_header.tables[0].rows]
    assert any("Smith & Associates" in t for t in left_texts)


def test_default_attorney_produces_placeholder_lines_in_header(tmp_path: Path) -> None:
    src = tmp_path / "source.docx"
    out = tmp_path / "out_ca.docx"
    make_motion(src)

    doc, _ = load(src)
    transform_2108(doc)
    transform_2111(doc)   # no attorney arg — uses defaults
    save(doc, out)

    reloaded, _ = load(out)
    fp_header = reloaded.sections[0].first_page_header
    left_texts = [row.cells[0].text for row in fp_header.tables[0].rows]
    assert any("[Attorney Name]" in t for t in left_texts)


def test_attorney_name_with_ampersand_is_xml_safe(tmp_path: Path) -> None:
    """Ampersands in attorney info must not break the XML."""
    src = tmp_path / "source.docx"
    out = tmp_path / "out_ca.docx"
    make_motion(src)

    attorney = AttorneyInfo(firm="Smith & Jones & Brown LLP")
    doc, _ = load(src)
    transform_2108(doc)
    transform_2111(doc, attorney=attorney)
    save(doc, out)   # must not raise

    reloaded, _ = load(out)
    fp_header = reloaded.sections[0].first_page_header
    left_texts = [row.cells[0].text for row in fp_header.tables[0].rows]
    assert any("Smith & Jones & Brown LLP" in t for t in left_texts)


# ── Multi-page structural test ────────────────────────────────────────────────

def test_long_motion_ca_transform_produces_correct_headers(tmp_path: Path) -> None:
    """Multi-page document: line-number header and 2.111 first-page header must survive."""
    src = tmp_path / "long_motion.docx"
    out = tmp_path / "long_motion_ca.docx"
    make_long_motion(src)

    doc, record = load(src)
    original_count = len(record.paragraphs)

    transform_2108(doc)
    transform_2111(doc)
    save(doc, out)

    reloaded, reloaded_record = load(out)
    assert len(reloaded_record.paragraphs) == original_count
    assert "doc-chameleon-ca-line-numbers" in reloaded.sections[0].header._element.xml
    assert "doc-chameleon-ca-2111" in reloaded.sections[0].first_page_header._element.xml


def test_long_motion_with_attorney_info(tmp_path: Path) -> None:
    src = tmp_path / "long_motion.docx"
    out = tmp_path / "long_motion_ca.docx"
    make_long_motion(src)

    attorney = AttorneyInfo(
        name="Jane Smith",
        sbn="123456",
        firm="Smith & Associates",
        address="123 Main St",
        city_state_zip="Los Angeles, CA 90001",
        phone="(213) 555-0100",
        email="jane@smithlaw.com",
        client="Plaintiff, ACME Corp",
    )
    doc, _ = load(src)
    transform_2108(doc)
    transform_2111(doc, attorney=attorney)
    save(doc, out)

    reloaded, _ = load(out)
    fp_header = reloaded.sections[0].first_page_header
    left_texts = [row.cells[0].text for row in fp_header.tables[0].rows]
    assert any("Jane Smith" in t for t in left_texts)
    assert any("Smith & Associates" in t for t in left_texts)
    assert any("ACME Corp" in t for t in left_texts)
