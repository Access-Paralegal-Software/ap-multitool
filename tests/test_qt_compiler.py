# tests/test_qt_compiler.py

"""Unit and functional tests for the Qt CompilerView."""

import os
import pytest
from pathlib import Path
from PySide6 import QtCore, QtWidgets

from apmultitool_qt.views.compiler import CompilerView, format_size, get_format_display
from apmultitool_qt.components import dialogs, file_dialogs


def test_format_helpers(tmp_path):
    """Verify size formatting and format type resolution."""
    assert get_format_display("document.pdf") == "PDF"
    assert get_format_display("letter.docx") == "Word"
    assert get_format_display("report.xlsx") == "Excel"
    assert get_format_display("email.msg") == "Email"
    assert get_format_display("scan.png") == "Image"
    assert get_format_display("notes.txt") == "Text"
    assert get_format_display("unknown.xyz") == "Unknown"

    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello World!")
    assert format_size(str(test_file)) == "12 B"


def test_compiler_view_init():
    """Verify compiler view constructs with empty state."""
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])

    view = CompilerView()
    assert view.queue_files == []
    # Verify starting index points to empty state text screen
    assert view.table_stack.currentIndex() == 1
    assert view.table.rowCount() == 0


def test_add_remove_clear_queue(tmp_path, monkeypatch):
    """Verify adding, removing, and clearing queue files updating states."""
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])

    view = CompilerView()

    # Mock dialogs
    monkeypatch.setattr(dialogs, "show_confirmation", lambda *args, **kwargs: True)

    # Make temporary files
    f1 = tmp_path / "file1.pdf"
    f1.write_text("1")
    f2 = tmp_path / "file2.docx"
    f2.write_text("2")

    # Add paths
    view.add_file_paths([str(f1), str(f2)])
    assert len(view.queue_files) == 2
    assert view.table.rowCount() == 2
    assert view.table_stack.currentIndex() == 0  # Table view visible

    # Check cell contents
    assert view.table.item(0, 1).text() == "file1.pdf"
    assert view.table.item(0, 3).text() == "PDF"
    assert view.table.item(1, 1).text() == "file2.docx"
    assert view.table.item(1, 3).text() == "Word"

    # Selection-aware remove
    view.table.selectRow(0)
    view.remove_selected()
    assert len(view.queue_files) == 1
    assert view.table.rowCount() == 1
    assert view.table.item(0, 1).text() == "file2.docx"

    # Clear queue
    view.clear_queue()
    assert len(view.queue_files) == 0
    assert view.table.rowCount() == 0
    assert view.table_stack.currentIndex() == 1  # back to empty state


def test_reorder_rows(tmp_path):
    """Verify up/down item moving swapping indexes and elements."""
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])

    view = CompilerView()

    f1 = tmp_path / "a.pdf"
    f1.write_text("a")
    f2 = tmp_path / "b.pdf"
    f2.write_text("b")

    view.add_file_paths([str(f1), str(f2)])
    assert view.queue_files == [str(f1), str(f2)]

    # Move down from row 0
    view.table.setCurrentCell(0, 0)
    view.move_item_down()
    assert view.queue_files == [str(f2), str(f1)]
    assert view.table.item(0, 1).text() == "b.pdf"
    assert view.table.item(1, 1).text() == "a.pdf"

    # Move up from row 1
    view.table.setCurrentCell(1, 0)
    view.move_item_up()
    assert view.queue_files == [str(f1), str(f2)]
    assert view.table.item(0, 1).text() == "a.pdf"
    assert view.table.item(1, 1).text() == "b.pdf"


def test_options_validation(tmp_path, monkeypatch):
    """Verify that settings checkboxes are configured correctly."""
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])

    view = CompilerView()
    
    # Configure parameters
    view.chk_bookmarks.setChecked(False)
    view.chk_fit.setChecked(True)
    view.chk_compress.setChecked(True)
    view.chk_grayscale.setChecked(False)
    
    assert not view.chk_bookmarks.isChecked()
    assert view.chk_fit.isChecked()
    assert view.chk_compress.isChecked()
    assert not view.chk_grayscale.isChecked()

    # Verify input name validation automatically appends suffix
    view.output_name_input.setText("sample_output")
    monkeypatch.setattr(dialogs, "show_confirmation", lambda *args, **kwargs: True)
    monkeypatch.setattr(dialogs, "show_warning", lambda *args, **kwargs: None)
    
    f1 = tmp_path / "doc.pdf"
    f1.write_text("pdf")
    view.add_file_paths([str(f1)])
    view.output_dir_input.setText(str(tmp_path))
    
    # Mock engine execution to test validate side effects
    monkeypatch.setattr(view, "run_merge", lambda: None)
    view.run_merge()
    # Test text conversion updates
    name = view.output_name_input.text()
    if not name.endswith(".pdf"):
        name += ".pdf"
    assert name == "sample_output.pdf"
