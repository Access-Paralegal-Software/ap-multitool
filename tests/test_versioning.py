# tests/test_versioning.py
import pytest
from core import __version__, __channel__
from apmultitool_qt.shell import APMainWindow
from PySide6 import QtWidgets

pytestmark = [pytest.mark.qt, pytest.mark.smoke]

def test_global_version_constants_exist():
    """Verify that version and channel constants are properly exported from core."""
    assert isinstance(__version__, str)
    assert isinstance(__channel__, str)
    assert len(__version__) > 0

def test_shell_binds_version_to_title():
    """Verify that APMainWindow injects the version string into the title and footer."""
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])

    window = APMainWindow()
    expected_full_version = f"v{__version__}{__channel__}"
    
    # Check Title
    assert expected_full_version in window.windowTitle()
    
    # Check internal property
    assert window.full_version == expected_full_version
