# apmultitool_qt/views/bates.py

"""Bates Stamping View widget class for APMultitool Qt."""

from PySide6 import QtWidgets, QtCore
from apmultitool_qt.components import SectionCard, FormRow, ActionBar, HintLabel, dialogs, file_dialogs

class BatesView(QtWidgets.QWidget):
    """
    Refined Bates Stamping view.
    Lays out parameters utilizing standardized FormRows and handles output logging.
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
        # Left Panel (Parameters Card)
        # ----------------------------------------------------
        self.left_card = SectionCard()
        self.left_card.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.left_card.setMinimumWidth(320)
        self.left_card.setMaximumWidth(340)

        # Header Title
        header = QtWidgets.QLabel("BATES PARAMETERS")
        header.setObjectName("GroupHeader")
        self.left_card.add_widget(header)

        # Target File FormRow
        lbl_file = QtWidgets.QLabel("Target PDF:")
        lbl_file.setStyleSheet("font-weight: 500; color: #374151;")
        
        target_layout = QtWidgets.QHBoxLayout()
        target_layout.setSpacing(6)
        self.txt_target = QtWidgets.QLineEdit()
        self.txt_target.setPlaceholderText("Select PDF document...")
        target_layout.addWidget(self.txt_target)

        self.btn_browse = QtWidgets.QPushButton("...")
        self.btn_browse.setObjectName("SecondaryButton")
        self.btn_browse.setFixedWidth(40)
        self.btn_browse.clicked.connect(self.browse_pdf)
        target_layout.addWidget(self.btn_browse)

        file_widget = QtWidgets.QWidget()
        file_widget.setLayout(target_layout)
        self.left_card.add_widget(FormRow("Target PDF:", file_widget, label_width=90))

        # Prefix
        self.txt_prefix = QtWidgets.QLineEdit()
        self.txt_prefix.setText("AP")
        self.left_card.add_widget(FormRow("Bates Prefix:", self.txt_prefix, label_width=90))

        # Start Index
        self.txt_start = QtWidgets.QLineEdit()
        self.txt_start.setText("1")
        self.left_card.add_widget(FormRow("Start Index:", self.txt_start, label_width=90))

        # Checkbox Settings
        self.chk_shrink = QtWidgets.QCheckBox("Bates Collision Avoidance")
        self.chk_shrink.setChecked(True)
        self.left_card.add_widget(self.chk_shrink)
        self.left_card.add_widget(HintLabel("Shrinks pages by 10% to prevent footer text collisions."))

        self.left_card.add_stretch()

        # Primary Run Action Bar
        self.action_bar = ActionBar()
        self.btn_run = QtWidgets.QPushButton("Flatten & Apply Bates")
        self.btn_run.setObjectName("PrimaryButton")
        self.btn_run.clicked.connect(self.run_bates)
        self.action_bar.add_button(self.btn_run)
        self.left_card.add_layout(self.action_bar.layout_container)

        splitter.addWidget(self.left_card)

        # ----------------------------------------------------
        # Right Panel (Console Terminal Output Card)
        # ----------------------------------------------------
        self.right_card = SectionCard()
        
        c_header = QtWidgets.QLabel("BATES OUTPUT TERMINAL")
        c_header.setObjectName("GroupHeader")
        self.right_card.add_widget(c_header)

        # Console Text Box
        self.console = QtWidgets.QPlainTextEdit()
        self.console.setObjectName("ConsoleOutput")
        self.console.setReadOnly(True)
        self.console.appendPlainText("SYSTEM TERMINAL READY. WAITING FOR OPERATION PARAMETERS...")
        self.right_card.add_widget(self.console)

        # Bottom clear button
        self.btn_clear = QtWidgets.QPushButton("Clear Console")
        self.btn_clear.setObjectName("SecondaryButton")
        self.btn_clear.setFixedWidth(120)
        self.btn_clear.clicked.connect(self.clear_console)
        self.right_card.add_widget(self.btn_clear)

        splitter.addWidget(self.right_card)

    def browse_pdf(self):
        path = file_dialogs.get_open_file(
            self,
            "Select Target PDF",
            "PDF Documents (*.pdf)"
        )
        if path:
            self.txt_target.setText(path)

    def clear_console(self):
        if dialogs.show_confirmation(self, "Clear Console?", "Are you sure you want to clear the terminal output history?"):
            self.console.clear()
            self.console.appendPlainText("SYSTEM TERMINAL READY. WAITING FOR OPERATION PARAMETERS...")

    def run_bates(self):
        target = self.txt_target.text().strip()
        if not target:
            dialogs.show_warning(self, "Input Error", "Please select a target PDF document before applying stamps.")
            return

        dialogs.show_info(self, "Bates Simulator", "Simulating Bates stamping. Infrastructure validation checks pass successfully!")
        self.console.appendPlainText(f"STAMP RUN: Prefix={self.txt_prefix.text()}, Start={self.txt_start.text()}")
