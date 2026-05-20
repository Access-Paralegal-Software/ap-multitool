# apmultitool_qt/views/about.py

"""Help & About View widget class for APMultitool Qt."""

from PySide6 import QtWidgets, QtCore
import config
from apmultitool_qt.core_bridge import DiagnosticWorker
from apmultitool_qt.components import SectionCard, ActionBar, HintLabel, dialogs

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
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(15)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        main_layout.addWidget(splitter)

        # ----------------------------------------------------
        # Left Panel (App Info Card & CLI Info)
        # ----------------------------------------------------
        self.left_card = SectionCard()
        self.left_card.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.left_card.setMinimumWidth(320)
        self.left_card.setMaximumWidth(340)

        header = QtWidgets.QLabel("ABOUT APMULTITOOL")
        header.setObjectName("GroupHeader")
        self.left_card.add_widget(header)

        lbl_logo = QtWidgets.QLabel("Access Paralegal Multitool")
        lbl_logo.setStyleSheet("font-size: 15px; font-weight: bold; color: #111827;")
        self.left_card.add_widget(lbl_logo)

        self.lbl_ver = QtWidgets.QLabel(f"Version: {config.__version__} (Qt/PySide6 Edition)")
        self.lbl_ver.setStyleSheet("color: #4B5563; font-size: 11px;")
        self.left_card.add_widget(self.lbl_ver)

        lbl_desc = QtWidgets.QLabel(
            "An internal command center designed to automate document "
            "compilation, Bates stamping, and case directory spin-ups."
        )
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("color: #4B5563; font-size: 11px; line-height: 14px;")
        self.left_card.add_widget(lbl_desc)

        # Divider
        divider = QtWidgets.QFrame()
        divider.setFrameShape(QtWidgets.QFrame.HLine)
        divider.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.left_card.add_widget(divider)

        # CLI Companion Card
        cli_header = QtWidgets.QLabel("💻 CLI COMPANION CARD")
        cli_header.setStyleSheet("font-weight: bold; color: #67BE5E; font-size: 11px;")
        self.left_card.add_widget(cli_header)

        cli_desc = QtWidgets.QLabel(
            "This application includes a powerful CLI engine!\n\n"
            "Open your terminal and run:\n"
            "  apmultitool --help\n\n"
            "You can automate PDF merges, Bates stamping, and Word/Excel "
            "conversions directly in batch scripts."
        )
        cli_desc.setWordWrap(True)
        cli_desc.setStyleSheet("color: #374151; font-family: 'Consolas', monospace; font-size: 10px; padding: 5px;")
        self.left_card.add_widget(cli_desc)

        # Divider for Telemetry
        divider_tel = QtWidgets.QFrame()
        divider_tel.setFrameShape(QtWidgets.QFrame.HLine)
        divider_tel.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.left_card.add_widget(divider_tel)

        # Telemetry Header
        tel_header = QtWidgets.QLabel("📊 APPLICATION TELEMETRY")
        tel_header.setStyleSheet("font-weight: bold; color: #10B981; font-size: 11px;")
        self.left_card.add_widget(tel_header)

        # Telemetry Labels
        self.lbl_tel_total = QtWidgets.QLabel("Total runs: 0")
        self.lbl_tel_total.setStyleSheet("color: #374151; font-size: 11px;")
        self.left_card.add_widget(self.lbl_tel_total)

        self.lbl_tel_rate = QtWidgets.QLabel("Success Rate: 100.0%")
        self.lbl_tel_rate.setStyleSheet("color: #374151; font-size: 11px; font-weight: bold;")
        self.left_card.add_widget(self.lbl_tel_rate)

        self.lbl_tel_failed = QtWidgets.QLabel("Failed runs: 0")
        self.lbl_tel_failed.setStyleSheet("color: #374151; font-size: 11px;")
        self.left_card.add_widget(self.lbl_tel_failed)

        self.lbl_tel_cancelled = QtWidgets.QLabel("Cancelled runs: 0")
        self.lbl_tel_cancelled.setStyleSheet("color: #374151; font-size: 11px;")
        self.left_card.add_widget(self.lbl_tel_cancelled)

        self.lbl_tel_last_err = QtWidgets.QLabel("")
        self.lbl_tel_last_err.setWordWrap(True)
        self.lbl_tel_last_err.setStyleSheet("color: #DC2626; font-size: 10px; font-style: italic;")
        self.lbl_tel_last_err.setVisible(False)
        self.left_card.add_widget(self.lbl_tel_last_err)

        # Reset Button
        self.btn_reset_tel = QtWidgets.QPushButton("Reset Telemetry")
        self.btn_reset_tel.setObjectName("SecondaryButton")
        self.btn_reset_tel.setFixedHeight(24)
        self.btn_reset_tel.clicked.connect(self.reset_telemetry)
        self.left_card.add_widget(self.btn_reset_tel)

        self.left_card.add_stretch()
        splitter.addWidget(self.left_card)

        # ----------------------------------------------------
        # Right Panel (Engine Diagnostic Thread Verification Card)
        # ----------------------------------------------------
        self.right_card = SectionCard()
        
        d_header = QtWidgets.QLabel("CORE ENGINE DIAGNOSTIC BRIDGE (POC)")
        d_header.setObjectName("GroupHeader")
        self.right_card.add_widget(d_header)

        d_desc = QtWidgets.QLabel(
            "Validate thread-safe communication between the PySide6 UI and the "
            "underlying python document processing engine. Click the diagnostic button below "
            "to run asynchronous checks on a separate worker thread."
        )
        d_desc.setWordWrap(True)
        d_desc.setStyleSheet("color: #4B5563; font-size: 11px;")
        self.right_card.add_widget(d_desc)

        # Console Logs
        self.diag_console = QtWidgets.QPlainTextEdit()
        self.diag_console.setObjectName("ConsoleOutput")
        self.diag_console.setReadOnly(True)
        self.diag_console.appendPlainText("DIAGNOSTIC CHANNEL STANDBY...")
        self.right_card.add_widget(self.diag_console)

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
        self.right_card.add_widget(self.progress_bar)

        # Action Buttons Row
        self.btn_layout = ActionBar()
        self.btn_run = QtWidgets.QPushButton("Run Core Engine Diagnostic")
        self.btn_run.setObjectName("PrimaryButton")
        self.btn_run.clicked.connect(self.start_diagnostic)
        self.btn_layout.add_button(self.btn_run)

        self.btn_cancel = QtWidgets.QPushButton("Cancel")
        self.btn_cancel.setObjectName("DangerButton")
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self.cancel_diagnostic)
        self.btn_layout.add_button(self.btn_cancel)

        self.right_card.add_layout(self.btn_layout.layout_container)
        splitter.addWidget(self.right_card)

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
            dialogs.show_info(
                self, "Diagnostic Pass", 
                "Core Engine Diagnostic passed successfully! Signals cross thread bounds correctly."
            )
        else:
            dialogs.show_warning(
                self, "Diagnostic Stopped", 
                f"Core Engine Diagnostic: {message}"
            )

        # Cleanup references
        self.worker = None
        self.thread = None

    def update_telemetry_display(self):
        """Reload telemetry logs and refresh dashboard labels."""
        try:
            from apmultitool_qt.telemetry import telemetry_manager
            telemetry_manager.load()
            stats = telemetry_manager.stats
            rate = telemetry_manager.get_success_rate()
            
            self.lbl_tel_total.setText(f"Total runs: {stats['total_runs']}")
            self.lbl_tel_rate.setText(f"Success Rate: {rate:.1f}%")
            self.lbl_tel_failed.setText(f"Failed runs: {stats['failed_runs']}")
            self.lbl_tel_cancelled.setText(f"Cancelled runs: {stats['cancelled_runs']}")
            
            if stats.get("last_error"):
                err_text = f"Last error: {stats['last_error']}\n({stats['last_error_time']})"
                if len(err_text) > 120:
                    err_text = err_text[:117] + "..."
                self.lbl_tel_last_err.setText(err_text)
                self.lbl_tel_last_err.setVisible(True)
            else:
                self.lbl_tel_last_err.setVisible(False)
        except Exception as e:
            self.lbl_tel_last_err.setText(f"Telemetry error: {str(e)}")
            self.lbl_tel_last_err.setVisible(True)

    def showEvent(self, event):
        """Update telemetry dashboard when view is brought into focus."""
        super().showEvent(event)
        self.update_telemetry_display()

    def reset_telemetry(self):
        """Ask for confirmation and reset telemetry metrics."""
        if dialogs.show_confirmation(self, "Reset Telemetry?", "Are you sure you want to clear all execution statistics?"):
            try:
                from apmultitool_qt.telemetry import telemetry_manager
                telemetry_manager.reset()
                self.update_telemetry_display()
            except Exception as e:
                dialogs.show_error(self, "Error", f"Failed to reset telemetry: {str(e)}")
