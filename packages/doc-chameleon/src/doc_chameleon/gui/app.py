"""
doc_chameleon.gui.app
Desktop production workbench for Doc-Chameleon.
Combines Vector Bates Stamping, Load-File Generation, and California CRC 2.111 PDF Pleading Overlays.
Maintained strictly by Alan Woodyard.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import io

try:
    from PySide6.QtCore import Qt, Signal
    from PySide6.QtGui import QFont, QColor, QDragEnterEvent, QDropEvent
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QComboBox, QLineEdit, QSpinBox, QTableWidget,
        QTableWidgetItem, QHeaderView, QFileDialog, QProgressBar, QFrame, QMessageBox, QCheckBox
    )
except ImportError:
    pass

from doc_chameleon.bates.stamper import BatesStampConfig, stamp_pdf_bytes
from doc_chameleon.bates.loadfile import generate_production_loadfiles
from doc_chameleon.rules.ca.pdf_stamper import stamp_ca_pleading_pdf
from doc_chameleon.rules.ca.transformer_2111 import transform_2111

COLOR_CANVAS = "#FBFBF9"
COLOR_SURFACE_A = "#FFFFFF"
COLOR_SURFACE_B = "#F3F3EE"
COLOR_BORDER = "#D1D5DB"
COLOR_TEXT_MAIN = "#1C1D1F"
COLOR_TEXT_MUTED = "#5A6065"
COLOR_ACCENT = "#073874"
COLOR_TAG_RESP = "#D8EAD8"
COLOR_TAG_WARN = "#FADBD8"

RAW_STYLESHEET = """
QMainWindow {
    background-color: __CANVAS__;
}
QWidget {
    font-family: 'Segoe UI', -apple-system, sans-serif;
    color: __TEXT_MAIN__;
    font-size: 13px;
}
QFrame#dropZone {
    background-color: __SURFACE_A__;
    border: 2px dashed __BORDER__;
    border-radius: 6px;
    padding: 16px;
}
QFrame#dropZone:hover {
    border-color: __ACCENT__;
    background-color: __SURFACE_B__;
}
QTableWidget {
    background-color: __CANVAS__;
    gridline-color: __BORDER__;
    border: 1px solid __BORDER__;
    border-radius: 4px;
    font-size: 12px;
}
QHeaderView::section {
    background-color: #E5E7EB;
    color: #374151;
    font-weight: bold;
    padding: 6px;
    border: 1px solid __BORDER__;
    font-size: 11px;
}
QLineEdit, QComboBox {
    background-color: __SURFACE_A__;
    border: 1px solid __BORDER__;
    border-radius: 3px;
    padding: 5px 8px;
    selection-background-color: __ACCENT__;
}
QSpinBox {
    background-color: __SURFACE_A__;
    border: 1px solid __BORDER__;
    border-radius: 3px;
    padding: 5px 24px 5px 8px;
    selection-background-color: __ACCENT__;
}
QPushButton#btnExecute {
    background-color: __ACCENT__;
    color: #FFFFFF;
    font-weight: bold;
    font-size: 13px;
    padding: 10px 20px;
    border-radius: 4px;
    border: none;
}
QPushButton#btnExecute:hover {
    background-color: #0b4994;
}
QPushButton#btnExecute:pressed {
    background-color: #05264f;
}
QProgressBar {
    border: 1px solid __BORDER__;
    border-radius: 3px;
    text-align: center;
    background-color: __SURFACE_B__;
    font-size: 11px;
}
QProgressBar::chunk {
    background-color: #2cee88;
}
"""

STYLESHEET = (
    RAW_STYLESHEET
    .replace("__CANVAS__", COLOR_CANVAS)
    .replace("__SURFACE_A__", COLOR_SURFACE_A)
    .replace("__SURFACE_B__", COLOR_SURFACE_B)
    .replace("__BORDER__", COLOR_BORDER)
    .replace("__TEXT_MAIN__", COLOR_TEXT_MAIN)
    .replace("__ACCENT__", COLOR_ACCENT)
)

class DropZoneWidget(QFrame):
    filesDropped = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        layout = QVBoxLayout(self)
        self.label = QLabel("Drag & Drop Discovery PDFs or Motion Drafts Here\n(or click to browse local files)", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 14px; font-weight: 500;")
        layout.addWidget(self.label)

    def mousePressEvent(self, event):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Documents", "", "Court Files (*.pdf *.docx);;All Files (*)"
        )
        if files:
            self.filesDropped.emit(files)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        files = [u.toLocalFile() for u in urls if u.isLocalFile()]
        valid_files = [f for f in files if f.lower().endswith(('.pdf', '.docx'))]
        if valid_files:
            self.filesDropped.emit(valid_files)

class DocChameleonWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Doc-Chameleon — Legal Document Production Workbench")
        self.resize(1060, 720)
        self.setStyleSheet(STYLESHEET)

        self.queued_files: List[Path] = []
        self._init_ui()

    def _init_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)

        # Header Title
        title_box = QHBoxLayout()
        title_lbl = QLabel("Doc-Chameleon")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; font-family: 'Century Schoolbook', Georgia, serif;")
        sub_lbl = QLabel("Court Pleading Formatting & Vector Bates Production Engine")
        sub_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px; margin-top: 5px;")
        title_box.addWidget(title_lbl)
        title_box.addSpacing(10)
        title_box.addWidget(sub_lbl)
        title_box.addStretch()
        main_layout.addLayout(title_box)

        # Drop Zone
        self.drop_zone = DropZoneWidget(self)
        self.drop_zone.filesDropped.connect(self.add_files)
        main_layout.addWidget(self.drop_zone)

        # Controls Row 1: Mode & Pleading Controls
        r1_layout = QHBoxLayout()
        r1_layout.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "Vector Bates Stamping & Production (PDF)",
            "California CRC 2.111 Pleading Overlay (PDF — Production)",
            "California CRC 2.111 Formatter (DOCX — Experimental)",
            "Texas TRCP 1.0\" Margins (DOCX — Experimental)"
        ])
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        r1_layout.addWidget(self.mode_combo)

        # Pleading Rail Controls
        self.lbl_rail = QLabel("Rail Style:")
        self.rail_combo = QComboBox()
        self.rail_combo.addItems([
            "Unruled (Modern Clean)",
            "Single Rail (Traditional)",
            "Double Rail (Classic)"
        ])
        r1_layout.addWidget(self.lbl_rail)
        r1_layout.addWidget(self.rail_combo)

        self.chk_clerk = QCheckBox("Page 1 Clerk Space ('FOR COURT USE ONLY')")
        self.chk_clerk.setChecked(True)
        r1_layout.addWidget(self.chk_clerk)

        r1_layout.addStretch()
        main_layout.addLayout(r1_layout)

        # Controls Row 2: Bates & Load-File Controls
        self.bates_row = QWidget()
        r2_layout = QHBoxLayout(self.bates_row)
        r2_layout.setContentsMargins(0, 0, 0, 0)

        r2_layout.addWidget(QLabel("Prefix:"))
        self.prefix_input = QLineEdit("ABC_")
        self.prefix_input.setMaximumWidth(80)
        r2_layout.addWidget(self.prefix_input)

        r2_layout.addWidget(QLabel("Start #:"))
        self.start_input = QSpinBox()
        self.start_input.setRange(1, 99999999)
        self.start_input.setValue(1)
        self.start_input.setMinimumWidth(105)
        r2_layout.addWidget(self.start_input)

        r2_layout.addWidget(QLabel("Digits:"))
        self.digits_input = QSpinBox()
        self.digits_input.setRange(3, 12)
        self.digits_input.setValue(8)
        self.digits_input.setMinimumWidth(85)
        r2_layout.addWidget(self.digits_input)

        r2_layout.addWidget(QLabel("Suffix / Slug:"))
        self.suffix_input = QLineEdit("")
        self.suffix_input.setPlaceholderText("CONFIDENTIAL")
        self.suffix_input.setMaximumWidth(120)
        r2_layout.addWidget(self.suffix_input)

        r2_layout.addWidget(QLabel("Position:"))
        self.pos_combo = QComboBox()
        self.pos_combo.addItems([
            "Bottom Right",
            "Bottom Center",
            "Bottom Left",
            "Top Right",
            "Top Center",
            "Top Left"
        ])
        r2_layout.addWidget(self.pos_combo)

        # Load file generation checkbox
        self.chk_loadfiles = QCheckBox("Generate Load Files (.DAT / .OPT / .CSV)")
        self.chk_loadfiles.setChecked(True)
        self.chk_loadfiles.setStyleSheet("font-weight: 500; color: #073874;")
        r2_layout.addWidget(self.chk_loadfiles)

        r2_layout.addStretch()
        main_layout.addWidget(self.bates_row)

        # Queue Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Status", "File Name", "Size", "Production Output Target"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        main_layout.addWidget(self.table)

        # Action Footer
        footer_layout = QHBoxLayout()
        self.progress = QProgressBar()
        self.progress.setValue(0)
        footer_layout.addWidget(self.progress)

        self.btn_clear = QPushButton("Clear Queue")
        self.btn_clear.clicked.connect(self.clear_queue)
        footer_layout.addWidget(self.btn_clear)

        self.btn_execute = QPushButton("Execute Production")
        self.btn_execute.setObjectName("btnExecute")
        self.btn_execute.clicked.connect(self.execute_batch)
        footer_layout.addWidget(self.btn_execute)

        main_layout.addLayout(footer_layout)
        self._on_mode_changed(self.mode_combo.currentIndex())

    def _on_mode_changed(self, index: int):
        is_bates = (index == 0)
        is_ca_pdf = (index == 1)
        is_ca_docx = (index == 2)

        self.lbl_rail.setVisible(is_ca_pdf or is_ca_docx)
        self.rail_combo.setVisible(is_ca_pdf or is_ca_docx)
        self.chk_clerk.setVisible(is_ca_pdf)
        self.bates_row.setVisible(is_bates)
        self.refresh_table()

    def add_files(self, file_paths: List[str]):
        for f in file_paths:
            p = Path(f)
            if p not in self.queued_files:
                self.queued_files.append(p)
        self.refresh_table()

    def clear_queue(self):
        self.queued_files.clear()
        self.refresh_table()
        self.progress.setValue(0)

    def refresh_table(self):
        self.table.setRowCount(len(self.queued_files))
        mode = self.mode_combo.currentIndex()
        cur_start = self.start_input.value()
        digits = self.digits_input.value()
        prefix = self.prefix_input.text()
        suffix = self.suffix_input.text().strip()
        suf_part = f" {suffix}" if suffix else ""

        for row, path in enumerate(self.queued_files):
            bg_color = QColor(COLOR_SURFACE_A) if row % 2 == 0 else QColor(COLOR_SURFACE_B)

            status_item = QTableWidgetItem("QUEUED")
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setBackground(bg_color)
            self.table.setItem(row, 0, status_item)

            name_item = QTableWidgetItem(path.name)
            name_item.setBackground(bg_color)
            self.table.setItem(row, 1, name_item)

            size_kb = path.stat().st_size / 1024.0 if path.exists() else 0
            size_item = QTableWidgetItem(f"{size_kb:.1f} KB")
            size_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            size_item.setBackground(bg_color)
            self.table.setItem(row, 2, size_item)

            if mode == 0:
                target_text = f"{prefix}{cur_start:0{digits}d}{suf_part}..."
            elif mode == 1:
                target_text = "CRC 2.111 PDF Overlay"
            else:
                target_text = "DOCX Pleading Format"

            target_item = QTableWidgetItem(target_text)
            target_item.setFont(QFont("Consolas", 10))
            target_item.setTextAlignment(Qt.AlignCenter)
            target_item.setBackground(bg_color)
            self.table.setItem(row, 3, target_item)

    def execute_batch(self):
        if not self.queued_files:
            QMessageBox.warning(self, "Empty Queue", "Please drag and drop files into the queue before executing.")
            return

        out_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not out_dir:
            return

        out_path = Path(out_dir)
        total = len(self.queued_files)
        mode = self.mode_combo.currentIndex()

        rail_map = {0: "none", 1: "single", 2: "double"}
        rail_choice = rail_map.get(self.rail_combo.currentIndex(), "none")

        pos_map = {
            0: "bottom_right", 1: "bottom_center", 2: "bottom_left",
            3: "top_right", 4: "top_center", 5: "top_left"
        }
        bates_pos = pos_map.get(self.pos_combo.currentIndex(), "bottom_right")

        cur_num = self.start_input.value()
        cfg = BatesStampConfig(
            prefix=self.prefix_input.text(),
            start=cur_num,
            digits=self.digits_input.value(),
            suffix=self.suffix_input.text(),
            position=bates_pos
        )

        prod_docs: List[Dict[str, Any]] = []

        for i, src_file in enumerate(self.queued_files):
            try:
                if mode == 0:
                    # Bates Stamping & Production Mode
                    raw_bytes = src_file.read_bytes()
                    stamped_bytes, manifest = stamp_pdf_bytes(raw_bytes, cfg)
                    beg_bates = manifest[0]["bates_id"]
                    end_bates = manifest[-1]["bates_id"]

                    # Save into IMAGES/ subfolder if load files are requested
                    img_dir = out_path / "IMAGES" if self.chk_loadfiles.isChecked() else out_path
                    img_dir.mkdir(parents=True, exist_ok=True)

                    dest_file = img_dir / f"{beg_bates}_{src_file.name}"
                    dest_file.write_bytes(stamped_bytes)

                    prod_docs.append({
                        "doc_id": i + 1,
                        "beg_bates": beg_bates,
                        "end_bates": end_bates,
                        "page_count": len(manifest),
                        "file_name": src_file.name,
                        "dest_file": dest_file.name,
                        "file_size": len(stamped_bytes),
                        "pages": manifest,
                    })

                    self.table.item(i, 0).setText("PROCESSED")
                    self.table.item(i, 0).setBackground(QColor(COLOR_TAG_RESP))
                    self.table.item(i, 3).setText(f"{beg_bates} - {end_bates}")

                    cur_num += len(manifest)
                    cfg.start = cur_num

                elif mode == 1:
                    # California CRC 2.111 PDF Overlay
                    dest_file = out_path / f"CRC2111_{src_file.stem}.pdf"
                    stamp_ca_pleading_pdf(
                        src_file,
                        dest_file,
                        rail_style=rail_choice,
                        include_clerk_box=self.chk_clerk.isChecked()
                    )
                    self.table.item(i, 0).setText("PROCESSED")
                    self.table.item(i, 0).setBackground(QColor(COLOR_TAG_RESP))
                    self.table.item(i, 3).setText(f"PDF Stamped ({rail_choice.upper()})")

                else:
                    # DOCX Transformers
                    dest_file = out_path / f"Formatted_{src_file.name}"
                    transform_2111(src_file, dest_file)
                    self.table.item(i, 0).setText("PROCESSED")
                    self.table.item(i, 0).setBackground(QColor(COLOR_TAG_RESP))
                    self.table.item(i, 3).setText("DOCX Formatted")

            except Exception as e:
                self.table.item(i, 0).setText("ERROR")
                self.table.item(i, 0).setBackground(QColor(COLOR_TAG_WARN))
                self.table.item(i, 3).setText(str(e)[:30])

            self.progress.setValue(int(((i + 1) / total) * 100))

        # Generate Load Files if enabled and Bates mode active
        loadfile_msg = ""
        if mode == 0 and self.chk_loadfiles.isChecked() and prod_docs:
            lf_dir = out_path / "DATA"
            generate_production_loadfiles(prod_docs, lf_dir, volume="VOL0001")
            loadfile_msg = f"\n\nLoad Files Generated in:\n{lf_dir}\n• VOL0001.dat (Concordance)\n• VOL0001.opt (Opticon)\n• VOL0001.csv (Index)"

        QMessageBox.information(
            self,
            "Production Complete",
            f"Successfully processed {total} documents into:\n{out_path}{loadfile_msg}"
        )

def launch_gui():
    app = QApplication(sys.argv)
    window = DocChameleonWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    launch_gui()
