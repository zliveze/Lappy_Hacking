# features/reset_machine_id.py - Reset Machine ID của Cursor
import os
import uuid
import json
import sqlite3
import re
from core.utils import get_cursor_paths, backup_file, check_file_exists, is_cursor_running, kill_cursor_processes

def generate_new_machine_id():
    """Tạo Machine ID mới"""
    import hashlib

    # Tạo các ID theo chuẩn của Cursor
    dev_device_id = str(uuid.uuid4())
    machine_id = hashlib.sha256(os.urandom(32)).hexdigest()
    mac_machine_id = hashlib.sha512(os.urandom(64)).hexdigest()
    sqm_id = "{" + str(uuid.uuid4()).upper() + "}"

    return {
        "telemetry.devDeviceId": dev_device_id,
        "telemetry.macMachineId": mac_machine_id,
        "telemetry.machineId": machine_id,
        "telemetry.sqmId": sqm_id,
        "storage.serviceMachineId": dev_device_id,
    }

def check_cursor_version():
    """Kiểm tra phiên bản Cursor"""
    try:
        cursor_paths = get_cursor_paths()
        if not cursor_paths:
            return False, "Không thể lấy đường dẫn Cursor"

        # Tìm package.json trong các vị trí có thể
        app_path = cursor_paths.get('cursor_path', '')
        if not app_path:
            return False, "Không tìm thấy đường dẫn Cursor app"

        # Danh sách các đường dẫn có thể chứa package.json
        possible_paths = [
            os.path.join(app_path, 'package.json'),
            os.path.join(app_path, 'resources', 'app', 'package.json'),
            os.path.join(app_path, 'Contents', 'Resources', 'app', 'package.json'),  # macOS
            # Windows paths
            os.path.join(os.getenv("LOCALAPPDATA", ""), "Programs", "Cursor", "resources", "app", "package.json"),
            # Linux paths
            "/opt/Cursor/resources/app/package.json",
            "/usr/share/cursor/resources/app/package.json",
            os.path.expanduser("~/.local/share/cursor/resources/app/package.json")
        ]

        package_json_path = None
        for path in possible_paths:
            if os.path.exists(path):
                package_json_path = path
                break

        if not package_json_path:
            return False, f"Không tìm thấy package.json tại: {possible_paths[0]}"

        # Đọc version
        with open(package_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        version = data.get('version', '')
        if not version:
            return False, "Không tìm thấy thông tin version"

        # Kiểm tra version >= 0.45.0
        version_parts = version.split('.')
        if len(version_parts) >= 3:
            major, minor, patch = map(int, version_parts[:3])
            if (major, minor, patch) >= (0, 45, 0):
                return True, f"Phiên bản Cursor: {version} (>= 0.45.0)"
            else:
                return False, f"Phiên bản Cursor: {version} (< 0.45.0, không cần patch getMachineId)"

        return False, f"Định dạng version không hợp lệ: {version}"

    except Exception as e:
        return False, f"Lỗi kiểm tra version: {str(e)}"

def patch_get_machine_id():
    """Patch getMachineId function trong main.js"""
    try:
        cursor_paths = get_cursor_paths()
        if not cursor_paths:
            return False, "Không thể lấy đường dẫn Cursor"

        app_path = cursor_paths.get('cursor_path', '')

        # Danh sách các đường dẫn có thể chứa main.js
        possible_paths = [
            os.path.join(app_path, 'out', 'main.js'),
            os.path.join(app_path, 'resources', 'app', 'out', 'main.js'),
            os.path.join(app_path, 'Contents', 'Resources', 'app', 'out', 'main.js'),  # macOS
            # Windows paths
            os.path.join(os.getenv("LOCALAPPDATA", ""), "Programs", "Cursor", "resources", "app", "out", "main.js"),
            # Linux paths
            "/opt/Cursor/resources/app/out/main.js",
            "/usr/share/cursor/resources/app/out/main.js",
            os.path.expanduser("~/.local/share/cursor/resources/app/out/main.js")
        ]

        main_js_path = None
        for path in possible_paths:
            if os.path.exists(path):
                main_js_path = path
                break

        if not main_js_path:
            return False, f"Không tìm thấy main.js tại: {possible_paths[0]}"

        # Backup file trước
        backup_path = backup_file(main_js_path)
        if not backup_path:
            return False, "Không thể tạo backup main.js"

        # Đọc nội dung file
        with open(main_js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Pattern để patch getMachineId
        patterns = {
            r"async getMachineId\(\)\{return [^??]+\?\?([^}]+)\}": r"async getMachineId(){return \1}",
            r"async getMacMachineId\(\)\{return [^??]+\?\?([^}]+)\}": r"async getMacMachineId(){return \1}",
        }

        patched = False
        for pattern, replacement in patterns.items():
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                patched = True
                print(f"Đã patch pattern: {pattern}")

        if patched:
            # Ghi file đã patch
            with open(main_js_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, f"Đã patch getMachineId thành công (Backup: {backup_path})"
        else:
            return False, "Không tìm thấy pattern getMachineId để patch"

    except Exception as e:
        return False, f"Lỗi patch getMachineId: {str(e)}"

def reset_machine_id_in_storage(storage_path, new_ids):
    """Reset Machine ID trong storage.json"""
    try:
        if not check_file_exists(storage_path):
            return False, "File storage.json không tồn tại"

        # Backup file trước
        backup_path = backup_file(storage_path)
        if not backup_path:
            return False, "Không thể tạo backup file storage.json"

        # Đọc file hiện tại
        with open(storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Cập nhật tất cả các ID
        updated_count = 0
        for key, value in new_ids.items():
            old_value = data.get(key, "không có")
            data[key] = value
            updated_count += 1
            print(f"Đã cập nhật {key}: {old_value} -> {value}")

        # Lưu file
        if updated_count > 0:
            with open(storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True, f"Đã cập nhật {updated_count} Machine ID trong storage.json (Backup: {backup_path})"
        else:
            return False, "Không có Machine ID nào được cập nhật"

    except Exception as e:
        return False, f"Lỗi reset Machine ID trong storage.json: {str(e)}"

def reset_machine_id_in_sqlite(sqlite_path, new_ids):
    """Reset Machine ID trong SQLite database"""
    try:
        if not check_file_exists(sqlite_path):
            return False, "File SQLite không tồn tại"

        # Backup file trước
        backup_path = backup_file(sqlite_path)
        if not backup_path:
            return False, "Không thể tạo backup file SQLite"

        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()

        # Tạo bảng ItemTable nếu chưa tồn tại
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ItemTable (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        updated_count = 0

        # Cập nhật từng key
        for key, value in new_ids.items():
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO ItemTable (key, value)
                    VALUES (?, ?)
                """, (key, value))
                updated_count += 1
                print(f"Đã cập nhật {key}: {value}")
            except Exception as e:
                print(f"Lỗi cập nhật {key}: {str(e)}")

        conn.commit()
        conn.close()

        if updated_count > 0:
            return True, f"Đã cập nhật {updated_count} record trong SQLite (Backup: {backup_path})"
        else:
            return False, "Không tìm thấy Machine ID để thay thế trong SQLite"

    except Exception as e:
        return False, f"Lỗi reset Machine ID trong SQLite: {str(e)}"

def reset_machine_id_file(machine_id_path, new_machine_id):
    """Reset Machine ID file"""
    try:
        # Tạo thư mục nếu chưa tồn tại
        machine_id_dir = os.path.dirname(machine_id_path)
        if not os.path.exists(machine_id_dir):
            try:
                os.makedirs(machine_id_dir, exist_ok=True)
                print(f"Đã tạo thư mục: {machine_id_dir}")
            except Exception as e:
                return False, f"Không thể tạo thư mục {machine_id_dir}: {str(e)}"

        # Backup file nếu tồn tại
        if check_file_exists(machine_id_path):
            backup_path = backup_file(machine_id_path)
            if backup_path:
                print(f"Đã backup file machineId: {backup_path}")

        # Thử ghi file với các cách khác nhau
        try:
            # Cách 1: Ghi trực tiếp
            with open(machine_id_path, 'w', encoding='utf-8') as f:
                f.write(new_machine_id)
            return True, f"Đã tạo/cập nhật file machineId: {machine_id_path}"

        except PermissionError:
            # Cách 2: Thử thay đổi quyền file trước
            try:
                if os.path.exists(machine_id_path):
                    # Thử thay đổi quyền file
                    import stat
                    os.chmod(machine_id_path, stat.S_IWRITE | stat.S_IREAD)

                with open(machine_id_path, 'w', encoding='utf-8') as f:
                    f.write(new_machine_id)
                return True, f"Đã tạo/cập nhật file machineId (sau khi thay đổi quyền): {machine_id_path}"

            except Exception:
                # Cách 3: Thử xóa file cũ và tạo mới
                try:
                    if os.path.exists(machine_id_path):
                        os.remove(machine_id_path)

                    with open(machine_id_path, 'w', encoding='utf-8') as f:
                        f.write(new_machine_id)
                    return True, f"Đã tạo file machineId mới: {machine_id_path}"

                except Exception as e3:
                    return False, f"Lỗi quyền truy cập file machineId: {str(e3)}"

    except Exception as e:
        return False, f"Lỗi reset Machine ID file: {str(e)}"

def reset_machine_id():
    """Reset Machine ID chính"""
    try:
        # Kiểm tra Cursor có đang chạy không
        if is_cursor_running():
            print("Cursor đang chạy, đang tắt...")
            killed = kill_cursor_processes()
            if killed > 0:
                print(f"Đã tắt {killed} process Cursor")
                import time
                time.sleep(2)  # Đợi process tắt hoàn toàn
            else:
                return False, "Không thể tắt Cursor. Vui lòng tắt thủ công trước khi reset Machine ID"

        # Lấy đường dẫn Cursor
        cursor_paths = get_cursor_paths()
        if not cursor_paths:
            return False, "Không thể lấy đường dẫn Cursor"

        # Tạo các Machine ID mới
        new_ids = generate_new_machine_id()
        print(f"Đã tạo các Machine ID mới:")
        for key, value in new_ids.items():
            print(f"  {key}: {value}")

        results = []
        success_count = 0

        # Reset trong storage.json
        storage_path = cursor_paths.get('storage_path')
        if storage_path:
            success, message = reset_machine_id_in_storage(storage_path, new_ids)
            results.append(f"Storage: {message}")
            if success:
                success_count += 1

        # Reset trong SQLite
        sqlite_path = cursor_paths.get('sqlite_path')
        if sqlite_path:
            success, message = reset_machine_id_in_sqlite(sqlite_path, new_ids)
            results.append(f"SQLite: {message}")
            if success:
                success_count += 1

        # Reset Machine ID file (sử dụng devDeviceId)
        machine_id_path = cursor_paths.get('machine_id_path')
        if machine_id_path:
            dev_device_id = new_ids.get('telemetry.devDeviceId', str(uuid.uuid4()))
            success, message = reset_machine_id_file(machine_id_path, dev_device_id)
            results.append(f"File: {message}")
            if success:
                success_count += 1

        # Kiểm tra và patch getMachineId nếu cần
        version_ok, version_msg = check_cursor_version()
        results.append(f"Version Check: {version_msg}")

        if version_ok:
            print("Đang patch getMachineId function...")
            patch_success, patch_msg = patch_get_machine_id()
            results.append(f"Patch getMachineId: {patch_msg}")
            if patch_success:
                success_count += 1

        # Tổng kết
        if success_count > 0:
            result_message = f"Reset Machine ID thành công ({success_count} vị trí):\n" + "\n".join(results)
            return True, result_message
        else:
            result_message = f"Reset Machine ID thất bại:\n" + "\n".join(results)
            return False, result_message

    except Exception as e:
        return False, f"Lỗi reset Machine ID: {str(e)}"

def verify_machine_id_reset():
    """Kiểm tra Machine ID đã được reset chưa"""
    try:
        cursor_paths = get_cursor_paths()
        if not cursor_paths:
            return False, "Không thể lấy đường dẫn Cursor"
        
        machine_ids = []
        
        # Kiểm tra storage.json
        storage_path = cursor_paths.get('storage_path')
        if storage_path and check_file_exists(storage_path):
            with open(storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for key in ['telemetry.machineId', 'machineId', 'machine_id']:
                if key in data:
                    machine_ids.append(f"Storage.{key}: {data[key]}")
        
        # Kiểm tra Machine ID file
        machine_id_path = cursor_paths.get('machine_id_path')
        if machine_id_path and check_file_exists(machine_id_path):
            with open(machine_id_path, 'r', encoding='utf-8') as f:
                file_id = f.read().strip()
                machine_ids.append(f"File: {file_id}")
        
        if machine_ids:
            return True, "Machine ID hiện tại:\n" + "\n".join(machine_ids)
        else:
            return False, "Không tìm thấy Machine ID"
            
    except Exception as e:
        return False, f"Lỗi kiểm tra Machine ID: {str(e)}"
