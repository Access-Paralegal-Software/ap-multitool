"""Central logging configuration for APMultitool."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import TextIO


LOG_ROOT_NAME = "apmultitool"
LEGACY_LOGGER_NAME = "APMultitool"
LOG_LEVEL_ENV_VAR = "APMULTITOOL_LOG_LEVEL"
LOG_FILE_ENV_VAR = "APMULTITOOL_LOG_FILE"
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_FILE_FORMAT = "%(asctime)s %(name)s %(levelname)s %(message)s"
DEFAULT_STREAM_FORMAT = "[%(levelname)s] %(message)s"


def _normalize_level_name(value: str | None) -> str:
    candidate = (value or DEFAULT_LOG_LEVEL).upper()
    return candidate if candidate in logging._nameToLevel else DEFAULT_LOG_LEVEL


def resolve_log_level(level_override: str | None = None) -> int:
    """Resolve the effective log level from override or environment."""
    source = level_override or os.environ.get(LOG_LEVEL_ENV_VAR) or DEFAULT_LOG_LEVEL
    return logging._nameToLevel[_normalize_level_name(source)]


def get_default_log_dir() -> Path:
    """Return the default per-user log directory."""
    if os.name == "nt":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            return Path(local_app_data) / "Access_Paralegal_Multitool" / "logs"
        return Path.home() / "AppData" / "Local" / "Access_Paralegal_Multitool" / "logs"
    return Path.home() / ".access_paralegal_logs"


def get_log_file_path() -> Path:
    """Return the configured log file path."""
    override = os.environ.get(LOG_FILE_ENV_VAR)
    if override:
        return Path(override).expanduser()
    return get_default_log_dir() / "apmultitool.log"


def safe_filename(pathish: str | Path | None) -> str:
    """Return a filename-only value safe for logs."""
    if pathish is None:
        return "<unknown>"
    return Path(str(pathish)).name or "<unknown>"


def _remove_managed_handlers(logger: logging.Logger) -> None:
    for handler in list(logger.handlers):
        if getattr(handler, "_apmultitool_managed", False):
            logger.removeHandler(handler)
            try:
                handler.close()
            except Exception:
                pass


def _ensure_legacy_alias(root: logging.Logger) -> None:
    legacy = logging.getLogger(LEGACY_LOGGER_NAME)
    legacy.setLevel(root.level)
    legacy.propagate = False
    _remove_managed_handlers(legacy)
    for handler in root.handlers:
        legacy.addHandler(handler)


def configure_logging(
    level_override: str | None = None,
    *,
    stream: TextIO | None = None,
    stream_format: str | None = None,
    force: bool = False,
) -> logging.Logger:
    """Configure the shared local log file and optional stream output."""
    root = logging.getLogger(LOG_ROOT_NAME)
    root.setLevel(resolve_log_level(level_override))
    root.propagate = False

    if force:
        _remove_managed_handlers(root)

    if not any(getattr(handler, "_apmultitool_file", False) for handler in root.handlers):
        log_file = get_log_file_path()
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(DEFAULT_FILE_FORMAT))
        file_handler._apmultitool_managed = True
        file_handler._apmultitool_file = True
        root.addHandler(file_handler)

    if stream is not None:
        existing_stream = next(
            (handler for handler in root.handlers if getattr(handler, "_apmultitool_stream", False)),
            None,
        )
        formatter = logging.Formatter(stream_format or DEFAULT_STREAM_FORMAT)
        if existing_stream is None:
            stream_handler = logging.StreamHandler(stream)
            stream_handler.setFormatter(formatter)
            stream_handler._apmultitool_managed = True
            stream_handler._apmultitool_stream = True
            root.addHandler(stream_handler)
        else:
            existing_stream.setStream(stream)
            existing_stream.setFormatter(formatter)

    _ensure_legacy_alias(root)
    return root


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a logger under the shared APMultitool namespace."""
    configure_logging()
    if not name:
        return logging.getLogger(LOG_ROOT_NAME)
    prefix = LOG_ROOT_NAME + "."
    normalized = name[len(prefix):] if name.startswith(prefix) else name
    return logging.getLogger(f"{LOG_ROOT_NAME}.{normalized}")


def flush_handlers() -> None:
    """Flush managed handlers so support bundles can capture recent logs."""
    for handler in logging.getLogger(LOG_ROOT_NAME).handlers:
        try:
            handler.flush()
        except Exception:
            pass


def configure_cli_logging(args: object) -> logging.Logger:
    """Configure shared logging for CLI execution."""
    if getattr(args, "silent", False) or getattr(args, "quiet", False):
        level_override = "ERROR"
        stream_format = DEFAULT_STREAM_FORMAT
    elif getattr(args, "verbose", False):
        level_override = "DEBUG"
        stream_format = "%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) %(message)s"
    else:
        level_override = getattr(args, "log_level", None)
        stream_format = DEFAULT_STREAM_FORMAT

    configure_logging(level_override, stream=sys.stderr, stream_format=stream_format)
    return get_logger("cli")
