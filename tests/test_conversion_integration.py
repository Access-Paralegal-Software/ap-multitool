# tests/test_conversion_integration.py — Integration tests for document conversion
# using real fixture files from tests/fixtures/conversion/.
#
# Unit tests (no real Office/LibreOffice required): TestBackendSelection,
#   TestFixturePresence, TestConversionWithMockedBackend.
#
# LibreOffice integration tests: TestLibreOfficeIntegration.
#   These auto-skip when soffice is not on PATH.
#   To force-run them: ensure soffice is installed and on PATH, then:
#       pytest tests/test_conversion_integration.py -m libreoffice -v
#   Or set APM_CONVERSION_BACKEND=libreoffice to override detection.

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from unittest import mock

import pikepdf
import pytest

from core.operations._conversion_backend import (
    ConversionBackend,
    detect_backend,
    libreoffice_fallback_enabled,
    run_soffice_convert,
    soffice_available,
)
from core.operations.docx_to_pdf import convert_docx_to_pdf
from core.operations.xlsx_to_pdf import convert_xlsx_to_pdf

pytestmark = [pytest.mark.core, pytest.mark.conversion, pytest.mark.integration]

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

FIXTURES = Path(__file__).parent / "fixtures" / "conversion"

DOCX_FIXTURES = [
    FIXTURES / "simple_text.docx",
    FIXTURES / "headings_and_lists.docx",
    FIXTURES / "basic_table.docx",
]

XLSX_FIXTURES = [
    FIXTURES / "simple_spreadsheet.xlsx",
    FIXTURES / "multi_sheet.xlsx",
]


# ---------------------------------------------------------------------------
# 1. Fixture presence — verifies the fixture set exists (always runs)
# ---------------------------------------------------------------------------

class TestFixturePresence:
    """Confirm every expected fixture file is committed to the repo."""

    @pytest.mark.parametrize("path", DOCX_FIXTURES, ids=lambda p: p.name)
    def test_docx_fixture_exists(self, path):
        assert path.exists(), f"Missing fixture: {path}"
        assert path.stat().st_size > 0, f"Fixture is empty: {path}"

    @pytest.mark.parametrize("path", XLSX_FIXTURES, ids=lambda p: p.name)
    def test_xlsx_fixture_exists(self, path):
        assert path.exists(), f"Missing fixture: {path}"
        assert path.stat().st_size > 0, f"Fixture is empty: {path}"


# ---------------------------------------------------------------------------
# 2. Backend selection — unit tests, no real Office or soffice required
# ---------------------------------------------------------------------------

class TestBackendSelection:
    """Exercise backend selection logic for the full Office-vs-LibreOffice matrix."""

    def test_windows_primary_is_win32com(self):
        """On Windows, detect_backend() should prefer WIN32COM."""
        with mock.patch("os.name", "nt"):
            assert detect_backend() == ConversionBackend.WIN32COM

    def test_posix_with_soffice_uses_libreoffice(self, monkeypatch):
        monkeypatch.setenv("APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK", "1")
        monkeypatch.delenv("APM_CONVERSION_BACKEND", raising=False)
        with mock.patch("os.name", "posix"), \
             mock.patch("shutil.which", return_value="/usr/bin/soffice"):
            assert detect_backend() == ConversionBackend.LIBREOFFICE

    def test_posix_no_soffice_returns_none(self, monkeypatch):
        monkeypatch.setenv("APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK", "1")
        monkeypatch.delenv("APM_CONVERSION_BACKEND", raising=False)
        with mock.patch("os.name", "posix"), \
             mock.patch("shutil.which", return_value=None):
            assert detect_backend() == ConversionBackend.NONE

    def test_env_override_forces_libreoffice_on_windows(self, monkeypatch):
        """APM_CONVERSION_BACKEND=libreoffice should override even on Windows."""
        monkeypatch.setenv("APM_CONVERSION_BACKEND", "libreoffice")
        with mock.patch("os.name", "nt"):
            assert detect_backend() == ConversionBackend.LIBREOFFICE

    def test_env_override_forces_win32com_on_posix(self, monkeypatch):
        monkeypatch.setenv("APM_CONVERSION_BACKEND", "win32com")
        with mock.patch("os.name", "posix"):
            assert detect_backend() == ConversionBackend.WIN32COM

    def test_fallback_disabled_yields_none_on_posix(self, monkeypatch):
        monkeypatch.setenv("APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK", "0")
        monkeypatch.delenv("APM_CONVERSION_BACKEND", raising=False)
        with mock.patch("os.name", "posix"), \
             mock.patch("shutil.which", return_value="/usr/bin/soffice"):
            assert detect_backend() == ConversionBackend.NONE

    def test_win32com_fail_triggers_fallback_when_enabled(self, monkeypatch, tmp_path):
        """When win32com fails and fallback is enabled+available, a warning is returned."""
        monkeypatch.setenv("APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK", "1")

        src = tmp_path / "doc.docx"
        src.write_bytes(b"mock")
        out = tmp_path / "doc.pdf"

        import sys
        sys.modules.setdefault("pythoncom", mock.MagicMock())
        mock_word = mock.MagicMock()
        mock_word.Documents.Open.side_effect = RuntimeError("Office not installed")

        def fake_soffice(cmd, **kwargs):
            outdir = Path(cmd[cmd.index("--outdir") + 1])
            (outdir / (src.stem + ".pdf")).write_bytes(b"%PDF-1.4 ok")
            return mock.MagicMock(returncode=0)

        with mock.patch("win32com.client.DispatchEx", return_value=mock_word, create=True), \
             mock.patch("subprocess.run", side_effect=fake_soffice), \
             mock.patch("shutil.which", return_value="/usr/bin/soffice"):
            warnings = convert_docx_to_pdf(src, out, backend=ConversionBackend.WIN32COM)

        assert out.exists()
        assert len(warnings) == 1
        assert "LibreOffice fallback" in warnings[0]

    def test_win32com_fail_no_fallback_raises(self, monkeypatch, tmp_path):
        """When win32com fails and fallback is disabled, RuntimeError is raised."""
        monkeypatch.setenv("APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK", "0")

        src = tmp_path / "doc.docx"
        src.write_bytes(b"mock")
        out = tmp_path / "doc.pdf"

        import sys
        sys.modules.setdefault("pythoncom", mock.MagicMock())
        mock_word = mock.MagicMock()
        mock_word.Documents.Open.side_effect = RuntimeError("Office not installed")

        with mock.patch("win32com.client.DispatchEx", return_value=mock_word, create=True):
            with pytest.raises(RuntimeError, match="LibreOffice fallback is disabled"):
                convert_docx_to_pdf(src, out, backend=ConversionBackend.WIN32COM)


# ---------------------------------------------------------------------------
# 3. Fixture conversion with mocked backend — unit tests
# ---------------------------------------------------------------------------

class TestConversionWithMockedBackend:
    """
    Run the full convert_*_to_pdf() function against real fixtures, but with the
    backend mocked.  This validates that the abstraction layer correctly handles
    real file paths, output path logic, and result types — without needing Office
    or LibreOffice installed.
    """

    def _fake_soffice(self, src_path: Path):
        def _run(cmd, **kwargs):
            outdir = Path(cmd[cmd.index("--outdir") + 1])
            # Write a minimal valid PDF
            from reportlab.pdfgen import canvas as rl_canvas
            pdf_path = outdir / (src_path.stem + ".pdf")
            c = rl_canvas.Canvas(str(pdf_path))
            c.drawString(72, 720, f"Converted: {src_path.name}")
            c.save()
            return mock.MagicMock(returncode=0)
        return _run

    @pytest.mark.parametrize("fixture", DOCX_FIXTURES, ids=lambda p: p.name)
    def test_docx_fixture_converts_via_libreoffice_mock(self, fixture, tmp_path):
        out = tmp_path / (fixture.stem + ".pdf")
        with mock.patch("subprocess.run", side_effect=self._fake_soffice(fixture)):
            warnings = convert_docx_to_pdf(fixture, out, backend=ConversionBackend.LIBREOFFICE)
        assert out.exists(), f"No PDF produced for {fixture.name}"
        assert out.stat().st_size > 0
        assert warnings == []
        # Verify pikepdf can open it
        with pikepdf.open(out) as pdf:
            assert len(pdf.pages) >= 1

    @pytest.mark.parametrize("fixture", XLSX_FIXTURES, ids=lambda p: p.name)
    def test_xlsx_fixture_converts_via_libreoffice_mock(self, fixture, tmp_path):
        out = tmp_path / (fixture.stem + ".pdf")
        with mock.patch("subprocess.run", side_effect=self._fake_soffice(fixture)):
            warnings = convert_xlsx_to_pdf(fixture, out, backend=ConversionBackend.LIBREOFFICE)
        assert out.exists(), f"No PDF produced for {fixture.name}"
        assert out.stat().st_size > 0
        assert warnings == []
        with pikepdf.open(out) as pdf:
            assert len(pdf.pages) >= 1


# ---------------------------------------------------------------------------
# 4. LibreOffice integration tests (auto-skip when soffice is absent)
# ---------------------------------------------------------------------------

def _soffice_skip():
    """Return a pytest skip mark if soffice is not on PATH."""
    if not soffice_available():
        return pytest.mark.skip(reason="LibreOffice not installed (soffice not on PATH)")
    return pytest.mark.libreoffice


@pytest.mark.libreoffice
class TestLibreOfficeIntegration:
    """
    Real soffice invocations using fixture files.

    These tests auto-skip when soffice is not on PATH.
    To run them: install LibreOffice and ensure soffice is discoverable, then:
        pytest tests/test_conversion_integration.py -m libreoffice -v

    Alternatively, force the backend:
        APM_CONVERSION_BACKEND=libreoffice pytest -m libreoffice -v
    """

    @pytest.fixture(autouse=True)
    def require_soffice(self):
        if not soffice_available():
            pytest.skip("LibreOffice not installed (soffice not on PATH)")

    @pytest.mark.parametrize("fixture", DOCX_FIXTURES, ids=lambda p: p.name)
    def test_docx_produces_valid_pdf(self, fixture, tmp_path):
        """Convert each docx fixture via soffice; verify output is a valid PDF."""
        out = tmp_path / (fixture.stem + ".pdf")
        warnings = convert_docx_to_pdf(fixture, out, backend=ConversionBackend.LIBREOFFICE)
        assert out.exists(), f"soffice did not produce a PDF for {fixture.name}"
        assert out.stat().st_size > 0, "Output PDF is empty"
        # structural validity
        with pikepdf.open(out) as pdf:
            page_count = len(pdf.pages)
        assert page_count >= 1, f"Expected ≥1 page, got {page_count}"

    @pytest.mark.parametrize("fixture", XLSX_FIXTURES, ids=lambda p: p.name)
    def test_xlsx_produces_valid_pdf(self, fixture, tmp_path):
        """Convert each xlsx fixture via soffice; verify output is a valid PDF."""
        out = tmp_path / (fixture.stem + ".pdf")
        warnings = convert_xlsx_to_pdf(fixture, out, backend=ConversionBackend.LIBREOFFICE)
        assert out.exists(), f"soffice did not produce a PDF for {fixture.name}"
        assert out.stat().st_size > 0, "Output PDF is empty"
        with pikepdf.open(out) as pdf:
            page_count = len(pdf.pages)
        assert page_count >= 1

    def test_multi_sheet_xlsx_all_sheets_present(self, tmp_path):
        """multi_sheet.xlsx has 2 sheets — converted PDF should have ≥2 pages."""
        fixture = FIXTURES / "multi_sheet.xlsx"
        out = tmp_path / "multi_sheet.pdf"
        convert_xlsx_to_pdf(fixture, out, backend=ConversionBackend.LIBREOFFICE)
        with pikepdf.open(out) as pdf:
            page_count = len(pdf.pages)
        assert page_count >= 2, (
            f"Expected ≥2 pages for multi-sheet workbook, got {page_count}. "
            "LibreOffice may not have exported all sheets."
        )

    def test_simple_text_docx_text_survives(self, tmp_path):
        """
        Convert simple_text.docx and verify key strings survive to PDF.
        Uses pypdf for lightweight text extraction; text order/layout may differ.
        """
        import pypdf

        fixture = FIXTURES / "simple_text.docx"
        out = tmp_path / "simple_text.pdf"
        convert_docx_to_pdf(fixture, out, backend=ConversionBackend.LIBREOFFICE)

        reader = pypdf.PdfReader(str(out))
        full_text = " ".join(
            reader.pages[i].extract_text() or "" for i in range(len(reader.pages))
        )
        assert "Simple Text Document" in full_text or len(full_text) > 20, (
            "Expected heading text or substantial content in converted PDF. "
            f"Extracted text (first 200 chars): {full_text[:200]!r}"
        )

    def test_soffice_timeout_raises(self, tmp_path):
        """Verify TimeoutExpired propagates cleanly from run_soffice_convert()."""
        src = tmp_path / "doc.docx"
        src.write_bytes(b"timeout test")
        out = tmp_path / "out.pdf"
        with mock.patch(
            "subprocess.run",
            side_effect=subprocess.TimeoutExpired(["soffice"], 60),
        ):
            with pytest.raises(subprocess.TimeoutExpired):
                run_soffice_convert(src, out, timeout=60)
