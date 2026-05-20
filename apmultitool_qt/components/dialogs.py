# apmultitool_qt/components/dialogs.py

"""Standardized modal dialog utility functions for APMultitool Qt."""

from PySide6 import QtWidgets, QtCore, QtGui

def show_info(parent: QtWidgets.QWidget, title: str, message: str):
    """Display a standard modal information dialog."""
    msg = QtWidgets.QMessageBox(parent)
    msg.setIcon(QtWidgets.QMessageBox.Information)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    # Apply global styling class references
    msg.exec()


def show_warning(parent: QtWidgets.QWidget, title: str, message: str):
    """Display a standard modal warning alert."""
    msg = QtWidgets.QMessageBox(parent)
    msg.setIcon(QtWidgets.QMessageBox.Warning)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg.exec()


def show_error(parent: QtWidgets.QWidget, title: str, message: str, details: str = None):
    """Display a standard modal error alert with optional detailed traceback logs."""
    msg = QtWidgets.QMessageBox(parent)
    msg.setIcon(QtWidgets.QMessageBox.Critical)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    
    if details:
        msg.setDetailedText(details)
        # Force scrollable details styling
        spacer = QtWidgets.QSpacerItem(400, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        layout = msg.layout()
        layout.addItem(spacer, layout.rowCount(), 0, 1, layout.columnCount())

    msg.exec()


def show_confirmation(parent: QtWidgets.QWidget, title: str, message: str) -> bool:
    """
    Display a confirmation prompt for destructive actions.
    Returns True if confirmed (Yes clicked), False otherwise (No clicked).
    """
    msg = QtWidgets.QMessageBox(parent)
    msg.setIcon(QtWidgets.QMessageBox.Question)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    msg.setDefaultButton(QtWidgets.QMessageBox.No)
    
    result = msg.exec()
    return result == QtWidgets.QMessageBox.Yes
