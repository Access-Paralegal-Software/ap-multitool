# -*- mode: python ; coding: utf-8 -*-
# ap_multitool.spec — PyInstaller bundle specification for APMultitool

from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

# ---------------------------------------------------------------------
# Analysis & Build config for GUI
# ---------------------------------------------------------------------
a_gui = Analysis(
    ['apps/desktop/gui_apmultitool_qt.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('apps/desktop/logo_small.png', '.'),
        ('apps/desktop/water_texture.png', '.')
    ],
    hiddenimports=collect_submodules('ap_core') + [
        'win32com', 
        'win32com.client', 
        'pythoncom',
        'pypdf',
        'reportlab',
        'pikepdf'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PySide6.QtWebEngine',
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtQml',
        'PySide6.QtQuick',
        'PySide6.QtNetwork',
        'PySide6.QtSql',
        'PySide6.QtBluetooth',
        'PySide6.QtMultimedia',
        'PySide6.QtPositioning',
        'PySide6.QtLocation',
        'PySide6.QtSensors',
        'PySide6.QtNfc',
        'PySide6.QtTextToSpeech',
        'PySide6.QtWebSockets',
        'tkinter'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz_gui = PYZ(
    a_gui.pure, 
    a_gui.zipped_data, 
    cipher=block_cipher
)

exe_gui = EXE(
    pyz_gui,
    a_gui.scripts,
    a_gui.binaries,
    a_gui.zipfiles,
    a_gui.datas,
    [],
    name='Access_Paralegal_Multitool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    version='packaging/windows/apmultitool_version_info.txt',
    codesign_identity=None,
    entitlements_file=None,
)

# ---------------------------------------------------------------------
# Analysis & Build config for CLI
# ---------------------------------------------------------------------
a_cli = Analysis(
    ['apps/cli/src/ap_cli/main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=collect_submodules('ap_core') + [
        'win32com', 
        'win32com.client', 
        'pythoncom',
        'pypdf',
        'reportlab',
        'pikepdf'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PySide6',
        'tkinter'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz_cli = PYZ(
    a_cli.pure, 
    a_cli.zipped_data, 
    cipher=block_cipher
)

exe_cli = EXE(
    pyz_cli,
    a_cli.scripts,
    a_cli.binaries,
    a_cli.zipfiles,
    a_cli.datas,
    [],
    name='apmultitool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    version='packaging/windows/apmultitool_version_info.txt',
    codesign_identity=None,
    entitlements_file=None,
)
