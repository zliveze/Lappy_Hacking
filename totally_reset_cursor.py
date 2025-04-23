import os
import sys
import shutil
import platform
import tempfile
import re
from colorama import Fore, Style, init
from utils import get_cursor_paths, is_admin
from config import EMOJI, get_config
from reset_machine_id import MachineIDResetter
from bypass_version import bypass_version
from bypass_token_limit import modify_workbench_js

# Khởi tạo colorama
init()

def patch_cursor_get_machine_id():
    """Patch hàm getMachineId của Cursor"""
    try:
        print(f"{Fore.CYAN}{EMOJI['INFO']} Đang bắt đầu patch getMachineId...{Style.RESET_ALL}")

        # Lấy đường dẫn
        paths = get_cursor_paths()
        cursor_path = paths.get('cursor_path', '')

        if not cursor_path or not os.path.exists(cursor_path):
            print(f"{Fore.RED}{EMOJI['ERROR']} Không tìm thấy thư mục Cursor.{Style.RESET_ALL}")
            return False

        # Đường dẫn đến file main.js (Đã sửa theo bản gốc)
        if platform.system() == "Windows":
            main_path = os.path.join(cursor_path, "out\\main.js")
        else:
            main_path = os.path.join(cursor_path, "out/main.js")

        # Kiểm tra quyền truy cập file
        if not os.path.isfile(main_path):
            print(f"{Fore.RED}{EMOJI['ERROR']} Không tìm thấy file: {main_path}{Style.RESET_ALL}")
            return False

        if not os.access(main_path, os.W_OK):
            print(f"{Fore.RED}{EMOJI['ERROR']} Không có quyền ghi file: {main_path}{Style.RESET_ALL}")
            return False

        # Lưu thông tin về file gốc
        original_stat = os.stat(main_path)
        original_mode = original_stat.st_mode

        # Tạo file tạm thời
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", errors="ignore", delete=False) as tmp_file:
            # Đọc nội dung file gốc
            with open(main_path, "r", encoding="utf-8", errors="ignore") as main_file:
                content = main_file.read()

            # Các mẫu cần thay thế
            patterns = {
                r"async getMachineId\(\)\{return [^??]+\?\?([^}]+)\}": r"async getMachineId(){return \1}",
                r"async getMacMachineId\(\)\{return [^??]+\?\?([^}]+)\}": r"async getMacMachineId(){return \1}",
            }

            # Thực hiện thay thế
            for pattern, replacement in patterns.items():
                content = re.sub(pattern, replacement, content)

            # Ghi vào file tạm thời
            tmp_file.write(content)
            tmp_path = tmp_file.name

        # Tạo backup
        backup_path = main_path + ".backup"
        shutil.copy2(main_path, backup_path)
        print(f"{Fore.GREEN}{EMOJI['BACKUP']} Đã tạo backup tại: {backup_path}{Style.RESET_ALL}")

        # Thay thế file gốc bằng file đã sửa
        with open(tmp_path, 'rb') as src_file:
            with open(main_path, 'wb') as dst_file:
                dst_file.write(src_file.read())
        os.chmod(main_path, original_mode)

        # Xóa file tạm thời
        os.unlink(tmp_path)

        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Đã patch getMachineId thành công!{Style.RESET_ALL}")
        return True

    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} Lỗi khi patch getMachineId: {str(e)}{Style.RESET_ALL}")
        if "tmp_path" in locals():
            try:
                os.unlink(tmp_path)
            except:
                pass
        return False

def check_cursor_version():
    """Kiểm tra phiên bản Cursor"""
    try:
        # Lấy đường dẫn đến file product.json
        paths = get_cursor_paths()
        product_json_path = paths.get('product_json_path', '')

        if not product_json_path or not os.path.exists(product_json_path):
            print(f"{Fore.RED}{EMOJI['ERROR']} Không tìm thấy file product.json.{Style.RESET_ALL}")
            return False

        # Đọc file product.json
        import json
        with open(product_json_path, "r", encoding="utf-8") as f:
            product_data = json.load(f)

        # Lấy phiên bản hiện tại
        current_version = product_data.get("version", "0.0.0")

        # So sánh với phiên bản 0.45.0
        from bypass_version import compare_versions
        return compare_versions(current_version, "0.45.0") >= 0

    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} Lỗi khi kiểm tra phiên bản Cursor: {str(e)}{Style.RESET_ALL}")
        return False

def totally_reset_cursor():
    """Reset hoàn toàn Cursor"""
    try:
        print(f"{Fore.CYAN}{EMOJI['INFO']} Đang bắt đầu reset hoàn toàn Cursor...{Style.RESET_ALL}")

        # Kiểm tra quyền admin trên Windows
        if platform.system() == "Windows" and not is_admin():
            print(f"{Fore.YELLOW}{EMOJI['WARNING']} Một số thao tác yêu cầu quyền admin. Vui lòng chạy lại với quyền admin.{Style.RESET_ALL}")
            return False

        # 1. Reset Machine ID
        print(f"{Fore.CYAN}{EMOJI['INFO']} Bước 1: Reset Machine ID{Style.RESET_ALL}")
        resetter = MachineIDResetter()
        resetter.reset_machine_ids()

        # 2. Bypass kiểm tra phiên bản
        print(f"{Fore.CYAN}{EMOJI['INFO']} Bước 2: Bypass kiểm tra phiên bản{Style.RESET_ALL}")
        bypass_version()

        # 3. Bypass giới hạn token
        print(f"{Fore.CYAN}{EMOJI['INFO']} Bước 3: Bypass giới hạn token{Style.RESET_ALL}")
        modify_workbench_js()

        # 4. Kiểm tra phiên bản và patch getMachineId nếu cần
        greater_than_0_45 = check_cursor_version()
        if greater_than_0_45:
            print(f"{Fore.CYAN}{EMOJI['INFO']} Phát hiện phiên bản >= 0.45.0, đang patch getMachineId{Style.RESET_ALL}")
            patch_cursor_get_machine_id()
        else:
            print(f"{Fore.YELLOW}{EMOJI['INFO']} Phiên bản < 0.45.0, không cần patch getMachineId{Style.RESET_ALL}")

        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Đã reset hoàn toàn Cursor thành công!{Style.RESET_ALL}")
        return True

    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} Lỗi khi reset hoàn toàn Cursor: {str(e)}{Style.RESET_ALL}")
        return False

def run():
    """Hàm chạy chính"""
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{EMOJI['RESET']} Reset hoàn toàn Cursor{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

    totally_reset_cursor()

    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

if __name__ == "__main__":
    run()
