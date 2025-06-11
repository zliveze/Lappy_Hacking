# features/bypass_version_check.py - Bỏ qua kiểm tra phiên bản Cursor
import os
import json
import platform
from core.utils import get_cursor_paths, backup_file, check_file_exists, is_cursor_running, kill_cursor_processes

def modify_product_json():
    """Chỉnh sửa product.json để bỏ qua kiểm tra phiên bản"""
    try:
        system = platform.system()
        product_json_paths = []
        
        if system == "Windows":
            localappdata = os.getenv("LOCALAPPDATA")
            product_json_paths = [
                os.path.join(localappdata, "Programs", "Cursor", "resources", "app", "product.json")
            ]
        elif system == "Darwin":  # macOS
            product_json_paths = [
                "/Applications/Cursor.app/Contents/Resources/app/product.json"
            ]
        else:  # Linux
            home = os.path.expanduser("~")
            product_json_paths = [
                os.path.join(home, ".config", "Cursor", "resources", "app", "product.json"),
                os.path.join(home, ".config", "cursor", "resources", "app", "product.json"),
                "/opt/cursor/resources/app/product.json",
                "/usr/share/cursor/resources/app/product.json"
            ]
        
        results = []
        success_count = 0
        
        for product_json_path in product_json_paths:
            if check_file_exists(product_json_path):
                try:
                    # Backup file
                    backup_path = backup_file(product_json_path)
                    
                    # Đọc file hiện tại
                    with open(product_json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Chỉnh sửa để bỏ qua kiểm tra phiên bản
                    modifications = []
                    
                    # Tắt kiểm tra phiên bản
                    if 'enableVersionCheck' in data:
                        data['enableVersionCheck'] = False
                        modifications.append("enableVersionCheck = False")
                    else:
                        data['enableVersionCheck'] = False
                        modifications.append("Thêm enableVersionCheck = False")
                    
                    # Tắt kiểm tra tương thích
                    if 'enableCompatibilityCheck' in data:
                        data['enableCompatibilityCheck'] = False
                        modifications.append("enableCompatibilityCheck = False")
                    else:
                        data['enableCompatibilityCheck'] = False
                        modifications.append("Thêm enableCompatibilityCheck = False")
                    
                    # Tắt kiểm tra cập nhật bắt buộc
                    if 'enableMandatoryUpdate' in data:
                        data['enableMandatoryUpdate'] = False
                        modifications.append("enableMandatoryUpdate = False")
                    else:
                        data['enableMandatoryUpdate'] = False
                        modifications.append("Thêm enableMandatoryUpdate = False")
                    
                    # Đặt phiên bản tối thiểu thấp
                    if 'minimumVersion' in data:
                        data['minimumVersion'] = "0.0.1"
                        modifications.append("minimumVersion = 0.0.1")
                    else:
                        data['minimumVersion'] = "0.0.1"
                        modifications.append("Thêm minimumVersion = 0.0.1")
                    
                    # Tắt kiểm tra server
                    if 'enableServerVersionCheck' in data:
                        data['enableServerVersionCheck'] = False
                        modifications.append("enableServerVersionCheck = False")
                    else:
                        data['enableServerVersionCheck'] = False
                        modifications.append("Thêm enableServerVersionCheck = False")
                    
                    # Ghi lại file
                    with open(product_json_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    results.append(f"✅ Đã chỉnh sửa {product_json_path}")
                    results.append(f"   Backup: {backup_path}")
                    results.append(f"   Thay đổi: {', '.join(modifications)}")
                    success_count += 1
                    
                except Exception as e:
                    results.append(f"❌ Lỗi chỉnh sửa {product_json_path}: {str(e)}")
            else:
                results.append(f"ℹ️ File không tồn tại: {product_json_path}")
        
        return success_count > 0, results
        
    except Exception as e:
        return False, [f"❌ Lỗi modify product.json: {str(e)}"]

def modify_settings_json():
    """Chỉnh sửa settings.json để bỏ qua kiểm tra phiên bản"""
    try:
        cursor_paths = get_cursor_paths()
        config_path = cursor_paths.get('config_path')
        
        if not config_path:
            return False, ["ℹ️ Không tìm thấy đường dẫn settings.json"]
        
        results = []
        
        # Tạo file settings.json nếu chưa tồn tại
        if not check_file_exists(config_path):
            # Tạo thư mục nếu cần
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # Tạo settings mặc định
            default_settings = {
                "cursor.general.enableVersionCheck": False,
                "cursor.general.enableCompatibilityCheck": False,
                "cursor.general.enableMandatoryUpdate": False,
                "cursor.general.enableServerVersionCheck": False,
                "update.mode": "none",
                "update.enableWindowsBackgroundUpdates": False,
                "update.showReleaseNotes": False
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_settings, f, indent=2, ensure_ascii=False)
            
            results.append(f"✅ Đã tạo settings.json mới: {config_path}")
            return True, results
        
        # Backup file hiện tại
        backup_path = backup_file(config_path)
        
        # Đọc settings hiện tại
        with open(config_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        # Chỉnh sửa settings
        modifications = []
        
        # Tắt các kiểm tra phiên bản
        version_check_settings = {
            "cursor.general.enableVersionCheck": False,
            "cursor.general.enableCompatibilityCheck": False,
            "cursor.general.enableMandatoryUpdate": False,
            "cursor.general.enableServerVersionCheck": False,
            "update.mode": "none",
            "update.enableWindowsBackgroundUpdates": False,
            "update.showReleaseNotes": False
        }
        
        for key, value in version_check_settings.items():
            if key in settings:
                if settings[key] != value:
                    settings[key] = value
                    modifications.append(f"{key} = {value}")
            else:
                settings[key] = value
                modifications.append(f"Thêm {key} = {value}")
        
        # Ghi lại settings
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        
        results.append(f"✅ Đã chỉnh sửa settings.json")
        results.append(f"   Backup: {backup_path}")
        if modifications:
            results.append(f"   Thay đổi: {', '.join(modifications)}")
        else:
            results.append("   Không có thay đổi (đã được cấu hình)")
        
        return True, results
        
    except Exception as e:
        return False, [f"❌ Lỗi modify settings.json: {str(e)}"]

def bypass_version_check():
    """Bỏ qua kiểm tra phiên bản Cursor"""
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
                return False, "Không thể tắt Cursor. Vui lòng tắt thủ công trước khi bỏ qua kiểm tra phiên bản"
        
        all_results = []
        total_success = 0
        
        # 1. Chỉnh sửa product.json
        print("Đang chỉnh sửa product.json...")
        success, results = modify_product_json()
        all_results.extend([f"PRODUCT.JSON: {result}" for result in results])
        if success:
            total_success += 1
        
        # 2. Chỉnh sửa settings.json
        print("Đang chỉnh sửa settings.json...")
        success, results = modify_settings_json()
        all_results.extend([f"SETTINGS.JSON: {result}" for result in results])
        if success:
            total_success += 1
        
        # Tổng kết
        if total_success > 0:
            result_message = f"Bỏ qua kiểm tra phiên bản thành công ({total_success} file):\n" + "\n".join(all_results)
            result_message += "\n\n✅ Cursor sẽ không kiểm tra phiên bản khi khởi động."
            return True, result_message
        else:
            result_message = f"Bỏ qua kiểm tra phiên bản thất bại:\n" + "\n".join(all_results)
            return False, result_message
            
    except Exception as e:
        return False, f"Lỗi bỏ qua kiểm tra phiên bản: {str(e)}"
