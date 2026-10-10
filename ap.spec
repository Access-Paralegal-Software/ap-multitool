# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

hidden_imports = (
    collect_submodules('reportlab') +
    collect_submodules('pikepdf') +
    collect_submodules('ap_core') +
    collect_submodules('doc_chameleon') +
    ['docx', 'openpyxl', 'extract_msg']
)

datas = (
    collect_data_files('reportlab') +
    collect_data_files('pikepdf')
)

a = Analysis(
    ['apps/cli/src/ap_cli/main.py'],
    pathex=['packages/ap-core/src', 'packages/doc-chameleon/src', 'apps/cli/src'],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PySide6', 'shiboken6', 'tkinter', 'matplotlib'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ap',
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
    codesign_identity=None,
    entitlements_file=None,
)
