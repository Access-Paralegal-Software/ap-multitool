# apmultitool_qt/components/file_dialogs.py

"""Platform-safe native file and directory selection helpers for APMultitool Qt."""

import os
from PySide6 import QtWidgets, QtCore

def get_open_file(parent: QtWidgets.QWidget, title: str = "Open File", filter_str: str = "All Files (*)") -> str:
    """
    Open a native file dialogue to select a single file.
    Returns the absolute path to the selected file, or an empty string if cancelled.
    """
    file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
        parent,
        title,
        os.path.expanduser("~"),
        filter_str
    )
    return file_path or ""


def get_open_files(parent: QtWidgets.QWidget, title: str = "Select Files", filter_str: str = "All Files (*)") -> list[str]:
    """
    Open a native file dialogue to select multiple files.
    Returns a list of absolute paths to selected files, or an empty list if cancelled.
    """
    file_paths, _ = QtWidgets.QFileDialog.getOpenFileNames(
        parent,
        title,
        os.path.expanduser("~"),
        filter_str
    )
    return file_paths or []


def get_existing_directory(parent: QtWidgets.QWidget, title: str = "Select Folder", default_dir: str = None) -> str:
    """
    Open a native folder selection dialogue.
    Returns the absolute directory path, or an empty string if cancelled.
    """
    start_dir = default_dir or os.path.expanduser("~")
    dir_path = QtWidgets.QFileDialog.getExistingDirectory(
        parent,
        title,
        start_dir,
        QtWidgets.QFileDialog.ShowDirsOnly
    )
    return dir_path or ""


def get_save_file(parent: QtWidgets.QWidget, title: str = "Save File As", filter_str: str = "PDF Document (*.pdf)") -> str:
    """
    Open a native save file dialogue.
    Returns the target path to save the output file, or an empty string if cancelled.
    """
    file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
        parent,
        title,
        os.path.expanduser("~"),
        filter_str
    )
    return file_path or ""
