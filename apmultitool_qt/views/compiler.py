# apmultitool_qt/views/compiler.py

"""Document Compiler View widget class for APMultitool Qt."""

from PySide6 import QtWidgets, QtCore

class CompilerView(QtWidgets.QWidget):
    """
    Placeholder View class for the Document Compiler workflow.
    Lays out a configuration sidebar and a document queue table.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        # Main layout is horizontal splitter separating left options from right queue
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(15)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        main_layout.addWidget(splitter)

        # ----------------------------------------------------
        # Left Panel (Fixed Config Sidebar)
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
        header = QtWidgets.QLabel("COMPILER SETTINGS")
        header.setObjectName("GroupHeader")
        left_layout.addWidget(header)

        # Checkboxes & Inputs
        self.chk_bookmarks = QtWidgets.QCheckBox("Create Table of Contents Bookmarks")
        self.chk_bookmarks.setChecked(True)
        self.chk_bookmarks.setToolTip("Generates hierarchical bookmarks mapping to merged document names.")
        left_layout.addWidget(self.chk_bookmarks)

        lbl_tip_bookmarks = QtWidgets.QLabel("Automatically converts file names into PDF sidecar outlines.")
        lbl_tip_bookmarks.setStyleSheet("color: #6B7280; font-size: 10px; margin-left: 26px;")
        left_layout.addWidget(lbl_tip_bookmarks)

        self.chk_fit = QtWidgets.QCheckBox("Enforce Standard Page Fit (Letter)")
        self.chk_fit.setChecked(True)
        left_layout.addWidget(self.chk_fit)

        lbl_tip_fit = QtWidgets.QLabel("Shrinks incoming images/pages to fit uniform 8.5x11 inches layout.")
        lbl_tip_fit.setStyleSheet("color: #6B7280; font-size: 10px; margin-left: 26px;")
        left_layout.addWidget(lbl_tip_fit)

        self.chk_compress = QtWidgets.QCheckBox("Compress Merged PDF Streams")
        left_layout.addWidget(self.chk_compress)

        lbl_tip_compress = QtWidgets.QLabel("Applies Deflate compression to output streams to optimize file size.")
        lbl_tip_compress.setStyleSheet("color: #6B7280; font-size: 10px; margin-left: 26px;")
        left_layout.addWidget(lbl_tip_compress)

        left_layout.addStretch()

        # Execute Button
        self.btn_run = QtWidgets.QPushButton("Combine & Merge Files")
        self.btn_run.setObjectName("PrimaryButton")
        left_layout.addWidget(self.btn_run)

        splitter.addWidget(left_panel)

        # ----------------------------------------------------
        # Right Panel (Stretching Files Queue)
        # ----------------------------------------------------
        right_panel = QtWidgets.QFrame()
        right_panel.setObjectName("GroupBoxContainer")

        right_layout = QtWidgets.QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(12)

        # Header
        q_header = QtWidgets.QLabel("COMPILATION QUEUE")
        q_header.setObjectName("GroupHeader")
        right_layout.addWidget(q_header)

        # Table
        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Order", "File Name", "File Size"])
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        right_layout.addWidget(self.table)

        # Prepopulate with placeholder documents for visual layout verification
        self.add_placeholder_row(1, "Exhibit_A1_Initial_Complaint.pdf", "4.2 MB")
        self.add_placeholder_row(2, "Exhibit_A2_Contract_Agreement.docx", "1.1 MB")
        self.add_placeholder_row(3, "Exhibit_B1_Invoice_Breakdown.xlsx", "850 KB")

        # Table Actions Buttons (Horizontal Row)
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(8)

        self.btn_add = QtWidgets.QPushButton("Add Files")
        self.btn_add.setObjectName("SecondaryButton")
        btn_layout.addWidget(self.btn_add)

        self.btn_up = QtWidgets.QPushButton("Move Up")
        self.btn_up.setObjectName("SecondaryButton")
        btn_layout.addWidget(self.btn_up)

        self.btn_down = QtWidgets.QPushButton("Move Down")
        self.btn_down.setObjectName("SecondaryButton")
        btn_layout.addWidget(self.btn_down)

        self.btn_remove = QtWidgets.QPushButton("Remove")
        self.btn_remove.setObjectName("SecondaryButton")
        btn_layout.addWidget(self.btn_remove)

        btn_layout.addStretch()

        self.btn_clear = QtWidgets.QPushButton("Clear")
        self.btn_clear.setObjectName("SecondaryButton")
        btn_layout.addWidget(self.btn_clear)

        right_layout.addLayout(btn_layout)

        splitter.addWidget(right_panel)

    def add_placeholder_row(self, order, name, size):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(order)))
        self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(name))
        self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(size))
