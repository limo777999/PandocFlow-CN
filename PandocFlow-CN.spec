# -*- mode: python ; coding: utf-8 -*-

import os

project_root = os.path.abspath(os.path.join(SPECPATH, os.pardir))
pandoc_path = os.environ.get('PANDOC_EXE', os.path.join(project_root, 'engines', 'pandoc.exe'))
typst_path = os.environ.get('TYPST_EXE', os.path.join(project_root, 'engines', 'typst.exe'))
binaries = []
if os.path.isfile(pandoc_path):
    binaries.append((pandoc_path, '.'))
if os.path.isfile(typst_path):
    binaries.append((typst_path, '.'))


a = Analysis(
    ['src\\main.py'],
    pathex=['src'],
    binaries=binaries,
    datas=[('src/default.ico', 'src'), ('THIRD_PARTY_NOTICES.txt', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PandocFlow-CN',
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
    codesign_identity=None,
    entitlements_file=None,
    icon=['src\\default.ico'],
)
