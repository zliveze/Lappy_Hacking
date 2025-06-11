# features/reset_full_cursor.py - Reset toàn bộ Cursor
import os
import shutil
from core.utils import get_cursor_paths, backup_file, check_file_exists, check_directory_exists, is_cursor_running, kill_cursor_processes, create_directory
from datetime import datetime

def backup_cursor_data():
    """Tạo backup toàn bộ dữ liệu Cursor"""
    try:
        cursor_paths = get_cursor_paths()
        if not cursor_paths:
            return False, "Không thể lấy đường dẫn Cursor"
        
        # Tạo thư mục backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(os.path.expanduser("~"), "Documents", "LappyLab_Backups", f"cursor_full_backup_{timestamp}")
        create_directory(backup_dir)
        
        backup_results = []
        
        # Backup storage.json
        storage_path = cursor_paths.get('storage_path')
        if storage_path and check_file_exists(storage_path):
            backup_storage = os.path.join(backup_dir, "storage.json")
            shutil.copy2(storage_path, backup_storage)
            backup_results.append(f"✅ Backup storage.json: {backup_storage}")
        
        # Backup SQLite database
        sqlite_path = cursor_paths.get('sqlite_path')
        if sqlite_path and check_file_exists(sqlite_path):
            backup_sqlite = os.path.join(backup_dir, "state.vscdb")
            shutil.copy2(sqlite_path, backup_sqlite)
            backup_results.append(f"✅ Backup SQLite: {backup_sqlite}")
        
        # Backup machine ID
        machine_id_path = cursor_paths.get('machine_id_path')
        if machine_id_path and check_file_exists(machine_id_path):
            backup_machine_id = os.path.join(backup_dir, "machineId")
            shutil.copy2(machine_id_path, backup_machine_id)
            backup_results.append(f"✅ Backup machineId: {backup_machine_id}")
        
        # Backup settings
        config_path = cursor_paths.get('config_path')
        if config_path and check_file_exists(config_path):
            backup_config = os.path.join(backup_dir, "settings.json")
            shutil.copy2(config_path, backup_config)
            backup_results.append(f"✅ Backup settings.json: {backup_config}")
        
        if backup_results:
            return True, f"Backup thành công tại {backup_dir}:\n" + "\n".join(backup_results)
        else:
            return False, "Không có file nào để backup"
            
    except Exception as e:
        return False, f"Lỗi tạo backup: {str(e)}"

def delete_cursor_user_data():
    """Xóa dữ liệu người dùng Cursor"""
    try:
        cursor_paths = get_cursor_paths()
        if not cursor_paths:
            return False, "Không thể lấy đường dẫn Cursor"
        
        delete_results = []
        success_count = 0
        
        # Xóa storage.json
        storage_path = cursor_paths.get('storage_path')
        if storage_path and check_file_exists(storage_path):
            try:
                os.remove(storage_path)
                delete_results.append(f"✅ Đã xóa storage.json: {storage_path}")
                success_count += 1
            except Exception as e:
                delete_results.append(f"❌ Lỗi xóa storage.json: {str(e)}")
        else:
            delete_results.append(f"ℹ️ storage.json không tồn tại: {storage_path}")
        
        # Xóa SQLite database
        sqlite_path = cursor_paths.get('sqlite_path')
        if sqlite_path and check_file_exists(sqlite_path):
            try:
                os.remove(sqlite_path)
                delete_results.append(f"✅ Đã xóa SQLite: {sqlite_path}")
                success_count += 1
            except Exception as e:
                delete_results.append(f"❌ Lỗi xóa SQLite: {str(e)}")
        else:
            delete_results.append(f"ℹ️ SQLite không tồn tại: {sqlite_path}")
        
        # Xóa machine ID
        machine_id_path = cursor_paths.get('machine_id_path')
        if machine_id_path and check_file_exists(machine_id_path):
            try:
                os.remove(machine_id_path)
                delete_results.append(f"✅ Đã xóa machineId: {machine_id_path}")
                success_count += 1
            except Exception as e:
                delete_results.append(f"❌ Lỗi xóa machineId: {str(e)}")
        else:
            delete_results.append(f"ℹ️ machineId không tồn tại: {machine_id_path}")
        
        # Xóa settings
        config_path = cursor_paths.get('config_path')
        if config_path and check_file_exists(config_path):
            try:
                os.remove(config_path)
                delete_results.append(f"✅ Đã xóa settings.json: {config_path}")
                success_count += 1
            except Exception as e:
                delete_results.append(f"❌ Lỗi xóa settings.json: {str(e)}")
        else:
            delete_results.append(f"ℹ️ settings.json không tồn tại: {config_path}")
        
        return success_count > 0, delete_results
        
    except Exception as e:
        return False, [f"❌ Lỗi xóa dữ liệu người dùng: {str(e)}"]

def reset_full_cursor():
    """Reset toàn bộ Cursor"""
    try:
        # Kiểm tra Cursor có đang chạy không
        if is_cursor_running():
            print("Cursor đang chạy, đang tắt...")
            killed = kill_cursor_processes()
            if killed > 0:
                print(f"Đã tắt {killed} process Cursor")
                import time
                time.sleep(3)  # Đợi process tắt hoàn toàn
            else:
                return False, "Không thể tắt Cursor. Vui lòng tắt thủ công trước khi reset"
        
        all_results = []
        total_success = 0
        
        # 1. Tạo backup trước
        print("Đang tạo backup...")
        success, message = backup_cursor_data()
        all_results.append(f"BACKUP: {message}")
        if success:
            total_success += 1
        
        # 2. Xóa dữ liệu người dùng
        print("Đang xóa dữ liệu người dùng...")
        success, results = delete_cursor_user_data()
        all_results.extend([f"USER DATA: {result}" for result in results])
        if success:
            total_success += 1
        
        # Tổng kết
        if total_success > 0:
            result_message = f"Reset toàn bộ Cursor thành công ({total_success} bước):\n" + "\n".join(all_results)
            result_message += "\n\n⚠️ Lưu ý: Cursor sẽ như mới cài đặt khi khởi động lại."
            return True, result_message
        else:
            result_message = f"Reset toàn bộ Cursor thất bại:\n" + "\n".join(all_results)
            return False, result_message
            
    except Exception as e:
        return False, f"Lỗi reset toàn bộ Cursor: {str(e)}"
