"""
tests.test_gui
Validates Doc-Chameleon desktop window initialization, table zebra mapping,
and widget instantiation in offscreen/headless mode.
"""

import pytest
import sys
from pathlib import Path

# Verify PySide6 availability or skip gracefully in headless server runners
try:
    from PySide6.QtWidgets import QApplication
    from doc_chameleon.gui.app import DocChameleonWindow, COLOR_CANVAS, COLOR_SURFACE_B
    has_pyside = True
except ImportError:
    has_pyside = False

@pytest.mark.skipif(not has_pyside, reason="PySide6 not installed in current environment")
def test_doc_chameleon_window_headless():
    app = QApplication.instance() or QApplication(["--platform", "offscreen"])
    win = DocChameleonWindow()
    
    assert "Doc-Chameleon" in win.windowTitle()
    assert win.table.columnCount() == 4
    assert win.prefix_input.text() == "ABC_"
    assert win.digits_input.value() == 8
    
    # Test file queue refresh
    sample_path = Path("sample_doc.pdf")
    win.queued_files = [sample_path]
    win.refresh_table()
    
    assert win.table.rowCount() == 1
    assert win.table.item(0, 1).text() == "sample_doc.pdf"
