# apmultitool_qt/main.py

"""QApplication startup and configuration bootstrap module for APMultitool Qt."""

import sys
from PySide6 import QtWidgets, QtCore, QtGui
from apmultitool_qt.shell import APMainWindow

def main() -> int:
    """
    Main application bootstrap entry point.
    Configures DPI scaling policies, instantiates QApplication, and displays shell window.
    """
    # 1. Enforce High-DPI scaling parameters for Retina and High-DPI displays (tablet compatibility)
    # Note: Attribute configurations must occur prior to QApplication construction.
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    app = QtWidgets.QApplication(sys.argv)
    
    # 2. Configure basic application metadata
    app.setApplicationName("APMultitool")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Access Paralegal")
    app.setOrganizationDomain("accessparalegal.com")

    # 3. Create and show main window shell
    main_window = APMainWindow()
    main_window.show()

    # 4. Execute main event loop
    return app.exec()
