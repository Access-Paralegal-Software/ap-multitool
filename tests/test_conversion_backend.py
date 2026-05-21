# tests/test_conversion_backend.py — Unit tests for backend detection, soffice utility,
# and convert_docx/xlsx_to_pdf abstraction functions.
#
# All tests are platform-agnostic: no real Office or LibreOffice installation required.
# Win32com calls and subprocess.run are always mocked.

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest import mock

import pytest
from reportlab.pdfgen import canvas as rl_canvas

from core.operations._conversion_backend import (
    ConversionBackend,
    detect_backend,
    libreoffice_fallback_enabled,
    run_soffice_convert,
    soffice_available,
)
from core.operations.docx_to_pdf import convert_docx_to_pdf
from core.operations.xlsx_to_pdf import convert_xlsx_to_pdf


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_minimal_pdf(path: Path) -> None:
    c = rl_canvas.Canvas(str(path))
    c.drawString(72, 720, "Test page")
    c.save()


def _soffice_fake_run(src_path: Path):
    """Return a fake subprocess.run callable that writes stem.pdf into --outdir."""
    def _run(cmd, **kwargs):
        outdir_idx = cmd.index("--outdir") + 1
        outdir = Path(cmd[outdir_idx])
        (outdir / (src_path.stem + ".pdf")).write_bytes(b"%PDF-1.4 minimal")
        return mock.MagicMock(returncode=0)
    return _run


# ---------------------------------------------------------------------------
# libreoffice_fallback_enabled()
# ---------------------------------------------------------------------------

class TestLibreOfficeFallbackEnabled:
    def test_default_enabled(self, monkeypatch):
        monkeypatch.delenv("APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK", raising=False)
        assert libreoffice_fallback_enabled() is True

    def test_explicit_1(self, monkeypatch):
        monkeypatch.setenv("APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK", "1")
        assert libreoffice_fallback_enabled() is True

    def test_explicit_true(self, monkeypatch):
        monkeypatch.setenv("APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK", "true")
        assert libreoffice_fallback_enabled() is True

    def test_zero_disables(self, monkeypatch):
        monkeypatch.setenv("APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK", "0")
        assert libreoffice_fallback_enabled() is False

    def test_false_disables(self, monkeypatch):
        monkeypatch.setenv("APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK", "false")
        assert libreoffice_fallback_enabled() is False

    def test_no_disables(self, monkeypatch):
        monkeypatch.setenv("APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK", "no")
        assert libreoffice_fallback_enabled() is False

    def test_off_disables(self, monkeypatch):
        monkeypatch.setenv("APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK", "off")
        assert libreoffice_fallback_enabled() is False


# ---------------------------------------------------------------------------
# detect_backend()
# ---------------------------------------------------------------------------

class TestDetectBackend:
    def _clear_env(self, monkeypatch):
        monkeypatch.delenv("APM_CONVERSION_BACKEND", raising=False)
        monkeypatch.delenv("APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK", raising=False)

    def test_override_param_win32com(self, monkeypatch):
        self._clear_env(monkeypatch)
        assert detect_backend(override="win32com") == ConversionBackend.WIN32COM

    def test_override_param_libreoffice(self, monkeypatch):
        self._clear_env(monkeypatch)
        assert detect_backend(override="libreoffice") == ConversionBackend.LIBREOFFICE

    def test_override_param_none_value(self, monkeypatch):
        self._clear_env(monkeypatch)
        assert detect_backend(override="none") == ConversionBackend.NONE

    def test_invalid_override_falls_through_to_posix_no_soffice(self, monkeypatch):
        self._clear_env(monkeypatch)
        monkeypatch.setenv("APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK", "1")
        with mock.patch("os.name", "posix"), mock.patch("shutil.which", return_value=None):
            result = detect_backend(override="__invalid__")
        assert result == ConversionBackend.NONE

    def test_env_var_libreoffice(self, monkeypatch):
        monkeypatch.setenv("APM_CONVERSION_BACKEND", "libreoffice")
        assert detect_backend() == ConversionBackend.LIBREOFFICE

    def test_env_var_win32com(self, monkeypatch):
        monkeypatch.setenv("APM_CONVERSION_BACKEND", "win32com")
        assert detect_backend() == ConversionBackend.WIN32COM

    def test_env_var_invalid_falls_through(self, monkeypatch):
        self._clear_env(monkeypatch)
        monkeypatch.setenv("APM_CONVERSION_BACKEND", "BADVALUE")
        monkeypatch.setenv("APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK", "1")
        with mock.patch("os.name", "posix"), mock.patch("shutil.which", return_value=None):
            result = detect_backend()
        assert result == ConversionBackend.NONE

    def test_windows_returns_win32com(self, monkeypatch):
        self._clear_env(monkeypatch)
        with mock.patch("os.name", "nt"):
            result = detect_backend()
        assert result == ConversionBackend.WIN32COM

    def test_posix_soffice_present_fallback_enabled(self, monkeypatch):
        self._clear_env(monkeypatch)
        monkeypatch.setenv("APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK", "1")
        with mock.patch("os.name", "posix"), \
             mock.patch("shutil.which", return_value="/usr/bin/soffice"):
            result = detect_backend()
        assert result == ConversionBackend.LIBREOFFICE

    def test_posix_soffice_present_fallback_disabled(self, monkeypatch):
        self._clear_env(monkeypatch)
        monkeypatch.setenv("APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK", "0")
        with mock.patch("os.name", "posix"), \
             mock.patch("shutil.which", return_value="/usr/bin/soffice"):
            result = detect_backend()
        assert result == ConversionBackend.NONE

    def test_posix_no_soffice(self, monkeypatch):
        self._clear_env(monkeypatch)
        monkeypatch.setenv("APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK", "1")
        with mock.patch("os.name", "posix"), mock.patch("shutil.which", return_value=None):
            result = detect_backend()
        assert result == ConversionBackend.NONE

    def test_override_takes_priority_over_env_var(self, monkeypatch):
        monkeypatch.setenv("APM_CONVERSION_BACKEND", "libreoffice")
        result = detect_backend(override="win32com")
        assert result == ConversionBackend.WIN32COM


# ---------------------------------------------------------------------------
# soffice_available()
# ---------------------------------------------------------------------------

class TestSofficeAvailable:
    def test_true_when_on_path(self):
        with mock.patch("shutil.which", return_value="/usr/bin/soffice"):
            assert soffice_available() is True

    def test_false_when_absent(self):
        with mock.patch("shutil.which", return_value=None):
            assert soffice_available() is False


# ---------------------------------------------------------------------------
# run_soffice_convert()
# ---------------------------------------------------------------------------

class TestRunSofficeConvert:
    @pytest.fixture
    def src(self, tmp_path):
        p = tmp_path / "document.docx"
        p.write_bytes(b"fake content")
        return p

    @pytest.fixture
    def out(self, tmp_path):
        return tmp_path / "result.pdf"

    def test_success_moves_output_to_out_path(self, src, out):
        with mock.patch("subprocess.run", side_effect=_soffice_fake_run(src)):
            run_soffice_convert(src, out)
        assert out.exists()
        assert out.read_bytes() == b"%PDF-1.4 minimal"

    def test_raises_file_not_found_when_soffice_absent(self, src, out):
        with mock.patch("subprocess.run", side_effect=FileNotFoundError()):
            with pytest.raises(FileNotFoundError, match="soffice not found on PATH"):
                run_soffice_convert(src, out)

    def test_raises_runtime_on_nonzero_exit(self, src, out):
        with mock.patch(
            "subprocess.run",
            side_effect=subprocess.CalledProcessError(1, ["soffice"], stderr=b"bad file"),
        ):
            with pytest.raises(RuntimeError, match="soffice exited with code 1"):
                run_soffice_convert(src, out)

    def test_raises_runtime_if_output_missing_after_success(self, src, out):
        # subprocess succeeds but writes nothing
        with mock.patch("subprocess.run", return_value=mock.MagicMock(returncode=0)):
            with pytest.raises(RuntimeError, match="output file was not found"):
                run_soffice_convert(src, out)

    def test_timeout_propagates(self, src, out):
        with mock.patch(
            "subprocess.run",
            side_effect=subprocess.TimeoutExpired(["soffice"], 60),
        ):
            with pytest.raises(subprocess.TimeoutExpired):
                run_soffice_convert(src, out)


# ---------------------------------------------------------------------------
# convert_docx_to_pdf() — abstraction layer
# ---------------------------------------------------------------------------

class TestConvertDocxToPdf:
    @pytest.fixture
    def src(self, tmp_path):
        p = tmp_path / "report.docx"
        p.write_bytes(b"mock docx binary")
        return p

    @pytest.fixture
    def out(self, tmp_path):
        return tmp_path / "report.pdf"

    def _mock_win32com_word(self, out_path: Path):
        """Return a mock_word whose SaveAs side-effect writes a real PDF."""
        mock_word = mock.MagicMock()
        mock_doc = mock.MagicMock()
        mock_word.Documents.Open.return_value = mock_doc

        def _save_as(dest, FileFormat):
            _write_minimal_pdf(Path(dest))

        mock_doc.SaveAs.side_effect = _save_as
        return mock_word

    def _setup_pythoncom(self):
        import sys
        sys.modules.setdefault("pythoncom", mock.MagicMock())

    def test_win32com_success_returns_empty_warnings(self, src, out):
        self._setup_pythoncom()
        mock_word = self._mock_win32com_word(out)
        with mock.patch("win32com.client.DispatchEx", return_value=mock_word, create=True):
            warnings = convert_docx_to_pdf(src, out, backend=ConversionBackend.WIN32COM)
        assert out.exists()
        assert warnings == []

    def test_libreoffice_success_returns_empty_warnings(self, src, out):
        with mock.patch("subprocess.run", side_effect=_soffice_fake_run(src)):
            warnings = convert_docx_to_pdf(src, out, backend=ConversionBackend.LIBREOFFICE)
        assert out.exists()
        assert warnings == []

    def test_none_backend_raises(self, src, out):
        with pytest.raises(RuntimeError, match="No conversion backend available"):
            convert_docx_to_pdf(src, out, backend=ConversionBackend.NONE)

    def test_missing_source_raises_file_not_found(self, tmp_path):
        missing = tmp_path / "gone.docx"
        out = tmp_path / "out.pdf"
        with pytest.raises(FileNotFoundError):
            convert_docx_to_pdf(missing, out)

    def test_win32com_fails_fallback_enabled_soffice_present(self, src, out, monkeypatch):
        monkeypatch.setenv("APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK", "1")
        self._setup_pythoncom()
        mock_word = mock.MagicMock()
        mock_word.Documents.Open.side_effect = RuntimeError("COM error")

        with mock.patch("win32com.client.DispatchEx", return_value=mock_word, create=True), \
             mock.patch("subprocess.run", side_effect=_soffice_fake_run(src)), \
             mock.patch("shutil.which", return_value="/usr/bin/soffice"):
            warnings = convert_docx_to_pdf(src, out, backend=ConversionBackend.WIN32COM)

        assert out.exists()
        assert len(warnings) == 1
        assert "LibreOffice fallback" in warnings[0]

    def test_win32com_fails_fallback_disabled_raises(self, src, out, monkeypatch):
        monkeypatch.setenv("APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK", "0")
        self._setup_pythoncom()
        mock_word = mock.MagicMock()
        mock_word.Documents.Open.side_effect = RuntimeError("COM error")

        with mock.patch("win32com.client.DispatchEx", return_value=mock_word, create=True):
            with pytest.raises(RuntimeError, match="LibreOffice fallback is disabled"):
                convert_docx_to_pdf(src, out, backend=ConversionBackend.WIN32COM)

    def test_win32com_fails_fallback_enabled_soffice_absent_raises(self, src, out, monkeypatch):
        monkeypatch.setenv("APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK", "1")
        self._setup_pythoncom()
        mock_word = mock.MagicMock()
        mock_word.Documents.Open.side_effect = RuntimeError("COM error")

        with mock.patch("win32com.client.DispatchEx", return_value=mock_word, create=True), \
             mock.patch("shutil.which", return_value=None):
            with pytest.raises(RuntimeError, match="LibreOffice fallback is disabled or unavailable"):
                convert_docx_to_pdf(src, out, backend=ConversionBackend.WIN32COM)


# ---------------------------------------------------------------------------
# convert_xlsx_to_pdf() — abstraction layer
# ---------------------------------------------------------------------------

class TestConvertXlsxToPdf:
    @pytest.fixture
    def src(self, tmp_path):
        p = tmp_path / "data.xlsx"
        p.write_bytes(b"mock xlsx binary")
        return p

    @pytest.fixture
    def out(self, tmp_path):
        return tmp_path / "data.pdf"

    def _mock_win32com_excel(self, out_path: Path):
        mock_excel = mock.MagicMock()
        mock_wb = mock.MagicMock()
        mock_excel.Workbooks.Open.return_value = mock_wb

        def _export(type_idx, dest):
            _write_minimal_pdf(Path(dest))

        mock_wb.ExportAsFixedFormat.side_effect = _export
        return mock_excel

    def _setup_pythoncom(self):
        import sys
        sys.modules.setdefault("pythoncom", mock.MagicMock())

    def test_win32com_success_returns_empty_warnings(self, src, out):
        self._setup_pythoncom()
        mock_excel = self._mock_win32com_excel(out)
        with mock.patch("win32com.client.DispatchEx", return_value=mock_excel, create=True):
            warnings = convert_xlsx_to_pdf(src, out, backend=ConversionBackend.WIN32COM)
        assert out.exists()
        assert warnings == []

    def test_libreoffice_success_returns_empty_warnings(self, src, out):
        with mock.patch("subprocess.run", side_effect=_soffice_fake_run(src)):
            warnings = convert_xlsx_to_pdf(src, out, backend=ConversionBackend.LIBREOFFICE)
        assert out.exists()
        assert warnings == []

    def test_none_backend_raises(self, src, out):
        with pytest.raises(RuntimeError, match="No conversion backend available"):
            convert_xlsx_to_pdf(src, out, backend=ConversionBackend.NONE)

    def test_missing_source_raises_file_not_found(self, tmp_path):
        missing = tmp_path / "gone.xlsx"
        out = tmp_path / "out.pdf"
        with pytest.raises(FileNotFoundError):
            convert_xlsx_to_pdf(missing, out)

    def test_win32com_fails_fallback_enabled_soffice_present(self, src, out, monkeypatch):
        monkeypatch.setenv("APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK", "1")
        self._setup_pythoncom()
        mock_excel = mock.MagicMock()
        mock_excel.Workbooks.Open.side_effect = RuntimeError("COM error")

        with mock.patch("win32com.client.DispatchEx", return_value=mock_excel, create=True), \
             mock.patch("subprocess.run", side_effect=_soffice_fake_run(src)), \
             mock.patch("shutil.which", return_value="/usr/bin/soffice"):
            warnings = convert_xlsx_to_pdf(src, out, backend=ConversionBackend.WIN32COM)

        assert out.exists()
        assert len(warnings) == 1
        assert "LibreOffice fallback" in warnings[0]

    def test_win32com_fails_fallback_disabled_raises(self, src, out, monkeypatch):
        monkeypatch.setenv("APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK", "0")
        self._setup_pythoncom()
        mock_excel = mock.MagicMock()
        mock_excel.Workbooks.Open.side_effect = RuntimeError("COM error")

        with mock.patch("win32com.client.DispatchEx", return_value=mock_excel, create=True):
            with pytest.raises(RuntimeError, match="LibreOffice fallback is disabled"):
                convert_xlsx_to_pdf(src, out, backend=ConversionBackend.WIN32COM)
