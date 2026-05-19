# core/operations/xlsx_to_pdf.py — Excel to PDF operation
"""Handler for converting an Excel spreadsheet (.xlsx, .xls, .csv) to PDF.

Enforces win32com application automation on Windows, with a subprocess fallback
to LibreOffice/soffice if win32com fails or is unavailable.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable

import pikepdf
from core.job import Job, JobResult, JobStatus, OperationCancelled, XlsxToPdfParams


def handle(job: Job, progress: Callable[[str, float], None]) -> JobResult:
    """Core engine entry point for the *xlsx_to_pdf* operation."""
    params: XlsxToPdfParams = job.params
    if len(job.inputs) != 1:
        raise ValueError("XlsxToPdf operation requires exactly one input specification.")

    def check_cancelled():
        if job.status == JobStatus.CANCELLED:
            raise OperationCancelled("Excel conversion was cancelled by user.")

    input_spec = job.inputs[0]
    src_path = Path(input_spec.path)
    if not src_path.exists():
        raise FileNotFoundError(f"Source file not found: {src_path}")

    warnings: list[str] = []
    temp_files: list[Path] = []

    try:
        check_cancelled()
        progress("Starting Excel conversion ...", 0.1)

        # Output folder and name
        out_dir = Path(job.output.directory)
        out_dir.mkdir(parents=True, exist_ok=True)
        
        default_name = src_path.stem + ".pdf"
        output_name = params.output_name or default_name
        final_dest = out_dir / output_name

        tmp_pdf = Path(tempfile.mktemp(suffix=".pdf"))
        temp_files.append(tmp_pdf)

        success = False

        # ---------------------------------------------------------------------
        # Try win32com Native Office automation first (if on Windows)
        # ---------------------------------------------------------------------
        if os.name == 'nt':
            try:
                progress("Initializing COM and Microsoft Excel ...", 0.3)
                import win32com.client
                import pythoncom
                
                pythoncom.CoInitialize()
                excel = None
                wb = None
                try:
                    excel = win32com.client.DispatchEx("Excel.Application")
                    excel.Visible = False
                    excel.DisplayAlerts = False
                    
                    check_cancelled()
                    progress("Opening Excel workbook ...", 0.5)
                    
                    wb = excel.Workbooks.Open(str(src_path.resolve()), ReadOnly=True)
                    check_cancelled()
                    
                    progress("Exporting workbook sheets to PDF ...", 0.7)
                    wb.ExportAsFixedFormat(0, str(tmp_pdf.resolve())) # 0 = xlTypePDF
                    success = tmp_pdf.exists()
                finally:
                    if wb:
                        try: wb.Close(SaveChanges=False)
                        except Exception: pass
                    if excel:
                        try: excel.Quit()
                        except Exception: pass
                    pythoncom.CoUninitialize()
            except Exception as win32_exc:
                warnings.append(f"Win32com Excel export failed: {win32_exc}. Attempting LibreOffice fallback.")

        # ---------------------------------------------------------------------
        # Fallback to LibreOffice / soffice CLI
        # ---------------------------------------------------------------------
        if not success:
            check_cancelled()
            progress("Invoking LibreOffice converter ...", 0.4)
            try:
                # soffice prints output directly in outdir.
                result = subprocess.run(
                    ["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(tmp_pdf.parent), str(src_path.resolve())],
                    capture_output=True, timeout=60, check=True
                )
                converted_file = tmp_pdf.parent / (src_path.stem + ".pdf")
                if converted_file.exists():
                    shutil.move(str(converted_file), str(tmp_pdf))
                    success = tmp_pdf.exists()
            except Exception as subprocess_exc:
                raise RuntimeError(
                    f"Excel conversion failed. Both Microsoft Excel automation and LibreOffice fallback failed.\n"
                    f"LibreOffice error: {subprocess_exc}"
                )

        check_cancelled()
        progress("Finalising output file ...", 0.9)

        # Move to destination
        if final_dest.exists() and not job.output.overwrite:
            # Append suffix to avoid overwrite if option is False
            stem = final_dest.stem
            ext = final_dest.suffix
            counter = 1
            while final_dest.exists():
                final_dest = out_dir / f"{stem}_{counter:02d}{ext}"
                counter += 1

        shutil.move(str(tmp_pdf), str(final_dest))

        # Check page count
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
            warnings=warnings,
            error=None
        )

    finally:
        for tmp in temp_files:
            try:
                if tmp.exists():
                    tmp.unlink()
            except Exception:
                pass
