# gui_apmultitool_qt.py

"""Top-level PySide6 bootstrap script for Access Paralegal Multitool."""

import sys
import os

# Add the current directory to python path to ensure imports resolve correctly.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from apmultitool_qt.main import main

if __name__ == "__main__":
    sys.exit(main())
