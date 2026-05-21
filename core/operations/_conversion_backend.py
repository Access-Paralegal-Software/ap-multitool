"""
core/operations/_conversion_backend.py — backend selection for Office-to-PDF conversion.

Centralises the logic that chooses between the Windows COM (win32com) path and the
cross-platform LibreOffice/soffice path.  Both handlers (docx_to_pdf, xlsx_to_pdf)
can import detect_backend() so the selection rule lives in one place and is testable.

Current callers still implement inline `if os.name == 'nt':` logic that matches the
behaviour of detect_backend().  This module is the designated consolidation point;
the handlers will be updated to call it directly in a future batch.
"""

from __future__ import annotations

import os
import shutil
from enum import Enum


class ConversionBackend(str, Enum):
    WIN32COM    = "win32com"     # Windows + Microsoft Office via COM automation
    LIBREOFFICE = "libreoffice"  # headless soffice CLI (macOS / Linux / Windows fallback)
    NONE        = "none"         # no backend available — conversion will fail


def detect_backend(override: str | None = None) -> ConversionBackend:
    """
    Return the preferred conversion backend for the current environment.

    Selection order:
      1. If *override* is provided, honour it (useful for testing or operator config).
      2. On Windows, prefer WIN32COM (requires Microsoft Office to be installed).
      3. If soffice is discoverable on PATH, use LIBREOFFICE.
      4. Otherwise, return NONE.

    Args:
        override: Optional string matching a ConversionBackend value, e.g.
                  "libreoffice" or "win32com".  An unrecognised value is ignored.

    Returns:
        A ConversionBackend enum value.

    Future config hooks (not yet wired):
        - config.CONVERSION_BACKEND_OVERRIDE
        - env var: APM_CONVERSION_BACKEND
        - CLI flag: --backend libreoffice
    """
    if override:
        try:
            return ConversionBackend(override.lower())
        except ValueError:
            pass  # unrecognised override — fall through to auto-detection

    if os.name == "nt":
        return ConversionBackend.WIN32COM

    if shutil.which("soffice") is not None:
        return ConversionBackend.LIBREOFFICE

    return ConversionBackend.NONE


def soffice_available() -> bool:
    """Return True if the soffice binary is discoverable on PATH."""
    return shutil.which("soffice") is not None
