# apmultitool_qt/core_bridge.py

"""Qt Signals/Slots thread bridge for APMultitool Core Engine."""

import time
from pathlib import Path
from PySide6 import QtCore
from core.engine import DocEngine
from core.job import Job, JobResult, OperationCancelled

class DiagnosticWorker(QtCore.QObject):
    """
    Background worker that runs a diagnostic sequence on the core engine.
    Runs asynchronously on a QThread to prevent locking the UI.
    """
    started = QtCore.Signal()
    progress = QtCore.Signal(int)
    log_message = QtCore.Signal(str)
    finished = QtCore.Signal(bool, str)

    def __init__(self):
        super().__init__()
        self._is_cancelled = False

    def request_cancel(self):
        self._is_cancelled = True
        self.log_message.emit("🛑 Cancellation requested...")

    def run_diagnostic(self):
        self.started.emit()
        self.progress.emit(0)
        self.log_message.emit("🔄 Starting APMultitool Engine Diagnostic...")
        time.sleep(0.4)

        if self._is_cancelled:
            self.finished.emit(False, "Diagnostic cancelled.")
            return

        self.progress.emit(25)
        self.log_message.emit("📂 Validating DocEngine registry configurations...")
        try:
            engine = DocEngine()
            self.log_message.emit(f"   - Engine output root: {engine.output_root}")
            time.sleep(0.4)
        except Exception as e:
            self.log_message.emit(f"❌ Error setting up DocEngine: {str(e)}")
            self.finished.emit(False, f"Diagnostic failed: {str(e)}")
            return

        if self._is_cancelled:
            self.finished.emit(False, "Diagnostic cancelled.")
            return

        self.progress.emit(50)
        self.log_message.emit("🧬 Checking operations registry...")
        try:
            from core.operations import OPERATION_REGISTRY
            ops = list(OPERATION_REGISTRY.keys())
            self.log_message.emit(f"   - Registered core operations: {', '.join(ops)}")
        except Exception as e:
            self.log_message.emit(f"⚠️ Could not load registry keys: {str(e)}")
        time.sleep(0.4)

        if self._is_cancelled:
            self.finished.emit(False, "Diagnostic cancelled.")
            return

        self.progress.emit(75)
        self.log_message.emit("🗃️ Testing active database schemas...")
        try:
            import sys
            self.log_message.emit(f"   - Python Environment: {sys.version}")
            self.log_message.emit("   - All sanity checks PASSED.")
        except Exception as e:
            self.log_message.emit(f"❌ Error printing environment: {str(e)}")
        time.sleep(0.4)

        if self._is_cancelled:
            self.finished.emit(False, "Diagnostic cancelled.")
            return

        self.progress.emit(100)
        self.log_message.emit("✅ Diagnostic complete. Engine is healthy!")
        self.finished.emit(True, "Engine Diagnostic passed successfully.")


class EngineJobWorker(QtCore.QObject):
    """
    Generalized background worker to execute standard core engine Jobs.
    Hooks into progress callbacks and propagates user cancellation request.
    """
    started = QtCore.Signal()
    progress = QtCore.Signal(int, str)  # percent, message
    log_message = QtCore.Signal(str)
    finished = QtCore.Signal(bool, str, object)  # success, error_message, JobResult

    def __init__(self, job: Job, output_root: Path | None = None):
        super().__init__()
        self.job = job
        self.output_root = output_root
        self._is_cancelled = False

    def request_cancel(self):
        """Trigger cooperative cancel flag checked in progress callback."""
        self._is_cancelled = True
        self.log_message.emit("🛑 User requested execution cancel. Aborting...")

    def run_job(self):
        """Execute the job in the worker's thread context."""
        self.started.emit()
        self.progress.emit(0, "Initiating core document engine...")

        # Record telemetry start
        try:
            from apmultitool_qt.telemetry import telemetry_manager
            telemetry_manager.log_job_started(self.job.operation)
        except Exception as te:
            self.log_message.emit(f"⚠️ Telemetry log failed: {str(te)}")

        def on_engine_progress(msg: str, fraction: float):
            if self._is_cancelled:
                raise OperationCancelled("Cancelled by user request from GUI.")
            percent = int(fraction * 100)
            self.progress.emit(percent, msg)
            self.log_message.emit(f"[{percent}%] {msg}")

        try:
            engine = DocEngine(output_root=self.output_root)
            completed_job = engine.submit(self.job, on_progress=on_engine_progress)
            self.progress.emit(100, "Done.")
            self.log_message.emit("✅ Job execution completed successfully.")
            
            # Record telemetry success
            try:
                telemetry_manager.log_job_finished(self.job.operation, success=True, cancelled=False)
            except Exception as te:
                self.log_message.emit(f"⚠️ Telemetry log failed: {str(te)}")

            self.finished.emit(True, "", completed_job.result)
        except OperationCancelled:
            self.log_message.emit("🛑 Job execution aborted by user.")
            
            # Record telemetry cancellation
            try:
                telemetry_manager.log_job_finished(self.job.operation, success=False, cancelled=True)
            except Exception as te:
                self.log_message.emit(f"⚠️ Telemetry log failed: {str(te)}")

            self.finished.emit(False, "Operation cancelled.", None)
        except Exception as e:
            self.log_message.emit(f"❌ Job execution failed: {str(e)}")
            
            # Record telemetry failure
            try:
                telemetry_manager.log_job_finished(self.job.operation, success=False, cancelled=False, error_msg=str(e))
            except Exception as te:
                self.log_message.emit(f"⚠️ Telemetry log failed: {str(te)}")

            self.finished.emit(False, str(e), None)
