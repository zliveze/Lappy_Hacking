import json
import os
from pathlib import Path
from datetime import datetime
import shutil
import traceback

class FileManager:
    def __init__(self):
        self._path_cache = {}
        self.app_name = "Cursor"
        self.storage_paths = {
            "Cursor": self._get_default_path("Cursor"),
            "Windsurf": self._get_default_path("Windsurf"),
            "AIDE": self._get_default_path("AIDE")
        }
        self.custom_paths = {app: None for app in self.storage_paths.keys()}
        
        # Define default paths
        self.default_paths = {
            "Cursor": self._get_default_path("Cursor"),
            "Windsurf": self._get_default_path("Windsurf"),
            "AIDE": self._get_default_path("AIDE")
        }
    
    def _get_default_path(self, app_name):
        """Get default path for an app with correct structure"""
        if app_name not in self._path_cache:
            base_folder = {
                "Cursor": "Cursor",
                "Windsurf": "Windsurf",
                "AIDE": "AIDE"
            }[app_name]
            
            path_components = [
                os.getenv('APPDATA'),
                base_folder,
                "User",  # Thêm thư mục User cho tất cả ứng dụng
                "globalStorage",
                "storage.json"
            ]
            
            self._path_cache[app_name] = os.path.join(*path_components)
        
        return self._path_cache[app_name]
    
    def _ensure_directory(self, path):
        """Ensure directory exists"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
    
    def _ensure_file(self, path):
        """Ensure file exists with valid JSON"""
        if not os.path.exists(path):
            with open(path, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=4)
    
    def set_app(self, app_name):
        """Set current app và chuẩn bị đường dẫn lưu trữ"""
        if app_name not in self.storage_paths:
            raise ValueError(f"Ứng dụng không được hỗ trợ: {app_name}")
        self.app_name = app_name

    def get_storage_path(self, app_name):
        """Lấy đường dẫn lưu trữ cho ứng dụng"""
        if self.custom_paths.get(app_name):
            return self.custom_paths[app_name]
        return self.storage_paths[app_name]
    
    def set_custom_path(self, app_name, custom_path):
        """Cập nhật đường dẫn tùy chỉnh với cấu trúc chuẩn"""
        if app_name not in self.storage_paths:
            raise ValueError(f"Ứng dụng không được hỗ trợ: {app_name}")
        
        # Tạo đường dẫn với cấu trúc User/globalStorage cho tất cả ứng dụng
        new_path = os.path.join(
            custom_path,
            "User",
            "globalStorage",
            "storage.json"
        )
        
        self.custom_paths[app_name] = new_path
        print(f"[CUSTOM PATH] Đã cập nhật {app_name} → {new_path}")
    
    def path_exists(self, app_name):
        """Check if storage path exists"""
        try:
            return os.path.exists(self.get_storage_path(app_name))
        except:
            return False
    
    def read_current_ids(self):
        """Read current IDs from storage"""
        if not self.storage_paths.get(self.app_name):
            raise ValueError("No application selected!")
        
        try:
            with open(self.get_storage_path(self.app_name), 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    key: data.get(key, "Not found")
                    for key in [
                        "telemetry.machineId",
                        "telemetry.sqmId",
                        "telemetry.devDeviceId",
                        "telemetry.macMachineId"
                    ]
                }
        except FileNotFoundError:
            return {key: "Not found" for key in [
                "telemetry.machineId",
                "telemetry.sqmId",
                "telemetry.devDeviceId",
                "telemetry.macMachineId"
            ]}
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in storage file")
    
    def create_backup(self):
        """Create backup of current storage"""
        if not self.storage_paths.get(self.app_name):
            raise ValueError("No application selected!")
        
        if not self.get_storage_path(self.app_name):
            raise FileNotFoundError("Storage file not found")
            
        backup_path = self.get_storage_path(self.app_name).parent / f"storage.json.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(self.get_storage_path(self.app_name), backup_path)
        return backup_path
    
    def save_ids(self, new_ids):
        """Lưu ID mới vào storage.json"""
        try:
            storage_path = self.get_storage_path(self.app_name)
            print(f"[DEBUG] Đường dẫn lưu: {storage_path}")
            
            # Đảm bảo thư mục tồn tại
            os.makedirs(os.path.dirname(storage_path), exist_ok=True)
            
            # Đọc dữ liệu cũ hoặc tạo mới
            if os.path.exists(storage_path):
                with open(storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {}
            
            # Chỉ cập nhật các trường telemetry
            telemetry_keys = [
                "telemetry.macMachineId",
                "telemetry.sqmId",
                "telemetry.machineId",
                "telemetry.devDeviceId"
            ]
            
            for key in telemetry_keys:
                if key in new_ids:
                    data[key] = new_ids[key]
            
            # Ghi file với định dạng đẹp
            with open(storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            print("[DEBUG] Lưu file thành công")
            return True
            
        except Exception as e:
            print(f"[SAVE ERROR] {traceback.format_exc()}")
            raise RuntimeError(f"Lỗi hệ thống: {str(e)}")
