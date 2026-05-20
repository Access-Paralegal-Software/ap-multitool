# apmultitool_qt/views/about.py

"""Help & About View widget class for APMultitool Qt."""

from PySide6 import QtWidgets, QtCore
import config
from apmultitool_qt.core_bridge import DiagnosticWorker

class AboutView(QtWidgets.QWidget):
    """
    Help and About panel view.
    Displays version information, CLI usage tips, and includes an interactive
    engine diagnostic test running on a background thread.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.thread = None
        self.setup_ui()

    def setup_ui(self):
        # Two panels: Left is About details & CLI tips; Right is Engine Diagnostic PoC
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(15)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        main_layout.addWidget(splitter)

        # ----------------------------------------------------
        # Left Panel (App Info Card & CLI Info)
        # ----------------------------------------------------
        left_panel = QtWidgets.QFrame()
        left_panel.setObjectName("GroupBoxContainer")
        left_panel.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        left_panel.setMinimumWidth(320)
        left_panel.setMaximumWidth(340)

        left_layout = QtWidgets.QVBoxLayout(left_panel)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(15)

        # App Identity
        header = QtWidgets.QLabel("ABOUT APMULTITOOL")
        header.setObjectName("GroupHeader")
        left_layout.addWidget(header)

        lbl_logo = QtWidgets.QLabel("Access Paralegal Multitool")
        lbl_logo.setStyleSheet("font-size: 15px; font-weight: bold; color: #111827;")
        left_layout.addWidget(lbl_logo)

        self.lbl_ver = QtWidgets.QLabel(f"Version: {config.__version__} (Qt/PySide6 Edition)")
        self.lbl_ver.setStyleSheet("color: #4B5563; font-size: 11px;")
        left_layout.addWidget(self.lbl_ver)

        lbl_desc = QtWidgets.QLabel(
            "An internal command center designed to automate document "
            "compilation, Bates stamping, and case directory spin-ups."
        )
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("color: #4B5563; font-size: 11px; line-height: 14px;")
        left_layout.addWidget(lbl_desc)

        # Divider
        divider = QtWidgets.QFrame()
        divider.setFrameShape(QtWidgets.QFrame.HLine)
        divider.setFrameShadow(QtWidgets.QFrame.Sunken)
        left_layout.addWidget(divider)

        # CLI Companion Card
        cli_header = QtWidgets.QLabel("💻 CLI COMPANION CARD")
        cli_header.setStyleSheet("font-weight: bold; color: #67BE5E; font-size: 11px;")
        left_layout.addWidget(cli_header)

        cli_desc = QtWidgets.QLabel(
            "This application includes a powerful CLI engine!\n\n"
            "Open your terminal and run:\n"
            "  apmultitool --help\n\n"
            "You can automate PDF merges, Bates stamping, and Word/Excel "
            "conversions directly in batch scripts."
        )
        cli_desc.setWordWrap(True)
        cli_desc.setStyleSheet("color: #374151; font-family: 'Consolas', monospace; font-size: 10px; padding: 5px;")
        left_layout.addWidget(cli_desc)

        left_layout.addStretch()
        splitter.addWidget(left_panel)

        # ----------------------------------------------------
        # Right Panel (Engine Diagnostic Thread Verification)
        # ----------------------------------------------------
        right_panel = QtWidgets.QFrame()
        right_panel.setObjectName("GroupBoxContainer")

        right_layout = QtWidgets.QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(12)

        # Header
        d_header = QtWidgets.QLabel("CORE ENGINE DIAGNOSTIC BRIDGE (POC)")
        d_header.setObjectName("GroupHeader")
        right_layout.addWidget(d_header)

        d_desc = QtWidgets.QLabel(
            "Validate thread-safe communication between the PySide6 UI and the "
            "underlying python document processing engine. Click the diagnostic button below "
            "to run asynchronous checks on a separate worker thread."
        )
        d_desc.setWordWrap(True)
        d_desc.setStyleSheet("color: #4B5563; font-size: 11px;")
        right_layout.addWidget(d_desc)

        # Console Logs
        self.diag_console = QtWidgets.QPlainTextEdit()
        self.diag_console.setObjectName("ConsoleOutput")
        self.diag_console.setReadOnly(True)
        self.diag_console.appendPlainText("DIAGNOSTIC CHANNEL STANDBY...")
        right_layout.addWidget(self.diag_console)

        # Progress Bar
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #E5E7EB;
                border-radius: 4px;
                text-align: center;
                background-color: #FFFFFF;
            }
            QProgressBar::chunk {
                background-color: #67BE5E;
            }
        """)
        right_layout.addWidget(self.progress_bar)

        # Action Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        self.btn_run = QtWidgets.QPushButton("Run Core Engine Diagnostic")
        self.btn_run.setObjectName("PrimaryButton")
        self.btn_run.clicked.connect(self.start_diagnostic)
        btn_layout.addWidget(self.btn_run)

        self.btn_cancel = QtWidgets.QPushButton("Cancel")
        self.btn_cancel.setObjectName("DangerButton")
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self.cancel_diagnostic)
        btn_layout.addWidget(self.btn_cancel)

        right_layout.addLayout(btn_layout)
        splitter.addWidget(right_panel)

    def start_diagnostic(self):
        self.diag_console.clear()
        self.progress_bar.setValue(0)

        # Instantiate worker and QThread
        self.thread = QtCore.QThread()
        self.worker = DiagnosticWorker()
        self.worker.moveToThread(self.thread)

        # Wire Signals/Slots
        self.thread.started.connect(self.worker.run_diagnostic)
        self.worker.started.connect(self.on_diagnostic_started)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.log_message.connect(self.diag_console.appendPlainText)
        self.worker.finished.connect(self.on_diagnostic_finished)

        # Start thread
        self.thread.start()

    def cancel_diagnostic(self):
        if self.worker:
            self.worker.request_cancel()
            self.btn_cancel.setEnabled(False)

    def on_diagnostic_started(self):
        self.btn_run.setEnabled(False)
        self.btn_cancel.setEnabled(True)

    def on_diagnostic_finished(self, success, message):
        # Shutdown thread gracefully
        if self.thread:
            self.thread.quit()
            self.thread.wait()

        self.btn_run.setEnabled(True)
        self.btn_cancel.setEnabled(False)

        if success:
            QtWidgets.QMessageBox.information(
                self, "Diagnostic Pass", 
                "Core Engine Diagnostic passed successfully! Signals cross thread bounds correctly."
            )
        else:
            QtWidgets.QMessageBox.warning(
                self, "Diagnostic Stopped", 
                f"Core Engine Diagnostic: {message}"
            )

        # Cleanup references
        self.worker = None
        self.thread = None
