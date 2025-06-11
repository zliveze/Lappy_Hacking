# features/disable_auto_update.py - Tắt tự động cập nhật Cursor
import os
import json
import platform
from core.utils import get_cursor_paths, backup_file, check_file_exists, check_directory_exists, is_cursor_running, kill_cursor_processes

def disable_auto_update_windows():
    """Tắt tự động cập nhật trên Windows"""
    try:
        results = []
        success_count = 0
        
        # 1. Xóa/đổi tên thư mục updater
        localappdata = os.getenv("LOCALAPPDATA")
        updater_path = os.path.join(localappdata, "cursor-updater")
        
        if check_directory_exists(updater_path):
            try:
                # Đổi tên thư mục updater
                disabled_path = f"{updater_path}_disabled"
                if os.path.exists(disabled_path):
                    import shutil
                    shutil.rmtree(disabled_path)
                os.rename(updater_path, disabled_path)
                results.append(f"✅ Đã vô hiệu hóa thư mục updater: {updater_path}")
                success_count += 1
            except Exception as e:
                results.append(f"❌ Lỗi vô hiệu hóa updater: {str(e)}")
        else:
            results.append(f"ℹ️ Thư mục updater không tồn tại: {updater_path}")
        
        # 2. Chỉnh sửa app-update.yml
        cursor_path = os.path.join(localappdata, "Programs", "Cursor")
        update_yml_path = os.path.join(cursor_path, "resources", "app-update.yml")
        
        if check_file_exists(update_yml_path):
            try:
                # Backup file
                backup_path = backup_file(update_yml_path)
                
                # Đọc và chỉnh sửa
                with open(update_yml_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Thay thế URL update
                modified_content = content.replace(
                    "https://download.cursor.sh/",
                    "https://localhost/disabled/"
                )
                
                # Ghi lại file
                with open(update_yml_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                
                results.append(f"✅ Đã chỉnh sửa app-update.yml (Backup: {backup_path})")
                success_count += 1
            except Exception as e:
                results.append(f"❌ Lỗi chỉnh sửa app-update.yml: {str(e)}")
        else:
            results.append(f"ℹ️ File app-update.yml không tồn tại: {update_yml_path}")
        
        # 3. Chỉnh sửa product.json
        product_json_path = os.path.join(cursor_path, "resources", "app", "product.json")
        
        if check_file_exists(product_json_path):
            try:
                # Backup file
                backup_path = backup_file(product_json_path)
                
                # Đọc và chỉnh sửa
                with open(product_json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Vô hiệu hóa update
                if 'updateUrl' in data:
                    data['updateUrl'] = "https://localhost/disabled/"
                if 'updateChannel' in data:
                    data['updateChannel'] = "disabled"
                if 'enableUpdateCheck' in data:
                    data['enableUpdateCheck'] = False
                
                # Ghi lại file
                with open(product_json_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                results.append(f"✅ Đã chỉnh sửa product.json (Backup: {backup_path})")
                success_count += 1
            except Exception as e:
                results.append(f"❌ Lỗi chỉnh sửa product.json: {str(e)}")
        else:
            results.append(f"ℹ️ File product.json không tồn tại: {product_json_path}")
        
        return success_count > 0, results
        
    except Exception as e:
        return False, [f"❌ Lỗi tắt auto update Windows: {str(e)}"]

def disable_auto_update_macos():
    """Tắt tự động cập nhật trên macOS"""
    try:
        results = []
        success_count = 0
        
        # 1. Xóa/đổi tên thư mục updater
        home = os.path.expanduser("~")
        updater_path = os.path.join(home, "Library", "Application Support", "cursor-updater")
        
        if check_directory_exists(updater_path):
            try:
                disabled_path = f"{updater_path}_disabled"
                if os.path.exists(disabled_path):
                    import shutil
                    shutil.rmtree(disabled_path)
                os.rename(updater_path, disabled_path)
                results.append(f"✅ Đã vô hiệu hóa thư mục updater: {updater_path}")
                success_count += 1
            except Exception as e:
                results.append(f"❌ Lỗi vô hiệu hóa updater: {str(e)}")
        else:
            results.append(f"ℹ️ Thư mục updater không tồn tại: {updater_path}")
        
        # 2. Chỉnh sửa app-update.yml
        update_yml_path = "/Applications/Cursor.app/Contents/Resources/app-update.yml"
        
        if check_file_exists(update_yml_path):
            try:
                backup_path = backup_file(update_yml_path)
                
                with open(update_yml_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                modified_content = content.replace(
                    "https://download.cursor.sh/",
                    "https://localhost/disabled/"
                )
                
                with open(update_yml_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                
                results.append(f"✅ Đã chỉnh sửa app-update.yml (Backup: {backup_path})")
                success_count += 1
            except Exception as e:
                results.append(f"❌ Lỗi chỉnh sửa app-update.yml: {str(e)}")
        else:
            results.append(f"ℹ️ File app-update.yml không tồn tại: {update_yml_path}")
        
        # 3. Chỉnh sửa product.json
        product_json_path = "/Applications/Cursor.app/Contents/Resources/app/product.json"
        
        if check_file_exists(product_json_path):
            try:
                backup_path = backup_file(product_json_path)
                
                with open(product_json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if 'updateUrl' in data:
                    data['updateUrl'] = "https://localhost/disabled/"
                if 'updateChannel' in data:
                    data['updateChannel'] = "disabled"
                if 'enableUpdateCheck' in data:
                    data['enableUpdateCheck'] = False
                
                with open(product_json_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                results.append(f"✅ Đã chỉnh sửa product.json (Backup: {backup_path})")
                success_count += 1
            except Exception as e:
                results.append(f"❌ Lỗi chỉnh sửa product.json: {str(e)}")
        else:
            results.append(f"ℹ️ File product.json không tồn tại: {product_json_path}")
        
        return success_count > 0, results
        
    except Exception as e:
        return False, [f"❌ Lỗi tắt auto update macOS: {str(e)}"]

def disable_auto_update_linux():
    """Tắt tự động cập nhật trên Linux"""
    try:
        results = []
        success_count = 0
        
        home = os.path.expanduser("~")
        
        # 1. Xóa/đổi tên thư mục updater
        updater_path = os.path.join(home, ".cursor-updater")
        
        if check_directory_exists(updater_path):
            try:
                disabled_path = f"{updater_path}_disabled"
                if os.path.exists(disabled_path):
                    import shutil
                    shutil.rmtree(disabled_path)
                os.rename(updater_path, disabled_path)
                results.append(f"✅ Đã vô hiệu hóa thư mục updater: {updater_path}")
                success_count += 1
            except Exception as e:
                results.append(f"❌ Lỗi vô hiệu hóa updater: {str(e)}")
        else:
            results.append(f"ℹ️ Thư mục updater không tồn tại: {updater_path}")
        
        # 2. Tìm và chỉnh sửa các file cấu hình Cursor
        cursor_dirs = [
            os.path.join(home, ".config", "Cursor"),
            os.path.join(home, ".config", "cursor"),
            "/opt/cursor",
            "/usr/share/cursor"
        ]
        
        for cursor_dir in cursor_dirs:
            if check_directory_exists(cursor_dir):
                # Chỉnh sửa product.json nếu có
                product_json_path = os.path.join(cursor_dir, "resources", "app", "product.json")
                if check_file_exists(product_json_path):
                    try:
                        backup_path = backup_file(product_json_path)
                        
                        with open(product_json_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        if 'updateUrl' in data:
                            data['updateUrl'] = "https://localhost/disabled/"
                        if 'updateChannel' in data:
                            data['updateChannel'] = "disabled"
                        if 'enableUpdateCheck' in data:
                            data['enableUpdateCheck'] = False
                        
                        with open(product_json_path, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)
                        
                        results.append(f"✅ Đã chỉnh sửa {product_json_path} (Backup: {backup_path})")
                        success_count += 1
                    except Exception as e:
                        results.append(f"❌ Lỗi chỉnh sửa {product_json_path}: {str(e)}")
        
        return success_count > 0, results
        
    except Exception as e:
        return False, [f"❌ Lỗi tắt auto update Linux: {str(e)}"]

def disable_auto_update_in_settings():
    """Tắt auto update trong settings của Cursor"""
    try:
        cursor_paths = get_cursor_paths()
        config_path = cursor_paths.get('config_path')
        
        if not config_path or not check_file_exists(config_path):
            return False, "File settings.json không tồn tại"
        
        # Backup file
        backup_path = backup_file(config_path)
        
        # Đọc settings hiện tại
        with open(config_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        # Tắt auto update
        settings['update.mode'] = 'none'
        settings['update.enableWindowsBackgroundUpdates'] = False
        settings['update.showReleaseNotes'] = False
        
        # Ghi lại settings
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        
        return True, f"Đã tắt auto update trong settings (Backup: {backup_path})"
        
    except Exception as e:
        return False, f"Lỗi tắt auto update trong settings: {str(e)}"

def disable_auto_update():
    """Tắt tự động cập nhật Cursor"""
    try:
        # Kiểm tra Cursor có đang chạy không
        if is_cursor_running():
            print("Cursor đang chạy, đang tắt...")
            killed = kill_cursor_processes()
            if killed > 0:
                print(f"Đã tắt {killed} process Cursor")
                import time
                time.sleep(2)
            else:
                return False, "Không thể tắt Cursor. Vui lòng tắt thủ công trước khi tắt auto update"
        
        all_results = []
        total_success = 0
        
        # Tắt auto update theo hệ điều hành
        system = platform.system()
        if system == "Windows":
            success, results = disable_auto_update_windows()
        elif system == "Darwin":
            success, results = disable_auto_update_macos()
        elif system == "Linux":
            success, results = disable_auto_update_linux()
        else:
            return False, f"Hệ điều hành {system} không được hỗ trợ"
        
        all_results.extend(results)
        if success:
            total_success += 1
        
        # Tắt auto update trong settings
        success, message = disable_auto_update_in_settings()
        all_results.append(message)
        if success:
            total_success += 1
        
        # Tổng kết
        if total_success > 0:
            result_message = f"Tắt auto update thành công ({total_success} phương pháp):\n" + "\n".join(all_results)
            return True, result_message
        else:
            result_message = f"Tắt auto update thất bại:\n" + "\n".join(all_results)
            return False, result_message
            
    except Exception as e:
        return False, f"Lỗi tắt auto update: {str(e)}"
