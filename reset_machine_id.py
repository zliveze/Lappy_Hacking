import os
import sys
import json
import shutil
import tempfile
import platform
import uuid
import hashlib
import re
import sqlite3
from colorama import Fore, Style, init
from utils import (
    get_cursor_machine_id_path,
    get_cursor_paths,
    generate_new_machine_id,
    update_windows_machine_guid,
    update_windows_machine_id,
    is_admin
)
from config import EMOJI, get_config

# Khởi tạo colorama
init()

class MachineIDResetter:
    def __init__(self):
        """Khởi tạo đối tượng MachineIDResetter"""
        self.config = get_config()

    def reset_machine_ids(self):
        """Reset tất cả machine ID"""
        try:
            print(f"{Fore.CYAN}{EMOJI['INFO']} Đang bắt đầu quá trình reset Machine ID...{Style.RESET_ALL}")

            # Kiểm tra quyền admin trên Windows
            if platform.system() == "Windows" and not is_admin():
                print(f"{Fore.YELLOW}{EMOJI['WARNING']} Một số thao tác có thể yêu cầu quyền admin.{Style.RESET_ALL}")

            # Tạo ID mới
            new_ids = generate_new_machine_id()

            # Cập nhật file machineId
            self.update_machine_id_file(new_ids["telemetry.devDeviceId"])

            # Cập nhật file storage.json
            self.update_storage_json(new_ids)

            # Cập nhật cơ sở dữ liệu SQLite
            self.update_sqlite_db(new_ids)

            # Cập nhật ID hệ thống
            self.update_system_ids(new_ids)

            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Reset Machine ID thành công!{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} Lỗi khi reset Machine ID: {str(e)}{Style.RESET_ALL}")
            return False

    def update_machine_id_file(self, new_id):
        """Cập nhật file machineId"""
        try:
            machine_id_path = get_cursor_machine_id_path()

            if not machine_id_path or not os.path.exists(os.path.dirname(machine_id_path)):
                print(f"{Fore.YELLOW}{EMOJI['WARNING']} Không tìm thấy thư mục Cursor.{Style.RESET_ALL}")
                return False

            # Tạo backup nếu file đã tồn tại
            if os.path.exists(machine_id_path):
                backup_path = machine_id_path + ".backup"
                shutil.copy2(machine_id_path, backup_path)
                print(f"{Fore.GREEN}{EMOJI['BACKUP']} Đã tạo backup tại: {backup_path}{Style.RESET_ALL}")

            # Ghi ID mới vào file
            with open(machine_id_path, "w") as f:
                f.write(new_id)

            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Đã cập nhật file machineId.{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} Lỗi khi cập nhật file machineId: {str(e)}{Style.RESET_ALL}")
            return False

    def update_storage_json(self, new_ids):
        """Cập nhật file storage.json"""
        try:
            paths = get_cursor_paths()
            storage_path = paths.get('storage_path', '')

            if not storage_path or not os.path.exists(storage_path):
                print(f"{Fore.YELLOW}{EMOJI['WARNING']} Không tìm thấy file storage.json.{Style.RESET_ALL}")
                return False

            # Tạo backup
            backup_path = storage_path + ".backup"
            shutil.copy2(storage_path, backup_path)
            print(f"{Fore.GREEN}{EMOJI['BACKUP']} Đã tạo backup tại: {backup_path}{Style.RESET_ALL}")

            # Đọc file storage.json
            with open(storage_path, "r", encoding="utf-8") as f:
                storage_data = json.load(f)

            # Cập nhật các ID
            for key, value in new_ids.items():
                if key in storage_data:
                    storage_data[key] = value

            # Ghi lại file
            with open(storage_path, "w", encoding="utf-8") as f:
                json.dump(storage_data, f, indent=2)

            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Đã cập nhật file storage.json.{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} Lỗi khi cập nhật file storage.json: {str(e)}{Style.RESET_ALL}")
            return False

    def update_sqlite_db(self, new_ids):
        """Cập nhật cơ sở dữ liệu SQLite"""
        try:
            paths = get_cursor_paths()
            sqlite_path = paths.get('sqlite_path', '')

            if not sqlite_path or not os.path.exists(sqlite_path):
                print(f"{Fore.YELLOW}{EMOJI['WARNING']} Không tìm thấy file SQLite.{Style.RESET_ALL}")
                return False

            # Tạo backup
            backup_path = sqlite_path + ".backup"
            shutil.copy2(sqlite_path, backup_path)
            print(f"{Fore.GREEN}{EMOJI['BACKUP']} Đã tạo backup tại: {backup_path}{Style.RESET_ALL}")

            # Kết nối đến cơ sở dữ liệu
            conn = sqlite3.connect(sqlite_path)
            cursor = conn.cursor()

            # Cập nhật các ID trong bảng ItemTable
            for key, value in new_ids.items():
                cursor.execute(
                    "UPDATE ItemTable SET value = ? WHERE key = ?",
                    (json.dumps(value), key)
                )

            # Lưu thay đổi và đóng kết nối
            conn.commit()
            conn.close()

            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Đã cập nhật cơ sở dữ liệu SQLite.{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} Lỗi khi cập nhật cơ sở dữ liệu SQLite: {str(e)}{Style.RESET_ALL}")
            return False

    def update_system_ids(self, new_ids):
        """Cập nhật ID hệ thống"""
        try:
            print(f"{Fore.CYAN}{EMOJI['INFO']} Đang cập nhật ID hệ thống...{Style.RESET_ALL}")

            if platform.system() == "Windows":
                # Cập nhật Machine GUID
                if update_windows_machine_guid():
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Đã cập nhật Windows Machine GUID.{Style.RESET_ALL}")

                # Cập nhật Machine ID
                if update_windows_machine_id():
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Đã cập nhật Windows Machine ID.{Style.RESET_ALL}")

            return True
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} Lỗi khi cập nhật ID hệ thống: {str(e)}{Style.RESET_ALL}")
            return False

def run():
    """Hàm chạy chính"""
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{EMOJI['RESET']} Reset Machine ID{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

    resetter = MachineIDResetter()
    resetter.reset_machine_ids()

    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

if __name__ == "__main__":
    run()
