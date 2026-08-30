"""Central configuration for Access Paralegal Multitool."""

import os

__version__ = "v1.0.0-beta1"
APP_NAME = "Access Paralegal Multitool"

CONVERSION_BACKEND_OVERRIDE: str | None = os.environ.get("APM_CONVERSION_BACKEND")
LIBREOFFICE_FALLBACK_ENABLED: bool = os.environ.get(
    "APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK", "1"
).lower() not in ("0", "false", "no", "off")

PAYWALL_ENFORCED: bool = os.environ.get(
    "APM_PAYWALL_ENFORCED", "1"
).lower() in ("1", "true", "yes", "on")
TRIAL_DURATION_DAYS: int = int(os.environ.get("APM_TRIAL_DAYS", "14"))
