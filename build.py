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
        return True
    except ImportError:
        print("❌ PyInstaller chưa được cài đặt")
        print("Cài đặt bằng lệnh: pip install pyinstaller")
        return False

def create_spec_file():
    """Tạo file .spec cho PyInstaller"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'colorama',
        'requests',
        'psutil',
        'json',
        'sqlite3',
        'uuid',
        'platform',
        'datetime',
        'threading',
        'time'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''
    
    with open('LappyLab.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ Đã tạo file LappyLab.spec")

def build_executable():
    """Build executable"""
    try:
        print("🔨 Đang build executable...")
        
        # Tạo spec file
        create_spec_file()
        
        # Chạy PyInstaller
        cmd = [sys.executable, '-m', 'PyInstaller', '--clean', 'LappyLab.spec']
        
        print(f"Chạy lệnh: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build thành công!")
            
            # Kiểm tra file executable
            exe_path = os.path.join('dist', 'LappyLab.exe' if os.name == 'nt' else 'LappyLab')
            if os.path.exists(exe_path):
                size = os.path.getsize(exe_path)
                print(f"📁 File executable: {exe_path}")
                print(f"📏 Kích thước: {size / (1024*1024):.1f} MB")
                return True
            else:
                print("❌ Không tìm thấy file executable")
                return False
        else:
            print("❌ Build thất bại!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Lỗi build: {str(e)}")
        return False

def clean_build_files():
    """Dọn dẹp file build"""
    try:
        dirs_to_remove = ['build', '__pycache__']
        files_to_remove = ['LappyLab.spec']
        
        for dir_name in dirs_to_remove:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)
                print(f"🗑️ Đã xóa thư mục: {dir_name}")
        
        for file_name in files_to_remove:
            if os.path.exists(file_name):
                os.remove(file_name)
                print(f"🗑️ Đã xóa file: {file_name}")
                
        # Xóa __pycache__ trong các thư mục con
        for root, dirs, files in os.walk('.'):
            for dir_name in dirs:
                if dir_name == '__pycache__':
                    pycache_path = os.path.join(root, dir_name)
                    shutil.rmtree(pycache_path)
                    print(f"🗑️ Đã xóa: {pycache_path}")
        
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
    print("🏗️ Lappy Lab 4.1 Build Script")
    print("=" * 40)
    
    # Kiểm tra PyInstaller
    if not check_pyinstaller():
        return
    
    # Menu
    while True:
        print("\nChọn hành động:")
        print("1. Build executable")
        print("2. Build + Clean")
        print("3. Build + Installer (Windows)")
        print("4. Clean build files")
        print("0. Thoát")
        
        choice = input("\nNhập lựa chọn (0-4): ").strip()
        
        if choice == '0':
            print("👋 Tạm biệt!")
            break
        elif choice == '1':
            build_executable()
        elif choice == '2':
            if build_executable():
                clean_build_files()
        elif choice == '3':
            if build_executable():
                create_installer()
                clean_build_files()
        elif choice == '4':
            clean_build_files()
        else:
            print("❌ Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    main()
