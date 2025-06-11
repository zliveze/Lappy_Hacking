#!/usr/bin/env python3
# run.py - Script chạy Lappy Lab 4.1
import sys
import os
import ctypes
import platform

def is_admin():
    """Kiểm tra xem có quyền admin không (chỉ trên Windows)"""
    if platform.system() != "Windows":
        return True  # Trên Linux/Mac không cần kiểm tra
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Chạy lại script với quyền admin (chỉ trên Windows)"""
    if platform.system() != "Windows":
        return True  # Trên Linux/Mac không cần admin

    if is_admin():
        return True
    else:
        try:
            # Lấy đường dẫn Python và script hiện tại
            python_exe = sys.executable
            script_path = os.path.abspath(__file__)

            print("⚠️  Cần quyền Administrator để chạy ứng dụng")
            print("🔄 Đang yêu cầu quyền Administrator...")

            # Chạy lại với quyền admin (0 = ẩn cửa sổ)
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                python_exe,
                f'"{script_path}"',
                None,
                0
            )
            return False
        except Exception as e:
            print(f"Không thể chạy với quyền admin: {e}")
            print("⚠️  Tiếp tục chạy với quyền thường...")
            return True  # Tiếp tục chạy bình thường

def check_python_version():
    """Kiểm tra phiên bản Python"""
    if sys.version_info < (3, 8):
        print("❌ Lỗi: Cần Python 3.8 trở lên")
        print(f"Phiên bản hiện tại: {sys.version}")
        return False
    return True

def check_dependencies():
    """Kiểm tra dependencies"""
    required_modules = [
        'tkinter',
        'colorama', 
        'requests',
        'psutil'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("❌ Thiếu các module sau:")
        for module in missing_modules:
            print(f"  - {module}")
        print("\nCài đặt bằng lệnh:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Hàm main"""
    print("🚀 Đang khởi động Lappy Lab 4.1...")

    # Kiểm tra và yêu cầu quyền admin nếu cần (chỉ trên Windows)
    if not run_as_admin():
        print("Đang khởi động lại với quyền Administrator...")
        sys.exit(0)

    if platform.system() == "Windows" and is_admin():
        print("✅ Đang chạy với quyền Administrator")

    # Kiểm tra Python version
    if not check_python_version():
        input("Nhấn Enter để thoát...")
        return
    
    # Kiểm tra dependencies
    if not check_dependencies():
        input("Nhấn Enter để thoát...")
        return
    
    # Import và chạy app
    try:
        from main import main as run_app
        print("✅ Đã tải thành công tất cả dependencies")
        print("🎯 Đang khởi động giao diện...")
        run_app()
    except Exception as e:
        print(f"❌ Lỗi khởi động ứng dụng: {str(e)}")
        print("\nChi tiết lỗi:")
        import traceback
        traceback.print_exc()
        input("Nhấn Enter để thoát...")

if __name__ == "__main__":
    main()
