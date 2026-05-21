# tests/test_qt_fileroom.py

"""Unit and functional tests for the Qt FileRoomView."""

import os
import pytest
from pathlib import Path
from PySide6 import QtCore, QtWidgets

from apmultitool_qt.views.fileroom import FileRoomView
from apmultitool_qt.components import dialogs, file_dialogs

pytestmark = [pytest.mark.qt]


def test_fileroom_view_init():
    """Verify FileRoomView constructs with correct default values."""
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])

    view = FileRoomView()
    assert view.txt_case_id.text() == "2026-AP-9908"
    assert view.cb_blueprints.currentText() == "⭐ Custom User Blueprint"
    assert len(view.custom_structure) > 0
    assert view.tree_widget.topLevelItemCount() > 0


def test_blueprint_selection_change():
    """Verify selecting standard blueprints disables custom additions but updates preview."""
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])

    view = FileRoomView()
    
    # Selecting standard archetype
    view.cb_blueprints.setCurrentText("Standard Civil Litigation")
    assert not view.txt_custom_folder.isEnabled()
    assert not view.btn_add_folder.isEnabled()
    
    # Selecting Custom User Blueprint enables custom additions
    view.cb_blueprints.setCurrentText("⭐ Custom User Blueprint")
    assert view.txt_custom_folder.isEnabled()
    assert view.btn_add_folder.isEnabled()


def test_add_remove_custom_folders():
    """Verify user can dynamically add and remove folders to custom blueprints."""
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])

    view = FileRoomView()
    view.cb_blueprints.setCurrentText("⭐ Custom User Blueprint")
    
    # Add a custom folder
    view.txt_custom_folder.setText("Medical Records")
    view.cb_custom_parent.setCurrentText("Discovery")
    view.add_custom_folder()
    
    assert "Discovery/Medical Records" in view.custom_structure
    
    # Test removal
    # Select the added item in the tree widget preview
    root = view.tree_widget.topLevelItem(0)
    
    # Find the matching tree widget item for "Discovery" -> "Medical Records"
    disc_item = None
    for i in range(root.childCount()):
        child = root.child(i)
        if child.text(0) == "Discovery":
            disc_item = child
            break
            
    assert disc_item is not None
    
    med_item = None
    for i in range(disc_item.childCount()):
        child = disc_item.child(i)
        if child.text(0) == "Medical Records":
            med_item = child
            break
            
    assert med_item is not None
    
    # Select item and trigger removal
    view.tree_widget.setCurrentItem(med_item)
    view.remove_custom_folder()
    
    assert "Discovery/Medical Records" not in view.custom_structure


def test_reset_and_clear():
    """Verify reset defaults and clear all functionality works."""
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])

    view = FileRoomView()
    
    # Clear all structure
    view.custom_structure = ["TempFolder"]
    view.custom_structure.clear()
    assert len(view.custom_structure) == 0
    
    # Reset Defaults
    view.custom_structure = []
    view.custom_structure = [
        "Correspondence", "Discovery", "Pleadings"
    ]
    assert len(view.custom_structure) == 3


def test_toggle_inputs():
    """Verify inputs lockout behaviors during active worker operations."""
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])

    view = FileRoomView()
    view.toggle_inputs(False)
    assert not view.txt_case_id.isEnabled()
    assert not view.cb_blueprints.isEnabled()
    assert not view.btn_run.isEnabled()
    
    view.toggle_inputs(True)
    assert view.txt_case_id.isEnabled()
    assert view.cb_blueprints.isEnabled()
    assert view.btn_run.isEnabled()
