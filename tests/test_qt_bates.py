# tests/test_qt_bates.py

"""Unit and functional tests for the Qt BatesView."""

import os
import pytest
from pathlib import Path
from PySide6 import QtCore, QtWidgets

from apmultitool_qt.views.bates import BatesView, BatesOptionsDialog
from apmultitool_qt.components import dialogs, file_dialogs

pytestmark = [pytest.mark.qt]


def test_bates_view_init():
    """Verify Bates view constructs with correct default values."""
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])

    view = BatesView()
    assert view.txt_prefix.text() == "AP"
    assert view.txt_start.text() == "1"
    assert view.cb_sep.currentText() == "_"
    assert view.progress_bar.value() == 0
    assert not view.progress_bar.isVisible()


def test_bates_options_dialog(monkeypatch):
    """Verify dialog correctly maps inputs and outputs options."""
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])

    current_opts = {
        "font": "Arial Bold",
        "size": 12,
        "pos": "Bottom Right (Outside Margin)",
        "shrink": True,
        "naming": "Prefix_Start-End",
        "output": "Nested Folder (Default)"
    }
    
    dialog = BatesOptionsDialog(None, current_opts)
    
    # Check loaded settings
    assert dialog.cb_font.currentText() == "Arial Bold"
    assert dialog.cb_size.currentText() == "12"
    assert dialog.chk_shrink.isChecked() is True
    
    # Change values
    dialog.cb_font.setCurrentText("Courier")
    dialog.cb_size.setCurrentText("10")
    dialog.chk_shrink.setChecked(False)
    dialog.cb_pos.setCurrentText("Top Center (Above Margin)")
    dialog.cb_naming.setCurrentText("Prefix_StartOnly")
    dialog.cb_output.setCurrentText("Same as Source")
    
    dialog.save_and_close()
    
    assert dialog.opts["font"] == "Courier"
    assert dialog.opts["size"] == 10
    assert dialog.opts["shrink"] is False
    assert dialog.opts["pos"] == "Top Center (Above Margin)"
    assert dialog.opts["naming"] == "Prefix_StartOnly"
    assert dialog.opts["output"] == "Same as Source"


def test_clear_console(monkeypatch):
    """Verify clearing the log console terminal clears output history."""
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])

    view = BatesView()
    view.console.appendPlainText("Message 1")
    
    # Cancel confirmation
    monkeypatch.setattr(dialogs, "show_confirmation", lambda *args: False)
    view.clear_console()
    assert "Message 1" in view.console.toPlainText()

    # Approve confirmation
    monkeypatch.setattr(dialogs, "show_confirmation", lambda *args: True)
    view.clear_console()
    assert "Message 1" not in view.console.toPlainText()
    assert "READY" in view.console.toPlainText()


def test_autoincrement_ledger_editing_finished():
    """Verify Bates ledger lookups auto-increment start number on editingFinished."""
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])

    # Mock shell main window hierarchy
    class MockMainWindow(QtWidgets.QMainWindow):
        def __init__(self):
            super().__init__()
            self.view_fileroom = type("MockFileRoom", (), {"txt_case_id": type("MockCaseId", (), {"text": lambda: "Matter-A"})})()

        def show_progress(self, percent, msg):
            pass

    main_win = MockMainWindow()
    view = BatesView(parent=main_win)
    
    # Seed the registry
    view.bates_registry["Matter-A"] = {"AP": 105}
    
    # Trigger FocusOut / Editing Finished
    view.txt_prefix.setText("AP")
    view.on_prefix_editing_finished()
    
    # Start Index should pull from registry
    assert view.txt_start.text() == "105"


def test_toggle_inputs():
    """Verify widget state controls lockout inputs during active background runs."""
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])

    view = BatesView()
    view.toggle_inputs(False)
    assert not view.txt_target.isEnabled()
    assert not view.btn_browse.isEnabled()
    assert not view.txt_prefix.isEnabled()
    assert not view.txt_start.isEnabled()
    assert not view.cb_sep.isEnabled()
    assert not view.btn_options.isEnabled()
    assert not view.btn_clear.isEnabled()

    view.toggle_inputs(True)
    assert view.txt_target.isEnabled()
    assert view.btn_browse.isEnabled()
    assert view.txt_prefix.isEnabled()
    assert view.txt_start.isEnabled()
    assert view.cb_sep.isEnabled()
    assert view.btn_options.isEnabled()
    assert view.btn_clear.isEnabled()
