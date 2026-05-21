# apmultitool_qt/views/compiler.py

"""Document Compiler View widget class for APMultitool Qt."""

import os
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui
from apmultitool_qt.components import (
    SectionCard,
    FormRow,
    ActionBar,
    HintLabel,
    EmptyStateWidget,
    dialogs,
    file_dialogs
)
from apmultitool_qt.core_bridge import EngineJobWorker


def format_size(path_str):
    """Format file size in human-readable notation."""
    try:
        sz = os.path.getsize(path_str)
        if sz > 1024 * 1024:
            return f"{sz / 1024 / 1024:.1f} MB"
        elif sz > 1024:
            return f"{sz / 1024:.1f} KB"
        else:
            return f"{sz} B"
    except Exception:
        return "Unknown"


def get_format_display(path_str):
    """Return formatted display name for file extensions."""
    ext = os.path.splitext(path_str.lower())[1]
    if ext == ".pdf":
        return "PDF"
    elif ext in (".docx", ".doc"):
        return "Word"
    elif ext in (".xlsx", ".xls"):
        return "Excel"
    elif ext in (".eml", ".msg"):
        return "Email"
    elif ext in (".png", ".jpg", ".jpeg", ".tiff", ".tif", ".gif", ".bmp"):
        return "Image"
    elif ext in (".txt", ".csv"):
        return "Text"
    else:
        return "Unknown"


class CompilerQueueTable(QtWidgets.QTableWidget):
    """
    Custom QTableWidget that accepts drag-and-drop files from the OS.
    """
    files_dropped = QtCore.Signal(list)

    def __init__(self, rows, cols, parent=None):
        super().__init__(rows, cols, parent)
        self.setAcceptDrops(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            paths = []
            for url in event.mimeData().urls():
                p = url.toLocalFile()
                if p:
                    paths.append(p)
            if paths:
                self.files_dropped.emit(paths)
        else:
            super().dropEvent(event)


class CompilerView(QtWidgets.QWidget):
    """
    Refined Document Compiler view.
    Lays out option containers using shared primitives and handles file table queues.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.queue_files = []
        self.thread = None
        self.active_worker = None
        
        # Resolve repository root and default output path
        self.repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.default_output_dir = os.path.join(self.repo_root, "Merged_Output")
        
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
        self.left_card.add_widget(HintLabel("Normalizes pages to fit uniform letter sizes."))

        self.chk_compress = QtWidgets.QCheckBox("Compress Merged PDF Streams")
        self.left_card.add_widget(self.chk_compress)
        self.left_card.add_widget(HintLabel("Applies compression to optimize target output size."))

        self.chk_grayscale = QtWidgets.QCheckBox("Grayscale Output")
        self.left_card.add_widget(self.chk_grayscale)
        self.left_card.add_widget(HintLabel("Converts source pages to black and white format."))

        # Output file name field
        self.output_name_input = QtWidgets.QLineEdit()
        self.output_name_input.setText("compiled_output.pdf")
        self.output_name_input.setPlaceholderText("e.g. Matter_123_Merge.pdf")
        self.output_name_input.editingFinished.connect(self.on_output_name_editing_finished)
        self.left_card.add_widget(FormRow("Output PDF Name:", self.output_name_input, label_width=120))

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

        # Output Folder selector row
        self.output_dir_input = QtWidgets.QLineEdit()
        self.output_dir_input.setText(self.default_output_dir)
        self.btn_browse = QtWidgets.QPushButton("Browse")
        self.btn_browse.clicked.connect(self.browse_output_dir)
        
        dir_widget = QtWidgets.QWidget()
        dir_layout = QtWidgets.QHBoxLayout(dir_widget)
        dir_layout.setContentsMargins(0, 0, 0, 0)
        dir_layout.setSpacing(5)
        dir_layout.addWidget(self.output_dir_input)
        dir_layout.addWidget(self.btn_browse)
        
        self.right_card.add_widget(FormRow("Output Folder:", dir_widget, label_width=100))

        # Table & Empty state side-by-side inside stacked layout
        self.table_stack = QtWidgets.QStackedWidget()
        
        self.table = CompilerQueueTable(0, 6)
        self.table.setHorizontalHeaderLabels(["#", "File Name", "Size", "Format", "Path", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table_stack.addWidget(self.table)
        
        self.empty_widget = EmptyStateWidget("Drag & Drop documents or click Add Files below to start...")
        self.table_stack.addWidget(self.empty_widget)

        self.right_card.add_widget(self.table_stack)
        self.table_stack.setCurrentIndex(1)  # start as empty state

        # Table Actions Buttons Row
        self.tbl_action_bar = ActionBar()
        
        self.btn_move_up = QtWidgets.QPushButton("Move Up ⬆")
        self.btn_move_up.setObjectName("SecondaryButton")
        self.btn_move_up.clicked.connect(self.move_item_up)
        self.tbl_action_bar.add_button(self.btn_move_up)

        self.btn_move_down = QtWidgets.QPushButton("Move Down ⬇")
        self.btn_move_down.setObjectName("SecondaryButton")
        self.btn_move_down.clicked.connect(self.move_item_down)
        self.tbl_action_bar.add_button(self.btn_move_down)
        
        self.tbl_action_bar.add_stretch()

        self.btn_add = QtWidgets.QPushButton("Add Files")
        self.btn_add.setObjectName("SecondaryButton")
        self.btn_add.clicked.connect(self.add_files)
        self.tbl_action_bar.add_button(self.btn_add)

        self.btn_add_dir = QtWidgets.QPushButton("Add Folder")
        self.btn_add_dir.setObjectName("SecondaryButton")
        self.btn_add_dir.clicked.connect(self.add_directory)
        self.tbl_action_bar.add_button(self.btn_add_dir)

        self.btn_remove = QtWidgets.QPushButton("Remove")
        self.btn_remove.setObjectName("SecondaryButton")
        self.btn_remove.clicked.connect(self.remove_selected)
        self.tbl_action_bar.add_button(self.btn_remove)

        self.btn_clear = QtWidgets.QPushButton("Clear Queue")
        self.btn_clear.setObjectName("SecondaryButton")
        self.btn_clear.clicked.connect(self.clear_queue)
        self.tbl_action_bar.add_button(self.btn_clear)

        self.right_card.add_layout(self.tbl_action_bar.layout_container)

        splitter.addWidget(self.right_card)

        # Wire table drop events to internal loader
        self.table.files_dropped.connect(self.add_file_paths)

    def get_main_window(self):
        """Helper to walk up parent widgets and locate the shell APMainWindow."""
        widget = self
        while widget is not None:
            if hasattr(widget, "show_progress"):
                return widget
            widget = widget.parent()
        return None

    def update_main_status(self, progress_percent: int, message: str):
        """Forward progress stats to main window shell indicators."""
        main_win = self.get_main_window()
        if main_win:
            main_win.show_progress(progress_percent, message)

    def clear_main_status(self):
        """Clear progress indicators on the main window shell."""
        main_win = self.get_main_window()
        if main_win:
            main_win.hide_progress("Ready")

    def on_output_name_editing_finished(self):
        """Ensure cleared output file name falls back to a safe default."""
        text = self.output_name_input.text().strip()
        if not text:
            self.output_name_input.setText("compiled.pdf")

    def browse_output_dir(self):
        """Select a target save folder and update field path."""
        target_dir = file_dialogs.get_existing_directory(
            self,
            "Select Output Save Folder"
        )
        if target_dir:
            self.output_dir_input.setText(target_dir)

    def add_file_paths(self, paths: list[str]):
        """Filter list of files/directories for supported formats and append to queue."""
        supported_exts = {
            ".pdf", ".docx", ".doc", ".xlsx", ".xls", ".eml", ".msg",
            ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".gif", ".bmp",
            ".txt", ".csv"
        }
        
        resolved_paths = []
        for p in paths:
            p = os.path.abspath(p)
            if os.path.isdir(p):
                # Scan directory for supported formats
                for root, _, files in os.walk(p):
                    for file in files:
                        ext = os.path.splitext(file.lower())[1]
                        if ext in supported_exts:
                            resolved_paths.append(os.path.join(root, file))
            else:
                ext = os.path.splitext(p.lower())[1]
                if ext in supported_exts:
                    resolved_paths.append(p)

        added = False
        self.table.blockSignals(True)
        for path_str in resolved_paths:
            if path_str not in self.queue_files:
                self.queue_files.append(path_str)
                name = os.path.basename(path_str)
                sz = format_size(path_str)
                fmt = get_format_display(path_str)
                
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(row + 1)))
                self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(name))
                self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(sz))
                self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(fmt))
                self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(path_str))
                self.table.setItem(row, 5, QtWidgets.QTableWidgetItem("Pending"))
                
                added = True
        self.table.blockSignals(False)

        if added:
            self.table_stack.setCurrentIndex(0)  # Show table view
            self.normalize_indices()

    def add_files(self):
        """Open native picker to load multiple document files."""
        files = file_dialogs.get_open_files(
            self,
            "Select Documents to Add",
            "Supported Formats (*.pdf *.docx *.doc *.xlsx *.xls *.eml *.msg *.png *.jpg *.jpeg *.tiff *.tif *.txt *.csv)"
        )
        if files:
            self.add_file_paths(files)

    def add_directory(self):
        """Open native picker to select and load all items from a directory."""
        dir_path = file_dialogs.get_existing_directory(
            self,
            "Select Folder containing Documents"
        )
        if dir_path:
            self.add_file_paths([dir_path])

    def remove_selected(self):
        """Remove currently selected rows in the table queue."""
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            dialogs.show_warning(self, "No Selection", "Please select a row in the compilation queue first.")
            return

        # Delete from table in reverse row index order
        for idx in sorted(selected, key=lambda x: x.row(), reverse=True):
            r = idx.row()
            if 0 <= r < len(self.queue_files):
                self.queue_files.pop(r)
            self.table.removeRow(r)

        self.normalize_indices()

        if self.table.rowCount() == 0:
            self.table_stack.setCurrentIndex(1)  # Show empty state

    def clear_queue(self):
        """Prompt to clear all document slots in compiler queue."""
        if self.table.rowCount() == 0:
            return
        if dialogs.show_confirmation(self, "Clear Queue?", "Are you sure you want to remove all files from the merge queue?"):
            self.table.setRowCount(0)
            self.queue_files.clear()
            self.table_stack.setCurrentIndex(1)

    def move_item_up(self):
        """Shift selected queue document up one index position."""
        row = self.table.currentRow()
        if row <= 0:
            return

        # Swap files list values
        self.queue_files[row], self.queue_files[row - 1] = self.queue_files[row - 1], self.queue_files[row]
        
        # Swap visual cell items
        self.swap_table_rows(row, row - 1)
        self.table.selectRow(row - 1)
        self.table.setCurrentCell(row - 1, 0)
        self.normalize_indices()

    def move_item_down(self):
        """Shift selected queue document down one index position."""
        row = self.table.currentRow()
        if row < 0 or row >= self.table.rowCount() - 1:
            return

        # Swap files list values
        self.queue_files[row], self.queue_files[row + 1] = self.queue_files[row + 1], self.queue_files[row]
        
        # Swap visual cell items
        self.swap_table_rows(row, row + 1)
        self.table.selectRow(row + 1)
        self.table.setCurrentCell(row + 1, 0)
        self.normalize_indices()

    def swap_table_rows(self, r1, r2):
        """Swap content items between two rows (retains '#' column index values)."""
        self.table.blockSignals(True)
        for col in range(self.table.columnCount()):
            if col == 0:
                continue
            item1 = self.table.takeItem(r1, col)
            item2 = self.table.takeItem(r2, col)
            self.table.setItem(r1, col, item2)
            self.table.setItem(r2, col, item1)
        self.table.blockSignals(False)

    def normalize_indices(self):
        """Reset serial counter indexes in column 0."""
        self.table.blockSignals(True)
        for r in range(self.table.rowCount()):
            self.table.setItem(r, 0, QtWidgets.QTableWidgetItem(str(r + 1)))
        self.table.blockSignals(False)

    def toggle_inputs(self, enabled: bool):
        """Toggle usability of inputs during background compile tasks."""
        self.chk_bookmarks.setEnabled(enabled)
        self.chk_fit.setEnabled(enabled)
        self.chk_compress.setEnabled(enabled)
        self.chk_grayscale.setEnabled(enabled)
        self.output_name_input.setEnabled(enabled)
        self.output_dir_input.setEnabled(enabled)
        self.btn_browse.setEnabled(enabled)
        self.btn_move_up.setEnabled(enabled)
        self.btn_move_down.setEnabled(enabled)
        self.btn_add.setEnabled(enabled)
        self.btn_add_dir.setEnabled(enabled)
        self.btn_remove.setEnabled(enabled)
        self.btn_clear.setEnabled(enabled)
        self.table.setAcceptDrops(enabled)

    def run_merge(self):
        """Initialize, validate, and invoke standard merge engine job on worker thread."""
        if self.active_worker:
            # Running! Act as cancellation request.
            self.active_worker.request_cancel()
            self.btn_run.setText("Cancelling...")
            self.btn_run.setEnabled(False)
            return

        if not self.queue_files:
            dialogs.show_warning(self, "Empty Queue", "No documents in compilation queue. Please add files before merging.")
            return

        out_dir_str = self.output_dir_input.text().strip()
        if not out_dir_str:
            dialogs.show_warning(self, "Invalid Path", "Please specify a target output directory.")
            return
            
        out_dir = Path(out_dir_str)
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            dialogs.show_error(self, "Directory Error", f"Could not create target directory: {str(e)}")
            return

        out_name = self.output_name_input.text().strip()
        if not out_name:
            dialogs.show_warning(self, "Invalid Output Name", "Please specify a target output PDF name.")
            return
        if not out_name.lower().endswith(".pdf"):
            out_name += ".pdf"
            self.output_name_input.setText(out_name)
            
        final_output_path = out_dir / out_name
        if final_output_path.exists():
            if not dialogs.show_confirmation(self, "Overwrite PDF?", f"The file '{out_name}' already exists in this folder.\n\nDo you want to overwrite it?"):
                return

        if not dialogs.show_confirmation(self, "Confirm Merge Order", "Please ensure the documents in the list are in the exact order you want them merged.\n\nProceed with compile merge?"):
            return

        # Prepare Core Engine spec structures
        from core.job import Job, InputSpec, MergeParams, OutputSpec
        
        job_inputs = []
        for idx, path_str in enumerate(self.queue_files):
            self.table.setItem(idx, 5, QtWidgets.QTableWidgetItem("Processing..."))
            job_inputs.append(InputSpec.from_path(Path(path_str), order_index=idx))

        job_params = MergeParams(
            bookmarks=self.chk_bookmarks.isChecked(),
            enforce_page_size=self.chk_fit.isChecked(),
            grayscale=self.chk_grayscale.isChecked(),
            output_name=out_name
        )
        
        job_output = OutputSpec(directory=out_dir, overwrite=True)
        
        job = Job(
            operation="merge",
            inputs=job_inputs,
            params=job_params,
            output=job_output
        )

        # Thread setup
        self.thread = QtCore.QThread()
        self.active_worker = EngineJobWorker(job, output_root=out_dir)
        self.active_worker.moveToThread(self.thread)

        # Wire Slots
        self.thread.started.connect(self.active_worker.run_job)
        self.active_worker.started.connect(self.on_merge_started)
        self.active_worker.progress.connect(self.on_merge_progress)
        self.active_worker.finished.connect(self.on_merge_finished)

        self.thread.start()

    def on_merge_started(self):
        """Prepare UI states for job execution."""
        self.toggle_inputs(False)
        self.btn_run.setText("🛑 CANCEL COMPILE")
        self.btn_run.setObjectName("DangerButton")
        self.btn_run.setStyleSheet("background-color: #DC2626; color: white;")

    def on_merge_progress(self, percent: int, msg: str):
        """Feed progress data to screen and table statuses."""
        self.update_main_status(percent, msg)
        
        # Highlight active row in progress
        for idx, filepath in enumerate(self.queue_files):
            filename = os.path.basename(filepath)
            if filename in msg:
                self.table.setItem(idx, 5, QtWidgets.QTableWidgetItem("Processing..."))
            elif percent >= 60 or "Merging" in msg or "Writing" in msg:
                item_status = self.table.item(idx, 5)
                if item_status and item_status.text() == "Processing...":
                    self.table.setItem(idx, 5, QtWidgets.QTableWidgetItem("✅ Combined"))

    def on_merge_finished(self, success: bool, error_msg: str, result: object):
        """Clean up thread variables and show success/fail status results."""
        if self.thread:
            self.thread.quit()
            self.thread.wait()
            self.thread = None

        self.active_worker = None
        self.toggle_inputs(True)
        self.btn_run.setText("Combine & Merge Files")
        self.btn_run.setObjectName("PrimaryButton")
        self.btn_run.setStyleSheet("")
        
        self.clear_main_status()

        if success:
            for r in range(self.table.rowCount()):
                self.table.setItem(r, 5, QtWidgets.QTableWidgetItem("✅ Combined"))
            dialogs.show_info(self, "Compilation Successful", "Document merge completed successfully!")
        else:
            if error_msg == "Operation cancelled.":
                for r in range(self.table.rowCount()):
                    status_item = self.table.item(r, 5)
                    if status_item and status_item.text() == "Processing...":
                        self.table.setItem(r, 5, QtWidgets.QTableWidgetItem("⚠️ Cancelled"))
                dialogs.show_info(self, "Compilation Cancelled", "Document compilation was cancelled.")
            else:
                for r in range(self.table.rowCount()):
                    status_item = self.table.item(r, 5)
                    if status_item and status_item.text() == "Processing...":
                        self.table.setItem(r, 5, QtWidgets.QTableWidgetItem("❌ Failed"))
                dialogs.show_error(self, "Compilation Failed", f"Merge failed: {error_msg}")
