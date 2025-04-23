import os
import sys
import configparser
from colorama import Fore, Style
from utils import get_user_documents_path

# Emoji cho các thông báo
EMOJI = {
    "INFO": "ℹ️",
    "WARNING": "⚠️",
    "ERROR": "❌",
    "SUCCESS": "✅",
    "ADMIN": "🔒",
    "ARROW": "➡️",
    "USER": "👤",
    "KEY": "🔑",
    "SETTINGS": "⚙️",
    "RESET": "🔄",
    "FILE": "📄",
    "BACKUP": "💾",
    "VERSION": "🏷️"
}

# Biến lưu trữ cấu hình toàn cục
_config_cache = None

def get_config():
    """Lấy cấu hình từ file config.ini hoặc tạo mới nếu chưa tồn tại"""
    global _config_cache
    
    # Nếu đã có cache, trả về luôn
    if _config_cache is not None:
        return _config_cache
    
    # Tạo thư mục cấu hình nếu chưa tồn tại
    config_dir = os.path.join(get_user_documents_path(), ".lappy-lab")
    os.makedirs(config_dir, exist_ok=True)
    
    # Đường dẫn đến file cấu hình
    config_file = os.path.join(config_dir, "config.ini")
    
    # Tạo đối tượng ConfigParser
    config = configparser.ConfigParser()
    
    # Nếu file cấu hình đã tồn tại, đọc nó
    if os.path.exists(config_file):
        config.read(config_file)
    
    # Nếu không, tạo cấu hình mặc định
    else:
        # Cấu hình mặc định
        default_config = {
            'General': {
                'version': '4.0',
                'release_date': '23/04/2025',
                'check_update': 'True'
            },
            'WindowsPaths': {
                'storage_path': os.path.join(os.getenv("APPDATA", ""), "Cursor", "User", "globalStorage", "storage.json"),
                'sqlite_path': os.path.join(os.getenv("APPDATA", ""), "Cursor", "User", "globalStorage", "state.vscdb"),
                'machine_id_path': os.path.join(os.getenv("APPDATA", ""), "Cursor", "machineId"),
                'cursor_path': os.path.join(os.getenv("LOCALAPPDATA", ""), "Programs", "Cursor", "resources", "app"),
                'updater_path': os.path.join(os.getenv("LOCALAPPDATA", ""), "cursor-updater"),
                'update_yml_path': os.path.join(os.getenv("LOCALAPPDATA", ""), "Programs", "Cursor", "resources", "app-update.yml"),
                'product_json_path': os.path.join(os.getenv("LOCALAPPDATA", ""), "Programs", "Cursor", "resources", "app", "product.json")
            },
            'UI': {
                'theme': 'xp',
                'log_max_lines': '1000'
            }
        }
        
        # Thêm các phần vào config
        for section, options in default_config.items():
            if not config.has_section(section):
                config.add_section(section)
            for option, value in options.items():
                config.set(section, option, value)
        
        # Lưu cấu hình vào file
        with open(config_file, 'w') as f:
            config.write(f)
    
    # Lưu vào cache
    _config_cache = config
    
    return config

def save_config(config):
    """Lưu cấu hình vào file"""
    config_dir = os.path.join(get_user_documents_path(), ".lappy-lab")
    config_file = os.path.join(config_dir, "config.ini")
    
    with open(config_file, 'w') as f:
        config.write(f)
    
    # Cập nhật cache
    global _config_cache
    _config_cache = config

def print_config(config):
    """In cấu hình ra màn hình"""
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{EMOJI['SETTINGS']} Cấu hình hiện tại:{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    
    for section in config.sections():
        print(f"\n{Fore.YELLOW}[{section}]{Style.RESET_ALL}")
        for option in config.options(section):
            value = config.get(section, option)
            print(f"{Fore.GREEN}{option}{Style.RESET_ALL} = {Fore.CYAN}{value}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
