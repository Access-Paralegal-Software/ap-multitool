# tests/test_telemetry.py

"""Unit tests for the APMultitool Telemetry tracking system."""

import os
import pytest
from PySide6 import QtWidgets
import apmultitool_qt.telemetry
from apmultitool_qt.telemetry import TelemetryManager
from apmultitool_qt.views import AboutView

@pytest.fixture
def temp_telemetry_file(tmp_path):
    """Fixture to redirect telemetry file storage during test run."""
    original_path = apmultitool_qt.telemetry.TELEMETRY_FILE
    temp_file = tmp_path / "temp_telemetry.json"
    apmultitool_qt.telemetry.TELEMETRY_FILE = str(temp_file)
    
    # Force the global manager to reload/reset to temp file bounds
    from apmultitool_qt.telemetry import telemetry_manager
    telemetry_manager.reset()
    
    yield str(temp_file)
    
    # Clean up and restore path
    apmultitool_qt.telemetry.TELEMETRY_FILE = original_path
    telemetry_manager.load()

def test_telemetry_manager_flow(temp_telemetry_file):
    """Verify that the TelemetryManager tracks operations and outcomes correctly."""
    manager = TelemetryManager()
    
    # 1. Clean initial state check
    assert manager.stats["total_runs"] == 0
    assert manager.get_success_rate() == 100.0
    
    # 2. Register job start
    manager.log_job_started("merge")
    assert manager.stats["total_runs"] == 1
    assert manager.stats["operations"]["merge"]["total"] == 1
    
    # 3. Register successful completion
    manager.log_job_finished("merge", success=True, cancelled=False)
    assert manager.stats["success_runs"] == 1
    assert manager.stats["operations"]["merge"]["success"] == 1
    assert manager.get_success_rate() == 100.0
    
    # 4. Register a failed job
    manager.log_job_started("bates_stamp")
    manager.log_job_finished("bates_stamp", success=False, cancelled=False, error_msg="PDF file corrupted")
    assert manager.stats["total_runs"] == 2
    assert manager.stats["failed_runs"] == 1
    assert manager.stats["operations"]["bates_stamp"]["failed"] == 1
    assert manager.stats["last_error"] == "PDF file corrupted"
    
    # Rate: 1 success / 2 runs (excluding cancellations) = 50.0%
    assert manager.get_success_rate() == 50.0
    
    # 5. Register a cancelled job (cancellations shouldn't count as failures)
    manager.log_job_started("folder_tree")
    manager.log_job_finished("folder_tree", success=False, cancelled=True)
    assert manager.stats["total_runs"] == 3
    assert manager.stats["cancelled_runs"] == 1
    assert manager.stats["operations"]["folder_tree"]["cancelled"] == 1
    
    # Success rate should remain 50%
    assert manager.get_success_rate() == 50.0
    
    # 6. Reset check
    manager.reset()
    assert manager.stats["total_runs"] == 0
    assert manager.stats["success_runs"] == 0
    assert manager.stats["failed_runs"] == 0
    assert manager.stats["cancelled_runs"] == 0
    assert manager.stats["last_error"] == ""

def test_about_view_telemetry_integration(temp_telemetry_file):
    """Verify that AboutView reads and displays telemetry aggregates accurately."""
    # Pre-populate metrics via the singleton manager instance
    from apmultitool_qt.telemetry import telemetry_manager
    telemetry_manager.log_job_started("merge")
    telemetry_manager.log_job_finished("merge", success=True, cancelled=False)
    telemetry_manager.log_job_started("bates_stamp")
    telemetry_manager.log_job_finished("bates_stamp", success=False, cancelled=False, error_msg="Write permission error")
    
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
        
    about_view = AboutView()
    about_view.update_telemetry_display()
    
    assert about_view.lbl_tel_total.text() == "Total runs: 2"
    assert about_view.lbl_tel_rate.text() == "Success Rate: 50.0%"
    assert about_view.lbl_tel_failed.text() == "Failed runs: 1"
    assert about_view.lbl_tel_cancelled.text() == "Cancelled runs: 0"
    assert about_view.lbl_tel_last_err.isHidden() is False
    assert "Write permission error" in about_view.lbl_tel_last_err.text()
    
    # Reset stats
    telemetry_manager.reset()
    about_view.update_telemetry_display()
    assert about_view.lbl_tel_total.text() == "Total runs: 0"
    assert about_view.lbl_tel_rate.text() == "Success Rate: 100.0%"
    assert about_view.lbl_tel_last_err.isHidden() is True
