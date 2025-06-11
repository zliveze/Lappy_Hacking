# core/utils.py - Các hàm tiện ích cho Lappy Lab 4.1
import os
import sys
import platform
import socket
import psutil
import json
import sqlite3
from datetime import datetime
from pathlib import Path

def get_system_info():
    """Lấy thông tin hệ thống"""
    try:
        system_info = {
            'os': f"{platform.system()} {platform.release()}",
            'pc_name': socket.gethostname(),
            'architecture': platform.architecture()[0],
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'memory_total': f"{psutil.virtual_memory().total // (1024**3)} GB",
            'memory_available': f"{psutil.virtual_memory().available // (1024**3)} GB",
            'disk_usage': f"{psutil.disk_usage('/').percent:.1f}%" if platform.system() != 'Windows' else f"{psutil.disk_usage('C:').percent:.1f}%"
        }
        return system_info
    except Exception as e:
        return {
            'os': 'Unknown',
            'pc_name': 'Unknown',
            'architecture': 'Unknown',
            'processor': 'Unknown',
            'python_version': 'Unknown',
            'memory_total': 'Unknown',
            'memory_available': 'Unknown',
            'disk_usage': 'Unknown'
        }

def get_user_documents_path():
    """Lấy đường dẫn thư mục Documents của user"""
    try:
        if platform.system() == "Windows":
            return os.path.join(os.path.expanduser("~"), "Documents")
        elif platform.system() == "Darwin":  # macOS
            return os.path.join(os.path.expanduser("~"), "Documents")
        else:  # Linux
            return os.path.join(os.path.expanduser("~"), "Documents")
    except:
        return os.path.expanduser("~")

def get_cursor_paths():
    """Lấy các đường dẫn quan trọng của Cursor"""
    system = platform.system()
    paths = {}
    
    try:
        if system == "Windows":
            appdata = os.getenv("APPDATA")
            localappdata = os.getenv("LOCALAPPDATA")
            
            paths = {
                'storage_path': os.path.join(appdata, "Cursor", "User", "globalStorage", "storage.json"),
                'sqlite_path': os.path.join(appdata, "Cursor", "User", "globalStorage", "state.vscdb"),
                'machine_id_path': os.path.join(appdata, "Cursor", "machineId"),
                'session_storage_path': os.path.join(appdata, "Cursor", "Session Storage"),
                'cursor_path': os.path.join(localappdata, "Programs", "Cursor"),
                'updater_path': os.path.join(localappdata, "cursor-updater"),
                'config_path': os.path.join(appdata, "Cursor", "User", "settings.json")
            }
            
        elif system == "Darwin":  # macOS
            home = os.path.expanduser("~")
            paths = {
                'storage_path': os.path.join(home, "Library", "Application Support", "Cursor", "User", "globalStorage", "storage.json"),
                'sqlite_path': os.path.join(home, "Library", "Application Support", "Cursor", "User", "globalStorage", "state.vscdb"),
                'machine_id_path': os.path.join(home, "Library", "Application Support", "Cursor", "machineId"),
                'session_storage_path': os.path.join(home, "Library", "Application Support", "Cursor", "Session Storage"),
                'cursor_path': "/Applications/Cursor.app",
                'updater_path': os.path.join(home, "Library", "Application Support", "cursor-updater"),
                'config_path': os.path.join(home, "Library", "Application Support", "Cursor", "User", "settings.json")
            }
            
        else:  # Linux
            home = os.path.expanduser("~")
            config_base = os.path.join(home, ".config")
            
            # Tìm thư mục Cursor (có thể là "Cursor" hoặc "cursor")
            cursor_dir = None
            for dirname in ["Cursor", "cursor"]:
                potential_path = os.path.join(config_base, dirname)
                if os.path.exists(potential_path):
                    cursor_dir = potential_path
                    break
            
            if cursor_dir:
                paths = {
                    'storage_path': os.path.join(cursor_dir, "User", "globalStorage", "storage.json"),
                    'sqlite_path': os.path.join(cursor_dir, "User", "globalStorage", "state.vscdb"),
                    'machine_id_path': os.path.join(cursor_dir, "machineId"),
                    'session_storage_path': os.path.join(cursor_dir, "Session Storage"),
                    'cursor_path': "/usr/bin/cursor",  # Hoặc đường dẫn cài đặt khác
                    'updater_path': os.path.join(home, ".cursor-updater"),
                    'config_path': os.path.join(cursor_dir, "User", "settings.json")
                }
            else:
                paths = {}
                
    except Exception as e:
        print(f"Lỗi khi lấy đường dẫn Cursor: {str(e)}")
        paths = {}
    
    return paths

def check_file_exists(file_path):
    """Kiểm tra file có tồn tại không"""
    try:
        return os.path.exists(file_path) and os.path.isfile(file_path)
    except:
        return False

def check_directory_exists(dir_path):
    """Kiểm tra thư mục có tồn tại không"""
    try:
        return os.path.exists(dir_path) and os.path.isdir(dir_path)
    except:
        return False

def get_file_size(file_path):
    """Lấy kích thước file"""
    try:
        if check_file_exists(file_path):
            return os.path.getsize(file_path)
        return 0
    except:
        return 0

def format_file_size(size_bytes):
    """Format kích thước file"""
    try:
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.2f} {size_names[i]}"
    except:
        return "Unknown"

def read_json_file(file_path):
    """Đọc file JSON"""
    try:
        if check_file_exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"Lỗi đọc file JSON {file_path}: {str(e)}")
        return None

def write_json_file(file_path, data):
    """Ghi file JSON"""
    try:
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Lỗi ghi file JSON {file_path}: {str(e)}")
        return False

def backup_file(file_path, backup_suffix=None):
    """Tạo backup file"""
    try:
        if not check_file_exists(file_path):
            return False
        
        if backup_suffix is None:
            backup_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        backup_path = f"{file_path}.bak.{backup_suffix}"
        
        import shutil
        shutil.copy2(file_path, backup_path)
        return backup_path
    except Exception as e:
        print(f"Lỗi tạo backup file {file_path}: {str(e)}")
        return False

def restore_file(backup_path, original_path):
    """Khôi phục file từ backup"""
    try:
        if not check_file_exists(backup_path):
            return False
        
        import shutil
        shutil.copy2(backup_path, original_path)
        return True
    except Exception as e:
        print(f"Lỗi khôi phục file từ {backup_path}: {str(e)}")
        return False

def is_cursor_running():
    """Kiểm tra Cursor có đang chạy không"""
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            if 'cursor' in proc.info['name'].lower():
                return True
        return False
    except:
        return False

def kill_cursor_processes():
    """Tắt tất cả process Cursor"""
    try:
        killed_count = 0
        for proc in psutil.process_iter(['pid', 'name']):
            if 'cursor' in proc.info['name'].lower():
                try:
                    proc.terminate()
                    killed_count += 1
                except:
                    pass
        return killed_count
    except:
        return 0

def log_message(message, level="INFO"):
    """Ghi log message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"
    print(log_entry)
    return log_entry

def create_directory(dir_path):
    """Tạo thư mục"""
    try:
        os.makedirs(dir_path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Lỗi tạo thư mục {dir_path}: {str(e)}")
        return False

def delete_file(file_path):
    """Xóa file"""
    try:
        if check_file_exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Lỗi xóa file {file_path}: {str(e)}")
        return False

def delete_directory(dir_path):
    """Xóa thư mục"""
    try:
        if check_directory_exists(dir_path):
            import shutil
            shutil.rmtree(dir_path)
            return True
        return False
    except Exception as e:
        print(f"Lỗi xóa thư mục {dir_path}: {str(e)}")
        return False

def get_cursor_version():
    """Lấy phiên bản Cursor"""
    try:
        paths = get_cursor_paths()
        if 'cursor_path' in paths:
            # Thử đọc từ package.json hoặc version file
            version_files = [
                os.path.join(paths['cursor_path'], "package.json"),
                os.path.join(paths['cursor_path'], "resources", "app", "package.json"),
                os.path.join(paths['cursor_path'], "version")
            ]
            
            for version_file in version_files:
                if check_file_exists(version_file):
                    if version_file.endswith('.json'):
                        data = read_json_file(version_file)
                        if data and 'version' in data:
                            return data['version']
                    else:
                        with open(version_file, 'r') as f:
                            return f.read().strip()
        
        return "Unknown"
    except:
        return "Unknown"
