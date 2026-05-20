# apmultitool_qt/views/compiler.py

"""Document Compiler View widget class for APMultitool Qt."""

import os
from PySide6 import QtWidgets, QtCore
from apmultitool_qt.components import SectionCard, FormRow, ActionBar, HintLabel, EmptyStateWidget, dialogs, file_dialogs

class CompilerView(QtWidgets.QWidget):
    """
    Refined Document Compiler view.
    Lays out option containers using shared primitives and handles file table queues.
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
        # Left Panel (Options Sidebar Card)
        # ----------------------------------------------------
        self.left_card = SectionCard()
        self.left_card.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.left_card.setMinimumWidth(320)
        self.left_card.setMaximumWidth(340)

        # Header Title
        header = QtWidgets.QLabel("COMPILER SETTINGS")
        header.setObjectName("GroupHeader")
        self.left_card.add_widget(header)

        # Parameter fields
        self.chk_bookmarks = QtWidgets.QCheckBox("Create Table of Contents Bookmarks")
        self.chk_bookmarks.setChecked(True)
        self.left_card.add_widget(self.chk_bookmarks)
        self.left_card.add_widget(HintLabel("Generates bookmarks mapping merged documents outlines."))

        self.chk_fit = QtWidgets.QCheckBox("Enforce Standard Page Fit (Letter)")
        self.chk_fit.setChecked(True)
        self.left_card.add_widget(self.chk_fit)
        self.left_card.add_widget(HintLabel("Shrinks pages to fit uniform 8.5x11 inches layout."))

        self.chk_compress = QtWidgets.QCheckBox("Compress Merged PDF Streams")
        self.left_card.add_widget(self.chk_compress)
        self.left_card.add_widget(HintLabel("Applies compression to optimize target output size."))

        self.left_card.add_stretch()

        # Primary Run Action Bar
        self.action_bar = ActionBar()
        self.btn_run = QtWidgets.QPushButton("Combine & Merge Files")
        self.btn_run.setObjectName("PrimaryButton")
        self.btn_run.clicked.connect(self.run_merge)
        self.action_bar.add_button(self.btn_run)
        self.left_card.add_layout(self.action_bar.layout_container)

        splitter.addWidget(self.left_card)

        # ----------------------------------------------------
        # Right Panel (Queue Layout Card)
        # ----------------------------------------------------
        self.right_card = SectionCard()
        
        q_header = QtWidgets.QLabel("COMPILATION QUEUE")
        q_header.setObjectName("GroupHeader")
        self.right_card.add_widget(q_header)

        # Table & Empty state side-by-side inside stacked layout
        self.table_stack = QtWidgets.QStackedWidget()
        
        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Order", "File Name", "File Size"])
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table_stack.addWidget(self.table)
        
        self.empty_widget = EmptyStateWidget("Add PDF, Word, or Excel files to compile...")
        self.table_stack.addWidget(self.empty_widget)

        self.right_card.add_widget(self.table_stack)

        # Prepopulate with placeholder documents
        self.add_row("Exhibit_A1_Initial_Complaint.pdf", "4.2 MB")
        self.add_row("Exhibit_A2_Contract_Agreement.docx", "1.1 MB")
        self.add_row("Exhibit_B1_Invoice_Breakdown.xlsx", "850 KB")

        # Table Actions Buttons Row
        self.tbl_action_bar = ActionBar()
        
        self.btn_add = QtWidgets.QPushButton("Add Files")
        self.btn_add.setObjectName("SecondaryButton")
        self.btn_add.clicked.connect(self.add_files)
        self.tbl_action_bar.add_button(self.btn_add)

        self.btn_remove = QtWidgets.QPushButton("Remove")
        self.btn_remove.setObjectName("SecondaryButton")
        self.btn_remove.clicked.connect(self.remove_selected)
        self.tbl_action_bar.add_button(self.btn_remove)

        self.tbl_action_bar.add_stretch()

        self.btn_clear = QtWidgets.QPushButton("Clear")
        self.btn_clear.setObjectName("SecondaryButton")
        self.btn_clear.clicked.connect(self.clear_queue)
        self.tbl_action_bar.add_button(self.btn_clear)

        self.right_card.add_layout(self.tbl_action_bar.layout_container)

        splitter.addWidget(self.right_card)

    def add_row(self, name: str, size: str):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(row + 1)))
        self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(name))
        self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(size))
        self.table_stack.setCurrentIndex(0)  # Show table

    def add_files(self):
        files = file_dialogs.get_open_files(
            self,
            "Select Documents to Add",
            "Supported Formats (*.pdf *.docx *.xlsx *.eml *.msg)"
        )
        for f in files:
            name = os.path.basename(f)
            # Fetch file size helper
            try:
                sz = os.path.getsize(f)
                sz_str = f"{sz / 1024 / 1024:.1f} MB" if sz > 1024*1024 else f"{sz / 1024:.1f} KB"
            except Exception:
                sz_str = "Unknown"
            self.add_row(name, sz_str)

    def remove_selected(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            dialogs.show_warning(self, "No Selection", "Please select a row in the compilation queue first.")
            return
        
        # Remove in reverse order
        for idx in sorted(selected, key=lambda x: x.row(), reverse=True):
            self.table.removeRow(idx.row())

        # Update order numbering
        for r in range(self.table.rowCount()):
            self.table.item(r, 0).setText(str(r + 1))

        if self.table.rowCount() == 0:
            self.table_stack.setCurrentIndex(1)  # Show empty state

    def clear_queue(self):
        if self.table.rowCount() == 0:
            return
        if dialogs.show_confirmation(self, "Clear Queue?", "Are you sure you want to remove all files from the merge queue?"):
            self.table.setRowCount(0)
            self.table_stack.setCurrentIndex(1)

    def run_merge(self):
        if self.table.rowCount() == 0:
            dialogs.show_warning(self, "Empty Queue", "No documents in compilation queue. Please add files before merging.")
            return

        dialogs.show_info(self, "Merge Simulator", "Simulating PDF compilation. Background engine infrastructure tests check out!")
