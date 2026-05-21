# core/operations/xlsx_to_pdf.py — Excel to PDF operation
"""Handler for converting an Excel spreadsheet (.xlsx, .xls, .csv) to PDF.

Conversion is performed by the platform-appropriate backend:
  - Windows: Microsoft Excel via win32com COM automation (primary).
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
from core.job import Job, JobResult, JobStatus, OperationCancelled, XlsxToPdfParams
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

def _convert_via_win32com_excel(src_path: Path, out_path: Path) -> None:
    """
    Convert *src_path* (Excel workbook) to PDF at *out_path* via win32com COM automation.

    Requires Windows OS, Microsoft Excel installed, and the pywin32 package.

    Raises:
        Exception: Any COM-level or win32com error propagates to the caller.
    """
    import win32com.client
    import pythoncom

    pythoncom.CoInitialize()
    excel = None
    wb = None
    try:
        excel = win32com.client.DispatchEx("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        wb = excel.Workbooks.Open(str(src_path.resolve()), ReadOnly=True)
        wb.ExportAsFixedFormat(0, str(out_path.resolve()))  # 0 = xlTypePDF
    finally:
        if wb:
            try:
                wb.Close(SaveChanges=False)
            except Exception:
                pass
        if excel:
            try:
                excel.Quit()
            except Exception:
                pass
        pythoncom.CoUninitialize()


# ---------------------------------------------------------------------------
# Public abstraction function
# ---------------------------------------------------------------------------

def convert_xlsx_to_pdf(
    src_path: Path,
    out_path: Path,
    backend: ConversionBackend | None = None,
) -> list[str]:
    """
    Convert an Excel workbook (.xlsx / .xls / .csv) to PDF.

    This is the single public entry point for Excel-to-PDF conversion.  It
    selects the appropriate backend automatically (or uses the supplied *backend*)
    and delegates to the platform-specific implementation.

    Backend cascade on Windows:
      1. Attempt win32com (Microsoft Excel COM automation).
      2. If win32com fails AND APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK is enabled
         AND soffice is on PATH: fall back to LibreOffice and emit a warning.
      3. If both fail (or fallback is disabled): raise RuntimeError.

    Backend on non-Windows:
      - LibreOffice soffice is used directly if available and enabled.
      - If unavailable: raise RuntimeError.

    Args:
        src_path: Path to the source Excel workbook.
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
            _convert_via_win32com_excel(src_path, out_path)
        except Exception as win32_exc:
            if libreoffice_fallback_enabled() and soffice_available():
                warnings.append(
                    f"Win32com Excel export failed: {win32_exc}. "
                    "Using LibreOffice fallback."
                )
                run_soffice_convert(src_path, out_path)
            else:
                raise RuntimeError(
                    f"Excel conversion failed (win32com): {win32_exc}. "
                    "LibreOffice fallback is disabled or unavailable "
                    "(set APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK=1 to enable)."
                ) from win32_exc

    elif backend == ConversionBackend.LIBREOFFICE:
        run_soffice_convert(src_path, out_path)

    else:  # ConversionBackend.NONE
        raise RuntimeError(
            "No conversion backend available for Excel documents. "
            "On Windows: install Microsoft Office. "
            "On macOS/Linux: install LibreOffice and ensure 'soffice' is on PATH."
        )

    return warnings


# ---------------------------------------------------------------------------
# Engine handler (Job-level entry point)
# ---------------------------------------------------------------------------

def handle(job: Job, progress: Callable[[str, float], None]) -> JobResult:
    """Core engine entry point for the *xlsx_to_pdf* operation."""
    params: XlsxToPdfParams = job.params
    if len(job.inputs) != 1:
        raise ValueError("XlsxToPdf operation requires exactly one input specification.")

    def check_cancelled() -> None:
        if job.status == JobStatus.CANCELLED:
            raise OperationCancelled("Excel conversion was cancelled by user.")

    input_spec = job.inputs[0]
    src_path = Path(input_spec.path)
    if not src_path.exists():
        raise FileNotFoundError(f"Source file not found: {src_path}")

    temp_files: list[Path] = []

    try:
        check_cancelled()
        progress("Starting Excel conversion ...", 0.1)

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
        progress("Converting workbook ...", 0.4)

        conv_warnings = convert_xlsx_to_pdf(src_path, tmp_pdf, backend)

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
