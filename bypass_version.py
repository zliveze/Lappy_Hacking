import os
import json
import shutil
import platform
import time
import traceback
from colorama import Fore, Style, init
from utils import get_cursor_paths
from config import EMOJI, get_config

# Khởi tạo colorama
init()

def compare_versions(version1, version2):
    """So sánh hai chuỗi phiên bản"""
    v1_parts = [int(x) for x in version1.split('.')]
    v2_parts = [int(x) for x in version2.split('.')]

    for i in range(max(len(v1_parts), len(v2_parts))):
        v1 = v1_parts[i] if i < len(v1_parts) else 0
        v2 = v2_parts[i] if i < len(v2_parts) else 0
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1

    return 0

def bypass_version():
    """Bypass kiểm tra phiên bản của Cursor bằng cách sửa đổi product.json"""
    try:
        print(f"\n{Fore.CYAN}{EMOJI['INFO']} Đang bắt đầu bypass kiểm tra phiên bản...{Style.RESET_ALL}")

        # Lấy đường dẫn đến file product.json
        paths = get_cursor_paths()
        product_json_path = paths.get('product_json_path', '')

        if not product_json_path or not os.path.exists(product_json_path):
            print(f"{Fore.RED}{EMOJI['ERROR']} Không tìm thấy file product.json.{Style.RESET_ALL}")
            return False

        print(f"{Fore.CYAN}{EMOJI['FILE']} Đã tìm thấy product.json: {product_json_path}{Style.RESET_ALL}")

        # Đọc file product.json
        with open(product_json_path, "r", encoding="utf-8", errors="ignore") as f:
            product_data = json.load(f)

        # Lấy phiên bản hiện tại
        current_version = product_data.get("version", "0.0.0")
        print(f"{Fore.CYAN}{EMOJI['VERSION']} Phiên bản hiện tại: {current_version}{Style.RESET_ALL}")

        # Kiểm tra xem phiên bản có cần được sửa đổi không
        if compare_versions(current_version, "0.46.0") < 0:
            # Tạo backup
            timestamp = time.strftime("%Y%m%d%H%M%S")
            backup_path = f"{product_json_path}.{timestamp}"
            shutil.copy2(product_json_path, backup_path)
            print(f"{Fore.GREEN}{EMOJI['BACKUP']} Đã tạo backup tại: {backup_path}{Style.RESET_ALL}")

            # Sửa đổi phiên bản
            new_version = "0.48.7"
            product_data["version"] = new_version

            # Ghi lại file
            with open(product_json_path, "w", encoding="utf-8", errors="ignore") as f:
                json.dump(product_data, f, indent=2)

            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Đã cập nhật phiên bản từ {current_version} lên {new_version}.{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.YELLOW}{EMOJI['INFO']} Không cần cập nhật. Phiên bản hiện tại {current_version} đã >= 0.46.0{Style.RESET_ALL}")
            return True

    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} Bypass phiên bản thất bại: {str(e)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{EMOJI['INFO']} Stack trace: {traceback.format_exc()}{Style.RESET_ALL}")
        return False

def run():
    """Hàm chạy chính"""
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{EMOJI['VERSION']} Bypass kiểm tra phiên bản{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

    bypass_version()

    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

if __name__ == "__main__":
    run()
