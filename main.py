import os
import sys
import platform
from colorama import Fore, Style, init
from utils import is_admin, run_as_admin
from config import EMOJI, get_config
from gui import run_gui

# Khởi tạo colorama
init()

def check_requirements():
    """Kiểm tra các yêu cầu trước khi chạy"""
    try:
        # Kiểm tra Python version
        python_version = platform.python_version_tuple()
        if int(python_version[0]) < 3 or (int(python_version[0]) == 3 and int(python_version[1]) < 6):
            print(f"{Fore.RED}{EMOJI['ERROR']} Lappy Lab yêu cầu Python 3.6 trở lên.{Style.RESET_ALL}")
            return False

        # Kiểm tra các thư viện
        required_modules = [
            "tkinter", "customtkinter", "PIL", "colorama", "requests", "psutil"
        ]

        missing_modules = []
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)

        if missing_modules:
            print(f"{Fore.RED}{EMOJI['ERROR']} Thiếu các thư viện sau: {', '.join(missing_modules)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{EMOJI['INFO']} Vui lòng cài đặt bằng lệnh: pip install -r requirements.txt{Style.RESET_ALL}")
            return False

        return True
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} Lỗi khi kiểm tra yêu cầu: {str(e)}{Style.RESET_ALL}")
        return False

def main():
    """Hàm chính"""
    print(f"{Fore.CYAN}{EMOJI['INFO']} Đang khởi động Lappy Lab 4.0...{Style.RESET_ALL}")

    # Kiểm tra quyền admin trên Windows
    if platform.system() == "Windows" and not is_admin():
        print(f"{Fore.YELLOW}{EMOJI['WARNING']} Lappy Lab yêu cầu quyền admin để hoạt động đầy đủ.{Style.RESET_ALL}")

        # Tự động chạy lại với quyền admin
        print(f"{Fore.CYAN}{EMOJI['INFO']} Đang yêu cầu quyền admin...{Style.RESET_ALL}")
        if run_as_admin():
            sys.exit(0)  # Thoát sau khi yêu cầu quyền admin
        else:
            print(f"{Fore.RED}{EMOJI['ERROR']} Không thể chạy với quyền admin. Một số chức năng có thể không hoạt động.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}{EMOJI['INFO']} Nhấn Enter để tiếp tục với quyền hiện tại...{Style.RESET_ALL}")

    # Kiểm tra các yêu cầu
    if not check_requirements():
        input(f"{Fore.RED}{EMOJI['ERROR']} Nhấn Enter để thoát...{Style.RESET_ALL}")
        sys.exit(1)

    # Khởi tạo cấu hình
    config = get_config()

    # Chạy giao diện người dùng
    run_gui()

if __name__ == "__main__":
    main()
