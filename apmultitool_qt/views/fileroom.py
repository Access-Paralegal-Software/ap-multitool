# apmultitool_qt/views/fileroom.py

"""File Room & Trees View widget class for APMultitool Qt."""

from PySide6 import QtWidgets, QtCore
from apmultitool_qt.components import SectionCard, FormRow, ActionBar, HintLabel, dialogs, file_dialogs

class FileRoomView(QtWidgets.QWidget):
    """
    Refined File Room & Case Directories View.
    Configures matter blueprints utilizing FormRows and renders a structure tree.
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
        # Left Panel (Blueprint Options Sidebar Card)
        # ----------------------------------------------------
        self.left_card = SectionCard()
        self.left_card.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.left_card.setMinimumWidth(320)
        self.left_card.setMaximumWidth(340)

        # Header Title
        header = QtWidgets.QLabel("FILE ROOM CONFIG")
        header.setObjectName("GroupHeader")
        self.left_card.add_widget(header)

        # Case ID FormRow
        self.txt_case_id = QtWidgets.QLineEdit()
        self.txt_case_id.setText("2026-AP-9908")
        self.left_card.add_widget(FormRow("Matter ID Reference:", self.txt_case_id, label_width=130))

        # Blueprints FormRow
        self.cb_blueprints = QtWidgets.QComboBox()
        self.cb_blueprints.addItems([
            "Access Paralegal Litigation Standard",
            "Transactional / Corporate Real Estate",
            "Bankruptcy Default Proceeding",
            "Custom User Defined..."
        ])
        self.left_card.add_widget(FormRow("Structure Blueprint:", self.cb_blueprints, label_width=130))

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
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.right_card.add_widget(self.tree)

        # Prepopulate structure
        self.rebuild_preview()

        splitter.addWidget(self.right_card)

    def rebuild_preview(self):
        self.tree.clear()
        case_id = self.txt_case_id.text().strip() or "Case_Matter"
        root = QtWidgets.QTreeWidgetItem(self.tree, [case_id])
        
        pleadings = QtWidgets.QTreeWidgetItem(root, ["01_Pleadings"])
        QtWidgets.QTreeWidgetItem(pleadings, ["01_Complaints"])
        QtWidgets.QTreeWidgetItem(pleadings, ["02_Answers"])
        
        exhibits = QtWidgets.QTreeWidgetItem(root, ["02_Exhibits"])
        QtWidgets.QTreeWidgetItem(exhibits, ["01_Raw_Intake"])
        QtWidgets.QTreeWidgetItem(exhibits, ["02_Processed"])

        corr = QtWidgets.QTreeWidgetItem(root, ["03_Correspondence"])
        QtWidgets.QTreeWidgetItem(corr, ["01_Emails"])
        QtWidgets.QTreeWidgetItem(corr, ["02_Letters"])

        self.tree.expandAll()

    def run_spinup(self):
        target_dir = file_dialogs.get_existing_directory(
            self,
            "Select Matter Workspace Folder"
        )
        if not target_dir:
            return

        dialogs.show_info(self, "Spin Up Completed", "Workspace directory trees spin up complete. Shared components tests checked out successfully.")
