# apmultitool_qt/views/bates.py

"""Bates Stamping View widget class for APMultitool Qt."""

from PySide6 import QtWidgets, QtCore

class BatesView(QtWidgets.QWidget):
    """
    Placeholder View class for the Bates Stamping workflow.
    Lays out configuration entries and a terminal logging screen.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(15)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        main_layout.addWidget(splitter)

        # ----------------------------------------------------
        # Left Panel (Fixed Parameters Sidebar)
        # ----------------------------------------------------
        left_panel = QtWidgets.QFrame()
        left_panel.setObjectName("GroupBoxContainer")
        left_panel.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        left_panel.setMinimumWidth(320)
        left_panel.setMaximumWidth(340)

        left_layout = QtWidgets.QVBoxLayout(left_panel)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(12)

        # Header
        header = QtWidgets.QLabel("BATES PARAMETERS")
        header.setObjectName("GroupHeader")
        left_layout.addWidget(header)

        # Target File Picker
        left_layout.addWidget(QtWidgets.QLabel("Target PDF Document:"))
        target_layout = QtWidgets.QHBoxLayout()
        self.txt_target = QtWidgets.QLineEdit()
        self.txt_target.setPlaceholderText("Select a PDF to stamp...")
        target_layout.addWidget(self.txt_target)

        self.btn_browse = QtWidgets.QPushButton("...")
        self.btn_browse.setObjectName("SecondaryButton")
        self.btn_browse.setFixedWidth(40)
        target_layout.addWidget(self.btn_browse)
        left_layout.addLayout(target_layout)

        # Prefix
        left_layout.addWidget(QtWidgets.QLabel("Bates Case Prefix:"))
        self.txt_prefix = QtWidgets.QLineEdit()
        self.txt_prefix.setText("AP")
        left_layout.addWidget(self.txt_prefix)

        # Start Index
        left_layout.addWidget(QtWidgets.QLabel("Bates Starting Index:"))
        self.txt_start = QtWidgets.QLineEdit()
        self.txt_start.setText("1")
        left_layout.addWidget(self.txt_start)

        # Collision Checkbox
        self.chk_shrink = QtWidgets.QCheckBox("Shrink Page: Bates Collision Avoidance")
        self.chk_shrink.setChecked(True)
        left_layout.addWidget(self.chk_shrink)

        lbl_tip_shrink = QtWidgets.QLabel("Resizes pages by 90% to avoid overlapping footer text.")
        lbl_tip_shrink.setStyleSheet("color: #6B7280; font-size: 10px; margin-left: 26px;")
        left_layout.addWidget(lbl_tip_shrink)

        # Advanced Settings Button
        self.btn_advanced = QtWidgets.QPushButton("Advanced Bates Setup")
        self.btn_advanced.setObjectName("SecondaryButton")
        left_layout.addWidget(self.btn_advanced)

        left_layout.addStretch()

        # Primary Run Action Button
        self.btn_run = QtWidgets.QPushButton("Flatten & Apply Bates")
        self.btn_run.setObjectName("PrimaryButton")
        left_layout.addWidget(self.btn_run)

        splitter.addWidget(left_panel)

        # ----------------------------------------------------
        # Right Panel (Bates Console Terminal)
        # ----------------------------------------------------
        right_panel = QtWidgets.QFrame()
        right_panel.setObjectName("GroupBoxContainer")

        right_layout = QtWidgets.QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(12)

        # Header
        c_header = QtWidgets.QLabel("BATES OUTPUT TERMINAL")
        c_header.setObjectName("GroupHeader")
        right_layout.addWidget(c_header)

        # Console Text Box
        self.console = QtWidgets.QPlainTextEdit()
        self.console.setObjectName("ConsoleOutput")
        self.console.setReadOnly(True)
        self.console.appendPlainText("SYSTEM TERMINAL READY. WAITING FOR OPERATION PARAMETERS...")
        right_layout.addWidget(self.console)

        # Bottom clear button
        self.btn_clear = QtWidgets.QPushButton("Clear Console")
        self.btn_clear.setObjectName("SecondaryButton")
        self.btn_clear.setFixedWidth(120)
        right_layout.addWidget(self.btn_clear)

        splitter.addWidget(right_panel)
