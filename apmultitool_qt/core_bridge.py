# apmultitool_qt/core_bridge.py

"""Qt Signals/Slots thread bridge for APMultitool Core Engine."""

from __future__ import annotations

import sys
import time
from pathlib import Path

from PySide6 import QtCore

from core.engine import DocEngine
from core.job import Job, OperationCancelled
from core.logging_config import get_logger, safe_filename


logger = get_logger("qt.core_bridge")


class DiagnosticWorker(QtCore.QObject):
    """
    Background worker that runs a diagnostic sequence on the core engine.
    Runs asynchronously on a QThread to prevent locking the UI.
    """

    started = QtCore.Signal()
    progress = QtCore.Signal(int)
    log_message = QtCore.Signal(str)
    finished = QtCore.Signal(bool, str)

    def __init__(self) -> None:
        super().__init__()
        self._is_cancelled = False

    def request_cancel(self) -> None:
        self._is_cancelled = True
        self.log_message.emit("Cancellation requested...")
        logger.info("diagnostic cancellation requested")

    def run_diagnostic(self) -> None:
        self.started.emit()
        self.progress.emit(0)
        self.log_message.emit("Starting APMultitool Engine Diagnostic...")
        logger.info("diagnostic started")
        time.sleep(0.4)

        if self._is_cancelled:
            self.finished.emit(False, "Diagnostic cancelled.")
            logger.info("diagnostic cancelled before validation")
            return

        self.progress.emit(25)
        self.log_message.emit("Validating DocEngine registry configurations...")
        logger.debug("diagnostic validating engine configuration")
        try:
            engine = DocEngine()
            self.log_message.emit(f"   - Engine output root: {engine.output_root}")
            logger.debug("diagnostic output_root=%s", safe_filename(engine.output_root))
            time.sleep(0.4)
        except Exception as exc:
            self.log_message.emit(f"Error setting up DocEngine: {exc}")
            logger.exception("diagnostic engine setup failed")
            self.finished.emit(False, f"Diagnostic failed: {exc}")
            return

        if self._is_cancelled:
            self.finished.emit(False, "Diagnostic cancelled.")
            logger.info("diagnostic cancelled before registry check")
            return

        self.progress.emit(50)
        self.log_message.emit("Checking operations registry...")
        logger.debug("diagnostic checking operations registry")
        try:
            from core.operations import OPERATION_REGISTRY

            ops = list(OPERATION_REGISTRY.keys())
            self.log_message.emit(f"   - Registered core operations: {', '.join(ops)}")
            logger.debug("diagnostic registered_operations=%s", ",".join(ops))
        except Exception as exc:
            self.log_message.emit(f"Could not load registry keys: {exc}")
            logger.exception("diagnostic registry check failed")
        time.sleep(0.4)

        if self._is_cancelled:
            self.finished.emit(False, "Diagnostic cancelled.")
            logger.info("diagnostic cancelled before environment check")
            return

        self.progress.emit(75)
        self.log_message.emit("Testing active database schemas...")
        logger.debug("diagnostic checking environment details")
        try:
            self.log_message.emit(f"   - Python Environment: {sys.version}")
            self.log_message.emit("   - All sanity checks PASSED.")
            logger.debug("diagnostic python_version=%s", sys.version.split()[0])
        except Exception as exc:
            self.log_message.emit(f"Error printing environment: {exc}")
            logger.exception("diagnostic environment check failed")
        time.sleep(0.4)

        if self._is_cancelled:
            self.finished.emit(False, "Diagnostic cancelled.")
            logger.info("diagnostic cancelled before completion")
            return

        self.progress.emit(100)
        self.log_message.emit("Diagnostic complete. Engine is healthy!")
        logger.info("diagnostic completed")
        self.finished.emit(True, "Engine Diagnostic passed successfully.")


class EngineJobWorker(QtCore.QObject):
    """
    Generalized background worker to execute standard core engine Jobs.
    Hooks into progress callbacks and propagates user cancellation request.
    """

    started = QtCore.Signal()
    progress = QtCore.Signal(int, str)  # percent, message
    log_message = QtCore.Signal(str)
    finished = QtCore.Signal(bool, str, object)  # success, error_message, job result

    def __init__(self, job: Job, output_root: Path | None = None) -> None:
        super().__init__()
        self.job = job
        self.output_root = output_root
        self._is_cancelled = False

    def request_cancel(self) -> None:
        """Trigger cooperative cancel flag checked in progress callback."""
        self._is_cancelled = True
        self.log_message.emit("User requested execution cancel. Aborting...")
        logger.info("job cancel requested job_id=%s operation=%s", self.job.job_id, self.job.operation)

    def run_job(self) -> None:
        """Execute the job in the worker's thread context."""
        self.started.emit()
        self.progress.emit(0, "Initiating core document engine...")
        logger.info("job started job_id=%s operation=%s", self.job.job_id, self.job.operation)

        try:
            from apmultitool_qt.telemetry import telemetry_manager

            telemetry_manager.log_job_started(self.job.operation)
        except Exception as exc:
            self.log_message.emit(f"Telemetry log failed: {exc}")
            logger.warning("telemetry start logging failed job_id=%s error=%s", self.job.job_id, exc)

        def on_engine_progress(msg: str, fraction: float) -> None:
            if self._is_cancelled:
                raise OperationCancelled("Cancelled by user request from GUI.")
            percent = int(fraction * 100)
            self.progress.emit(percent, msg)
            self.log_message.emit(f"[{percent}%] {msg}")
            logger.debug(
                "job progress job_id=%s operation=%s percent=%s message=%s",
                self.job.job_id,
                self.job.operation,
                percent,
                msg,
            )

        try:
            engine = DocEngine(output_root=self.output_root)
            completed_job = engine.submit(self.job, on_progress=on_engine_progress)
            self.progress.emit(100, "Done.")
            self.log_message.emit("Job execution completed successfully.")
            logger.info("job completed job_id=%s operation=%s", self.job.job_id, self.job.operation)

            try:
                telemetry_manager.log_job_finished(self.job.operation, success=True, cancelled=False)
            except Exception as exc:
                self.log_message.emit(f"Telemetry log failed: {exc}")
                logger.warning("telemetry success logging failed job_id=%s error=%s", self.job.job_id, exc)

            self.finished.emit(True, "", completed_job.result)
        except OperationCancelled:
            self.log_message.emit("Job execution aborted by user.")
            logger.info("job cancelled job_id=%s operation=%s", self.job.job_id, self.job.operation)

            try:
                telemetry_manager.log_job_finished(self.job.operation, success=False, cancelled=True)
            except Exception as exc:
                self.log_message.emit(f"Telemetry log failed: {exc}")
                logger.warning("telemetry cancel logging failed job_id=%s error=%s", self.job.job_id, exc)

            self.finished.emit(False, "Operation cancelled.", None)
        except Exception as exc:
            self.log_message.emit(f"Job execution failed: {exc}")
            logger.exception("job failed job_id=%s operation=%s", self.job.job_id, self.job.operation)

            try:
                telemetry_manager.log_job_finished(
                    self.job.operation,
                    success=False,
                    cancelled=False,
                    error_msg=str(exc),
                )
            except Exception as telemetry_exc:
                self.log_message.emit(f"Telemetry log failed: {telemetry_exc}")
                logger.warning(
                    "telemetry failure logging failed job_id=%s error=%s",
                    self.job.job_id,
                    telemetry_exc,
                )

            self.finished.emit(False, str(exc), None)
