# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Thêm các file resources
added_files = [
    ('public/image/icon.jpg', 'public/image'),
    ('public/image/cursor-icon.jpg', 'public/image'),
    ('public/image/windsurf-icon.png', 'public/image'),
    ('public/image/aide.png', 'public/image'),
    ('app/utils/*.py', 'app/utils'),
    ('app/components/*.py', 'app/components')
]

# Thu thập tất cả submodules
hidden_imports = [
    'webbrowser',
    'json',
    'uuid',
    'winreg',
    'ctypes',
    'requests',
    'packaging',
    'PIL',
    'win32gui',
    'win32con',
    'tkinter',
    'traceback',
    'datetime',
    'platform'
]

a = Analysis(
    ['main.py'],
    pathex=[os.path.dirname(os.path.abspath(SPEC))],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Xóa các file không cần thiết khỏi bundle
def remove_from_list(list_, patterns):
    for file_ in list_[:]:
        for pattern in patterns:
            if pattern in file_[0]:
                list_.remove(file_)
                break

# patterns_to_exclude = ['tkinter/test', 'lib2to3', 'unittest']
# remove_from_list(a.datas, patterns_to_exclude)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Lappy_Lab_3.1',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='public/image/icon.ico',
    version='file_version_info.txt'
)

