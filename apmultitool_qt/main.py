# apmultitool_qt/main.py

"""QApplication startup and configuration bootstrap module for APMultitool Qt."""

import sys
from PySide6 import QtWidgets, QtCore, QtGui
from apmultitool_qt.shell import APMainWindow
from core import __version__, __channel__

def main() -> int:
    """
    Main application bootstrap entry point.
    Configures DPI scaling policies, instantiates QApplication, and displays shell window.
    """
    # 0. Configure rotating file logging
    try:
        from core.support import setup_app_logging
        logger = setup_app_logging()
        logger.info("APMultitool GUI application starting...")
    except Exception as e:
        sys.stderr.write(f"Failed to configure file logging: {e}\n")

    # 1. Enforce High-DPI scaling parameters for Retina and High-DPI displays (tablet compatibility)
    # Note: Attribute configurations must occur prior to QApplication construction.
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    app = QtWidgets.QApplication(sys.argv)
    
    # 2. Configure basic application metadata
    app.setApplicationName("APMultitool")
    app.setApplicationVersion(f"{__version__}{__channel__}")
    app.setOrganizationName("Access Paralegal")
    app.setOrganizationDomain("accessparalegal.com")

    # 3. Create and show main window shell
    main_window = APMainWindow()
    main_window.show()

    # 4. Execute main event loop
    return app.exec()
