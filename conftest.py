# conftest.py — pytest configuration and marker registration
import os
import sys
from unittest.mock import MagicMock
import pytest

# Ensure win32com and submodules exist in sys.modules on non-Windows platforms so mock.patch works
if sys.platform != "win32":
    win32com_mock = MagicMock()
    client_mock = MagicMock()
    win32com_mock.client = client_mock
    sys.modules["win32com"] = win32com_mock
    sys.modules["win32com.client"] = client_mock
    sys.modules["pythoncom"] = MagicMock()
    os.environ.setdefault("APM_CONVERSION_BACKEND", "win32com")


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "integration_windows: requires Windows OS and Microsoft Office installed",
    )
    config.addinivalue_line(
        "markers",
        "integration_libreoffice: requires LibreOffice installed with soffice on PATH",
    )
