# core/operations/docx_to_pdf.py — Word to PDF operation
"""Handler for converting a Word document (.docx or .doc) to PDF.

Conversion is performed by the platform-appropriate backend:
  - Windows: Microsoft Word via win32com COM automation (primary).
  - Any platform: LibreOffice headless soffice (fallback / non-Windows primary).

The LibreOffice fallback is controlled by the APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK
environment variable (default: enabled — set to "0" to disable).
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import Callable

import pikepdf
from core.job import Job, JobResult, JobStatus, OperationCancelled, DocxToPdfParams
from core.operations._conversion_backend import (
    ConversionBackend,
    detect_backend,
    libreoffice_fallback_enabled,
    run_soffice_convert,
    soffice_available,
)


# ---------------------------------------------------------------------------
# Private backend implementation — Windows COM
# ---------------------------------------------------------------------------

def _convert_via_win32com_word(src_path: Path, out_path: Path) -> None:
    """
    Convert *src_path* (Word document) to PDF at *out_path* via win32com COM automation.

    Requires Windows OS, Microsoft Word installed, and the pywin32 package.

    Raises:
        Exception: Any COM-level or win32com error propagates to the caller.
    """
    import win32com.client
    import pythoncom

    pythoncom.CoInitialize()
    word = None
    doc = None
    try:
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = False
        doc = word.Documents.Open(str(src_path.resolve()), ReadOnly=True)
        doc.SaveAs(str(out_path.resolve()), FileFormat=17)  # 17 = wdFormatPDF
    finally:
        if doc:
            try:
                doc.Close(SaveChanges=0)
            except Exception:
                pass
        if word:
            try:
                word.Quit()
            except Exception:
                pass
        pythoncom.CoUninitialize()


# ---------------------------------------------------------------------------
# Public abstraction function
# ---------------------------------------------------------------------------

def convert_docx_to_pdf(
    src_path: Path,
    out_path: Path,
    backend: ConversionBackend | None = None,
) -> list[str]:
    """
    Convert a Word document (.docx / .doc) to PDF.

    This is the single public entry point for Word-to-PDF conversion.  It
    selects the appropriate backend automatically (or uses the supplied *backend*)
    and delegates to the platform-specific implementation.

    Backend cascade on Windows:
      1. Attempt win32com (Microsoft Word COM automation).
      2. If win32com fails AND APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK is enabled
         AND soffice is on PATH: fall back to LibreOffice and emit a warning.
      3. If both fail (or fallback is disabled): raise RuntimeError.

    Backend on non-Windows:
      - LibreOffice soffice is used directly if available and enabled.
      - If unavailable: raise RuntimeError.

    Args:
        src_path: Path to the source Word document.
        out_path: Destination path for the output PDF.
        backend:  Optional ConversionBackend override.  If None, detect_backend()
                  is called to auto-select the appropriate backend.

    Returns:
        A list of warning strings (empty on a clean, warning-free conversion).

    Raises:
        FileNotFoundError: If src_path does not exist, or soffice is absent from PATH.
        RuntimeError: If all available backends fail, or no backend is available.
    """
    if not src_path.exists():
        raise FileNotFoundError(f"Source file not found: {src_path}")

    if backend is None:
        backend = detect_backend()

    warnings: list[str] = []

    if backend == ConversionBackend.WIN32COM:
        try:
            _convert_via_win32com_word(src_path, out_path)
        except Exception as win32_exc:
            if libreoffice_fallback_enabled() and soffice_available():
                warnings.append(
                    f"Win32com Word export failed: {win32_exc}. "
                    "Using LibreOffice fallback."
                )
                run_soffice_convert(src_path, out_path)
            else:
                raise RuntimeError(
                    f"Word conversion failed (win32com): {win32_exc}. "
                    "LibreOffice fallback is disabled or unavailable "
                    "(set APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK=1 to enable)."
                ) from win32_exc

    elif backend == ConversionBackend.LIBREOFFICE:
        run_soffice_convert(src_path, out_path)

    else:  # ConversionBackend.NONE
        raise RuntimeError(
            "No conversion backend available for Word documents. "
            "On Windows: install Microsoft Office. "
            "On macOS/Linux: install LibreOffice and ensure 'soffice' is on PATH."
        )

    return warnings


# ---------------------------------------------------------------------------
# Engine handler (Job-level entry point)
# ---------------------------------------------------------------------------

def handle(job: Job, progress: Callable[[str, float], None]) -> JobResult:
    """Core engine entry point for the *docx_to_pdf* operation."""
    params: DocxToPdfParams = job.params
    if len(job.inputs) != 1:
        raise ValueError("DocxToPdf operation requires exactly one input specification.")

    def check_cancelled() -> None:
        if job.status == JobStatus.CANCELLED:
            raise OperationCancelled("Word conversion was cancelled by user.")

    input_spec = job.inputs[0]
    src_path = Path(input_spec.path)
    if not src_path.exists():
        raise FileNotFoundError(f"Source file not found: {src_path}")

    temp_files: list[Path] = []

    try:
        check_cancelled()
        progress("Starting Word conversion ...", 0.1)

        out_dir = Path(job.output.directory)
        out_dir.mkdir(parents=True, exist_ok=True)

        default_name = src_path.stem + ".pdf"
        output_name = params.output_name or default_name
        final_dest = out_dir / output_name

        tmp_pdf = Path(tempfile.mktemp(suffix=".pdf"))
        temp_files.append(tmp_pdf)

        backend = detect_backend()
        progress(f"Backend: {backend.value} ...", 0.2)

        check_cancelled()
        progress("Converting document ...", 0.4)

        conv_warnings = convert_docx_to_pdf(src_path, tmp_pdf, backend)

        check_cancelled()
        progress("Finalising output file ...", 0.9)

        if final_dest.exists() and not job.output.overwrite:
            stem = final_dest.stem
            ext = final_dest.suffix
            counter = 1
            while final_dest.exists():
                final_dest = out_dir / f"{stem}_{counter:02d}{ext}"
                counter += 1

        shutil.move(str(tmp_pdf), str(final_dest))

        page_count = 0
        try:
            with pikepdf.open(final_dest) as pdf:
                page_count = len(pdf.pages)
        except Exception:
            pass

        progress("Done.", 1.0)
        return JobResult(
            outputs=[final_dest],
            page_count_in=page_count,
            page_count_out=page_count,
            warnings=conv_warnings,
            error=None,
        )

    finally:
        for tmp in temp_files:
            try:
                if tmp.exists():
                    tmp.unlink()
            except Exception:
                pass
