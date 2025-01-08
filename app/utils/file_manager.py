import json
import os
from pathlib import Path
from datetime import datetime
import shutil

class FileManager:
    def __init__(self):
        self.storage_path = None
        self.app_name = None
        self.custom_paths = {
            "Cursor": None,
            "Windsurf": None
        }
        
    def set_app(self, app_name):
        self.app_name = app_name
        if self.custom_paths[app_name]:
            self.storage_path = Path(self.custom_paths[app_name]) / "storage.json"
        else:
            roaming_path = Path(os.getenv('APPDATA'))
            app_dir = roaming_path / app_name / "User" / "globalStorage"
            self.storage_path = app_dir / "storage.json"
        
        # Create directory structure if it doesn't exist
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create empty storage file if it doesn't exist
        if not self.storage_path.exists():
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=4)
    
    def set_custom_path(self, app_name, path):
        """Set custom storage path for an application"""
        self.custom_paths[app_name] = path
        if self.app_name == app_name:  # Update current path if it's the active app
            self.set_app(app_name)
    
    def get_storage_path(self, app_name):
        """Get current storage path for an application"""
        if self.custom_paths[app_name]:
            return str(Path(self.custom_paths[app_name]) / "storage.json")
        roaming_path = Path(os.getenv('APPDATA'))
        return str(roaming_path / app_name / "User" / "globalStorage" / "storage.json")
    
    def path_exists(self, app_name):
        """Check if storage path exists for an application"""
        path = Path(self.get_storage_path(app_name))
        return path.exists()
        
    def read_current_ids(self):
        if not self.storage_path:
            raise ValueError("No application selected!")
            
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    "telemetry.machineId": data.get("telemetry.machineId", "Not found"),
                    "telemetry.sqmId": data.get("telemetry.sqmId", "Not found"),
                    "telemetry.devDeviceId": data.get("telemetry.devDeviceId", "Not found"),
                    "telemetry.macMachineId": data.get("telemetry.macMachineId", "Not found")
                }
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "telemetry.machineId": "Not found",
                "telemetry.sqmId": "Not found",
                "telemetry.devDeviceId": "Not found",
                "telemetry.macMachineId": "Not found"
            }
        
    def create_backup(self):
        if not self.storage_path:
            raise ValueError("No application selected!")
            
        backup_path = self.storage_path.parent / f"storage.json.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(self.storage_path, backup_path)
        return backup_path
        
    def save_ids(self, new_ids):
        if not self.storage_path:
            raise ValueError("No application selected!")
            
        # Read existing data
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
            
        # Update with new IDs
        data.update(new_ids)
        
        # Save back to file
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
