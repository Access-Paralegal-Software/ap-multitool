# core/support.py
"""
APMultitool support bundle generation module.

Handles local offline support bundle collection:
- Locates log directories and files
- Locates telemetry file
- Collects environment metadata
- Scrubs sensitive paths / PII
- Assembles zipped diagnostic bundle
"""

from __future__ import annotations

import getpass
import json
import logging
import os
import platform
import re
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import config
import core
from core.logging_config import configure_logging, flush_handlers, get_log_file_path, get_logger

def get_log_dir() -> Path:
    """
    Return the standard log directory for the current OS.
    - Windows: %LOCALAPPDATA%\\Access_Paralegal_Multitool\\logs
    - macOS/Linux: ~/.access_paralegal_logs
    """
    return get_log_file_path().parent

def setup_app_logging() -> logging.Logger:
    """Configure standard rotating file logger. Returns the ui.main logger instance."""
    configure_logging()
    return get_logger("ui.main")


def get_display_scaling() -> str:
    """
    Retrieve the primary screen display scaling factor on Windows,
    or return 100% on other platforms.
    """
    if os.name == "nt":
        try:
            import ctypes
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(2) # PROCESS_PER_MONITOR_DPI_AWARE
            except Exception:
                try:
                    ctypes.windll.user32.SetProcessDPIAware()
                except Exception:
                    pass
            scale = ctypes.windll.shcore.GetScaleFactorForDevice(0)
            return f"{scale}%"
        except Exception:
            pass
    return "100%"

def get_libreoffice_path() -> str | None:
    """
    Find the LibreOffice soffice binary path if installed.
    """
    soffice_name = "soffice.exe" if os.name == "nt" else "soffice"
    p = shutil.which(soffice_name)
    if p:
        return str(Path(p).resolve())
    if os.name == "nt":
        # Check standard installation locations
        common_paths = [
            Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "LibreOffice" / "program" / "soffice.exe",
            Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "LibreOffice" / "program" / "soffice.exe",
        ]
        for cp in common_paths:
            if cp.exists():
                return str(cp.resolve())
    return None

def check_ms_office_presence() -> tuple[bool, bool, bool]:
    """
    Check if Microsoft Word and Excel COM automation are available on Windows.
    Returns (office_installed, word_present, excel_present).
    """
    if os.name != "nt":
        return False, False, False

    word_present = False
    excel_present = False
    word = None
    excel = None

    try:
        import win32com.client
        import pythoncom
        pythoncom.CoInitialize()
        try:
            word = win32com.client.DispatchEx("Word.Application")
            word_present = True
            try:
                word.Quit()
            except Exception:
                pass
        except Exception:
            pass
        finally:
            word = None

        try:
            excel = win32com.client.DispatchEx("Excel.Application")
            excel_present = True
            try:
                excel.Quit()
            except Exception:
                pass
        except Exception:
            pass
        finally:
            excel = None

        pythoncom.CoUninitialize()
    except Exception:
        pass

    return (word_present or excel_present), word_present, excel_present

def get_user_profiles_to_scrub() -> list[str]:
    """
    Gather a list of paths and usernames to search and scrub in diagnostic text.
    Sorted by length in descending order.
    """
    candidates = []
    for env_var in ["USERPROFILE", "HOME", "HOMEPATH"]:
        val = os.environ.get(env_var)
        if val:
            candidates.append(os.path.normpath(val))
            candidates.append(val.replace("\\", "/"))
    try:
        candidates.append(os.path.expanduser("~"))
    except Exception:
        pass
    try:
        username = getpass.getuser()
        if username:
            candidates.append(username)
    except Exception:
        pass

    # Normalize paths and gather unique values
    normalized = []
    for c in candidates:
        if c:
            normalized.append(c)
            try:
                normalized.append(os.path.abspath(c))
            except Exception:
                pass

    valid = []
    for p in set(normalized):
        p_clean = p.strip()
        # Do not scrub paths that are too short to avoid false positives (e.g. "C:", "/")
        if len(p_clean) > 3:
            valid.append(p_clean)

    return sorted(valid, key=len, reverse=True)

def scrub_text(text: str, profiles: list[str]) -> str:
    """
    Replace occurrences of sensitive path patterns or usernames in text with <USERPROFILE>.
    """
    if not text:
        return text
    scrubbed = text
    for p in profiles:
        # Check case-insensitive pattern replacement
        pattern = re.escape(p)
        scrubbed = re.sub(pattern, "<USERPROFILE>", scrubbed, flags=re.IGNORECASE)
        # Check for forward slash alternative
        p_alt = p.replace("\\", "/")
        if p_alt != p:
            pattern_alt = re.escape(p_alt)
            scrubbed = re.sub(pattern_alt, "<USERPROFILE>", scrubbed, flags=re.IGNORECASE)
    return scrubbed

def create_support_bundle(target_dir: Path | None = None, display_scaling: str | None = None) -> Path:
    """
    Create a local support bundle ZIP package containing metadata, local telemetry,
    and application logs with sensitive user profiles scrubbed.
    
    Args:
        target_dir: Directory where the zip file should be saved.
                    If None, defaults to the user's Desktop (or current working directory if Desktop doesn't exist).
        display_scaling: Explicit override for display scaling info (e.g. "125%").
        
    Returns:
        Path of the generated ZIP file.
    """
    logger = get_logger("support.bundle")
    if target_dir is None:
        desktop = Path.home() / "Desktop"
        if desktop.exists():
            target_dir = desktop
        else:
            target_dir = Path.cwd()
    else:
        target_dir = Path(target_dir)

    target_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    file_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"apmultitool_support_bundle_{file_timestamp}.zip"
    zip_path = target_dir / zip_name
    logger.info("support_bundle_started bundle_filename=%s", zip_name)

    # Gather environment profiles for scrubbing
    profiles = get_user_profiles_to_scrub()

    # 1. Gather Metadata
    office_installed, word_present, excel_present = check_ms_office_presence()
    libreoffice_path = get_libreoffice_path()
    
    # Scrub libreoffice path if found
    if libreoffice_path:
        libreoffice_path = scrub_text(libreoffice_path, profiles)

    libreoffice_fallback_enabled = getattr(config, "LIBREOFFICE_FALLBACK_ENABLED", True)
    active_backend_override = getattr(config, "CONVERSION_BACKEND_OVERRIDE", None)

    metadata = {
        "timestamp": timestamp,
        "app": {
            "version": getattr(core, "__version__", "1.0.0"),
            "channel": getattr(core, "__channel__", ""),
            "build_id": f"v{getattr(core, '__version__', '1.0.0')}{getattr(core, '__channel__', '')}"
        },
        "environment": {
            "os_platform": platform.platform(),
            "os_release": platform.release(),
            "python_version": platform.python_version(),
            "display_scaling": display_scaling or get_display_scaling()
        },
        "engines": {
            "office_installed": office_installed,
            "word_present": word_present,
            "excel_present": excel_present,
            "libreoffice_path": libreoffice_path,
            "libreoffice_fallback_enabled": libreoffice_fallback_enabled,
            "active_backend_override": active_backend_override
        }
    }

    # Scrub metadata json values as double precaution
    metadata_json_str = json.dumps(metadata, indent=2)
    metadata_json_str = scrub_text(metadata_json_str, profiles)

    # 2. Retrieve Telemetry File
    telemetry_path = Path.home() / ".access_paralegal_telemetry.json"
    telemetry_content = "{}"
    if telemetry_path.exists():
        try:
            with open(telemetry_path, "r", encoding="utf-8", errors="replace") as f:
                raw_telemetry = f.read()
                telemetry_content = scrub_text(raw_telemetry, profiles)
        except Exception:
            pass

    # 3. Retrieve log files
    log_dir = get_log_dir()
    logs_to_zip = [] # list of (archive_name, content_str)
    flush_handlers()
    if log_dir.exists():
        for log_file in log_dir.glob("apmultitool.log*"):
            if log_file.is_file():
                try:
                    with open(log_file, "r", encoding="utf-8", errors="replace") as f:
                        raw_log = f.read()
                        scrubbed_log = scrub_text(raw_log, profiles)
                        logs_to_zip.append((f"logs/{log_file.name}", scrubbed_log))
                except Exception:
                    pass

    # 4. Compile ZIP Archive
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("metadata.json", metadata_json_str)
        z.writestr("telemetry.json", telemetry_content)
        for arcname, content in logs_to_zip:
            z.writestr(arcname, content)

    logger.info(
        "support_bundle_completed bundle_filename=%s log_files=%s telemetry_present=%s",
        zip_name,
        len(logs_to_zip),
        telemetry_path.exists(),
    )
    return zip_path
