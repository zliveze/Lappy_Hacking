# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

# Sửa lại cách copy resources
added_files = [
    ('public/image/icon.jpg', 'public/image'),
    ('public/image/cursor-icon.jpg', 'public/image'),
    ('public/image/windsurf-icon.png', 'public/image'),
    ('public/image/aide.png', 'public/image'),
    ('public/image/icon.ico', 'public/image'),
    ('app/utils/*.py', 'app/utils')
]

a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath(SPECPATH)],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'PIL',
        'PIL._imagingtk',
        'PIL._tkinter_finder',
        'app',
        'app.utils',
        'app.utils.id_generator',
        'app.utils.file_manager',
        'app.utils.message_box',
        'app.utils.settings_manager',
        'app.utils.version_info_dialog',
        'packaging.version',
        'packaging.specifiers',
        'packaging.requirements',
        'packaging.markers',
        'webbrowser',
        'json',
        'uuid',
        'winreg',
        'ctypes',
        'requests',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        're',
        'datetime',
        'platform',
        'traceback'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'numpy', 'pandas', 'scipy', 'matplotlib',
        'PyQt5', 'PyQt6', 'PySide6', 'wx',
        'test', 'unittest'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

excludes_patterns = [
    '*test*',
    '*docs*',
    '*.pyc',
    '*__pycache__*'
]

def remove_from_list(list_, patterns):
    import fnmatch
    for file_ in list_[:]:
        for pattern in patterns:
            if fnmatch.fnmatch(file_[0], pattern):
                list_.remove(file_)
                break

remove_from_list(a.datas, excludes_patterns)
remove_from_list(a.binaries, excludes_patterns)

# Bỏ qua việc strip binary files
a.binaries = [x for x in a.binaries if not x[0].startswith('api-ms-win')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Lappy_Lab',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Tạm thời bật console để xem lỗi
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='public/image/icon.ico',
    version='file_version_info.txt',
    uac_admin=True,
    onefile=True
)

