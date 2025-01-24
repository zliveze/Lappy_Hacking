import json
import os
from pathlib import Path
from datetime import datetime
import shutil

class FileManager:
    def __init__(self):
        self.storage_path = None
        self.app_name = None
        
        # Cache paths
        self._path_cache = {}
        
        # Define default paths
        self.default_paths = {
            "Cursor": self._get_default_path("Code"),
            "Windsurf": self._get_default_path("Windsurf"),
            "AIDE": self._get_default_path("Aide")
        }
        
        # Custom paths
        self.custom_paths = {app: None for app in self.default_paths}
    
    def _get_default_path(self, app_name):
        """Get default path for an app"""
        if app_name not in self._path_cache:
            folder_name = "Code" if app_name == "Code" else app_name
            self._path_cache[app_name] = os.path.join(
                os.getenv('APPDATA'),
                folder_name,
                "User",
                "globalStorage",
                "storage.json"
            )
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
        """Set current app and prepare storage"""
        if app_name not in self.default_paths:
            raise ValueError(f"Unsupported application: {app_name}")
            
        self.app_name = app_name
        self.storage_path = Path(self.custom_paths[app_name] or self.default_paths[app_name])
        
        try:
            self._ensure_directory(str(self.storage_path))
            self._ensure_file(str(self.storage_path))
        except Exception as e:
            raise ValueError(f"Could not prepare storage: {str(e)}")
    
    def set_custom_path(self, app_name, path):
        """Set custom storage path"""
        if app_name not in self.default_paths:
            raise ValueError(f"Unsupported application: {app_name}")
            
        self.custom_paths[app_name] = path
        if self.app_name == app_name:
            self.set_app(app_name)
    
    def get_storage_path(self, app_name):
        """Get storage path for an app"""
        if app_name not in self.default_paths:
            raise ValueError(f"Unsupported application: {app_name}")
            
        return str(Path(self.custom_paths[app_name] or self.default_paths[app_name]))
    
    def path_exists(self, app_name):
        """Check if storage path exists"""
        try:
            return os.path.exists(self.get_storage_path(app_name))
        except:
            return False
    
    def read_current_ids(self):
        """Read current IDs from storage"""
        if not self.storage_path:
            raise ValueError("No application selected!")
        
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
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
        if not self.storage_path:
            raise ValueError("No application selected!")
        
        if not self.storage_path.exists():
            raise FileNotFoundError("Storage file not found")
            
        backup_path = self.storage_path.parent / f"storage.json.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(self.storage_path, backup_path)
        return backup_path
    
    def save_ids(self, new_ids):
        """Save new IDs to storage"""
        if not self.storage_path:
            raise ValueError("No application selected!")
        
        try:
            self._ensure_directory(str(self.storage_path))
            
            # Read existing data or create new
            try:
                with open(str(self.storage_path), 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                data = {}
            
            # Update with new IDs
            data.update(new_ids)
            
            # Save back to file
            with open(str(self.storage_path), 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
                
        except Exception as e:
            raise ValueError(f"Error saving IDs: {str(e)}")
