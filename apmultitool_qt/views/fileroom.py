# apmultitool_qt/views/fileroom.py

"""File Room & Trees View widget class for APMultitool Qt."""

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


class FileRoomView(QtWidgets.QWidget):
    """
    Refined File Room & Case Directories View.
    Configures matter blueprints and folder tree generation using standard Qt patterns.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread = None
        self.active_worker = None
        
        # Factory default legal hierarchy custom case structure
        self.custom_structure = [
            "Correspondence",
            "Correspondence/Client Correspondence",
            "Correspondence/Opposing Counsel",
            "Correspondence/Court Correspondence",
            "Correspondence/{Date}",
            "Discovery",
            "Discovery/Written Discovery",
            "Discovery/Document Production",
            "Discovery/Depositions",
            "Discovery/Experts",
            "Pleadings",
            "Pleadings/Motions",
            "Pleadings/Orders",
            "Pleadings/Briefs & Memoranda",
            "Client Documents",
            "Client Documents/Intake & Retainer",
            "Client Documents/Financial Records",
            "Research",
            "Research/Caselaw",
            "Research/Fact Research",
            "Trial",
            "Trial/Exhibits"
        ]

        self.setup_ui()

    def setup_ui(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(15)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        main_layout.addWidget(splitter)

        # ----------------------------------------------------
        # Left Panel (Blueprint Options Card)
        # ----------------------------------------------------
        self.left_card = SectionCard()
        self.left_card.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.left_card.setMinimumWidth(340)
        self.left_card.setMaximumWidth(360)

        # Header Title
        header = QtWidgets.QLabel("FILE ROOM CONFIG")
        header.setObjectName("GroupHeader")
        self.left_card.add_widget(header)

        # Case ID FormRow
        self.txt_case_id = QtWidgets.QLineEdit()
        self.txt_case_id.setText("2026-AP-9908")
        self.txt_case_id.textChanged.connect(self.rebuild_preview)
        self.left_card.add_widget(FormRow("Matter ID Reference:", self.txt_case_id, label_width=130))

        # Blueprints FormRow
        self.cb_blueprints = QtWidgets.QComboBox()
        self.cb_blueprints.addItems([
            "⭐ Custom User Blueprint",
            "Standard Civil Litigation",
            "Trial Notebook Model",
            "Solo / Freelance Core"
        ])
        self.cb_blueprints.setCurrentText("⭐ Custom User Blueprint")
        self.cb_blueprints.currentTextChanged.connect(self.on_blueprint_changed)
        self.left_card.add_widget(FormRow("Structure Blueprint:", self.cb_blueprints, label_width=130))

        # ----------------------------------------------------
        # Custom Architect Design Group (collapsible or enabled for Custom User)
        # ----------------------------------------------------
        self.lbl_architect = QtWidgets.QLabel("CASE BLUEPRINT ARCHITECT")
        self.lbl_architect.setStyleSheet("font-size: 11px; font-weight: bold; color: #10B981; margin-top: 10px;")
        self.left_card.add_widget(self.lbl_architect)

        # Custom Folder Name Input
        self.txt_custom_folder = QtWidgets.QLineEdit()
        self.txt_custom_folder.setPlaceholderText("e.g., Medical Records")
        self.left_card.add_widget(FormRow("Folder Name:", self.txt_custom_folder, label_width=130))

        # Custom Parent Node Select
        self.cb_custom_parent = QtWidgets.QComboBox()
        self.cb_custom_parent.addItems([
            "Root Level",
            "Correspondence",
            "Discovery",
            "Pleadings",
            "Research",
            "Client Documents",
            "Trial"
        ])
        self.left_card.add_widget(FormRow("Parent Node:", self.cb_custom_parent, label_width=130))

        # Architect Action Buttons
        self.arch_actions = ActionBar()
        
        self.btn_add_folder = QtWidgets.QPushButton("+ Add Folder")
        self.btn_add_folder.setObjectName("SecondaryButton")
        self.btn_add_folder.clicked.connect(self.add_custom_folder)
        self.arch_actions.add_button(self.btn_add_folder)

        self.btn_remove_folder = QtWidgets.QPushButton("❌ Remove")
        self.btn_remove_folder.setObjectName("SecondaryButton")
        self.btn_remove_folder.clicked.connect(self.remove_custom_folder)
        self.arch_actions.add_button(self.btn_remove_folder)

        self.left_card.add_layout(self.arch_actions.layout_container)

        self.arch_global_actions = ActionBar()

        self.btn_reset = QtWidgets.QPushButton("🔄 Reset Defaults")
        self.btn_reset.setObjectName("SecondaryButton")
        self.btn_reset.clicked.connect(self.reset_defaults)
        self.arch_global_actions.add_button(self.btn_reset)

        self.btn_clear = QtWidgets.QPushButton("🗑️ Clear All")
        self.btn_clear.setObjectName("SecondaryButton")
        self.btn_clear.clicked.connect(self.clear_custom_structure)
        self.arch_global_actions.add_button(self.btn_clear)

        self.left_card.add_layout(self.arch_global_actions.layout_container)

        self.left_card.add_stretch()

        # Primary Run Action Bar
        self.action_bar = ActionBar()
        self.btn_run = QtWidgets.QPushButton("Spin Up Folder Tree")
        self.btn_run.setObjectName("PrimaryButton")
        self.btn_run.clicked.connect(self.run_spinup)
        self.action_bar.add_button(self.btn_run)
        self.left_card.add_layout(self.action_bar.layout_container)

        splitter.addWidget(self.left_card)

        # ----------------------------------------------------
        # Right Panel (Structural Preview Tree Card)
        # ----------------------------------------------------
        self.right_card = SectionCard()
        
        t_header = QtWidgets.QLabel("FOLDER TREE ARCHITECTURE PREVIEW")
        t_header.setObjectName("GroupHeader")
        self.right_card.add_widget(t_header)

        # Tree Widget
        self.tree_widget = QtWidgets.QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.right_card.add_widget(self.tree_widget)

        # Prepopulate structure preview
        self.rebuild_preview()

        splitter.addWidget(self.right_card)

        # Enable/Disable architect buttons based on initial blueprint selection
        self.on_blueprint_changed("⭐ Custom User Blueprint")

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

    def on_blueprint_changed(self, choice):
        """Enable custom architect configuration inputs only for User Blueprints."""
        is_custom = choice == "⭐ Custom User Blueprint"
        self.txt_custom_folder.setEnabled(is_custom)
        self.cb_custom_parent.setEnabled(is_custom)
        self.btn_add_folder.setEnabled(is_custom)
        self.btn_remove_folder.setEnabled(is_custom)
        self.btn_reset.setEnabled(is_custom)
        self.btn_clear.setEnabled(is_custom)
        self.rebuild_preview()

    def rebuild_preview(self):
        """Update structural hierarchy preview inside the QTreeWidget."""
        self.tree_widget.clear()
        case_id = self.txt_case_id.text().strip() or "Matter_Root"
        root_item = QtWidgets.QTreeWidgetItem(self.tree_widget, [case_id])
        
        # Get active blueprint directories
        archetype = self.cb_blueprints.currentText()
        subdirs = []
        if archetype == "⭐ Custom User Blueprint":
            subdirs = self.custom_structure
        elif archetype == "Standard Civil Litigation":
            subdirs = ["01_Pleadings", "02_Discovery", "03_Correspondence", "04_Court_Orders", "05_Research"]
        elif archetype == "Trial Notebook Model":
            subdirs = ["Exhibits_Plaintiff", "Exhibits_Defendant", "Witness_Outlines", "Jury_Instructions", "Opening_Closing_Statements"]
        else:
            subdirs = ["Admin_Billing", "Client_Intake", "Outbound_Production"]

        curr_date = time.strftime("%Y-%m-%d")
        
        # Build nested tree hierarchy mapping
        node_map = {"": root_item}
        for sub in sorted(subdirs, key=str.lower):
            resolved_sub = sub.replace("{Date}", curr_date).replace("{Matter ID}", case_id)
            parts = resolved_sub.split('/')
            
            parent_key = ""
            for i, part in enumerate(parts):
                current_key = "/".join(parts[:i+1])
                if current_key not in node_map:
                    parent_node = node_map[parent_key]
                    new_item = QtWidgets.QTreeWidgetItem(parent_node, [part])
                    node_map[current_key] = new_item
                parent_key = current_key

        self.tree_widget.expandAll()

    def add_custom_folder(self):
        """Append folder name and resolve parent path attachment to blueprint."""
        txt = self.txt_custom_folder.text().strip()
        if not txt:
            dialogs.show_warning(self, "Invalid Name", "Please enter a valid folder name.")
            return

        # clean name of basic illegal chars
        for c in ['/', '\\', '*', '?', '"', '<', '>', '|', ':']:
            txt = txt.replace(c, "")

        parent = self.cb_custom_parent.currentText()
        final_path = txt
        if parent != "Root Level":
            if parent not in self.custom_structure:
                self.custom_structure.append(parent)
            final_path = f"{parent}/{txt}"

        if final_path not in self.custom_structure:
            self.custom_structure.append(final_path)
            self.txt_custom_folder.clear()
            self.rebuild_preview()
            # update combo parent box if we added a new root node
            if parent == "Root Level" and txt not in [self.cb_custom_parent.itemText(i) for i in range(self.cb_custom_parent.count())]:
                self.cb_custom_parent.addItem(txt)

    def remove_custom_folder(self):
        """Remove selected node from custom blueprint list."""
        selected = self.tree_widget.currentItem()
        if not selected or selected == self.tree_widget.topLevelItem(0):
            dialogs.show_warning(self, "No Selection", "Please select a custom folder in the preview tree first.")
            return

        # Backtrace selected item to resolve its blueprint string key
        parts = []
        curr = selected
        while curr and curr.parent():
            parts.insert(0, curr.text(0))
            curr = curr.parent()

        # Since date might have been expanded in the preview, let's map back
        # The easiest approach is matching folder names
        full_sub_path = "/".join(parts)
        curr_date = time.strftime("%Y-%m-%d")
        
        # Loop and check which custom blueprint entry expands to this string
        match_entry = None
        for entry in self.custom_structure:
            resolved = entry.replace("{Date}", curr_date)
            if resolved == full_sub_path:
                match_entry = entry
                break

        if match_entry and match_entry in self.custom_structure:
            self.custom_structure.remove(match_entry)
            self.rebuild_preview()
        else:
            dialogs.show_warning(self, "Delete Warning", "Could not locate blueprint model item to delete.")

    def reset_defaults(self):
        """Restore factory default litigation folders blueprint structure."""
        if dialogs.show_confirmation(self, "Reset Blueprint?", "Are you sure you want to reset case tree structure back to the factory defaults?"):
            self.custom_structure = [
                "Correspondence", "Correspondence/Client Correspondence", "Correspondence/Opposing Counsel", 
                "Correspondence/Court Correspondence", "Correspondence/{Date}", "Discovery", 
                "Discovery/Written Discovery", "Discovery/Document Production", "Discovery/Depositions", 
                "Discovery/Experts", "Pleadings", "Pleadings/Motions", "Pleadings/Orders", 
                "Pleadings/Briefs & Memoranda", "Client Documents", "Client Documents/Intake & Retainer", 
                "Client Documents/Financial Records", "Research", "Research/Caselaw", 
                "Research/Fact Research", "Trial", "Trial/Exhibits"
            ]
            self.rebuild_preview()

    def clear_custom_structure(self):
        """Clear custom structure list to build a blueprint from scratch."""
        if dialogs.show_confirmation(self, "Clear Blueprint?", "Clear all items? You will start with a blank canvas."):
            self.custom_structure = []
            self.rebuild_preview()

    def toggle_inputs(self, enabled: bool):
        """Lock controls during active directory tree creation runs."""
        self.txt_case_id.setEnabled(enabled)
        self.cb_blueprints.setEnabled(enabled)
        
        # only enable if custom user blueprint
        is_custom = self.cb_blueprints.currentText() == "⭐ Custom User Blueprint" and enabled
        self.txt_custom_folder.setEnabled(is_custom)
        self.cb_custom_parent.setEnabled(is_custom)
        self.btn_add_folder.setEnabled(is_custom)
        self.btn_remove_folder.setEnabled(is_custom)
        self.btn_reset.setEnabled(is_custom)
        self.btn_clear.setEnabled(is_custom)
        self.btn_run.setEnabled(enabled)

    def run_spinup(self):
        """Select destination and launch standard folder tree creation job via EngineWorker."""
        if self.active_worker:
            return  # already running

        target_root = file_dialogs.get_existing_directory(
            self,
            "Select Parent Folder to Generate Matter Structure"
        )
        if not target_root:
            return

        # Directory collision check
        try:
            if os.path.exists(target_root) and len(os.listdir(target_root)) > 0:
                if not dialogs.show_confirmation(
                    self,
                    "Folder Contains Files",
                    "The selected folder contains existing files or subdirectories.\n\nDo you want to proceed and merge structures?"
                ):
                    return
        except Exception:
            pass

        # Prepare parameters and core Job structures
        from core.job import Job, FolderTreeParams, OutputSpec
        
        case_id = self.txt_case_id.text().strip() or "Matter_Root"
        archetype = self.cb_blueprints.currentText()
        
        job_params = FolderTreeParams(
            archetype=archetype,
            custom_subdirs=list(self.custom_structure),
            matter_id=case_id
        )
        job_output = OutputSpec(directory=Path(target_root), overwrite=True)

        job = Job(
            operation="folder_tree",
            inputs=[],
            params=job_params,
            output=job_output
        )

        self.toggle_inputs(False)

        # Thread setup
        self.thread = QtCore.QThread()
        self.active_worker = EngineJobWorker(job, output_root=Path(target_root))
        self.active_worker.moveToThread(self.thread)

        # Wire Slots
        self.thread.started.connect(self.active_worker.run_job)
        self.active_worker.progress.connect(self.on_fileroom_progress)
        self.active_worker.finished.connect(self.on_fileroom_finished)

        self.thread.start()

    def on_fileroom_progress(self, percent: int, msg: str):
        """Update progress bar overlay inside shell statusbar."""
        self.update_main_status(percent, msg)

    def on_fileroom_finished(self, success: bool, error_msg: str, result: object):
        """Unlock layout buttons and notify user of folder creation results."""
        if self.thread:
            self.thread.quit()
            self.thread.wait()
            self.thread = None

        self.active_worker = None
        self.toggle_inputs(True)
        self.clear_main_status()

        if success:
            count = len(result.outputs)
            dialogs.show_info(
                self,
                "Structure Created",
                f"Directory Tree construction successfully completed!\n\nInstantiated {count} customized subfolders."
            )
            # Open parent directory
            if result.outputs:
                parent_dir = os.path.dirname(result.outputs[0])
                try:
                    os.startfile(parent_dir)
                except Exception:
                    pass
        else:
            dialogs.show_error(
                self,
                "Generation Failure",
                f"Could not build directory architectures: {error_msg}"
            )
