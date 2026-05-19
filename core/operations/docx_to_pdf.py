# core/operations/docx_to_pdf.py — Word to PDF operation
"""Handler for converting a Word document (.docx or .doc) to PDF.

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
from core.job import Job, JobResult, JobStatus, OperationCancelled, DocxToPdfParams


def handle(job: Job, progress: Callable[[str, float], None]) -> JobResult:
    """Core engine entry point for the *docx_to_pdf* operation."""
    params: DocxToPdfParams = job.params
    if len(job.inputs) != 1:
        raise ValueError("DocxToPdf operation requires exactly one input specification.")

    def check_cancelled():
        if job.status == JobStatus.CANCELLED:
            raise OperationCancelled("Word conversion was cancelled by user.")

    input_spec = job.inputs[0]
    src_path = Path(input_spec.path)
    if not src_path.exists():
        raise FileNotFoundError(f"Source file not found: {src_path}")

    warnings: list[str] = []
    temp_files: list[Path] = []

    try:
        check_cancelled()
        progress("Starting Word conversion ...", 0.1)

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
                progress("Initializing COM and Microsoft Word ...", 0.3)
                import win32com.client
                import pythoncom
                
                pythoncom.CoInitialize()
                word = None
                doc = None
                try:
                    word = win32com.client.DispatchEx("Word.Application")
                    word.Visible = False
                    word.DisplayAlerts = False
                    
                    check_cancelled()
                    progress("Opening Word document ...", 0.5)
                    
                    doc = word.Documents.Open(str(src_path.resolve()), ReadOnly=True)
                    check_cancelled()
                    
                    progress("Saving document as PDF ...", 0.7)
                    doc.SaveAs(str(tmp_pdf.resolve()), FileFormat=17) # 17 = wdFormatPDF
                    success = tmp_pdf.exists()
                finally:
                    if doc:
                        try: doc.Close(SaveChanges=0)
                        except Exception: pass
                    if word:
                        try: word.Quit()
                        except Exception: pass
                    pythoncom.CoUninitialize()
            except Exception as win32_exc:
                warnings.append(f"Win32com Word export failed: {win32_exc}. Attempting LibreOffice fallback.")

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
                    f"Word conversion failed. Both Microsoft Word automation and LibreOffice fallback failed.\n"
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
