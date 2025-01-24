# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import os
import sys
from PyInstaller.utils.hooks import collect_data_files

# Sử dụng đường dẫn tuyệt đối
base_path = os.path.abspath(os.getcwd())

# Thu thập tất cả tệp dữ liệu
datas = [
    ('public', 'public'),
    ('app', 'app'),
    ('LICENSE', '.'),
    ('README.md', '.'),
]

a = Analysis(
    ['main.py'],
    pathex=[base_path],
    binaries=[],
    datas=datas,
    hiddenimports=['PIL', 'PIL._imagingtk', 'PIL._tkinter_finder'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Thêm tệp bổ sung vào bundle
a.datas += [('LICENSE', 'LICENSE', 'DATA')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Lappy_Hacking',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='public/image/icon.ico',
    version='file_version_info.txt',
    uac_admin=False,
) 


Lệnh build python -m PyInstaller --clean --noconfirm lappy_hacking.spec