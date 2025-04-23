# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# --- Lấy đường dẫn gốc của script ---
basedir = os.path.dirname(SPECPATH)

# --- Các tệp dữ liệu cần đưa vào ---
# Thêm icon và các tài nguyên khác nếu cần
datas = [
    (os.path.join(basedir, 'public', 'images', 'icon.ico'), os.path.join('public', 'images')),
    (os.path.join(basedir, 'manifest.xml'), '.'),  # Thêm manifest.xml để yêu cầu quyền admin
    # Thêm các tệp/thư mục dữ liệu khác tại đây nếu có
    # Ví dụ: ('locales', 'locales') nếu bạn có thư mục locales
]

# --- Cấu hình Analysis ---
a = Analysis(
    ['main.py'], # Script chính
    pathex=[basedir], # Đường dẫn tìm kiếm module
    binaries=[],
    datas=datas,
    hiddenimports=[
        'babel.numbers', # Thêm các thư viện ẩn cần thiết
        'PIL._tkinter_finder', # Cần cho Pillow trong Tkinter
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'colorama',
        'customtkinter',
        # Thêm các module khác nếu PyInstaller không tự tìm thấy
        'reset_machine_id',
        'bypass_version',
        'bypass_token_limit',
        'check_user_authorized',
        'config',
        'cursor_acc_info',
        'disable_auto_update',
        'gui',
        'preview',
        'quit_cursor',
        'show_config',
        'totally_reset_cursor',
        'utils',
        'admin_helper'
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

# --- Cấu hình PYZ (Python Archive) ---
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# --- Cấu hình EXE ---
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LappyLab', # Tên file .exe
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True, # Sử dụng UPX để nén nếu có
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False, # Đặt là False cho ứng dụng GUI
    icon=os.path.join(basedir, 'public', 'images', 'icon.ico'), # Đường dẫn đến icon
    manifest=os.path.join(basedir, 'manifest.xml') # Sử dụng manifest để yêu cầu quyền admin
)

# --- Cấu hình COLLECT (Không cần thiết cho onefile=True) ---
# coll = COLLECT(...) # Bỏ qua nếu dùng onefile
