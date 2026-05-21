# config.py

"""Central configuration for Access Paralegal Multitool (APMultitool)."""

import os

# Semantic version for the release – update as needed.
__version__ = "v1.0.0-alpha1"

# Application name used throughout UI and docs.
APP_NAME = "Access Paralegal Multitool"

# ---------------------------------------------------------------------------
# Document conversion settings
# ---------------------------------------------------------------------------

# Set APM_CONVERSION_BACKEND=libreoffice (or win32com) to override auto-detection.
CONVERSION_BACKEND_OVERRIDE: str | None = os.environ.get("APM_CONVERSION_BACKEND")

# Controls whether the LibreOffice/soffice fallback is enabled.
# Default: "1" (enabled) — preserves backward compatibility.
# Set APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK=0 to disable the fallback entirely.
LIBREOFFICE_FALLBACK_ENABLED: bool = os.environ.get(
    "APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK", "1"
).lower() not in ("0", "false", "no", "off")
