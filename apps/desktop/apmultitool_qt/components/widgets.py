# apmultitool_qt/components/widgets.py

"""Shared reusable UI widget primitives for APMultitool Qt."""

from PySide6 import QtWidgets, QtCore, QtGui

class SectionCard(QtWidgets.QFrame):
    """
    Standard container frame for grouping related fields.
    Automatically applies styling IDs and structural margin boundaries.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("GroupBoxContainer")
        self.layout_container = QtWidgets.QVBoxLayout(self)
        self.layout_container.setContentsMargins(15, 15, 15, 15)
        self.layout_container.setSpacing(12)

    def add_widget(self, widget: QtWidgets.QWidget):
        self.layout_container.addWidget(widget)

    def add_layout(self, layout: QtWidgets.QLayout):
        self.layout_container.addLayout(layout)

    def add_stretch(self):
        self.layout_container.addStretch()


class FormRow(QtWidgets.QWidget):
    """
    Standard layout pairing a label on the left with an interactive input widget on the right.
    Ensures uniform aligned spacing across form screens.
    """
    def __init__(self, label_text: str, input_widget: QtWidgets.QWidget, label_width: int = 140, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.label = QtWidgets.QLabel(label_text)
        self.label.setFixedWidth(label_width)
        self.label.setStyleSheet("font-weight: 500; color: #374151;")
        
        self.input_widget = input_widget
        self.input_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

        layout.addWidget(self.label)
        layout.addWidget(self.input_widget)


class ActionBar(QtWidgets.QFrame):
    """
    Horizontal button container styled for placing execution actions at the bottom of views.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout_container = QtWidgets.QHBoxLayout(self)
        self.layout_container.setContentsMargins(0, 5, 0, 0)
        self.layout_container.setSpacing(8)

    def add_button(self, button: QtWidgets.QPushButton):
        self.layout_container.addWidget(button)

    def add_stretch(self):
        self.layout_container.addStretch()


class HintLabel(QtWidgets.QLabel):
    """
    Low-contrast informational label for displaying tooltips and help hints under input fields.
    """
    def __init__(self, text: str, indent: int = 26, parent=None):
        super().__init__(text, parent)
        self.setWordWrap(True)
        self.setStyleSheet(f"color: #6B7280; font-size: 10px; margin-left: {indent}px; line-height: 12px;")


class EmptyStateWidget(QtWidgets.QWidget):
    """
    Visual placeholder displaying a centered prompt when lists/queues are empty.
    """
    def __init__(self, message_text: str = "No Items in Queue", parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(20, 20, 20, 20)

        self.lbl_text = QtWidgets.QLabel(message_text)
        self.lbl_text.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_text.setStyleSheet("""
            color: #9CA3AF;
            font-size: 13px;
            font-weight: 500;
            padding: 10px;
        """)
        
        layout.addWidget(self.lbl_text)
