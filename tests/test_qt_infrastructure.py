# tests/test_qt_infrastructure.py

"""Infrastructure, component, and worker threading tests for APMultitool Qt."""

import os
import pytest
from pathlib import Path
from PySide6 import QtCore, QtWidgets

from apmultitool_qt.components import (
    SectionCard,
    FormRow,
    ActionBar,
    HintLabel,
    EmptyStateWidget,
    dialogs,
    file_dialogs
)
from apmultitool_qt.core_bridge import EngineJobWorker
from core.job import Job, MergeParams, OutputSpec

def test_shared_primitives():
    """Verify that custom widgets can be instantiated and configured correctly."""
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])

    # Test SectionCard
    card = SectionCard()
    assert card.layout_container is not None
    lbl = QtWidgets.QLabel("Test Item")
    card.add_widget(lbl)
    assert card.layout_container.count() == 1

    # Test FormRow
    input_widget = QtWidgets.QLineEdit()
    form = FormRow("Test Label:", input_widget, label_width=100)
    assert form.label.text() == "Test Label:"
    assert form.input_widget == input_widget

    # Test ActionBar
    action = ActionBar()
    btn = QtWidgets.QPushButton("Run")
    action.add_button(btn)
    assert action.layout_container.count() == 1

    # Test HintLabel
    hint = HintLabel("This is a tip", indent=15)
    assert hint.text() == "This is a tip"
    assert "margin-left: 15px" in hint.styleSheet()

    # Test EmptyStateWidget
    empty = EmptyStateWidget("List is empty")
    assert empty.lbl_text.text() == "List is empty"


def test_file_dialog_helpers(monkeypatch):
    """Verify native dialog wrappers fall back or handle cancellations correctly."""
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])

    # Mock Qt Dialog methods to simulate cancel click (returning empty strings/lists)
    monkeypatch.setattr(QtWidgets.QFileDialog, "getOpenFileName", lambda *args, **kwargs: ("", ""))
    monkeypatch.setattr(QtWidgets.QFileDialog, "getOpenFileNames", lambda *args, **kwargs: ([], ""))
    monkeypatch.setattr(QtWidgets.QFileDialog, "getExistingDirectory", lambda *args, **kwargs: "")
    monkeypatch.setattr(QtWidgets.QFileDialog, "getSaveFileName", lambda *args, **kwargs: ("", ""))

    parent = QtWidgets.QWidget()
    assert file_dialogs.get_open_file(parent) == ""
    assert file_dialogs.get_open_files(parent) == []
    assert file_dialogs.get_existing_directory(parent) == ""
    assert file_dialogs.get_save_file(parent) == ""


def test_engine_job_worker(tmp_path):
    """Verify background EngineJobWorker registers callbacks, threads and executes jobs."""
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])

    # Setup a dummy job
    job = Job(
        operation="merge",
        inputs=[],
        params=MergeParams(bookmarks=True),
        output=OutputSpec(directory=tmp_path)
    )

    worker = EngineJobWorker(job, output_root=tmp_path)
    
    # We want to test starting and running a job
    # Create thread
    thread = QtCore.QThread()
    worker.moveToThread(thread)

    # Wire verification variables
    signals_received = {
        "started": False,
        "finished": False,
        "success": False
    }

    def on_started():
        signals_received["started"] = True

    def on_finished(success, err, result):
        signals_received["finished"] = True
        signals_received["success"] = success
        thread.quit()

    worker.started.connect(on_started)
    worker.finished.connect(on_finished)
    thread.started.connect(worker.run_job)

    # Execute thread synchronously for testing
    thread.start()
    thread.wait()

    # The merge succeeds by creating an empty PDF file using pikepdf, which is valid behavior
    assert signals_received["started"] is True
    assert signals_received["finished"] is True
    assert signals_received["success"] is True  # expected to succeed by creating an empty output PDF

