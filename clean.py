#!/usr/bin/env python3
# clean.py - Script dọn dẹp các file không cần thiết

import os
import shutil
import glob

def clean_pycache():
    """Xóa tất cả thư mục __pycache__"""
    try:
        count = 0
        for root, dirs, files in os.walk('.'):
            for dir_name in dirs[:]:  # Copy list to avoid modification during iteration
                if dir_name == '__pycache__':
                    pycache_path = os.path.join(root, dir_name)
                    try:
                        shutil.rmtree(pycache_path)
                        print(f"✅ Đã xóa: {pycache_path}")
                        count += 1
                        dirs.remove(dir_name)  # Don't recurse into deleted directory
                    except Exception as e:
                        print(f"❌ Lỗi xóa {pycache_path}: {str(e)}")
        
        print(f"🧹 Đã xóa {count} thư mục __pycache__")
        return count > 0
    except Exception as e:
        print(f"❌ Lỗi dọn dẹp __pycache__: {str(e)}")
        return False

def clean_pyc_files():
    """Xóa tất cả file .pyc"""
    try:
        count = 0
        for pattern in ['**/*.pyc', '**/*.pyo', '**/*.pyd']:
            for file_path in glob.glob(pattern, recursive=True):
                try:
                    os.remove(file_path)
                    print(f"✅ Đã xóa: {file_path}")
                    count += 1
                except Exception as e:
                    print(f"❌ Lỗi xóa {file_path}: {str(e)}")
        
        print(f"🧹 Đã xóa {count} file .pyc/.pyo/.pyd")
        return count > 0
    except Exception as e:
        print(f"❌ Lỗi dọn dẹp file .pyc: {str(e)}")
        return False

def clean_build_artifacts():
    """Xóa các file build artifacts"""
    try:
        count = 0
        artifacts = [
            'build/',
            'dist/',
            '*.egg-info/',
            '*.spec',
            'LappyLab_Setup.exe',
            'installer.nsi'
        ]
        
        for pattern in artifacts:
            if pattern.endswith('/'):
                # Directory
                for dir_path in glob.glob(pattern[:-1]):
                    if os.path.isdir(dir_path):
                        try:
                            shutil.rmtree(dir_path)
                            print(f"✅ Đã xóa thư mục: {dir_path}")
                            count += 1
                        except Exception as e:
                            print(f"❌ Lỗi xóa {dir_path}: {str(e)}")
            else:
                # File
                for file_path in glob.glob(pattern):
                    try:
                        os.remove(file_path)
                        print(f"✅ Đã xóa file: {file_path}")
                        count += 1
                    except Exception as e:
                        print(f"❌ Lỗi xóa {file_path}: {str(e)}")
        
        print(f"🧹 Đã xóa {count} build artifacts")
        return count > 0
    except Exception as e:
        print(f"❌ Lỗi dọn dẹp build artifacts: {str(e)}")
        return False

def clean_temp_files():
    """Xóa các file tạm"""
    try:
        count = 0
        temp_patterns = [
            '*.tmp',
            '*.temp',
            '*~',
            '.DS_Store',
            'Thumbs.db',
            'desktop.ini'
        ]
        
        for pattern in temp_patterns:
            for file_path in glob.glob(pattern, recursive=True):
                try:
                    os.remove(file_path)
                    print(f"✅ Đã xóa temp file: {file_path}")
                    count += 1
                except Exception as e:
                    print(f"❌ Lỗi xóa {file_path}: {str(e)}")
        
        print(f"🧹 Đã xóa {count} temp files")
        return count > 0
    except Exception as e:
        print(f"❌ Lỗi dọn dẹp temp files: {str(e)}")
        return False

def main():
    """Hàm main"""
    print("🧹 Lappy Lab 4.1 - Clean Script")
    print("=" * 40)
    
    total_cleaned = 0
    
    print("\n1. Dọn dẹp __pycache__...")
    if clean_pycache():
        total_cleaned += 1
    
    print("\n2. Dọn dẹp file .pyc...")
    if clean_pyc_files():
        total_cleaned += 1
    
    print("\n3. Dọn dẹp build artifacts...")
    if clean_build_artifacts():
        total_cleaned += 1
    
    print("\n4. Dọn dẹp temp files...")
    if clean_temp_files():
        total_cleaned += 1
    
    print("\n" + "=" * 40)
    if total_cleaned > 0:
        print(f"✅ Dọn dẹp hoàn tất! ({total_cleaned} loại file đã được xóa)")
    else:
        print("ℹ️ Không có file nào cần dọn dẹp")
    
    print("🎉 Dự án đã sạch sẽ!")

if __name__ == "__main__":
    main()
