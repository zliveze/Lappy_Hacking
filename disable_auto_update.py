import os
import sys
import yaml
import shutil
import platform
import subprocess
import tempfile
from colorama import Fore, Style, init
from utils import get_cursor_paths, is_admin, get_user_documents_path
from config import EMOJI, get_config
from quit_cursor import quit_cursor
from admin_helper import create_admin_script, run_as_admin_powershell, create_disable_auto_update_script

# Khởi tạo colorama
init()

def create_dummy_update_yml(path):
    """Tạo file app-update.yml giả lập với cấu hình vô hiệu hóa cập nhật"""
    try:
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Tạo cấu hình vô hiệu hóa cập nhật
        update_data = {
            'autoUpdater': {
                'autoDownload': False,
                'autoInstallOnAppQuit': False
            }
        }

        # Ghi file
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(update_data, f)

        return True
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} Lỗi khi tạo file giả lập: {str(e)}{Style.RESET_ALL}")
        return False

def kill_cursor_processes():
    """Kết thúc tất cả tiến trình Cursor"""
    try:
        print(f"{Fore.CYAN}{EMOJI['INFO']} Đang kết thúc các tiến trình Cursor...{Style.RESET_ALL}")

        # Sử dụng module quit_cursor để đóng Cursor một cách an toàn
        if quit_cursor(timeout=10):
            return True

        # Nếu không thành công, thử sử dụng cách mạnh hơn
        if platform.system() == "Windows":
            try:
                subprocess.run(['taskkill', '/F', '/IM', 'Cursor.exe', '/T'], capture_output=True)
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Đã kết thúc các tiến trình Cursor.{Style.RESET_ALL}")
                return True
            except Exception as e:
                print(f"{Fore.RED}{EMOJI['ERROR']} Lỗi khi kết thúc tiến trình: {str(e)}{Style.RESET_ALL}")
                return False
        else:
            try:
                subprocess.run(['pkill', '-f', 'Cursor'], capture_output=True)
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Đã kết thúc các tiến trình Cursor.{Style.RESET_ALL}")
                return True
            except Exception as e:
                print(f"{Fore.RED}{EMOJI['ERROR']} Lỗi khi kết thúc tiến trình: {str(e)}{Style.RESET_ALL}")
                return False
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} Lỗi khi kết thúc tiến trình Cursor: {str(e)}{Style.RESET_ALL}")
        return False

def disable_auto_update():
    """Vô hiệu hóa tự động cập nhật của Cursor"""
    try:
        print(f"{Fore.CYAN}{EMOJI['INFO']} Đang bắt đầu vô hiệu hóa tự động cập nhật...{Style.RESET_ALL}")

        # 1. Kết thúc các tiến trình Cursor trước
        kill_cursor_processes()

        # Kiểm tra quyền admin trên Windows
        if platform.system() == "Windows":
            if not is_admin():
                print(f"{Fore.YELLOW}{EMOJI['WARNING']} Không có quyền admin. Thử sử dụng script PowerShell với quyền admin...{Style.RESET_ALL}")

                # Lấy đường dẫn
                paths = get_cursor_paths()
                update_yml_path = paths.get('update_yml_path', '')
                updater_path = paths.get('updater_path', '')

                if update_yml_path:
                    # Tạo script PowerShell để vô hiệu hóa tự động cập nhật
                    script_content = create_disable_auto_update_script(update_yml_path, updater_path)
                    script_path = create_admin_script(script_content, "disable_cursor_update.ps1")

                    if script_path and run_as_admin_powershell(script_path):
                        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Đã vô hiệu hóa tự động cập nhật thành công với quyền admin!{Style.RESET_ALL}")
                        return True
                    else:
                        print(f"{Fore.YELLOW}{EMOJI['WARNING']} Không thể chạy script với quyền admin. Sử dụng phương pháp thay thế.{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}{EMOJI['WARNING']} Không thể xác định đường dẫn file app-update.yml. Sử dụng phương pháp thay thế.{Style.RESET_ALL}")

        # Lấy đường dẫn đến file app-update.yml
        paths = get_cursor_paths()
        update_yml_path = paths.get('update_yml_path', '')

        if not update_yml_path:
            print(f"{Fore.YELLOW}{EMOJI['WARNING']} Không thể xác định đường dẫn file app-update.yml.{Style.RESET_ALL}")
            return False

        # Phương pháp 1: Thử sử dụng cách trực tiếp
        try:
            # Tạo backup nếu có thể
            if os.path.exists(update_yml_path):
                try:
                    backup_path = update_yml_path + ".backup"
                    shutil.copy2(update_yml_path, backup_path)
                    print(f"{Fore.GREEN}{EMOJI['BACKUP']} Đã tạo backup tại: {backup_path}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.YELLOW}{EMOJI['WARNING']} Không thể tạo backup: {str(e)}{Style.RESET_ALL}")

            # Đọc file hiện tại hoặc tạo mới nếu không tồn tại
            if os.path.exists(update_yml_path):
                with open(update_yml_path, "r", encoding="utf-8") as f:
                    update_data = yaml.safe_load(f) or {}
            else:
                update_data = {}

            # Vô hiệu hóa tự động cập nhật
            if 'autoUpdater' not in update_data:
                update_data['autoUpdater'] = {}

            update_data['autoUpdater']['autoDownload'] = False
            update_data['autoUpdater']['autoInstallOnAppQuit'] = False

            # Ghi lại file
            with open(update_yml_path, "w", encoding="utf-8") as f:
                yaml.dump(update_data, f)

            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Đã vô hiệu hóa tự động cập nhật thành công!{Style.RESET_ALL}")

            # Phương pháp 2: Vô hiệu hóa thư mục cursor-updater
            updater_path = paths.get('updater_path', '')
            if updater_path and os.path.exists(updater_path):
                try:
                    # Đổi tên thư mục
                    disabled_path = updater_path + ".disabled"
                    if os.path.exists(disabled_path):
                        shutil.rmtree(disabled_path)

                    shutil.move(updater_path, disabled_path)
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Đã vô hiệu hóa thư mục cursor-updater.{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.YELLOW}{EMOJI['WARNING']} Không thể vô hiệu hóa thư mục cursor-updater: {str(e)}{Style.RESET_ALL}")

            return True

        except PermissionError:
            print(f"{Fore.YELLOW}{EMOJI['WARNING']} Lỗi quyền truy cập. Thử phương pháp thay thế...{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW}{EMOJI['WARNING']} Lỗi khi sử dụng phương pháp trực tiếp: {str(e)}{Style.RESET_ALL}")

        # Phương pháp 3: Tạo file giả lập trong thư mục Documents
        try:
            # Tạo đường dẫn đến file giả lập trong thư mục Documents
            docs_path = get_user_documents_path()
            fake_update_yml_path = os.path.join(docs_path, ".lappy-lab", "app-update.yml")

            # Tạo file giả lập
            if create_dummy_update_yml(fake_update_yml_path):
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Đã tạo file giả lập tại: {fake_update_yml_path}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{EMOJI['INFO']} Bạn có thể cần sao chép file này vào {update_yml_path} với quyền admin.{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}{EMOJI['ERROR']} Không thể tạo file giả lập.{Style.RESET_ALL}")
                return False

        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} Lỗi khi vô hiệu hóa tự động cập nhật: {str(e)}{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} Lỗi khi vô hiệu hóa tự động cập nhật: {str(e)}{Style.RESET_ALL}")
        return False

def run():
    """Hàm chạy chính"""
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{EMOJI['SETTINGS']} Vô hiệu hóa tự động cập nhật{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

    disable_auto_update()

    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

if __name__ == "__main__":
    run()
