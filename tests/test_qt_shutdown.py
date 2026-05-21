# tests/test_qt_shutdown.py
import pytest
from PySide6 import QtWidgets, QtCore
from apmultitool_qt.shell import APMainWindow

pytestmark = [pytest.mark.qt]
from apmultitool_qt.core_bridge import EngineJobWorker
from core.job import Job, InputSpec, MergeParams, OutputSpec
from pathlib import Path

def test_shell_shutdown_cleans_workers():
    """
    Validate that APMainWindow's closeEvent successfully issues cancel requests
    to any active background workers to prevent thread memory leaks on exit.
    """
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])

    window = APMainWindow()
    
    # Mock an active worker
    job = Job(
        operation="merge",
        inputs=[InputSpec.from_path(Path("fake.pdf"))],
        params=MergeParams(output_name="test.pdf"),
        output=OutputSpec(directory=Path("out"), overwrite=True)
    )
    
    worker = EngineJobWorker(job, Path("out"))
    
    # Force inject into view
    window.view_compiler.active_worker = worker
    
    # Confirm initial state
    assert worker._is_cancelled is False
    
    # Trigger close
    window.close()
    
    # Verify cancellation was requested by the closeEvent
    assert worker._is_cancelled is True
