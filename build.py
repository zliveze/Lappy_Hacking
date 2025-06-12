#!/usr/bin/env python3
# build.py - Script build executable cho Lappy Lab 4.1
import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """Kiểm tra PyInstaller"""
    try:
        import PyInstaller
        print(f"✅ PyInstaller version: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("❌ PyInstaller chưa được cài đặt")
        print("💡 Cài đặt bằng lệnh: pip install pyinstaller")
        return False

def check_icon():
    """Kiểm tra và chuẩn bị icon"""
    icon_paths = [
        "public/image/icon.ico",
        "public/image/icon.jpg",
        "assets/icons/icon.ico",
        "icon.ico"
    ]

    for icon_path in icon_paths:
        if os.path.exists(icon_path):
            print(f"✅ Tìm thấy icon: {icon_path}")
            return icon_path

    print("⚠️ Không tìm thấy icon, sẽ build không có icon")
    return None

def create_spec_file(icon_path=None):
    """Tạo file .spec cho PyInstaller"""

    # Chuẩn bị icon path cho spec file
    icon_line = f"icon='{icon_path}'," if icon_path else "# icon=None,"

    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# Lappy Lab 4.1 - PyInstaller Spec File

block_cipher = None

a = Analysis(
    ['main.pyw'],  # Sử dụng main.pyw để không hiển thị console
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),  # Bao gồm thư mục src
        ('public', 'public'),  # Bao gồm thư mục public (icons, images)
        ('locales', 'locales'),  # Bao gồm thư mục locales
        ('assets', 'assets'),  # Bao gồm thư mục assets nếu có
    ],
    hiddenimports=[
        # GUI modules
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'tkinter.font',
        # Core modules
        'json',
        'sqlite3',
        'uuid',
        'platform',
        'datetime',
        'threading',
        'time',
        'os',
        'sys',
        'ctypes',
        'subprocess',
        # Third-party modules
        'colorama',
        'requests',
        'psutil',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        # Project modules
        'src.gui.main_window',
        'src.core.config',
        'src.core.utils',
        'src.features',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'IPython',
        'jupyter',
    ],
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
    name='LappyLab',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Không hiển thị console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    {icon_line}
    version='version_info.txt',  # Thông tin version nếu có
)
'''

    with open('LappyLab.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)

    print("✅ Đã tạo file LappyLab.spec")
    if icon_path:
        print(f"🎨 Sử dụng icon: {icon_path}")
    else:
        print("⚠️ Không có icon")

def create_version_info():
    """Tạo file thông tin version cho Windows"""
    version_info = '''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(4,1,0,0),
    prodvers=(4,1,0,0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Lappy Team'),
        StringStruct(u'FileDescription', u'Lappy Lab - Cursor Management Tool'),
        StringStruct(u'FileVersion', u'4.1.0.0'),
        StringStruct(u'InternalName', u'LappyLab'),
        StringStruct(u'LegalCopyright', u'© 2024 Lappy Team. All rights reserved.'),
        StringStruct(u'OriginalFilename', u'LappyLab.exe'),
        StringStruct(u'ProductName', u'Lappy Lab'),
        StringStruct(u'ProductVersion', u'4.1.0.0')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''

    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_info)

    print("✅ Đã tạo file version_info.txt")

def build_executable():
    """Build executable với icon và thông tin version"""
    try:
        print("🔨 Đang build executable...")
        print("=" * 50)

        # Kiểm tra icon
        icon_path = check_icon()

        # Tạo version info
        create_version_info()

        # Tạo spec file với icon
        create_spec_file(icon_path)

        # Chạy PyInstaller
        cmd = [sys.executable, '-m', 'PyInstaller', '--clean', '--noconfirm', 'LappyLab.spec']

        print(f"🚀 Chạy lệnh: {' '.join(cmd)}")
        print("⏳ Đang build... (có thể mất vài phút)")

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Build thành công!")

            # Kiểm tra file executable
            exe_path = os.path.join('dist', 'LappyLab.exe' if os.name == 'nt' else 'LappyLab')
            if os.path.exists(exe_path):
                size = os.path.getsize(exe_path)
                print(f"📁 File executable: {exe_path}")
                print(f"📏 Kích thước: {size / (1024*1024):.1f} MB")
                print(f"🎯 Có thể chạy: {exe_path}")
                return True
            else:
                print("❌ Không tìm thấy file executable")
                return False
        else:
            print("❌ Build thất bại!")
            print("\n📋 STDOUT:")
            print(result.stdout)
            print("\n📋 STDERR:")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"❌ Lỗi build: {str(e)}")
        return False

def clean_build_files():
    """Dọn dẹp file build"""
    try:
        print("🧹 Đang dọn dẹp files build...")

        dirs_to_remove = ['build', '__pycache__']
        files_to_remove = ['LappyLab.spec', 'version_info.txt', 'installer.nsi']

        # Xóa thư mục
        for dir_name in dirs_to_remove:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)
                print(f"🗑️ Đã xóa thư mục: {dir_name}")

        # Xóa files
        for file_name in files_to_remove:
            if os.path.exists(file_name):
                os.remove(file_name)
                print(f"🗑️ Đã xóa file: {file_name}")

        # Xóa __pycache__ trong các thư mục con
        for root, dirs, _ in os.walk('.'):
            for dir_name in dirs[:]:  # Copy list để tránh modification during iteration
                if dir_name == '__pycache__':
                    pycache_path = os.path.join(root, dir_name)
                    try:
                        shutil.rmtree(pycache_path)
                        print(f"🗑️ Đã xóa: {pycache_path}")
                        dirs.remove(dir_name)  # Không recurse vào thư mục đã xóa
                    except Exception as e:
                        print(f"⚠️ Không thể xóa {pycache_path}: {e}")

        print("✅ Dọn dẹp hoàn tất")

    except Exception as e:
        print(f"❌ Lỗi dọn dẹp: {str(e)}")

def create_installer():
    """Tạo installer (Windows only)"""
    if os.name != 'nt':
        print("ℹ️ Installer chỉ hỗ trợ Windows")
        return
    
    try:
        # Kiểm tra NSIS
        nsis_path = shutil.which('makensis')
        if not nsis_path:
            print("❌ NSIS chưa được cài đặt")
            print("Tải NSIS tại: https://nsis.sourceforge.io/")
            return
        
        # Tạo script NSIS
        nsis_script = '''
!define APP_NAME "Lappy Lab"
!define APP_VERSION "4.1"
!define APP_PUBLISHER "Lappy Team"
!define APP_EXE "LappyLab.exe"

Name "${APP_NAME}"
OutFile "LappyLab_Setup.exe"
InstallDir "$PROGRAMFILES\\${APP_NAME}"

Page directory
Page instfiles

Section "Install"
    SetOutPath $INSTDIR
    File "dist\\${APP_EXE}"
    
    CreateDirectory "$SMPROGRAMS\\${APP_NAME}"
    CreateShortCut "$SMPROGRAMS\\${APP_NAME}\\${APP_NAME}.lnk" "$INSTDIR\\${APP_EXE}"
    CreateShortCut "$DESKTOP\\${APP_NAME}.lnk" "$INSTDIR\\${APP_EXE}"
    
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\${APP_EXE}"
    Delete "$INSTDIR\\Uninstall.exe"
    Delete "$SMPROGRAMS\\${APP_NAME}\\${APP_NAME}.lnk"
    Delete "$DESKTOP\\${APP_NAME}.lnk"
    RMDir "$SMPROGRAMS\\${APP_NAME}"
    RMDir "$INSTDIR"
SectionEnd
'''
        
        with open('installer.nsi', 'w', encoding='utf-8') as f:
            f.write(nsis_script)
        
        # Chạy NSIS
        cmd = [nsis_path, 'installer.nsi']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Tạo installer thành công!")
            if os.path.exists('LappyLab_Setup.exe'):
                size = os.path.getsize('LappyLab_Setup.exe')
                print(f"📦 Installer: LappyLab_Setup.exe ({size / (1024*1024):.1f} MB)")
        else:
            print("❌ Tạo installer thất bại!")
            print("STDERR:", result.stderr)
        
        # Xóa file script
        if os.path.exists('installer.nsi'):
            os.remove('installer.nsi')
            
    except Exception as e:
        print(f"❌ Lỗi tạo installer: {str(e)}")

def main():
    """Hàm main"""
    print("🏗️ Lappy Lab 4.1 - Build Script")
    print("=" * 50)
    print("📦 Đóng gói ứng dụng thành file .exe với icon")
    print("=" * 50)

    # Kiểm tra PyInstaller
    if not check_pyinstaller():
        print("\n💡 Cài đặt PyInstaller:")
        print("   pip install pyinstaller")
        return

    # Kiểm tra icon
    icon_path = check_icon()
    if icon_path:
        print(f"🎨 Icon sẽ được sử dụng: {icon_path}")
    else:
        print("⚠️ Không tìm thấy icon, app sẽ không có icon")

    # Menu
    while True:
        print("\n" + "=" * 50)
        print("📋 MENU BUILD:")
        print("1. 🔨 Build executable (.exe)")
        print("2. 🔨 Build + Clean (Khuyến nghị)")
        print("3. 📦 Build + Installer (Windows)")
        print("4. 🧹 Clean build files")
        print("5. ℹ️ Thông tin build")
        print("0. 🚪 Thoát")
        print("=" * 50)

        choice = input("Nhập lựa chọn (0-5): ").strip()

        if choice == '0':
            print("👋 Tạm biệt!")
            break
        elif choice == '1':
            print("\n🔨 Bắt đầu build executable...")
            build_executable()
        elif choice == '2':
            print("\n🔨 Bắt đầu build + clean...")
            if build_executable():
                print("\n🧹 Dọn dẹp files tạm...")
                clean_build_files()
        elif choice == '3':
            print("\n📦 Bắt đầu build + installer...")
            if build_executable():
                print("\n📦 Tạo installer...")
                create_installer()
                print("\n🧹 Dọn dẹp files tạm...")
                clean_build_files()
        elif choice == '4':
            clean_build_files()
        elif choice == '5':
            show_build_info()
        else:
            print("❌ Lựa chọn không hợp lệ!")

def show_build_info():
    """Hiển thị thông tin build"""
    print("\n" + "=" * 50)
    print("ℹ️ THÔNG TIN BUILD")
    print("=" * 50)
    print("📁 Entry point: main.pyw (không hiển thị console)")
    print("🎨 Icon: public/image/icon.ico")
    print("📦 Output: dist/LappyLab.exe")
    print("📋 Bao gồm:")
    print("   - Thư mục src/ (source code)")
    print("   - Thư mục public/ (icons, images)")
    print("   - Thư mục locales/ (ngôn ngữ)")
    print("   - Thư mục assets/ (tài nguyên)")
    print("🔧 Cấu hình:")
    print("   - Console: False (không hiển thị CMD)")
    print("   - UPX: True (nén file)")
    print("   - One file: True (1 file .exe duy nhất)")
    print("=" * 50)

if __name__ == "__main__":
    main()
