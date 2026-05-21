# tests/test_qt_foundation.py

"""Basic structure and import sanity tests for the APMultitool Qt application."""

import sys
import os
import pytest

from PySide6 import QtCore, QtWidgets

# Make sure we can import package modules
from apmultitool_qt.shell import APMainWindow
from apmultitool_qt.styles import GLOBAL_STYLE
from apmultitool_qt.core_bridge import DiagnosticWorker
from apmultitool_qt.views import CompilerView, BatesView, FileRoomView, AboutView

pytestmark = [pytest.mark.qt, pytest.mark.smoke]

def test_styles_import():
    """Verify QSS style variables exist and export a valid QSS string."""
    assert GLOBAL_STYLE is not None
    assert "SidebarFrame" in GLOBAL_STYLE
    assert "ConsoleOutput" in GLOBAL_STYLE

def test_views_structure():
    """Verify that all target views can be instantiated without crashing."""
    # We must instantiate a QApplication first to create widgets
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])

    compiler = CompilerView()
    assert compiler.table is not None
    assert compiler.table.columnCount() == 6
    assert compiler.btn_run is not None

    bates = BatesView()
    assert bates.console is not None
    assert bates.txt_prefix.text() == "AP"
    assert bates.btn_run is not None

    fileroom = FileRoomView()
    assert fileroom.tree_widget is not None
    assert fileroom.txt_case_id.text() == "2026-AP-9908"
    assert fileroom.btn_run is not None

    about = AboutView()
    assert about.lbl_ver is not None
    assert "Qt/PySide6 Edition" in about.lbl_ver.text()

def test_shell_structure():
    """Verify the QMainWindow shell navigation bindings."""
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])

    window = APMainWindow()
    assert window.windowTitle() == f"Access Paralegal Multitool {window.full_version} (Qt Edition)"
    assert window.stacked_widget.count() == 4
    assert window.btn_compiler.isChecked() is True

    # Test switching views
    window.switch_view(1)
    assert window.stacked_widget.currentIndex() == 1
    assert window.lbl_title.text() == "Bates Stamping & Compliance"

    window.switch_view(3)
    assert window.stacked_widget.currentIndex() == 3
    assert window.lbl_title.text() == "Help & About"
