import os
import sys
import platform
from colorama import Fore, Style, init
from utils import get_user_documents_path, get_cursor_paths
from config import EMOJI, get_config, print_config

# Khởi tạo colorama
init()

def show_cursor_paths():
    """Hiển thị các đường dẫn liên quan đến Cursor"""
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{EMOJI['FILE']} Đường dẫn Cursor:{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    
    paths = get_cursor_paths()
    if not paths:
        print(f"{Fore.YELLOW}{EMOJI['WARNING']} Không tìm thấy đường dẫn Cursor.{Style.RESET_ALL}")
        return
    
    for key, path in paths.items():
        exists = os.path.exists(path)
        status = f"{Fore.GREEN}[Tồn tại]{Style.RESET_ALL}" if exists else f"{Fore.RED}[Không tồn tại]{Style.RESET_ALL}"
        print(f"{Fore.GREEN}{key}{Style.RESET_ALL}: {Fore.CYAN}{path}{Style.RESET_ALL} {status}")

def show_system_info():
    """Hiển thị thông tin hệ thống"""
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{EMOJI['INFO']} Thông tin hệ thống:{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    
    # Thông tin hệ điều hành
    print(f"{Fore.GREEN}Hệ điều hành:{Style.RESET_ALL} {Fore.CYAN}{platform.system()} {platform.release()}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Phiên bản:{Style.RESET_ALL} {Fore.CYAN}{platform.version()}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Kiến trúc:{Style.RESET_ALL} {Fore.CYAN}{platform.machine()}{Style.RESET_ALL}")
    
    # Thông tin Python
    print(f"{Fore.GREEN}Python:{Style.RESET_ALL} {Fore.CYAN}{platform.python_version()}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Đường dẫn Python:{Style.RESET_ALL} {Fore.CYAN}{sys.executable}{Style.RESET_ALL}")
    
    # Thông tin người dùng
    print(f"{Fore.GREEN}Tên máy tính:{Style.RESET_ALL} {Fore.CYAN}{platform.node()}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Thư mục người dùng:{Style.RESET_ALL} {Fore.CYAN}{os.path.expanduser('~')}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Thư mục Documents:{Style.RESET_ALL} {Fore.CYAN}{get_user_documents_path()}{Style.RESET_ALL}")

def check_cursor_files():
    """Kiểm tra các file quan trọng của Cursor"""
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{EMOJI['FILE']} Kiểm tra file Cursor:{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    
    paths = get_cursor_paths()
    if not paths:
        print(f"{Fore.YELLOW}{EMOJI['WARNING']} Không tìm thấy đường dẫn Cursor.{Style.RESET_ALL}")
        return
    
    # Kiểm tra file storage.json
    storage_path = paths.get('storage_path', '')
    if storage_path and os.path.exists(storage_path):
        try:
            # Lấy thông tin file
            stat = os.stat(storage_path)
            print(f"{Fore.GREEN}{EMOJI['INFO']} File storage.json:{Style.RESET_ALL}")
            print(f"  {Fore.GREEN}Đường dẫn:{Style.RESET_ALL} {Fore.CYAN}{storage_path}{Style.RESET_ALL}")
            print(f"  {Fore.GREEN}Kích thước:{Style.RESET_ALL} {Fore.CYAN}{stat.st_size} bytes{Style.RESET_ALL}")
            print(f"  {Fore.GREEN}Quyền truy cập:{Style.RESET_ALL} {Fore.CYAN}{oct(stat.st_mode & 0o777)}{Style.RESET_ALL}")
            
            # Kiểm tra quyền đọc/ghi
            if os.access(storage_path, os.R_OK | os.W_OK):
                print(f"  {Fore.GREEN}Quyền đọc/ghi:{Style.RESET_ALL} {Fore.GREEN}Có{Style.RESET_ALL}")
            else:
                print(f"  {Fore.GREEN}Quyền đọc/ghi:{Style.RESET_ALL} {Fore.RED}Không{Style.RESET_ALL}")
                print(f"  {Fore.YELLOW}{EMOJI['WARNING']} Không có quyền đọc/ghi file storage.json.{Style.RESET_ALL}")
            
            # Thử đọc file để kiểm tra nội dung
            try:
                with open(storage_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not content.strip():
                        print(f"  {Fore.YELLOW}{EMOJI['WARNING']} File storage.json trống.{Style.RESET_ALL}")
                    else:
                        print(f"  {Fore.GREEN}{EMOJI['SUCCESS']} File storage.json hợp lệ và có dữ liệu.{Style.RESET_ALL}")
            except Exception as e:
                print(f"  {Fore.RED}{EMOJI['ERROR']} Lỗi khi đọc file storage.json: {str(e)}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} Lỗi khi kiểm tra file storage.json: {str(e)}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}{EMOJI['WARNING']} Không tìm thấy file storage.json.{Style.RESET_ALL}")
    
    # Kiểm tra file SQLite
    sqlite_path = paths.get('sqlite_path', '')
    if sqlite_path and os.path.exists(sqlite_path):
        try:
            # Lấy thông tin file
            stat = os.stat(sqlite_path)
            print(f"\n{Fore.GREEN}{EMOJI['INFO']} File SQLite:{Style.RESET_ALL}")
            print(f"  {Fore.GREEN}Đường dẫn:{Style.RESET_ALL} {Fore.CYAN}{sqlite_path}{Style.RESET_ALL}")
            print(f"  {Fore.GREEN}Kích thước:{Style.RESET_ALL} {Fore.CYAN}{stat.st_size} bytes{Style.RESET_ALL}")
            print(f"  {Fore.GREEN}Quyền truy cập:{Style.RESET_ALL} {Fore.CYAN}{oct(stat.st_mode & 0o777)}{Style.RESET_ALL}")
            
            # Kiểm tra quyền đọc/ghi
            if os.access(sqlite_path, os.R_OK | os.W_OK):
                print(f"  {Fore.GREEN}Quyền đọc/ghi:{Style.RESET_ALL} {Fore.GREEN}Có{Style.RESET_ALL}")
            else:
                print(f"  {Fore.GREEN}Quyền đọc/ghi:{Style.RESET_ALL} {Fore.RED}Không{Style.RESET_ALL}")
                print(f"  {Fore.YELLOW}{EMOJI['WARNING']} Không có quyền đọc/ghi file SQLite.{Style.RESET_ALL}")
            
            # Thử kết nối đến cơ sở dữ liệu SQLite
            try:
                import sqlite3
                conn = sqlite3.connect(sqlite_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                conn.close()
                print(f"  {Fore.GREEN}{EMOJI['SUCCESS']} Kết nối đến cơ sở dữ liệu SQLite thành công.{Style.RESET_ALL}")
                print(f"  {Fore.GREEN}Số bảng:{Style.RESET_ALL} {Fore.CYAN}{len(tables)}{Style.RESET_ALL}")
            except Exception as e:
                print(f"  {Fore.RED}{EMOJI['ERROR']} Lỗi khi kết nối đến cơ sở dữ liệu SQLite: {str(e)}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} Lỗi khi kiểm tra file SQLite: {str(e)}{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.YELLOW}{EMOJI['WARNING']} Không tìm thấy file SQLite.{Style.RESET_ALL}")

def run():
    """Hàm chạy chính"""
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{EMOJI['SETTINGS']} Hiển thị cấu hình{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    
    # Hiển thị cấu hình
    config = get_config()
    print_config(config)
    
    # Hiển thị đường dẫn Cursor
    show_cursor_paths()
    
    # Hiển thị thông tin hệ thống
    show_system_info()
    
    # Kiểm tra các file quan trọng
    check_cursor_files()
    
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

if __name__ == "__main__":
    run()
