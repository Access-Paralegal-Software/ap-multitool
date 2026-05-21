# conftest.py — pytest configuration and marker registration
import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "integration_windows: requires Windows OS and Microsoft Office installed",
    )
    config.addinivalue_line(
        "markers",
        "integration_libreoffice: requires LibreOffice installed with soffice on PATH",
    )
