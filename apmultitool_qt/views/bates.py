# apmultitool_qt/views/bates.py

"""Bates Stamping View widget class for APMultitool Qt."""

import os
import time
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui

from apmultitool_qt.components import (
    SectionCard,
    FormRow,
    ActionBar,
    HintLabel,
    dialogs,
    file_dialogs
)
from apmultitool_qt.core_bridge import EngineJobWorker


def create_gear_icon(color_hex="#374151", size=16):
    """Draw a clean, high-resolution vector gear icon using QPainter."""
    pixmap = QtGui.QPixmap(size * 2, size * 2)
    pixmap.fill(QtCore.Qt.transparent)
    
    painter = QtGui.QPainter(pixmap)
    painter.setRenderHint(QtGui.QPainter.Antialiasing)
    painter.scale(2.0, 2.0)
    
    color = QtGui.QColor(color_hex)
    painter.setBrush(color)
    painter.setPen(QtCore.Qt.NoPen)
    
    cx, cy = size / 2.0, size / 2.0
    
    path = QtGui.QPainterPath()
    # Outer circle
    path.addEllipse(QtCore.QPointF(cx, cy), size * 0.30, size * 0.30)
    
    # Add 8 teeth
    for i in range(8):
        angle = i * 45.0
        r1 = size * 0.26
        r2 = size * 0.44
        w1 = size * 0.12
        w2 = size * 0.08
        
        polygon = QtGui.QPolygonF([
            QtCore.QPointF(cx - w1/2, cy - r1),
            QtCore.QPointF(cx - w2/2, cy - r2),
            QtCore.QPointF(cx + w2/2, cy - r2),
            QtCore.QPointF(cx + w1/2, cy - r1)
        ])
        
        transform = QtGui.QTransform()
        transform.translate(cx, cy)
        transform.rotate(angle)
        transform.translate(-cx, -cy)
        
        rotated_poly = transform.map(polygon)
        path.addPolygon(rotated_poly)
        
    # Subtract center hole
    hole = QtGui.QPainterPath()
    hole.addEllipse(QtCore.QPointF(cx, cy), size * 0.12, size * 0.12)
    
    final_path = path.subtracted(hole)
    painter.drawPath(final_path)
    painter.end()
    
    return QtGui.QIcon(pixmap)


class BatesOptionsDialog(QtWidgets.QDialog):
    """Advanced stamp configurations modal dialog."""
    def __init__(self, parent, current_opts):
        super().__init__(parent)
        self.opts = current_opts.copy()
        self.setWindowTitle("Advanced Stamp Options")
        self.setModal(True)
        self.setMinimumWidth(440)
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Form fields layout
        form = QtWidgets.QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(QtCore.Qt.AlignRight)

        # Font Combo
        self.cb_font = QtWidgets.QComboBox()
        self.cb_font.addItems(["Arial", "Arial Bold", "Calibri", "Times New Roman", "Helvetica", "Courier"])
        self.cb_font.setCurrentText(self.opts.get("font", "Arial Bold"))
        form.addRow("Font Face:", self.cb_font)

        # Font Size Combo
        self.cb_size = QtWidgets.QComboBox()
        self.cb_size.addItems(["10", "11", "12", "14"])
        self.cb_size.setCurrentText(str(self.opts.get("size", 12)))
        form.addRow("Font Size (pt):", self.cb_size)

        # Placement Combo
        self.cb_pos = QtWidgets.QComboBox()
        self.cb_pos.addItems([
            "Bottom Right (Outside Margin)", "Bottom Center (Outside Margin)", 
            "Top Center (Above Margin)", "Top Right (Above Margin)", 
            "Top Left (Above Margin)", "Bottom Left (Outside Margin)"
        ])
        self.cb_pos.setCurrentText(self.opts.get("pos", "Bottom Right (Outside Margin)"))
        form.addRow("Stamp Position:", self.cb_pos)

        # Collision Checkbox
        self.chk_shrink = QtWidgets.QCheckBox("Collision Avoidance: Shrink page to fit margins")
        self.chk_shrink.setChecked(self.opts.get("shrink", True))
        form.addRow("", self.chk_shrink)

        # Naming policy Combo
        self.cb_naming = QtWidgets.QComboBox()
        self.cb_naming.addItems(["Prefix_Start-End", "Prefix_StartOnly"])
        self.cb_naming.setCurrentText(self.opts.get("naming", "Prefix_Start-End"))
        form.addRow("Naming Protocol:", self.cb_naming)

        # Output dir policy Combo
        self.cb_output = QtWidgets.QComboBox()
        self.cb_output.addItems(["Nested Folder (Default)", "Same as Source", "Custom Location..."])
        self.cb_output.setCurrentText(self.opts.get("output", "Nested Folder (Default)"))
        form.addRow("Output Folder Policy:", self.cb_output)

        layout.addLayout(form)

        # Hint text
        hint = HintLabel("Saves setting parameters locally for the active session.")
        layout.addWidget(hint)

        # Action Button
        self.btn_save = QtWidgets.QPushButton("✅ SAVE PROTOCOL")
        self.btn_save.setObjectName("PrimaryButton")
        self.btn_save.clicked.connect(self.save_and_close)
        layout.addWidget(self.btn_save)

    def save_and_close(self):
        self.opts["font"] = self.cb_font.currentText()
        self.opts["size"] = int(self.cb_size.currentText())
        self.opts["pos"] = self.cb_pos.currentText()
        self.opts["shrink"] = self.chk_shrink.isChecked()
        self.opts["naming"] = self.cb_naming.currentText()
        self.opts["output"] = self.cb_output.currentText()
        self.accept()


class BatesView(QtWidgets.QWidget):
    """
    Refined Bates Stamping view.
    Lays out parameters utilizing standardized FormRows and handles output logging.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread = None
        self.active_worker = None
        self.bates_registry = {}
        
        # Default options matching legacy specs
        self.bates_opts = {
            "prefix": "AP",
            "sep": "_",
            "start": 1,
            "padding": 7,
            "font": "Arial Bold",
            "size": 12,
            "pos": "Bottom Right (Outside Margin)",
            "shrink": True,
            "naming": "Prefix_Start-End",
            "output": "Nested Folder (Default)",
            "custom_out_dir": ""
        }

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
        self.txt_prefix.setText(self.bates_opts["prefix"])
        self.txt_prefix.editingFinished.connect(self.on_prefix_editing_finished)
        self.left_card.add_widget(FormRow("Bates Prefix:", self.txt_prefix, label_width=90))

        # Start Index
        self.txt_start = QtWidgets.QLineEdit()
        self.txt_start.setText(str(self.bates_opts["start"]))
        self.left_card.add_widget(FormRow("Start Index:", self.txt_start, label_width=90))

        # Separator
        self.cb_sep = QtWidgets.QComboBox()
        self.cb_sep.addItems(["_", "-", "(None)"])
        self.cb_sep.setCurrentText(self.bates_opts["sep"])
        self.left_card.add_widget(FormRow("Separator:", self.cb_sep, label_width=90))

        # Advanced Settings Dialog Trigger
        self.btn_options = QtWidgets.QPushButton(" ADVANCED STAMP OPTIONS")
        self.btn_options.setObjectName("SecondaryButton")
        self.btn_options.setIcon(create_gear_icon("#374151", 16))
        self.btn_options.setIconSize(QtCore.QSize(16, 16))
        self.btn_options.clicked.connect(self.show_options)
        self.left_card.add_widget(self.btn_options)

        self.left_card.add_stretch()

        # Primary Run Action Bar
        self.action_bar = ActionBar()
        self.btn_run = QtWidgets.QPushButton("⚡ FLATTEN & APPLY BATES STAMPS")
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

        # Progress bar
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #E5E7EB;
                border-radius: 4px;
                text-align: center;
                background-color: #FFFFFF;
                height: 12px;
            }
            QProgressBar::chunk {
                background-color: #67BE5E;
            }
        """)
        self.right_card.add_widget(self.progress_bar)

        # Bottom clear button
        self.btn_clear = QtWidgets.QPushButton("Clear Console")
        self.btn_clear.setObjectName("SecondaryButton")
        self.btn_clear.setFixedWidth(120)
        self.btn_clear.clicked.connect(self.clear_console)
        self.right_card.add_widget(self.btn_clear)

        splitter.addWidget(self.right_card)

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
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(progress_percent)

    def clear_main_status(self):
        """Clear progress indicators on the main window shell."""
        main_win = self.get_main_window()
        if main_win:
            main_win.hide_progress("Ready")
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)

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

    def log_message(self, msg):
        """Append log message with current timestamp to terminal."""
        t_str = time.strftime('%H:%M:%S')
        self.console.appendPlainText(f"[{t_str}] {msg}")

    def on_prefix_editing_finished(self):
        """Autoincrement focus out check utilizing matter ledger registry."""
        prefix = self.txt_prefix.text().strip()
        main_win = self.get_main_window()
        matter_name = "Default_Matter"
        if main_win and hasattr(main_win, "view_fileroom"):
            matter_name = main_win.view_fileroom.txt_case_id.text().strip() or "Default_Matter"
            
        if prefix and matter_name in self.bates_registry:
            last_num = self.bates_registry[matter_name].get(prefix)
            if last_num is not None:
                self.txt_start.setText(str(last_num))

    def show_options(self):
        """Open Advanced Option Dialog Modal."""
        # Sync values from left panel inputs to self.bates_opts
        self.bates_opts["prefix"] = self.txt_prefix.text().strip()
        sep_char = self.cb_sep.currentText()
        self.bates_opts["sep"] = "" if sep_char == "(None)" else sep_char
        
        try:
            self.bates_opts["start"] = int(self.txt_start.text().strip())
        except ValueError:
            self.bates_opts["start"] = 1

        dlg = BatesOptionsDialog(self, self.bates_opts)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            self.bates_opts = dlg.opts
            # Update inputs from options values
            self.txt_prefix.setText(self.bates_opts.get("prefix", "AP"))
            self.txt_start.setText(str(self.bates_opts.get("start", 1)))
            
            sep_val = self.bates_opts.get("sep", "_")
            if sep_val == "":
                self.cb_sep.setCurrentText("(None)")
            else:
                self.cb_sep.setCurrentText(sep_val)

    def toggle_inputs(self, enabled: bool):
        """Lock input parameter controls during active execution run."""
        self.txt_target.setEnabled(enabled)
        self.btn_browse.setEnabled(enabled)
        self.txt_prefix.setEnabled(enabled)
        self.txt_start.setEnabled(enabled)
        self.cb_sep.setEnabled(enabled)
        self.btn_options.setEnabled(enabled)
        self.btn_clear.setEnabled(enabled)

    def run_bates(self):
        """Submit high performance bates production task on background thread."""
        if self.active_worker:
            # Active worker running. Act as cancellation!
            self.active_worker.request_cancel()
            self.btn_run.setText("Cancelling...")
            self.btn_run.setEnabled(False)
            return

        target = self.txt_target.text().strip()
        if not target or not os.path.exists(target):
            dialogs.show_warning(self, "Input Error", "Please select a valid PDF file to Bates Number.")
            return

        source_dir = os.path.dirname(target)

        # Sync values from left panel inputs
        self.bates_opts["prefix"] = self.txt_prefix.text().strip()
        sep_char = self.cb_sep.currentText()
        self.bates_opts["sep"] = "" if sep_char == "(None)" else sep_char
        
        try:
            start_idx = int(self.txt_start.text().strip())
            self.bates_opts["start"] = start_idx
        except ValueError:
            start_idx = 1
            self.txt_start.setText("1")
            self.bates_opts["start"] = 1

        opts = self.bates_opts

        # Resolve Output Folder policy
        if opts["output"] == "Same as Source":
            out_dir = source_dir
        elif opts["output"] == "Custom Location...":
            out_dir = file_dialogs.get_existing_directory(self, "Select Output Folder")
            if not out_dir:
                return  # user cancelled directory select
        else: # Nested Folder (Default)
            folder_name = f"{opts['prefix']}-Bates-{time.strftime('%Y-%m-%d')}"
            out_dir = os.path.join(source_dir, folder_name)
            try:
                os.makedirs(out_dir, exist_ok=True)
            except Exception as e:
                dialogs.show_error(self, "Folder Error", f"Could not create folder: {str(e)}")
                return

        # Prepare core Job structures
        from core.job import Job, InputSpec, BatesParams, OutputSpec
        
        job_input = InputSpec.from_path(Path(target))
        job_params = BatesParams(
            prefix=opts["prefix"],
            start_number=start_idx,
            padding=opts["padding"],
            position=opts.get("pos", "Bottom Right (Outside Margin)"),
            font_size=opts.get("size", 12),
            shrink_conflict=opts.get("shrink", True),
            sep=opts["sep"],
            font_name=opts.get("font", "Arial Bold"),
            naming=opts.get("naming", "Prefix_Start-End"),
            output_name=None
        )
        job_output = OutputSpec(directory=Path(out_dir), overwrite=True)

        job = Job(
            operation="bates_stamp",
            inputs=[job_input],
            params=job_params,
            output=job_output
        )

        self.console.clear()
        self.log_message(f"Initiating Bates production for: {os.path.basename(target)}")
        self.log_message(f"Parameters: Prefix='{opts['prefix']}', Separator='{opts['sep']}', Start={start_idx}")
        self.log_message(f"Style: Font={opts['font']}, Size={opts['size']}pt, Placement='{opts['pos']}'")
        self.log_message(f"Destination: {out_dir}")

        # Thread setup
        self.thread = QtCore.QThread()
        self.active_worker = EngineJobWorker(job, output_root=Path(out_dir))
        self.active_worker.moveToThread(self.thread)

        # Wire Slots
        self.thread.started.connect(self.active_worker.run_job)
        self.active_worker.started.connect(self.on_bates_started)
        self.active_worker.progress.connect(self.on_bates_progress)
        self.active_worker.finished.connect(self.on_bates_finished)

        self.thread.start()

    def on_bates_started(self):
        """Disable input fields and style run button to show active running state."""
        self.toggle_inputs(False)
        self.btn_run.setText("🛑 CANCEL PRODUCTION")
        self.btn_run.setObjectName("DangerButton")
        self.btn_run.setStyleSheet("background-color: #DC2626; color: white;")

    def on_bates_progress(self, percent: int, msg: str):
        """Update logs and progress bar values."""
        self.update_main_status(percent, msg)
        if msg:
            self.log_message(msg)

    def on_bates_finished(self, success: bool, error_msg: str, result: object):
        """Restore controls state and log output summary metadata."""
        if self.thread:
            self.thread.quit()
            self.thread.wait()
            self.thread = None

        self.active_worker = None
        self.toggle_inputs(True)
        self.btn_run.setText("⚡ FLATTEN & APPLY BATES STAMPS")
        self.btn_run.setObjectName("PrimaryButton")
        self.btn_run.setStyleSheet("")
        self.btn_run.setEnabled(True)
        
        self.clear_main_status()

        if success:
            out_path = result.outputs[0]
            out_name = os.path.basename(out_path)
            page_count = result.page_count_out
            
            self.log_message("🎉 Production successfully completed.")
            self.log_message(f"Output File: {out_name}")
            self.log_message(f"Stamping completed. Total Pages: {page_count}")
            
            # Update local matter bates index ledger
            main_win = self.get_main_window()
            matter_name = "Default_Matter"
            if main_win and hasattr(main_win, "view_fileroom"):
                matter_name = main_win.view_fileroom.txt_case_id.text().strip() or "Default_Matter"
                
            prefix = self.bates_opts["prefix"]
            if matter_name not in self.bates_registry:
                self.bates_registry[matter_name] = {}
            
            # Next start index is current index + page count stamped
            next_index = self.bates_opts["start"] + page_count
            self.bates_registry[matter_name][prefix] = next_index
            self.txt_start.setText(str(next_index))

            dialogs.show_info(self, "Success", f"Bates Production Complete!\n\nFile: {out_name}\nPages: {page_count}")
            
            # Open target directory
            out_dir = os.path.dirname(out_path)
            try:
                os.startfile(out_dir)
            except Exception:
                pass
        else:
            if error_msg == "Operation cancelled.":
                self.log_message("⚠️ Stamping operation cancelled by user.")
                dialogs.show_info(self, "Cancelled", "Bates stamping was cancelled.")
            else:
                self.log_message(f"❌ Error during execution: {error_msg}")
                dialogs.show_error(self, "Production Error", f"Bates execution failed: {error_msg}")
