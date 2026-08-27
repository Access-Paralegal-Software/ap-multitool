# apmultitool_qt/views/reconcile_view.py

"""Interactive Bates Audit Review queue list view class for APMultitool Qt."""

import os
import csv
import re
import hashlib
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui

from apmultitool_qt.components import (
    SectionCard,
    FormRow,
    ActionBar,
    HintLabel
)

class ReconcileView(QtWidgets.QWidget):
    """
    Paralegal Bates Audit queue list view.
    Lays out unmatched pages and lets the user manually type the resolved Bates number.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.roqui_dir = r"C:\Users\aewoo\Downloads\Roqui"
        self.csv_path = os.path.join(self.roqui_dir, "FINAL_BATES_EXACT_MATCH.csv")
        
        self.missing_pages = []
        self.current_index = -1
        self.src_file_map = {}
        
        # Load master configurations
        self.master_configs = [
            ("ROQUI_TR_000001-001666.pdf", "ROQUI_TR_", 1),
            ("ROQUI_TR_001667-002794.pdf", "ROQUI_TR_", 1667),
            ("PalmaRFP_000001-431.pdf", "PalmaRFP_", 1)
        ]
        
        self.setup_ui()
        # Load queue on startup
        QtCore.QTimer.singleShot(100, self.load_database)

    def setup_ui(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Splitter to divide left list queue from right entry card
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        main_layout.addWidget(self.splitter)

        # ----------------------------------------------------
        # Left Panel: Missing Pages Queue List
        # ----------------------------------------------------
        self.left_panel = SectionCard()
        self.left_panel.setMinimumWidth(320)
        self.left_panel.setMaximumWidth(400)

        lbl_list_title = QtWidgets.QLabel("UNRESOLVED PAGES QUEUE")
        lbl_list_title.setObjectName("GroupHeader")
        self.left_panel.add_widget(lbl_list_title)

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setObjectName("FileQueueList")
        self.list_widget.currentRowChanged.connect(self.on_queue_selection_changed)
        self.left_panel.add_widget(self.list_widget)

        self.lbl_summary = QtWidgets.QLabel("0 pages remaining to resolve")
        self.lbl_summary.setStyleSheet("color: #6B7280; font-size: 11px; padding: 5px;")
        self.left_panel.add_widget(self.lbl_summary)

        self.splitter.addWidget(self.left_panel)

        # ----------------------------------------------------
        # Right Panel: Manual Audit Entry Card
        # ----------------------------------------------------
        self.right_panel = SectionCard()
        
        lbl_right_title = QtWidgets.QLabel("MANUAL AUDIT DECISION ENTRY")
        lbl_right_title.setObjectName("GroupHeader")
        self.right_panel.add_widget(lbl_right_title)

        # Current details display
        self.lbl_current_doc = QtWidgets.QLabel("No Document Selected")
        self.lbl_current_doc.setStyleSheet("font-size: 15px; font-weight: bold; color: #1F2937; margin-top: 10px;")
        self.right_panel.add_widget(self.lbl_current_doc)
        
        self.lbl_current_details = QtWidgets.QLabel("Select a missing page from the queue on the left to resolve.")
        self.lbl_current_details.setStyleSheet("color: #4B5563; font-size: 12px; margin-bottom: 20px;")
        self.right_panel.add_widget(self.lbl_current_details)

        # Form layout
        form = QtWidgets.QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(QtCore.Qt.AlignRight)

        self.txt_bates = QtWidgets.QLineEdit()
        self.txt_bates.setPlaceholderText("Type resolved Bates number (e.g. ROQUI_TR_000273)")
        self.txt_bates.setStyleSheet("font-size: 14px; font-weight: bold; padding: 8px;")
        self.txt_bates.returnPressed.connect(self.save_match)
        form.addRow("Bates Stamp:", self.txt_bates)

        self.right_panel.add_layout(form)

        # Guidance helper text
        hint = HintLabel("Search in Adobe Acrobat for this document page. Once identified, enter the exact Bates stamp above and press Enter (or click Confirm Match) to link the page and recompile.")
        self.right_panel.add_widget(hint)

        self.right_panel.add_stretch()

        # Action Buttons
        self.action_bar = ActionBar()
        
        self.btn_save = QtWidgets.QPushButton("Confirm Match & Recompile")
        self.btn_save.setObjectName("PrimaryButton")
        self.btn_save.setMinimumHeight(36)
        self.btn_save.clicked.connect(self.save_match)
        self.action_bar.add_button(self.btn_save)

        self.btn_omit = QtWidgets.QPushButton("Skip / Keep Omitted")
        self.btn_omit.setObjectName("SecondaryButton")
        self.btn_omit.setMinimumHeight(36)
        self.btn_omit.clicked.connect(self.mark_omitted)
        self.action_bar.add_button(self.btn_omit)
        
        self.right_panel.add_layout(self.action_bar.layout_container)
        self.splitter.addWidget(self.right_panel)

    def get_google_drive_rel_path(self, rel_path):
        return rel_path

    def load_database(self):
        """Map target source files and build unmatched pages queue."""
        if not os.path.exists(self.csv_path):
            return
            
        # 1. Map target files
        self.src_file_map = {}
        for root, dirs, files in os.walk(self.roqui_dir):
            if any(p in root.replace("\\", "/").split("/") for p in ["identified-bates", "Tuesday Final"]):
                continue
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in [".pdf", ".png", ".jpg", ".jpeg"] and not f.startswith("."):
                    full_path = os.path.join(root, f)
                    rel_path = os.path.relpath(full_path, self.roqui_dir)
                    if rel_path in ["ROQUI_TR_000001-001666.pdf", "ROQUI_TR_001667-002794.pdf", "PalmaRFP_000001-431.pdf"]:
                        continue
                    # Compute standard file subpath
                    parts = rel_path.replace("\\", "/").split("/")
                    file_subpath = parts[-1]
                    for grp_folder in ["palma-senderos", "palma-custom", "palma-madero", "palma-eg", "custom", "eg", "serco", "stc", "stc-20260821t161145z-1-001", "stc-20260821t161149z-1-001"]:
                        if grp_folder in [p.lower() for p in parts]:
                            for p_i, p_val in enumerate(parts):
                                if p_val.lower() == grp_folder:
                                    file_subpath = "/".join(parts[p_i+1:])
                                    break
                            break
                    group = self.classify_group_from_rel(rel_path)
                    # Keep full_path and rel_path to map properly
                    self.src_file_map[(group, file_subpath)] = (full_path, rel_path)

        # 2. Read missing pages from CSV
        self.missing_pages = []
        self.list_widget.clear()
        
        with open(self.csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                group, file_subpath, page_label, bates, master_info, status = row
                if bates == "N/A":
                    p_num = int(page_label.replace("Page ", ""))
                    map_val = self.src_file_map.get((group, file_subpath))
                    if map_val:
                        self.missing_pages.append({
                            "group": group,
                            "file_subpath": file_subpath,
                            "page_label": page_label,
                            "p_num": p_num,
                            "src_path": map_val[0],
                            "rel_path": map_val[1],
                            "row_data": row
                        })
                        self.list_widget.addItem(f"{group} - {os.path.basename(file_subpath)} ({page_label})")

        self.lbl_summary.setText(f"{len(self.missing_pages)} pages remaining to resolve")
        if self.missing_pages:
            self.list_widget.setCurrentRow(0)

    def on_queue_selection_changed(self, index):
        if index < 0 or index >= len(self.missing_pages):
            self.current_index = -1
            self.lbl_current_doc.setText("No Document Selected")
            self.lbl_current_details.setText("Select an unmatched page from the queue.")
            self.txt_bates.clear()
            return
            
        self.current_index = index
        item = self.missing_pages[index]
        
        self.lbl_current_doc.setText(f"{item['group']} — {os.path.basename(item['file_subpath'])}")
        self.lbl_current_details.setText(f"Original Path: {item['file_subpath']} | {item['page_label']}")
        self.txt_bates.clear()
        self.txt_bates.setFocus()

    def save_match(self):
        if self.current_index < 0:
            return
            
        bates_input = self.txt_bates.text().strip().upper()
        if not bates_input:
            QtWidgets.QMessageBox.warning(self, "Invalid Bates Stamp", "Please type the Bates number to link this page.")
            return
            
        item = self.missing_pages[self.current_index]
        group = item["group"]
        file_sub = item["file_subpath"]
        page_lbl = item["page_label"]
        
        master_info = "N/A"
        m = re.match(r"^([A-Z_]+)(\d+)$", bates_input)
        if m:
            prefix = m.group(1)
            num = int(m.group(2))
            for filename, pfx, offset in self.master_configs:
                if pfx == prefix:
                    m_path = os.path.join(self.roqui_dir, filename)
                    if os.path.exists(m_path):
                        try:
                            import fitz
                            with fitz.open(m_path) as doc:
                                total = len(doc)
                                page_idx = num - offset + 1
                                if 1 <= page_idx <= total:
                                    master_info = f"{filename} (Page {page_idx})"
                                    break
                        except Exception:
                            pass
        
        if master_info == "N/A":
            QtWidgets.QMessageBox.warning(self, "Bates Not Found", f"Bates stamp '{bates_input}' could not be resolved to any page inside the court production master PDFs.")
            return

        # 1. Update the CSV mapping database on disk
        rows = []
        updated = False
        with open(self.csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                r_group, r_file, r_page, r_bates, r_master, r_status = row
                if r_group == group and r_file == file_sub and r_page == page_lbl:
                    row = [group, file_sub, page_lbl, bates_input, master_info, "Manual Audit Review Matched"]
                    updated = True
                rows.append(row)
                
        if updated:
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(rows)
                
            self.compile_document_on_the_fly(group, file_sub)
            
            nxt_idx = self.current_index
            self.load_database()
            if self.missing_pages:
                if nxt_idx >= len(self.missing_pages):
                    nxt_idx = len(self.missing_pages) - 1
                self.list_widget.setCurrentRow(nxt_idx)
            else:
                self.list_widget.setCurrentRow(-1)
                QtWidgets.QMessageBox.information(self, "Audit Complete", "All unmatched pages have been successfully resolved!")

    def compile_document_on_the_fly(self, group, file_subpath):
        """Compile the Bates stamp PDF and exceptions report immediately for the matched document."""
        try:
            dst_root = os.path.join(self.roqui_dir, "Tuesday Final")
            map_val = self.src_file_map.get((group, file_subpath))
            if not map_val:
                return
            src_path, rel_path = map_val
            gdrive_rel_path = self.get_google_drive_rel_path(rel_path)
            
            pages_data = []
            with open(self.csv_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    r_grp, r_file, r_page, r_bates, r_master, r_status = row
                    if r_grp == group and r_file == file_subpath:
                        p_num = int(r_page.replace("Page ", ""))
                        pages_data.append((p_num, r_bates, r_master))
                        
            pages_data.sort(key=lambda x: x[0])
            
            sub_dir, fname = os.path.split(gdrive_rel_path)
            f_base, f_ext = os.path.splitext(fname)
            
            exceptions_dir = os.path.join(dst_root, "exceptions", sub_dir)
            missing_pdf_path = os.path.join(exceptions_dir, f"{f_base}-missing{f_ext}")
            if os.path.exists(missing_pdf_path):
                os.remove(missing_pdf_path)
                
            missing_pages = [p[0] for p in pages_data if p[1] == "N/A"]
            if missing_pages:
                os.makedirs(exceptions_dir, exist_ok=True)
                import pikepdf
                with pikepdf.Pdf.open(src_path) as src_pdf:
                    dst_missing_pdf = pikepdf.Pdf.new()
                    for p_num in missing_pages:
                        dst_missing_pdf.pages.append(src_pdf.pages[p_num - 1])
                    dst_missing_pdf.save(missing_pdf_path)
                    dst_missing_pdf.close()
                    
            has_bates = any(p[1] != "N/A" for p in pages_data)
            dst_bates_path = os.path.join(dst_root, sub_dir, f"{f_base} (Bates){f_ext}")
            if has_bates:
                os.makedirs(os.path.dirname(dst_bates_path), exist_ok=True)
                import pikepdf
                dst_pdf = pikepdf.Pdf.new()
                for p_num, bates, master_info in pages_data:
                    if bates != "N/A":
                        m = re.match(r"^(.+?)\s+\(Page\s+(\d+)\)$", master_info)
                        if m:
                            m_file = m.group(1)
                            m_page = int(m.group(2))
                            m_path = os.path.join(self.roqui_dir, m_file)
                            with pikepdf.Pdf.open(m_path) as m_pdf:
                                dst_pdf.pages.append(m_pdf.pages[m_page - 1])
                dst_pdf.save(dst_bates_path)
                dst_pdf.close()
                
            self.rebuild_exceptions_report(dst_root)
            self.regenerate_production_load_files(dst_root)
            
        except Exception as e:
            print(f"Error compiling on-the-fly: {e}")

    def rebuild_exceptions_report(self, dst_root):
        exceptions_map = {}
        with open(self.csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                r_group, r_file, r_page, r_bates, r_master, r_status = row
                if r_bates == "N/A":
                    # Resolve to gdrive path
                    map_val = self.src_file_map.get((r_group, r_file))
                    if map_val:
                        gdrive_path = self.get_google_drive_rel_path(map_val[1])
                        if gdrive_path not in exceptions_map:
                            exceptions_map[gdrive_path] = []
                        p_num = int(r_page.replace("Page ", ""))
                        exceptions_map[gdrive_path].append(p_num)
                    
        report_path = os.path.join(dst_root, "exceptions", "exceptions_report.txt")
        if exceptions_map:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write("AP MULTITOOL: BATES AUDIT GLOBAL EXCEPTIONS REPORT\n")
                f.write(f"Total Files with Exceptions: {len(exceptions_map)}\n")
                f.write("=" * 80 + "\n\n")
                for file_sub, missing_pages in sorted(exceptions_map.items()):
                    f.write(f"File Path: {file_sub}\n")
                    f.write(f"  Missing Pages: {', '.join([str(p) for p in sorted(missing_pages)])}\n")
                    f.write("-" * 80 + "\n")
        else:
            if os.path.exists(report_path):
                os.remove(report_path)

    def regenerate_production_load_files(self, dst_root):
        dat_path = os.path.join(dst_root, "production_loadfile.dat")
        opt_path = os.path.join(dst_root, "production_images.opt")
        
        document_pages = {}
        with open(self.csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                group, file_subpath, page_label, bates, master_info, status = row
                key = (group, file_subpath)
                if key not in document_pages:
                    document_pages[key] = []
                try:
                    p_num = int(page_label.replace("Page ", ""))
                except ValueError:
                    p_num = 1
                document_pages[key].append((p_num, bates, master_info))
                
        with open(dat_path, "w", newline="", encoding="utf-8") as f_dat:
            writer = csv.writer(f_dat)
            writer.writerow(["DocID", "BatesStart", "BatesEnd", "PageCount", "OriginalPath", "MD5Hash", "Status"])
            
            for key, pages in sorted(document_pages.items()):
                group, file_subpath = key
                pages.sort(key=lambda x: x[0])
                
                valid_pages = [p for p in pages if p[1] != "N/A"]
                if not valid_pages:
                    continue
                    
                bates_start = valid_pages[0][1]
                bates_end = valid_pages[-1][1]
                page_count = len(valid_pages)
                
                map_val = self.src_file_map.get(key)
                gdrive_path = self.get_google_drive_rel_path(map_val[1]) if map_val else file_subpath
                
                doc_id = os.path.splitext(os.path.basename(file_subpath))[0]
                md5_hash = hashlib.md5(gdrive_path.encode()).hexdigest()
                
                status = "Complete" if len(valid_pages) == len(pages) else "Partial Omission"
                writer.writerow([doc_id, bates_start, bates_end, page_count, gdrive_path.replace("\\", "/"), md5_hash, status])
                
        with open(opt_path, "w", encoding="utf-8") as f_opt:
            for key, pages in sorted(document_pages.items()):
                group, file_subpath = key
                pages.sort(key=lambda x: x[0])
                
                valid_pages = [p for p in pages if p[1] != "N/A"]
                if not valid_pages:
                    continue
                    
                map_val = self.src_file_map.get(key)
                gdrive_path = self.get_google_drive_rel_path(map_val[1]) if map_val else file_subpath
                sub_dir, fname = os.path.split(gdrive_path)
                f_base, f_ext = os.path.splitext(fname)
                bates_pdf_rel = f"{sub_dir}/{f_base} (Bates){f_ext}".replace("\\", "/").replace("//", "/")
                if bates_pdf_rel.startswith("/"):
                    bates_pdf_rel = bates_pdf_rel[1:]
                
                for idx, (p_num, bates, master_info) in enumerate(valid_pages):
                    is_first = "Y" if idx == 0 else ""
                    pg_count = len(valid_pages) if idx == 0 else ""
                    f_opt.write(f"{bates},VOL001,{bates_pdf_rel},{is_first},,,{pg_count}\n")

    def mark_omitted(self):
        """Advance queue and confirm page remains N/A (omitted)."""
        if self.current_index < 0:
            return
            
        nxt_idx = self.current_index + 1
        if nxt_idx >= len(self.missing_pages):
            nxt_idx = len(self.missing_pages) - 1
            
        self.list_widget.setCurrentRow(nxt_idx)

    def classify_group_from_rel(self, rel_path):
        parts = rel_path.lower().replace("\\", "/").split("/")
        if "senderos" in parts or any("palma-senderos" in p for p in parts):
            return "Senderos"
        if "custom" in parts or "palma-custom" in parts:
            return "Custom"
        if "madero" in parts or any("palma-madero" in p for p in parts):
            return "Madero"
        if "jr" in parts or "jr constructions" in parts or "jr_constructions" in parts:
            return "JR Constructions"
        if "eg" in parts or "eg logistic" in parts or "eg_logistic" in parts or any("palma-eg" in p for p in parts):
            return "EG Logistic"
        if "serco" in parts:
            return "SERCO"
        if "stc" in parts or any("stc" in p for p in parts):
            if "check" in parts or "check" in rel_path.lower():
                return "STC Check"
            return "STC"
        return "Unknown"
