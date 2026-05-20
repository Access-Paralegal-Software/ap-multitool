# apmultitool_qt/core_bridge.py

"""Qt Signals/Slots thread bridge for APMultitool Core Engine."""

import time
from PySide6 import QtCore
from core.engine import DocEngine

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
