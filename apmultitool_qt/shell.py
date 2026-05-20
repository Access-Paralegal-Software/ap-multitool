# apmultitool_qt/shell.py

"""Main Shell Window implementing sidebar navigation for APMultitool Qt."""

from PySide6 import QtWidgets, QtCore, QtGui
from apmultitool_qt.styles import GLOBAL_STYLE
from apmultitool_qt.views import CompilerView, BatesView, FileRoomView, AboutView
from apmultitool_qt.security import vault
from core import __version__, __channel__

class APMainWindow(QtWidgets.QMainWindow):
    """
    Main shell interface for Access Paralegal Multitool.
    Integrates a left-side navigation sidebar, header, and content stacked layout.
    """
    def __init__(self):
        super().__init__()
        self.full_version = f"v{__version__}{__channel__}"
        self.setWindowTitle(f"Access Paralegal Multitool {self.full_version} (Qt Edition)")
        self.setMinimumSize(960, 760)
        self.setStyleSheet(GLOBAL_STYLE)
        self.setup_ui()
        QtCore.QTimer.singleShot(0, self.check_security)

    def check_security(self):
        if not vault.is_pro_activated:
            self.show_activation_dialog()
        else:
            self.load_vault_data()

    def show_activation_dialog(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Pro Activation Required")
        dialog.setModal(True)
        dialog.setFixedSize(400, 200)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        lbl_info = QtWidgets.QLabel("Enterprise Security requires hardware lock.")
        lbl_info.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(lbl_info)
        
        layout.addWidget(QtWidgets.QLabel("Enter License Key to Activate:"))
        
        key_input = QtWidgets.QLineEdit()
        layout.addWidget(key_input)
        
        btn_activate = QtWidgets.QPushButton("Activate")
        btn_activate.setObjectName("PrimaryButton")
        layout.addWidget(btn_activate)
        
        def attempt_activation():
            if vault.activate_license(key_input.text()):
                QtWidgets.QMessageBox.information(self, "Success", "License activated and locked to this terminal.")
                dialog.accept()
                self.load_vault_data()
            else:
                QtWidgets.QMessageBox.warning(self, "Error", "Invalid License Key!")
                
        btn_activate.clicked.connect(attempt_activation)
        dialog.exec()
        
        if not vault.is_pro_activated:
            # Quit if they cancel activation
            QtWidgets.QApplication.quit()
            
    def load_vault_data(self):
        data = vault.load_case_vault()
        # Optionally distribute 'data' to the views if needed
        self.set_status("Vault Loaded & Decrypted Successfully")

    def setup_ui(self):
        # Main central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        # Main horizontal layout dividing Sidebar (left) from Content (right)
        layout = QtWidgets.QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ----------------------------------------------------
        # 1. Left Sidebar Frame (Relative narrow width)
        # ----------------------------------------------------
        sidebar = QtWidgets.QFrame()
        sidebar.setObjectName("SidebarFrame")
        sidebar_layout = QtWidgets.QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Header Title
        sb_title = QtWidgets.QLabel("APMULTITOOL")
        sb_title.setObjectName("SidebarHeader")
        sb_title.setAlignment(QtCore.Qt.AlignCenter)
        sidebar_layout.addWidget(sb_title)

        # Navigation Buttons Group
        self.btn_group = QtWidgets.QButtonGroup(self)
        self.btn_group.setExclusive(True)

        self.btn_compiler = QtWidgets.QPushButton("📄  Document Compiler")
        self.btn_compiler.setObjectName("SidebarButton")
        self.btn_compiler.setCheckable(True)
        self.btn_compiler.setChecked(True)
        self.btn_group.addButton(self.btn_compiler, 0)
        sidebar_layout.addWidget(self.btn_compiler)

        self.btn_bates = QtWidgets.QPushButton("🔢  Bates Stamping")
        self.btn_bates.setObjectName("SidebarButton")
        self.btn_bates.setCheckable(True)
        self.btn_group.addButton(self.btn_bates, 1)
        sidebar_layout.addWidget(self.btn_bates)

        self.btn_fileroom = QtWidgets.QPushButton("🏛️  File Room & Trees")
        self.btn_fileroom.setObjectName("SidebarButton")
        self.btn_fileroom.setCheckable(True)
        self.btn_group.addButton(self.btn_fileroom, 2)
        sidebar_layout.addWidget(self.btn_fileroom)

        self.btn_about = QtWidgets.QPushButton("ℹ️  Help & About")
        self.btn_about.setObjectName("SidebarButton")
        self.btn_about.setCheckable(True)
        self.btn_group.addButton(self.btn_about, 3)
        sidebar_layout.addWidget(self.btn_about)

        sidebar_layout.addStretch()

        # Footer Label
        footer = QtWidgets.QLabel(f"Access Paralegal {self.full_version}")
        footer.setStyleSheet("color: #6B7280; font-size: 10px; padding: 15px; text-align: center;")
        footer.setAlignment(QtCore.Qt.AlignCenter)
        sidebar_layout.addWidget(footer)

        layout.addWidget(sidebar)

        # ----------------------------------------------------
        # 2. Right Area Layout (Header Banner + Stacked View)
        # ----------------------------------------------------
        right_container = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Header Banner Frame
        header_banner = QtWidgets.QFrame()
        header_banner.setObjectName("HeaderBanner")
        header_layout = QtWidgets.QVBoxLayout(header_banner)
        header_layout.setContentsMargins(25, 15, 25, 15)
        header_layout.setSpacing(4)

        self.lbl_title = QtWidgets.QLabel("Document Compiler")
        self.lbl_title.setObjectName("BannerTitle")
        header_layout.addWidget(self.lbl_title)

        self.lbl_sub = QtWidgets.QLabel("Queue, convert, and merge multiple documents and exhibits into a single PDF.")
        self.lbl_sub.setObjectName("BannerSub")
        header_layout.addWidget(self.lbl_sub)

        right_layout.addWidget(header_banner)

        # QStackedWidget Content Area
        self.stacked_widget = QtWidgets.QStackedWidget()
        
        self.view_compiler = CompilerView()
        self.view_bates = BatesView()
        self.view_fileroom = FileRoomView()
        self.view_about = AboutView()

        self.stacked_widget.addWidget(self.view_compiler)
        self.stacked_widget.addWidget(self.view_bates)
        self.stacked_widget.addWidget(self.view_fileroom)
        self.stacked_widget.addWidget(self.view_about)

        right_layout.addWidget(self.stacked_widget)
        layout.addWidget(right_container)

        # Wire navigation buttons to switch views
        self.btn_group.idClicked.connect(self.switch_view)

        # ----------------------------------------------------
        # 3. Status Bar & Persistent Progress Bar
        # ----------------------------------------------------
        self.status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(self.status_bar)

        # Standard status label
        self.status_label = QtWidgets.QLabel("Ready")
        self.status_bar.addWidget(self.status_label, 1)

        # Determinate progress bar overlay inside the statusbar, hidden by default
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setFixedWidth(180)
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #E5E7EB;
                border-radius: 4px;
                text-align: center;
                background-color: #FFFFFF;
                height: 14px;
            }
            QProgressBar::chunk {
                background-color: #67BE5E;
            }
        """)
        self.status_bar.addPermanentWidget(self.progress_bar)

    def closeEvent(self, event: QtGui.QCloseEvent):
        """Handle safe termination of background worker threads upon application close."""
        def safe_stop(view):
            if getattr(view, "active_worker", None) and hasattr(view.active_worker, "request_cancel"):
                view.active_worker.request_cancel()
            if getattr(view, "thread", None) and view.thread.isRunning():
                view.thread.quit()
                view.thread.wait()

        safe_stop(self.view_compiler)
        safe_stop(self.view_bates)
        safe_stop(self.view_fileroom)
        
        event.accept()

    def set_status(self, text: str):
        """Update standard statusbar text label."""
        self.status_label.setText(text)

    def show_progress(self, percent: int, msg: str | None = None):
        """Display progress bar and update its active state."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(percent)
        if msg:
            self.set_status(msg)

    def hide_progress(self, msg: str = "Ready"):
        """Hide statusbar progress indicators."""
        self.progress_bar.setVisible(False)
        self.set_status(msg)

    def switch_view(self, view_id):
        # Switch stacked widget active index
        self.stacked_widget.setCurrentIndex(view_id)

        # Update header banner labels
        if view_id == 0:
            self.lbl_title.setText("Document Compiler")
            self.lbl_sub.setText("Queue, convert, and merge multiple documents and exhibits into a single PDF.")
        elif view_id == 1:
            self.lbl_title.setText("Bates Stamping & Compliance")
            self.lbl_sub.setText("Apply sequential Bates labeling numbering to files with collision avoidance safety.")
        elif view_id == 2:
            self.lbl_title.setText("File Room Matter Structure Architect")
            self.lbl_sub.setText("Spin up standardized case directory structures automatically from blueprints.")
        elif view_id == 3:
            self.lbl_title.setText("Help & Application Support")
            self.lbl_sub.setText("System operational metadata metrics and background threading diagnostics.")
