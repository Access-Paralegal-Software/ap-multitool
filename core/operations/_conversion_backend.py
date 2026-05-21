"""
core/operations/_conversion_backend.py — backend selection + shared utilities
for Office-to-PDF conversion.

Responsibilities:
  - ConversionBackend enum: names the supported backend paths.
  - libreoffice_fallback_enabled(): reads the APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK flag.
  - detect_backend(): choose the right primary backend for the current environment.
  - soffice_available(): check whether soffice is on PATH.
  - run_soffice_convert(): shared headless LibreOffice subprocess invocation.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from enum import Enum
from pathlib import Path


class ConversionBackend(str, Enum):
    WIN32COM    = "win32com"     # Windows + Microsoft Office via COM automation
    LIBREOFFICE = "libreoffice"  # headless soffice CLI (macOS / Linux / Windows fallback)
    NONE        = "none"         # no backend available — conversion will fail


def libreoffice_fallback_enabled() -> bool:
    """
    Return True if the LibreOffice fallback/backend is enabled.

    Reads APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK from the environment.
    Defaults to True (enabled) for backward compatibility with the pre-flag behavior.

    To disable:
        set APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK=0   (or false / no / off)
    """
    val = os.environ.get("APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK", "1")
    return val.lower() not in ("0", "false", "no", "off")


def detect_backend(override: str | None = None) -> ConversionBackend:
    """
    Return the preferred PRIMARY conversion backend for the current environment.

    Selection order:
      1. Explicit *override* parameter (for tests / one-off operator overrides).
      2. APM_CONVERSION_BACKEND environment variable.
      3. Windows (os.name == 'nt') → WIN32COM (Microsoft Office preferred).
      4. Non-Windows + soffice on PATH + LibreOffice fallback enabled → LIBREOFFICE.
      5. → NONE (no backend available).

    Note: on Windows, this always returns WIN32COM.  Whether LibreOffice is tried
    when win32com fails at runtime is controlled separately by
    libreoffice_fallback_enabled() inside convert_docx_to_pdf / convert_xlsx_to_pdf.

    Args:
        override: Optional string matching a ConversionBackend value.
                  An unrecognised value is silently ignored (falls through to auto-detect).
    """
    # 1. Caller-supplied override
    if override:
        try:
            return ConversionBackend(override.lower())
        except ValueError:
            pass

    # 2. Environment variable override
    env_val = os.environ.get("APM_CONVERSION_BACKEND")
    if env_val:
        try:
            return ConversionBackend(env_val.lower())
        except ValueError:
            pass

    # 3. Windows — prefer COM automation
    if os.name == "nt":
        return ConversionBackend.WIN32COM

    # 4. Non-Windows — use LibreOffice if available and enabled
    if libreoffice_fallback_enabled() and shutil.which("soffice") is not None:
        return ConversionBackend.LIBREOFFICE

    return ConversionBackend.NONE


def soffice_available() -> bool:
    """Return True if the soffice binary is discoverable on PATH."""
    return shutil.which("soffice") is not None


def run_soffice_convert(src_path: Path, out_path: Path, timeout: int = 60) -> None:
    """
    Invoke headless LibreOffice (soffice) to convert src_path to a PDF at out_path.

    Uses an isolated temporary directory for soffice output to prevent file naming
    collisions and partial writes at the final destination path.

    Args:
        src_path: Absolute path to the source document (.docx, .xlsx, etc.).
        out_path: Destination path for the produced PDF file.
        timeout:  Maximum seconds to wait for soffice (default 60).

    Raises:
        FileNotFoundError: If soffice is not found on PATH.
        RuntimeError: If soffice exits with a non-zero code, or the expected output
                      file is not produced after a reported success.
        subprocess.TimeoutExpired: If soffice does not finish within *timeout* seconds.
    """
    with tempfile.TemporaryDirectory() as _tmp:
        tmp_dir = Path(_tmp)

        try:
            subprocess.run(
                [
                    "soffice",
                    "--headless",
                    "--convert-to", "pdf",
                    "--outdir", str(tmp_dir),
                    str(src_path.resolve()),
                ],
                capture_output=True,
                timeout=timeout,
                check=True,
            )
        except FileNotFoundError:
            raise FileNotFoundError(
                "soffice not found on PATH. "
                "Install LibreOffice to use the fallback conversion backend."
            )
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.decode(errors="replace") if exc.stderr else ""
            raise RuntimeError(
                f"soffice exited with code {exc.returncode}. {stderr}".strip()
            ) from exc

        converted = tmp_dir / (src_path.stem + ".pdf")
        if not converted.exists():
            raise RuntimeError(
                f"soffice reported success but output file was not found: {converted}. "
                "Verify the source file is a valid document."
            )

        shutil.move(str(converted), str(out_path))
