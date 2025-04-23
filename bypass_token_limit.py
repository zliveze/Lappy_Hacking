import os
import shutil
import platform
import tempfile
import re
from colorama import Fore, Style, init
from utils import get_cursor_paths
from config import EMOJI, get_config

# Khởi tạo colorama
init()

def get_workbench_cursor_path():
    """Lấy đường dẫn đến file workbench.desktop.main.js của Cursor"""
    paths = get_cursor_paths()
    cursor_path = paths.get('cursor_path', '')

    if not cursor_path or not os.path.exists(cursor_path):
        return None

    if platform.system() == "Windows":
        return os.path.join(cursor_path, "out\\vs\\workbench\\workbench.desktop.main.js")
    else:
        return os.path.join(cursor_path, "out/vs/workbench/workbench.desktop.main.js")

def modify_workbench_js():
    """Sửa đổi file workbench.desktop.main.js để bypass giới hạn token"""
    try:
        # Lấy đường dẫn đến file workbench.desktop.main.js
        workbench_path = get_workbench_cursor_path()

        if not workbench_path or not os.path.exists(workbench_path):
            print(f"{Fore.RED}{EMOJI['ERROR']} Không tìm thấy file workbench.desktop.main.js.{Style.RESET_ALL}")
            return False

        print(f"{Fore.CYAN}{EMOJI['FILE']} Đã tìm thấy workbench.desktop.main.js: {workbench_path}{Style.RESET_ALL}")

        # Lưu thông tin về file gốc
        original_stat = os.stat(workbench_path)
        original_mode = original_stat.st_mode

        # Tạo file tạm thời
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", errors="ignore", delete=False) as tmp_file:
            # Đọc nội dung file gốc
            with open(workbench_path, "r", encoding="utf-8", errors="ignore") as main_file:
                content = main_file.read()

            # Các mẫu cần thay thế
            patterns = {
                # Bypass giới hạn token
                r'async getEffectiveTokenLimit\(e\)\{const n=e\.modelName;if\(!n\)return 2e5;': r'async getEffectiveTokenLimit(e){return 9000000;const n=e.modelName;if(!n)return 9e5;',

                # Thêm Pro
                r'var DWr=ne\("<div class=settings__item_description>You are currently signed in with <strong></strong>"\);': r'var DWr=ne("<div class=settings__item_description>You are currently signed in with <strong></strong>. <h1>Pro</h1>");',

                # Ẩn thông báo
                r'notifications-toasts': r'notifications-toasts hidden'
            }

            # Thực hiện thay thế
            for old_pattern, new_pattern in patterns.items():
                content = content.replace(old_pattern, new_pattern)

            # Ghi vào file tạm thời
            tmp_file.write(content)
            tmp_path = tmp_file.name

        # Tạo backup
        backup_path = workbench_path + ".backup"
        shutil.copy2(workbench_path, backup_path)
        print(f"{Fore.GREEN}{EMOJI['BACKUP']} Đã tạo backup tại: {backup_path}{Style.RESET_ALL}")

        # Thay thế file gốc bằng file đã sửa
        with open(tmp_path, 'rb') as src_file:
            with open(workbench_path, 'wb') as dst_file:
                dst_file.write(src_file.read())
        os.chmod(workbench_path, original_mode)

        # Xóa file tạm thời
        os.unlink(tmp_path)

        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Đã bypass giới hạn token thành công!{Style.RESET_ALL}")
        return True

    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} Lỗi khi sửa đổi file: {str(e)}{Style.RESET_ALL}")
        if "tmp_path" in locals():
            try:
                os.unlink(tmp_path)
            except:
                pass
        return False

def run():
    """Hàm chạy chính"""
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{EMOJI['RESET']} Bypass giới hạn token{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

    modify_workbench_js()

    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

if __name__ == "__main__":
    run()
