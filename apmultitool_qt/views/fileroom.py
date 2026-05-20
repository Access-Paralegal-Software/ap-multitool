# apmultitool_qt/views/fileroom.py

"""File Room & Trees View widget class for APMultitool Qt."""

from PySide6 import QtWidgets, QtCore, QtGui

class FileRoomView(QtWidgets.QWidget):
    """
    Placeholder View class for the File Room and Directory Tree Architect.
    Lays out matter selectors and visual folder-hierarchy trees.
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
        # Left Panel (Fixed Blueprint Options Sidebar)
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
        header = QtWidgets.QLabel("FILE ROOM CONFIG")
        header.setObjectName("GroupHeader")
        left_layout.addWidget(header)

        # Case ID
        left_layout.addWidget(QtWidgets.QLabel("Case Matter ID Reference:"))
        self.txt_case_id = QtWidgets.QLineEdit()
        self.txt_case_id.setText("2026-AP-9908")
        left_layout.addWidget(self.txt_case_id)

        # Blueprints Select
        left_layout.addWidget(QtWidgets.QLabel("Select Structure Blueprint:"))
        self.cb_blueprints = QtWidgets.QComboBox()
        self.cb_blueprints.addItems([
            "Access Paralegal Litigation Standard",
            "Transactional / Corporate Real Estate",
            "Bankruptcy Default Proceeding",
            "Custom User Defined..."
        ])
        left_layout.addWidget(self.cb_blueprints)

        left_layout.addStretch()

        # Primary Run Action Button
        self.btn_run = QtWidgets.QPushButton("Spin Up Folder Tree")
        self.btn_run.setObjectName("PrimaryButton")
        left_layout.addWidget(self.btn_run)

        splitter.addWidget(left_panel)

        # ----------------------------------------------------
        # Right Panel (Folder Tree Visualizer Preview)
        # ----------------------------------------------------
        right_panel = QtWidgets.QFrame()
        right_panel.setObjectName("GroupBoxContainer")

        right_layout = QtWidgets.QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(12)

        # Header
        t_header = QtWidgets.QLabel("FOLDER TREE ARCHITECTURE PREVIEW")
        t_header.setObjectName("GroupHeader")
        right_layout.addWidget(t_header)

        # Tree Widget
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderHidden(True)
        right_layout.addWidget(self.tree)

        # Prepopulate with folder mock outlines
        root = QtWidgets.QTreeWidgetItem(self.tree, ["Case_2026-AP-9908"])
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

        splitter.addWidget(right_panel)
