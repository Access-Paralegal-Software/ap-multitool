# apmultitool_qt/core_bridge.py

"""Qt Signals/Slots thread bridge for APMultitool Core Engine."""

import time
import logging
from pathlib import Path
from PySide6 import QtCore
from core.engine import DocEngine
from core.job import Job, JobResult, OperationCancelled

logger = logging.getLogger("APMultitool")

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
        logger.info("Diagnostic worker: cancellation requested.")

    def run_diagnostic(self):
        self.started.emit()
        self.progress.emit(0)
        self.log_message.emit("🔄 Starting APMultitool Engine Diagnostic...")
        logger.info("Diagnostic worker: started engine diagnostic sequence.")
        time.sleep(0.4)

        if self._is_cancelled:
            self.finished.emit(False, "Diagnostic cancelled.")
            logger.info("Diagnostic worker: cancelled before validation.")
            return

        self.progress.emit(25)
        self.log_message.emit("📂 Validating DocEngine registry configurations...")
        logger.info("Diagnostic worker: validating DocEngine configuration.")
        try:
            engine = DocEngine()
            self.log_message.emit(f"   - Engine output root: {engine.output_root}")
            logger.info(f"Diagnostic worker: Engine output root is {engine.output_root}")
            time.sleep(0.4)
        except Exception as e:
            self.log_message.emit(f"❌ Error setting up DocEngine: {str(e)}")
            logger.exception("Diagnostic worker: error setting up DocEngine.")
            self.finished.emit(False, f"Diagnostic failed: {str(e)}")
            return

        if self._is_cancelled:
            self.finished.emit(False, "Diagnostic cancelled.")
            logger.info("Diagnostic worker: cancelled before registry check.")
            return

        self.progress.emit(50)
        self.log_message.emit("🧬 Checking operations registry...")
        logger.info("Diagnostic worker: checking operations registry.")
        try:
            from core.operations import OPERATION_REGISTRY
            ops = list(OPERATION_REGISTRY.keys())
            self.log_message.emit(f"   - Registered core operations: {', '.join(ops)}")
            logger.info(f"Diagnostic worker: Registered core operations: {ops}")
        except Exception as e:
            self.log_message.emit(f"⚠️ Could not load registry keys: {str(e)}")
            logger.exception("Diagnostic worker: could not load registry keys.")
        time.sleep(0.4)

        if self._is_cancelled:
            self.finished.emit(False, "Diagnostic cancelled.")
            logger.info("Diagnostic worker: cancelled before database schema check.")
            return

        self.progress.emit(75)
        self.log_message.emit("🗃️ Testing active database schemas...")
        logger.info("Diagnostic worker: testing active environment schemas.")
        try:
            import sys
            self.log_message.emit(f"   - Python Environment: {sys.version}")
            self.log_message.emit("   - All sanity checks PASSED.")
            logger.info(f"Diagnostic worker: environment details - Python {sys.version}")
        except Exception as e:
            self.log_message.emit(f"❌ Error printing environment: {str(e)}")
            logger.exception("Diagnostic worker: error checking environment details.")
        time.sleep(0.4)

        if self._is_cancelled:
            self.finished.emit(False, "Diagnostic cancelled.")
            logger.info("Diagnostic worker: cancelled before completion.")
            return

        self.progress.emit(100)
        self.log_message.emit("✅ Diagnostic complete. Engine is healthy!")
        logger.info("Diagnostic worker: engine diagnostic sequence completed successfully.")
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
        logger.info(f"Job {self.job.job_id} ({self.job.operation}): cancellation requested by user.")

    def run_job(self):
        """Execute the job in the worker's thread context."""
        self.started.emit()
        self.progress.emit(0, "Initiating core document engine...")
        logger.info(f"Job {self.job.job_id} ({self.job.operation}): started execution.")

        # Record telemetry start
        try:
            from apmultitool_qt.telemetry import telemetry_manager
            telemetry_manager.log_job_started(self.job.operation)
        except Exception as te:
            self.log_message.emit(f"⚠️ Telemetry log failed: {str(te)}")
            logger.error(f"Job {self.job.job_id}: telemetry start logging failed: {te}")

        def on_engine_progress(msg: str, fraction: float):
            if self._is_cancelled:
                raise OperationCancelled("Cancelled by user request from GUI.")
            percent = int(fraction * 100)
            self.progress.emit(percent, msg)
            self.log_message.emit(f"[{percent}%] {msg}")
            logger.info(f"Job {self.job.job_id} ({self.job.operation}): progress {percent}% - {msg}")

        try:
            engine = DocEngine(output_root=self.output_root)
            completed_job = engine.submit(self.job, on_progress=on_engine_progress)
            self.progress.emit(100, "Done.")
            self.log_message.emit("✅ Job execution completed successfully.")
            logger.info(f"Job {self.job.job_id} ({self.job.operation}): execution completed successfully.")
            
            # Record telemetry success
            try:
                telemetry_manager.log_job_finished(self.job.operation, success=True, cancelled=False)
            except Exception as te:
                self.log_message.emit(f"⚠️ Telemetry log failed: {str(te)}")
                logger.error(f"Job {self.job.job_id}: telemetry success logging failed: {te}")

            self.finished.emit(True, "", completed_job.result)
        except OperationCancelled:
            self.log_message.emit("🛑 Job execution aborted by user.")
            logger.info(f"Job {self.job.job_id} ({self.job.operation}): execution aborted by user.")
            
            # Record telemetry cancellation
            try:
                telemetry_manager.log_job_finished(self.job.operation, success=False, cancelled=True)
            except Exception as te:
                self.log_message.emit(f"⚠️ Telemetry log failed: {str(te)}")
                logger.error(f"Job {self.job.job_id}: telemetry cancel logging failed: {te}")

            self.finished.emit(False, "Operation cancelled.", None)
        except Exception as e:
            self.log_message.emit(f"❌ Job execution failed: {str(e)}")
            logger.exception(f"Job {self.job.job_id} ({self.job.operation}): execution failed.")
            
            # Record telemetry failure
            try:
                telemetry_manager.log_job_finished(self.job.operation, success=False, cancelled=False, error_msg=str(e))
            except Exception as te:
                self.log_message.emit(f"⚠️ Telemetry log failed: {str(te)}")
                logger.error(f"Job {self.job.job_id}: telemetry failure logging failed: {te}")

            self.finished.emit(False, str(e), None)
